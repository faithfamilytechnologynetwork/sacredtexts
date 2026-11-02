// Sharded run artifacts on a static host (Cloudflare Pages). Browser-safe: no node imports.
//
// Pages rejects any single asset over 25 MiB, and the synthetic panel run's answers.jsonl is
// far larger. So the bake (vite/bakeRuns.ts) splits any artifact over SHARD_BYTES at line
// boundaries into parts next to a small manifest `<artifact>.parts.json`, and does NOT write
// the whole file. The dev endpoint never shards: it serves the whole artifact, so the client
// only reads a manifest after the whole-file fetch came back missing (a 404, or the SPA
// index.html a static host serves for an unknown path).
//
// The manifest pins the reassembly: the concatenated parts must match `bytes`, `sha256` and
// `rows` exactly, or the load fails loudly. A partial or stale deploy is never rendered.

/** Bake shards any artifact larger than this (20 MiB, under Pages' 25 MiB per-file cap). */
export const SHARD_BYTES = 20 * 1024 * 1024;

export interface ShardManifest {
  /** Part file names, in order, relative to the manifest's directory. */
  parts: string[];
  /** Byte length of the concatenation (= the dev endpoint's whole artifact). */
  bytes: number;
  /** Non-blank lines in the concatenation (what parseJsonl would read). */
  rows: number;
  /** Lowercase hex sha256 of the concatenation. */
  sha256: string;
}

export function manifestUrl(artifactUrl: string): string {
  return `${artifactUrl}.parts.json`;
}

export function partName(artifactName: string, index: number): string {
  return `${artifactName}.part${String(index).padStart(3, "0")}`;
}

/** Non-blank lines, the same rows parseJsonl reads. */
export function countRows(text: string): number {
  let n = 0;
  for (const line of text.split("\n")) if (line.trim()) n++;
  return n;
}

export type ShardFetch =
  | { ok: true; text: string }
  | { ok: false; kind: "http" | "malformed"; message: string };

function parseManifest(raw: unknown): ShardManifest | null {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return null;
  const m = raw as Record<string, unknown>;
  if (!Array.isArray(m.parts) || m.parts.length === 0) return null;
  if (!m.parts.every((p) => typeof p === "string" && p.length > 0 && !p.includes("/"))) return null;
  if (typeof m.bytes !== "number" || !Number.isInteger(m.bytes) || m.bytes < 0) return null;
  if (typeof m.rows !== "number" || !Number.isInteger(m.rows) || m.rows < 0) return null;
  if (typeof m.sha256 !== "string" || !/^[0-9a-f]{64}$/.test(m.sha256)) return null;
  return { parts: m.parts as string[], bytes: m.bytes, rows: m.rows, sha256: m.sha256 };
}

async function sha256Hex(bytes: Uint8Array<ArrayBuffer>): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, "0")).join("");
}

/**
 * Reassemble a sharded artifact from `<url>.parts.json`. Returns null when there is no
 * manifest (a 404 or the SPA's HTML fallback), so the caller keeps its original "missing".
 * Anything else that goes wrong is an error, never a partial artifact: a malformed manifest,
 * a part that is not served, or a concatenation whose size, sha256 or row count disagrees
 * with the manifest.
 */
export async function fetchSharded(fetcher: typeof fetch, url: string): Promise<ShardFetch | null> {
  const mUrl = manifestUrl(url);
  let res: Response;
  try {
    res = await fetcher(mUrl);
  } catch (e) {
    return { ok: false, kind: "http", message: `${mUrl}: ${(e as Error).message}` };
  }
  if (res.status === 404) return null;
  if (!res.ok) return { ok: false, kind: "http", message: `${mUrl}: HTTP ${res.status}` };
  let mText: string;
  try {
    mText = await res.text();
  } catch (e) {
    return { ok: false, kind: "http", message: `${mUrl}: ${(e as Error).message}` };
  }
  if (mText.trimStart().startsWith("<")) return null; // SPA fallback: no manifest here
  let manifest: ShardManifest | null;
  try {
    manifest = parseManifest(JSON.parse(mText));
  } catch {
    manifest = null;
  }
  if (!manifest) return { ok: false, kind: "malformed", message: `${mUrl}: not a shard manifest` };

  const dir = url.slice(0, url.lastIndexOf("/") + 1);
  const chunks: Uint8Array[] = [];
  for (const part of manifest.parts) {
    const pUrl = `${dir}${part}`;
    let pRes: Response;
    try {
      pRes = await fetcher(pUrl);
    } catch (e) {
      return { ok: false, kind: "http", message: `${pUrl}: ${(e as Error).message}` };
    }
    if (!pRes.ok) return { ok: false, kind: "malformed", message: `${pUrl}: shard part not served (HTTP ${pRes.status})` };
    let buf: ArrayBuffer;
    try {
      buf = await pRes.arrayBuffer();
    } catch (e) {
      return { ok: false, kind: "http", message: `${pUrl}: ${(e as Error).message}` };
    }
    chunks.push(new Uint8Array(buf));
  }
  if (!globalThis.crypto?.subtle) {
    // crypto.subtle exists only in a secure context (https, or localhost).
    return { ok: false, kind: "http", message: `${mUrl}: cannot verify shards here (crypto.subtle needs https or localhost)` };
  }
  const total = chunks.reduce((n, c) => n + c.byteLength, 0);
  if (total !== manifest.bytes) {
    return { ok: false, kind: "malformed", message: `${mUrl}: parts total ${total} bytes, manifest says ${manifest.bytes}` };
  }
  const whole = new Uint8Array(total);
  let at = 0;
  for (const c of chunks) {
    whole.set(c, at);
    at += c.byteLength;
  }
  const digest = await sha256Hex(whole);
  if (digest !== manifest.sha256) {
    return { ok: false, kind: "malformed", message: `${mUrl}: parts sha256 ${digest} does not match the manifest` };
  }
  let text: string;
  try {
    text = new TextDecoder("utf-8", { fatal: true }).decode(whole);
  } catch (e) {
    return { ok: false, kind: "malformed", message: `${mUrl}: parts are not UTF-8 (${(e as Error).message})` };
  }
  const rows = countRows(text);
  if (rows !== manifest.rows) {
    return { ok: false, kind: "malformed", message: `${mUrl}: parts hold ${rows} rows, manifest says ${manifest.rows}` };
  }
  return { ok: true, text };
}
