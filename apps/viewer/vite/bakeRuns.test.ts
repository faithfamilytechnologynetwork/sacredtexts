import { describe, it, expect, beforeAll, afterAll } from "vitest";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import type { AddressInfo } from "node:net";
import { createRunsHandler, listRuns } from "./runsEndpoint";
import {
  assertPagesReady,
  bakeRuns,
  callHandler,
  clientRunUrls,
  splitAtLines,
  staticPathFor,
  PAGES_MAX_FILE_BYTES,
  type BakeResult,
} from "./bakeRuns";
import { loadRun, loadSummary } from "../src/lib/localResults";
import { manifestUrl, type ShardManifest } from "../src/lib/shards";

// Byte parity between the dev endpoint and the baked static tree, over REAL HTTP on both sides:
//   dev    — createRunsHandler mounted at /runs the way vite.config.ts mounts it (Connect strips
//            the /runs prefix before the handler sees req.url);
//   static — a file server over the baked dist/ that copies Cloudflare's asset-server rules
//            (written independently of bakeRuns.ts, so the bake is not checking itself).

const SPA_SHELL = '<!doctype html><html><body><div id="root"></div></body></html>';

function devServer(runsDir: string): http.Server {
  const handler = createRunsHandler(runsDir);
  return http.createServer((req, res) => {
    const url = req.url ?? "/";
    if (url === "/runs" || url.startsWith("/runs/") || url.startsWith("/runs?")) {
      req.url = url.slice("/runs".length) || "/";
      handler(req, res);
      return;
    }
    res.statusCode = 404;
    res.end("not found");
  });
}

// Cloudflare's workers-shared asset server (decodePath / encodePath in assets.worker.js): each
// segment is decodeURIComponent'd, so %2F becomes a real separator; a path whose re-encoding
// differs from the request gets a 307 to the canonical form; an unknown path serves
// index.html with 200 (Pages' SPA mode, on whenever dist has no top-level 404.html).
const decodePath = (p: string) =>
  p
    .split("/")
    .map((x) => {
      try {
        return decodeURIComponent(x);
      } catch {
        return x;
      }
    })
    .join("/")
    .replace(/\/+/g, "/");
const encodePath = (p: string) =>
  p
    .split("/")
    .map((x) => encodeURIComponent(x))
    .join("/");

function cloudflareLikeStatic(distDir: string): http.Server {
  return http.createServer((req, res) => {
    const u = new URL(req.url ?? "/", "http://host");
    const decoded = decodePath(u.pathname);
    const file = path.join(distDir, ...decoded.split("/").filter(Boolean));
    let isFile = false;
    try {
      isFile = file.startsWith(distDir + path.sep) && fs.statSync(file).isFile();
    } catch {
      isFile = false;
    }
    if (isFile) {
      const canonical = encodePath(decoded);
      if (canonical !== u.pathname) {
        res.statusCode = 307;
        res.setHeader("Location", canonical + u.search);
        res.end();
        return;
      }
      res.end(fs.readFileSync(file));
      return;
    }
    res.setHeader("Content-Type", "text/html");
    res.end(fs.readFileSync(path.join(distDir, "index.html")));
  });
}

async function listen(server: http.Server): Promise<string> {
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  return `http://127.0.0.1:${(server.address() as AddressInfo).port}`;
}

async function close(server: http.Server): Promise<void> {
  await new Promise<void>((resolve) => server.close(() => resolve()));
}

async function get(url: string): Promise<{ status: number; body: Buffer }> {
  const res = await fetch(url);
  return { status: res.status, body: Buffer.from(await res.arrayBuffer()) };
}

/** Bake runsDir into a fresh dist (with an SPA shell), serve both sides, and return handles. */
async function setUp(runsDir: string, shardBytes?: number) {
  const dist = fs.mkdtempSync(path.join(os.tmpdir(), "bake-dist-"));
  fs.writeFileSync(path.join(dist, "index.html"), SPA_SHELL);
  const result = bakeRuns(runsDir, path.join(dist, "runs"), { shardBytes });
  const dev = devServer(runsDir);
  const stat = cloudflareLikeStatic(dist);
  const devBase = await listen(dev);
  const staticBase = await listen(stat);
  return {
    dist,
    result,
    devBase,
    staticBase,
    async tearDown() {
      await close(dev);
      await close(stat);
      fs.rmSync(dist, { recursive: true, force: true });
    },
  };
}

/**
 * For every URL the client can request: dev 200 ⇒ static serves the same bytes (whole, or
 * reassembled from its parts when sharded); dev 404 ⇒ static has no file (the SPA shell).
 * Returns how many URLs took each path, so callers can assert coverage.
 */
async function assertParity(runsDir: string, env: Awaited<ReturnType<typeof setUp>>) {
  const counts = { whole: 0, sharded: 0, absent: 0 };
  const sharded = new Set(env.result.sharded.map((s) => s.url));
  for (const url of clientRunUrls(runsDir)) {
    const dev = await get(`${env.devBase}/runs${url}`);
    const stat = await get(`${env.staticBase}/runs${url}`);
    if (dev.status === 404) {
      expect(stat.body.toString(), `${url}: dev 404s it, so static must not have a file`).toBe(SPA_SHELL);
      counts.absent++;
      continue;
    }
    expect(dev.status, url).toBe(200);
    if (sharded.has(url)) {
      // The whole file is not deployed; the parts concatenate to the dev bytes exactly.
      expect(stat.body.toString(), `${url}: a sharded artifact has no whole file`).toBe(SPA_SHELL);
      const m = await get(`${env.staticBase}/runs${manifestUrl(url)}`);
      expect(m.status).toBe(200);
      const manifest = JSON.parse(m.body.toString()) as ShardManifest;
      const dir = url.slice(0, url.lastIndexOf("/") + 1);
      const parts: Buffer[] = [];
      for (const p of manifest.parts) {
        const part = await get(`${env.staticBase}/runs${dir}${p}`);
        expect(part.status).toBe(200);
        expect(part.body.toString(), `${url}: part ${p} not served`).not.toBe(SPA_SHELL);
        parts.push(part.body);
      }
      expect(Buffer.concat(parts).equals(dev.body), `${url}: parts != dev bytes`).toBe(true);
      expect(manifest.bytes).toBe(dev.body.byteLength);
      counts.sharded++;
      continue;
    }
    expect(stat.status, url).toBe(200);
    expect(stat.body.equals(dev.body), `${url}: static bytes != dev bytes`).toBe(true);
    counts.whole++;
  }
  return counts;
}

// ---- fixture: real runs, an archive run, a run missing artifacts, a panel, and a gap ----

let root: string;
let runsDir: string;

function writeJsonl(file: string, rows: unknown[]): void {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, rows.map((r) => JSON.stringify(r)).join("\n") + "\n");
}

function writeRun(dir: string, model: string, ids: string[], generatedAt: string, trad = "Islam"): void {
  fs.mkdirSync(dir, { recursive: true });
  const source = { tradition: [trad], work: "Qur'an", version: "Tanzil", language: "ar", citation: "1:1" };
  const questions = ids.map((id) => ({ id, task: "retrieve_quote", prompt: `What is ${id}?`, expected: { text: "بِسْمِ ٱللَّهِ" }, source }));
  writeJsonl(path.join(dir, "questions.jsonl"), questions);
  writeJsonl(
    path.join(dir, "scores.jsonl"),
    ids.map((id, i) => ({ question_id: id, model_id: model, task: "retrieve_quote", metrics: { exact: i % 2, normalized: i % 2, token_f1: 0.5, correct: i % 2, outcome: i % 2 ? "correct" : "incorrect" } })),
  );
  writeJsonl(
    path.join(dir, "answers.jsonl"),
    ids.map((id) => ({ question_id: id, model_id: model, task: "retrieve_quote", answer: `بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ — ${id} ${"ـ".repeat(40)}`, question: questions.find((q) => q.id === id) })),
  );
  const cell = { n: ids.length, correct: Math.floor(ids.length / 2), incorrect: Math.ceil(ids.length / 2), refused: 0, accuracy: 0.5 };
  fs.writeFileSync(
    path.join(dir, "summary.json"),
    JSON.stringify({ generated_at: generatedAt, models: { [model]: { retrieve_quote: cell, _overall: cell } }, by_tradition: { [model]: { [trad]: { retrieve_quote: cell } } } }),
  );
}

beforeAll(() => {
  root = fs.mkdtempSync(path.join(os.tmpdir(), "bake-root-"));
  runsDir = path.join(root, "runs");
  writeRun(path.join(runsDir, "run-a"), "haiku", ["q1", "q2"], "2026-10-01T00:00:00Z");
  writeRun(path.join(runsDir, "archive", "old-2026-01-01"), "opus", ["q1", "q2", "q3"], "2026-01-01T00:00:00Z");
  // run-b has a summary (so it is indexed) but no other artifact: dev 404s three URLs.
  fs.mkdirSync(path.join(runsDir, "run-b"));
  fs.writeFileSync(path.join(runsDir, "run-b", "summary.json"), '{"models":{}}');
  // Panel: model folders with no summary of their own, nested base/<trad> results, and the
  // roster under items/for-test/<trad>/.
  const roster = ["p1", "p2", "p3", "p4"];
  for (const model of ["m1", "m2"]) {
    const dir = path.join(runsDir, model, "base", "islam");
    writeRun(dir, model, roster, "2026-10-20T00:00:00Z");
    fs.rmSync(path.join(dir, "questions.jsonl"));
  }
  writeJsonl(
    path.join(root, "items", "for-test", "islam", "questions.jsonl"),
    roster.map((id) => ({ id, task: "retrieve_quote", prompt: `What is ${id}?`, expected: { text: "بِسْمِ ٱللَّهِ" }, source: { tradition: ["Islam"], citation: id } })),
  );
  // A named panel folder (a `join_run.py --run-dir runs/rerun-…` rerun): its own virtual run,
  // kept out of the default panel.
  const rerun = path.join(runsDir, "rerun-2026-11-03", "m1", "base", "islam");
  writeRun(rerun, "m1", ["p1", "p2"], "2026-11-03T00:00:00Z");
  fs.rmSync(path.join(rerun, "questions.jsonl"));
  // A gap: answers saved with no summary (an unfinished collect), one roster row unsaved.
  writeJsonl(path.join(root, "items", "for-test", "judaism", "questions.jsonl"), [
    { id: "j1", task: "retrieve_quote", source: { tradition: ["Judaism"], citation: "Gen 1:1" } },
    { id: "j2", task: "retrieve_quote", source: { tradition: ["Judaism"], citation: "Gen 1:2" } },
  ]);
  writeJsonl(path.join(runsDir, "m2", "base", "judaism", "answers.jsonl"), [{ question_id: "j1", answer: "" }]);
});

afterAll(() => {
  fs.rmSync(root, { recursive: true, force: true });
});

describe("clientRunUrls", () => {
  it("covers _index, _gaps, and the four artifacts of every indexed run incl. both panels + archive", () => {
    const urls = clientRunUrls(runsDir);
    const ids = listRuns(runsDir).map((r) => r.id);
    expect(ids).toEqual(
      expect.arrayContaining(["panel", "rerun-2026-11-03", "run-a", "run-b", "archive/old-2026-01-01"]),
    );
    expect(urls).toContain("/rerun-2026-11-03/summary.json");
    expect(urls.slice(0, 3)).toEqual(["/_index", "/_gaps", "/_judge"]);
    expect(urls).toHaveLength(3 + 4 * ids.length);
    expect(urls).toContain("/panel/answers.jsonl");
    // Encoded exactly as the client encodes a run id (encodeURIComponent).
    expect(urls).toContain("/archive%2Fold-2026-01-01/summary.json");
  });
});

describe("staticPathFor", () => {
  it("decodes each segment like Cloudflare, so %2F becomes a directory", () => {
    expect(staticPathFor("/archive%2Fold-2026-01-01/summary.json")).toBe("archive/old-2026-01-01/summary.json");
    expect(staticPathFor("/_index")).toBe("_index");
  });

  it("refuses a URL that would escape or collapse the output tree", () => {
    expect(() => staticPathFor("/a%2F..%2F..%2Fx/summary.json")).toThrow(/confined/);
    expect(() => staticPathFor("/../x")).toThrow(/confined/);
    expect(() => staticPathFor("/a//b")).toThrow(/confined/);
  });
});

describe("splitAtLines", () => {
  it("cuts only after a newline, keeps every part within the limit, and loses no byte", () => {
    const body = Buffer.from("aaaa\nbbbbbb\ncc\nدد\n", "utf8");
    const parts = splitAtLines(body, 8);
    expect(parts.every((p) => p.byteLength <= 8)).toBe(true);
    expect(parts.slice(0, -1).every((p) => p[p.byteLength - 1] === 0x0a)).toBe(true);
    expect(Buffer.concat(parts).equals(body)).toBe(true);
  });

  it("fails loudly on a line longer than the limit", () => {
    expect(() => splitAtLines(Buffer.from("short\nthis line is far too long\n"), 8)).toThrow(/single line/);
  });
});

describe("bakeRuns: the static tree serves the dev endpoint's bytes for every client URL", () => {
  let env: Awaited<ReturnType<typeof setUp>>;
  let result: BakeResult;
  let shardBytes: number;

  beforeAll(async () => {
    // Half the panel's answers: the largest artifact (as in the real runs/) splits into parts,
    // while every other artifact, and every single line, stays under the limit.
    shardBytes = Math.floor(callHandler(createRunsHandler(runsDir), "/panel/answers.jsonl").body.byteLength / 2);
    env = await setUp(runsDir, shardBytes);
    result = env.result;
  });
  afterAll(async () => env?.tearDown());

  it("matches byte-for-byte: whole files, sharded parts, and 404s alike", async () => {
    const counts = await assertParity(runsDir, env);
    // 5 runs x 4 artifacts + _index + _gaps + _judge = 23 URLs: 1 sharded, 3 absent, 19 whole.
    expect(counts).toEqual({ whole: 19, sharded: 1, absent: 3 });
    expect(fs.existsSync(path.join(env.dist, "runs", "rerun-2026-11-03", "summary.json"))).toBe(true);
    expect(result.notFound.sort()).toEqual(["/run-b/answers.jsonl", "/run-b/questions.jsonl", "/run-b/scores.jsonl"]);
    expect(result.sharded.map((s) => s.url)).toEqual(["/panel/answers.jsonl"]);
    expect(result.sharded[0]!.parts).toBeGreaterThan(1);
  });

  it("bakes a non-empty gap list", async () => {
    const gaps = JSON.parse((await get(`${env.staticBase}/runs/_gaps`)).body.toString()) as { file: string }[];
    expect(gaps.map((g) => g.file)).toEqual([path.join("m2", "base", "judaism")]);
  });

  it("the client's loadRun reads the same run from the static host as from dev (panels + archive)", async () => {
    for (const id of ["panel", "rerun-2026-11-03", "archive/old-2026-01-01", "run-a"]) {
      const base = `/runs/${encodeURIComponent(id)}`;
      const fromDev = await loadRun(`${env.devBase}${base}`, fetch);
      const fromStatic = await loadRun(`${env.staticBase}${base}`, fetch);
      expect(fromDev.ok, id).toBe(true);
      expect(fromStatic, id).toEqual(fromDev);
    }
    // run-b is missing artifacts on both hosts, and both report it the same way.
    const devB = await loadRun(`${env.devBase}/runs/run-b`, fetch);
    const staticB = await loadRun(`${env.staticBase}/runs/run-b`, fetch);
    expect(devB.ok).toBe(false);
    expect(staticB.ok).toBe(false);
    if (!devB.ok && !staticB.ok) expect(staticB.kind).toBe(devB.kind);
    expect((await loadSummary(`${env.staticBase}/runs/panel`, fetch)).ok).toBe(true);
  });

  it("re-baking replaces the tree (a stale file from a previous bake does not survive)", () => {
    const out = path.join(env.dist, "runs");
    fs.writeFileSync(path.join(out, "stale.json"), "{}");
    bakeRuns(runsDir, out, { shardBytes });
    expect(fs.existsSync(path.join(out, "stale.json"))).toBe(false);
  });
});

describe("assertPagesReady", () => {
  it("rejects a file over 25 MiB and a top-level 404.html; accepts a clean dist", () => {
    const dist = fs.mkdtempSync(path.join(os.tmpdir(), "pages-ready-"));
    try {
      fs.writeFileSync(path.join(dist, "index.html"), SPA_SHELL);
      expect(() => assertPagesReady(dist)).not.toThrow();
      fs.writeFileSync(path.join(dist, "404.html"), "x");
      expect(() => assertPagesReady(dist)).toThrow(/SPA fallback/);
      fs.rmSync(path.join(dist, "404.html"));
      fs.mkdirSync(path.join(dist, "runs"));
      fs.writeFileSync(path.join(dist, "runs", "big.jsonl"), Buffer.alloc(PAGES_MAX_FILE_BYTES + 1));
      expect(() => assertPagesReady(dist)).toThrow(/runs\/big\.jsonl.*25 MiB/);
    } finally {
      fs.rmSync(dist, { recursive: true, force: true });
    }
  });
});

// The committed evidence itself, at the production shard size: every client URL matches dev,
// and the result fits Pages' per-file limit. This is what `pnpm build:pages` ships.
describe("bakeRuns over the repo's real runs/", () => {
  const realRuns = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../../runs");
  let env: Awaited<ReturnType<typeof setUp>>;

  beforeAll(async () => {
    env = await setUp(realRuns);
  }, 120_000);
  afterAll(async () => env?.tearDown());

  it("is byte-identical to the dev endpoint and deployable to Pages", async () => {
    expect(listRuns(realRuns).map((r) => r.id)).toContain("panel");
    const counts = await assertParity(realRuns, env);
    expect(counts.whole + counts.sharded).toBe(env.result.baked.length);
    expect(() => assertPagesReady(env.dist)).not.toThrow();
  }, 120_000);
});
