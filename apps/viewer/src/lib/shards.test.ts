import { describe, it, expect, afterEach, vi } from "vitest";
import { createHash } from "node:crypto";
import { countRows, fetchSharded, manifestUrl, partName, type ShardManifest } from "./shards";
import { loadRun } from "./localResults";
import { sampleAnswersJsonl, sampleQuestionsJsonl, sampleScoresJsonl, sampleSummary } from "../local/sample";

// A static host: exact-path files with real Responses; anything else is the SPA shell (200 HTML),
// which is what Pages serves for an unknown path.
const SHELL = '<!doctype html><div id="root"></div>';
function host(files: Record<string, string>, opts: { notFound404?: boolean } = {}): typeof fetch {
  return (async (url: string) => {
    if (url in files) return new Response(files[url]);
    return opts.notFound404 ? new Response("not found", { status: 404 }) : new Response(SHELL, { headers: { "Content-Type": "text/html" } });
  }) as unknown as typeof fetch;
}

/** Shard `text` into parts of the given line counts, returning the files a bake would write. */
function shard(url: string, text: string, linesPerPart: number[], tamper: Partial<ShardManifest> = {}) {
  const lines = text.split(/(?<=\n)/);
  const files: Record<string, string> = {};
  const name = url.slice(url.lastIndexOf("/") + 1);
  const dir = url.slice(0, url.lastIndexOf("/") + 1);
  const parts: string[] = [];
  let at = 0;
  linesPerPart.forEach((n, i) => {
    parts.push(partName(name, i));
    files[`${dir}${partName(name, i)}`] = lines.slice(at, at + n).join("");
    at += n;
  });
  const bytes = Buffer.byteLength(text, "utf8");
  const manifest: ShardManifest = {
    parts,
    bytes,
    rows: countRows(text),
    sha256: createHash("sha256").update(text, "utf8").digest("hex"),
    ...tamper,
  };
  files[manifestUrl(url)] = JSON.stringify(manifest);
  return files;
}

const URL_ = "/runs/panel/answers.jsonl";
const TEXT = '{"a":"بِسْمِ"}\n{"b":2}\n\n{"c":3}\n';

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("fetchSharded", () => {
  it("reassembles parts into the exact original text", async () => {
    const res = await fetchSharded(host(shard(URL_, TEXT, [1, 2, 1])), URL_);
    expect(res).toEqual({ ok: true, text: TEXT });
  });

  it("returns null (no shards) when the manifest is the SPA shell or a 404", async () => {
    expect(await fetchSharded(host({}), URL_)).toBeNull();
    expect(await fetchSharded(host({}, { notFound404: true }), URL_)).toBeNull();
  });

  it("fails loudly on a manifest that does not match the parts (sha256, bytes, rows)", async () => {
    const badSha = await fetchSharded(host(shard(URL_, TEXT, [2, 2], { sha256: "0".repeat(64) })), URL_);
    expect(badSha).toMatchObject({ ok: false, kind: "malformed", message: expect.stringMatching(/sha256/) });
    const badBytes = await fetchSharded(host(shard(URL_, TEXT, [2, 2], { bytes: 3 })), URL_);
    expect(badBytes).toMatchObject({ ok: false, kind: "malformed", message: expect.stringMatching(/bytes/) });
    const badRows = await fetchSharded(host(shard(URL_, TEXT, [2, 2], { rows: 99 })), URL_);
    expect(badRows).toMatchObject({ ok: false, kind: "malformed", message: expect.stringMatching(/rows/) });
  });

  it("fails loudly when a part is not served (404, or the SPA shell in its place)", async () => {
    const files = shard(URL_, TEXT, [2, 2]);
    delete files[`/runs/panel/${partName("answers.jsonl", 1)}`];
    expect(await fetchSharded(host(files, { notFound404: true }), URL_)).toMatchObject({ ok: false, kind: "malformed" });
    // On Pages the missing part is the 200 SPA shell; the byte/sha check catches it.
    expect(await fetchSharded(host(files), URL_)).toMatchObject({ ok: false, kind: "malformed" });
  });

  it("rejects a manifest that is not a shard manifest", async () => {
    for (const body of ["{}", '{"parts":[],"bytes":0,"rows":0,"sha256":"x"}', '{"parts":["../x"],"bytes":1,"rows":1,"sha256":"' + "a".repeat(64) + '"}', "not json"]) {
      const res = await fetchSharded(host({ [manifestUrl(URL_)]: body }), URL_);
      expect(res, body).toMatchObject({ ok: false, kind: "malformed" });
    }
  });

  it("reports, not throws, when crypto.subtle is unavailable (a non-secure origin)", async () => {
    vi.stubGlobal("crypto", {});
    const res = await fetchSharded(host(shard(URL_, TEXT, [2, 2])), URL_);
    expect(res).toMatchObject({ ok: false, message: expect.stringMatching(/crypto\.subtle/) });
  });
});

describe("loadRun on a static host with a sharded artifact", () => {
  const base = "/runs/panel";
  const whole = {
    [`${base}/summary.json`]: JSON.stringify(sampleSummary),
    [`${base}/scores.jsonl`]: sampleScoresJsonl,
    [`${base}/questions.jsonl`]: sampleQuestionsJsonl,
  };

  it("loads exactly what the unsharded artifact loads", async () => {
    const answersUrl = `${base}/answers.jsonl`;
    const plain = await loadRun(base, host({ ...whole, [answersUrl]: sampleAnswersJsonl }));
    const sharded = await loadRun(base, host({ ...whole, ...shard(answersUrl, sampleAnswersJsonl, [2, 1, 99]) }));
    expect(plain.ok).toBe(true);
    expect(sharded).toEqual(plain);
  });

  it("keeps the original 'missing' when there is neither a whole file nor a manifest", async () => {
    const res = await loadRun(base, host(whole));
    expect(res).toMatchObject({ ok: false, kind: "missing", message: expect.stringContaining(`${base}/answers.jsonl`) });
  });
});
