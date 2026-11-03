// Bake the dev run endpoint into static files for a static host (Cloudflare Pages).
// node-only, like runsEndpoint.ts beside it; the CLI is scripts/bake-runs.ts.
//
// In dev, createRunsHandler computes /runs/* on the fly: the _index, the _gaps list, the
// synthetic panel run, and confined copies of each real run's artifacts. A static host has no
// such endpoint, so the bake asks the SAME handler for every URL the client can request and
// writes each answer to disk at the path a static host will look up. Driving the handler
// (instead of re-deriving its routing) keeps the baked tree byte-identical to dev.
//
// The one deliberate difference is size. Pages rejects any file over 25 MiB, so an artifact
// over SHARD_BYTES is written as line-boundary parts plus a manifest (src/lib/shards.ts), and
// the client reassembles them. A URL the handler 404s is left absent, as it is in dev.

import fs from "node:fs";
import path from "node:path";
import { createHash } from "node:crypto";
import { createRunsHandler, listRuns } from "./runsEndpoint";
import { SHARD_BYTES, countRows, manifestUrl, partName, type ShardManifest } from "../src/lib/shards";

/** The four artifacts the client fetches per run (loadRun; loadSummary reads the first). */
export const RUN_ARTIFACTS = ["summary.json", "scores.jsonl", "answers.jsonl", "questions.jsonl"] as const;

/** The computed collections the client fetches: fetchRunIndex and GapsPage. */
export const COLLECTION_URLS = ["/_index", "/_gaps", "/_judge"] as const;

/** Cloudflare Pages' per-file limit. */
export const PAGES_MAX_FILE_BYTES = 25 * 1024 * 1024;

/**
 * Every /runs URL the client can request, relative to the /runs mount (the form the handler
 * receives once Connect strips the prefix). Run ids are encoded exactly as the client encodes
 * them (`encodeURIComponent`), so an `archive/<name>` id arrives as `archive%2F<name>`.
 * listRuns already includes the synthetic panel run whenever buildPanel finds one, and the
 * gap list is the single `/_gaps` collection.
 */
export function clientRunUrls(runsDir: string): string[] {
  const urls: string[] = [...COLLECTION_URLS];
  for (const run of listRuns(runsDir)) {
    const base = `/${encodeURIComponent(run.id)}`;
    for (const name of RUN_ARTIFACTS) urls.push(`${base}/${name}`);
  }
  return urls;
}

/**
 * The file a static host serves for `url`. This copies Cloudflare's asset server, which splits
 * the path on `/`, decodes each segment with decodeURIComponent, and rejoins it. So
 * `/archive%2Fx/summary.json` is the file `archive/x/summary.json`. Pages answers the encoded
 * form with a 307 to that path, and fetch follows it. Throws on any path that would not be
 * confined to the output directory.
 */
export function staticPathFor(url: string): string {
  if (!url.startsWith("/")) throw new Error(`not an absolute /runs URL: ${url}`);
  const rel = url
    .slice(1)
    .split("/")
    .map((s) => decodeURIComponent(s))
    .join("/");
  const parts = rel.split("/");
  if (parts.some((p) => p === "" || p === "." || p === "..")) {
    throw new Error(`URL ${url} does not map to a confined file path (${rel})`);
  }
  return rel;
}

type Handler = ReturnType<typeof createRunsHandler>;

/** One synchronous request to the dev handler, with the bytes it would put on the wire. */
export function callHandler(handler: Handler, url: string): { status: number; body: Buffer } {
  let body: Buffer | undefined;
  const res = {
    statusCode: 200,
    setHeader() {},
    end(chunk?: unknown) {
      if (chunk === undefined) body = Buffer.alloc(0);
      else if (Buffer.isBuffer(chunk)) body = chunk;
      else if (typeof chunk === "string") body = Buffer.from(chunk, "utf8");
      else throw new Error(`handler ended ${url} with an unexpected body type`);
    },
  };
  handler({ url }, res as never);
  if (body === undefined) throw new Error(`handler did not answer ${url}`);
  return { status: res.statusCode, body };
}

/** Split at line boundaries into chunks of at most `max` bytes; a longer line is an error. */
export function splitAtLines(body: Buffer, max: number): Buffer[] {
  const parts: Buffer[] = [];
  let start = 0;
  while (body.byteLength - start > max) {
    const cut = body.lastIndexOf(0x0a, start + max - 1);
    if (cut < start) throw new Error(`a single line is longer than ${max} bytes; cannot shard at a line boundary`);
    parts.push(body.subarray(start, cut + 1));
    start = cut + 1;
  }
  parts.push(body.subarray(start));
  return parts;
}

export interface BakeResult {
  /** Every URL baked, whole or sharded. */
  baked: string[];
  /** URLs written as parts + manifest instead of one file. */
  sharded: { url: string; bytes: number; parts: number }[];
  /** URLs the dev endpoint answers 404; left absent, so both hosts read them as missing. */
  notFound: string[];
}

/**
 * Bake every client URL into `outDir` (replaced wholesale: it is generated output). Files are
 * written exclusively, so two URLs that map to one path fail instead of overwriting.
 */
export function bakeRuns(runsDir: string, outDir: string, opts: { shardBytes?: number } = {}): BakeResult {
  const shardBytes = opts.shardBytes ?? SHARD_BYTES;
  const handler = createRunsHandler(runsDir);
  const result: BakeResult = { baked: [], sharded: [], notFound: [] };
  fs.rmSync(outDir, { recursive: true, force: true });
  fs.mkdirSync(outDir, { recursive: true });

  for (const url of clientRunUrls(runsDir)) {
    const { status, body } = callHandler(handler, url);
    if (status === 404) {
      result.notFound.push(url);
      continue;
    }
    if (status !== 200) throw new Error(`dev endpoint answered ${status} for /runs${url}: ${body.toString("utf8")}`);
    const dest = path.join(outDir, ...staticPathFor(url).split("/"));
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    result.baked.push(url);

    if (body.byteLength <= shardBytes) {
      fs.writeFileSync(dest, body, { flag: "wx" });
      continue;
    }
    // Only run artifacts go through fetchArtifact, which knows how to reassemble parts.
    if ((COLLECTION_URLS as readonly string[]).includes(url)) {
      throw new Error(`/runs${url} is ${body.byteLength} bytes; collections cannot be sharded`);
    }
    const name = path.basename(dest);
    const chunks = splitAtLines(body, shardBytes);
    const manifest: ShardManifest = {
      parts: chunks.map((_, i) => partName(name, i)),
      bytes: body.byteLength,
      rows: countRows(body.toString("utf8")),
      sha256: createHash("sha256").update(body).digest("hex"),
    };
    chunks.forEach((chunk, i) => {
      fs.writeFileSync(path.join(path.dirname(dest), manifest.parts[i]!), chunk, { flag: "wx" });
    });
    fs.writeFileSync(path.join(outDir, ...staticPathFor(manifestUrl(url)).split("/")), JSON.stringify(manifest), {
      flag: "wx",
    });
    result.sharded.push({ url, bytes: body.byteLength, parts: chunks.length });
  }
  return result;
}

/**
 * Fail loudly if `distDir` cannot go to Cloudflare Pages as built: any file over the 25 MiB
 * limit, or a top-level 404.html. With a 404.html, Pages stops serving index.html for unknown
 * paths, and every deep link (/standings, /run/...) would 404.
 */
export function assertPagesReady(distDir: string): void {
  const problems: string[] = [];
  if (!fs.existsSync(path.join(distDir, "index.html"))) problems.push("no index.html (run vite build first)");
  if (fs.existsSync(path.join(distDir, "404.html"))) {
    problems.push("404.html at the root turns off Pages' SPA fallback, so deep links would 404");
  }
  const walk = (dir: string) => {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      const p = path.join(dir, e.name);
      if (e.isDirectory()) walk(p);
      else if (e.isFile()) {
        const size = fs.statSync(p).size;
        if (size > PAGES_MAX_FILE_BYTES) {
          problems.push(`${path.relative(distDir, p)} is ${(size / 1048576).toFixed(2)} MiB (Pages limit 25 MiB)`);
        }
      }
    }
  };
  walk(distDir);
  if (problems.length > 0) throw new Error(`dist is not deployable to Cloudflare Pages:\n  ${problems.join("\n  ")}`);
}
