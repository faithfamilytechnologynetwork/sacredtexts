import { describe, it, expect, beforeAll, afterAll } from "vitest";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { listRuns, resolveRunFile, createRunsHandler, collectGaps, negativeKind } from "./runsEndpoint";

let tmp: string; // the runs root
let outside: string; // a dir outside runs/, the target of symlink-escape attempts
let symlinked = false;

beforeAll(() => {
  tmp = fs.mkdtempSync(path.join(os.tmpdir(), "runs-"));
  outside = fs.mkdtempSync(path.join(os.tmpdir(), "outside-"));
  // a valid run (has summary.json)
  fs.mkdirSync(path.join(tmp, "run-a"));
  fs.writeFileSync(path.join(tmp, "run-a", "summary.json"), '{"models":{}}');
  // a directory WITHOUT summary.json — must not be listed
  fs.mkdirSync(path.join(tmp, "not-a-run"));
  // a secret outside the root, and a symlink under runs/ pointing at it
  fs.writeFileSync(path.join(outside, "secret.json"), '{"secret":true}');
  // a run dir whose summary.json is itself a SYMLINK — must not be indexed
  fs.mkdirSync(path.join(tmp, "symsummary"));
  try {
    fs.symlinkSync(outside, path.join(tmp, "escape"), "dir");
    // an IN-root symlink (points at a real run inside the root) — still rejected, since the
    // requirement is to never traverse a symlink, not only escaping ones.
    fs.symlinkSync(path.join(tmp, "run-a"), path.join(tmp, "inlink"), "dir");
    // a symlinked summary.json pointing at the outside secret
    fs.symlinkSync(path.join(outside, "secret.json"), path.join(tmp, "symsummary", "summary.json"), "file");
    symlinked = true;
  } catch {
    symlinked = false; // symlinks may be unavailable on some platforms
  }
});

afterAll(() => {
  fs.rmSync(tmp, { recursive: true, force: true });
  fs.rmSync(outside, { recursive: true, force: true });
});

// A minimal Connect-style response double.
function fakeRes() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const res: any = {
    statusCode: 200,
    headers: {} as Record<string, string>,
    body: undefined as unknown,
    setHeader(k: string, v: string) {
      this.headers[k] = v;
    },
    end(b?: unknown) {
      this.body = b;
    },
  };
  return res;
}

describe("runsEndpoint listRuns", () => {
  it("lists only subdirectories containing a readable, non-symlinked summary.json", () => {
    const ids = listRuns(tmp).map((r) => r.id);
    expect(ids).toContain("run-a");
    expect(ids).not.toContain("not-a-run");
    expect(ids).not.toContain("escape"); // a symlink entry is not a directory listing target
    if (symlinked) expect(ids).not.toContain("symsummary"); // summary.json is a symlink
  });

  it("lists a dated run under archive/ and skips an archive child with no summary", () => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "archive-"));
    try {
      fs.mkdirSync(path.join(root, "archive", "original-2026-10-21"), { recursive: true });
      fs.writeFileSync(path.join(root, "archive", "original-2026-10-21", "summary.json"), "{}");
      fs.mkdirSync(path.join(root, "archive", "for-test"));
      const ids = listRuns(root).map((r) => r.id);
      expect(ids).toContain("archive/original-2026-10-21");
      expect(ids).not.toContain("archive");
      expect(ids).not.toContain("archive/for-test");
    } finally {
      fs.rmSync(root, { recursive: true, force: true });
    }
  });

  it("returns [] for a nonexistent root (the empty state, not a throw)", () => {
    expect(listRuns(path.join(tmp, "does-not-exist"))).toEqual([]);
  });

  it("surfaces summary.generated_at and orders by recency, not mtime (Issue #7)", () => {
    // A temp root of its own so the collapsed-mtime scenario is isolated from run-a above.
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "recency-"));
    try {
      // Two runs; `older` has the newer generated_at, `newer-by-id`... has an older one. We
      // then touch both to the SAME mtime (the fresh-clone collapse) so only generated_at
      // can order them correctly.
      fs.mkdirSync(path.join(root, "z-run-2026-10-10"));
      fs.writeFileSync(
        path.join(root, "z-run-2026-10-10", "summary.json"),
        JSON.stringify({ models: {}, generated_at: "2026-10-12T00:00:00+00:00" }),
      );
      fs.mkdirSync(path.join(root, "a-run-2026-10-10"));
      fs.writeFileSync(
        path.join(root, "a-run-2026-10-10", "summary.json"),
        JSON.stringify({ models: {}, generated_at: "2026-10-11T00:00:00+00:00" }),
      );
      const when = new Date("2020-01-01T00:00:00Z"); // identical mtime for both dirs
      fs.utimesSync(path.join(root, "z-run-2026-10-10"), when, when);
      fs.utimesSync(path.join(root, "a-run-2026-10-10"), when, when);

      const runs = listRuns(root);
      // Newer generated_at first, even though its id ("z-…") would sort LAST by id-asc.
      expect(runs.map((r) => r.id)).toEqual(["z-run-2026-10-10", "a-run-2026-10-10"]);
      expect(runs[0]!.generatedAt).toBe("2026-10-12T00:00:00+00:00");
    } finally {
      fs.rmSync(root, { recursive: true, force: true });
    }
  });

  it("lists a run whose summary.json has no generated_at (generatedAt undefined)", () => {
    // run-a's summary ('{"models":{}}') carries no generated_at — still listed, just without it.
    const entry = listRuns(tmp).find((r) => r.id === "run-a");
    expect(entry).toBeDefined();
    expect(entry!.generatedAt).toBeUndefined();
  });

  it("rolls nested runs/<model>/base/**/summary.json into one panel run", () => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "panel-"));
    try {
      const cell = (correct: number, incorrect: number) => ({
        n: correct + incorrect,
        accuracy: correct / (correct + incorrect),
        coverage: 1,
        correct,
        incorrect,
        refused: 0,
        refused_rate: 0,
      });
      const a = path.join(root, "haiku", "base", "christianity", "english", "population");
      const b = path.join(root, "haiku", "base", "judaism", "english", "population");
      fs.mkdirSync(a, { recursive: true });
      fs.mkdirSync(b, { recursive: true });
      fs.writeFileSync(
        path.join(a, "summary.json"),
        JSON.stringify({
          models: { haiku: { retrieve_quote: cell(8, 2), _overall: cell(8, 2) } },
          by_tradition: { haiku: { Christianity: { retrieve_quote: cell(8, 2), _overall: cell(8, 2) } } },
          generated_at: "2026-11-02T19:00:00+00:00",
          usage: { per_model: { haiku: { calls: 10, in: 100, out: 50 } }, total: { calls: 10, in: 100, out: 50 } },
        }),
      );
      fs.writeFileSync(
        path.join(b, "summary.json"),
        JSON.stringify({
          models: { haiku: { retrieve_quote: cell(1, 9), _overall: cell(1, 9) } },
          by_tradition: { haiku: { Judaism: { retrieve_quote: cell(1, 9), _overall: cell(1, 9) } } },
          generated_at: "2026-11-02T20:00:00+00:00",
          usage: { per_model: { haiku: { calls: 10, in: 40, out: 10 } }, total: { calls: 10, in: 40, out: 10 } },
        }),
      );
      fs.writeFileSync(path.join(a, "scores.jsonl"), '{"question_id":"q1"}\n');
      const ids = listRuns(root).map((r) => r.id);
      expect(ids).toContain("panel");
      expect(ids).not.toContain("haiku");
      const res = fakeRes();
      createRunsHandler(root)({ url: "/panel/summary.json" }, res);
      const body = JSON.parse(String(res.body)) as {
        models: { haiku: { _overall: { n: number; correct: number; accuracy: number } } };
        by_tradition: { haiku: Record<string, unknown> };
        usage: { total: { calls: number } };
        generated_at: string;
      };
      expect(body.models.haiku._overall).toMatchObject({ n: 20, correct: 9, accuracy: 0.45 });
      expect(Object.keys(body.by_tradition.haiku).sort()).toEqual(["Christianity", "Judaism"]);
      expect(body.usage.total.calls).toBe(20);
      expect(body.generated_at).toBe("2026-11-02T20:00:00+00:00");
      const scores = fakeRes();
      createRunsHandler(root)({ url: "/panel/scores.jsonl" }, scores);
      expect(String(scores.body)).toContain("q1");
    } finally {
      fs.rmSync(root, { recursive: true, force: true });
    }
  });
});

describe("runsEndpoint resolveRunFile confinement", () => {
  it("resolves a normal file within the root", () => {
    const f = resolveRunFile(tmp, "run-a/summary.json");
    expect(f).not.toBeNull();
    expect(fs.readFileSync(f!, "utf8")).toContain("models");
  });

  it("rejects path traversal that escapes the root", () => {
    expect(resolveRunFile(tmp, `../${path.basename(outside)}/secret.json`)).toBeNull();
  });

  it("rejects a symlink under runs/ that resolves outside the root", () => {
    if (!symlinked) return; // skip where symlinks are unavailable
    expect(resolveRunFile(tmp, "escape/secret.json")).toBeNull();
  });

  it("rejects an in-root symlink component (no symlink is ever traversed)", () => {
    if (!symlinked) return;
    // "inlink" points at run-a inside the root, yet is still rejected.
    expect(resolveRunFile(tmp, "inlink/summary.json")).toBeNull();
  });
});

describe("negativeKind", () => {
  it("splits an alphabet check from the two hard canon checks", () => {
    expect(negativeKind("pa", "Sikhism", "Islam")).toBe("Different script");
    expect(negativeKind("en", "Book of Mormon", "Encyclicals")).toBe("Book of Mormon shown an encyclical");
    expect(negativeKind("he", "Judaism", "Christianity")).toBe("Talmud shown the Bible");
  });
});

describe("collectGaps", () => {
  it("lists unsaved questions on a file with no summary, and empty answers", () => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "gaps-"));
    const qdir = fs.mkdtempSync(path.join(os.tmpdir(), "q-"));
    try {
      const run = path.join(root, "haiku", "base", "islam", "english", "population");
      fs.mkdirSync(run, { recursive: true });
      const questions = path.join(qdir, "items", "for-test", "islam", "english", "population", "questions.jsonl");
      fs.mkdirSync(path.dirname(questions), { recursive: true });
      fs.writeFileSync(
        questions,
        [
          JSON.stringify({ id: "kept", task: "retrieve_quote", source: { tradition: ["Islam"], citation: "1:1" } }),
          JSON.stringify({ id: "gone", task: "cite_passage", source: { tradition: ["Islam"], citation: "2:2" } }),
        ].join("\n") + "\n",
      );
      fs.writeFileSync(
        path.join(run, "answers.jsonl"),
        JSON.stringify({ question_id: "kept", task: "retrieve_quote", answer: "text", question: { source: { tradition: ["Islam"], citation: "1:1" } } }) + "\n" +
          JSON.stringify({ question_id: "blank", task: "verify_source", answer: "  ", question: { source: { tradition: ["Islam"], citation: "3:3" } } }) + "\n",
      );
      // questionsForSummary resolves ../items/for-test from the runs root. Point the
      // fixture's sibling items tree at the questions we just wrote by using a runs
      // root whose parent contains items/for-test. Rebuild under qdir.
      const runs = path.join(qdir, "runs");
      const dest = path.join(runs, "haiku", "base", "islam", "english", "population");
      fs.mkdirSync(dest, { recursive: true });
      fs.copyFileSync(path.join(run, "answers.jsonl"), path.join(dest, "answers.jsonl"));
      const gaps = collectGaps(runs);
      expect(gaps).toHaveLength(1);
      expect(gaps[0]!.missing.map((m) => m.id)).toEqual(["gone"]);
      expect(gaps[0]!.missing[0]!.citation).toBe("2:2");
      expect(gaps[0]!.empty.map((m) => m.id)).toEqual(["blank"]);
    } finally {
      fs.rmSync(root, { recursive: true, force: true });
      fs.rmSync(qdir, { recursive: true, force: true });
    }
  });
});

describe("runsEndpoint handler", () => {
  it("serves the run index JSON for the collection request", () => {
    const res = fakeRes();
    createRunsHandler(tmp)({ url: "/_index" }, res);
    const parsed = JSON.parse(String(res.body)) as { id: string }[];
    expect(parsed.map((r) => r.id)).toContain("run-a");
  });

  it("returns 400 on malformed percent-encoding", () => {
    const res = fakeRes();
    createRunsHandler(tmp)({ url: "/%E0%A4%A" }, res);
    expect(res.statusCode).toBe(400);
  });

  it("404s a file request that escapes the root", () => {
    const res = fakeRes();
    createRunsHandler(tmp)({ url: `/../${path.basename(outside)}/secret.json` }, res);
    expect(res.statusCode).toBe(404);
  });
});

describe("endpoint is node-only (not imported by client source)", () => {
  it("no src/ module references the node-only run endpoint", () => {
    const srcDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../src");
    const offenders: string[] = [];
    const walk = (d: string) => {
      for (const e of fs.readdirSync(d, { withFileTypes: true })) {
        const p = path.join(d, e.name);
        if (e.isDirectory()) walk(p);
        else if (/\.(ts|tsx)$/.test(e.name) && fs.readFileSync(p, "utf8").includes("runsEndpoint")) {
          offenders.push(path.relative(srcDir, p));
        }
      }
    };
    walk(srcDir);
    expect(offenders).toEqual([]);
  });
});
