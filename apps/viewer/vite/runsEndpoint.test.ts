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

describe("named panel runs (runs/<name>/<model>/base/**)", () => {
  let root: string;
  let runs: string;
  const cell = (correct: number, incorrect: number) => ({
    n: correct + incorrect,
    accuracy: correct / (correct + incorrect),
    coverage: 1,
    correct,
    incorrect,
    refused: 0,
    refused_rate: 0,
  });
  const summary = (model: string, correct: number, incorrect: number, generatedAt?: string) =>
    JSON.stringify({
      models: { [model]: { retrieve_quote: cell(correct, incorrect), _overall: cell(correct, incorrect) } },
      by_tradition: { [model]: { Islam: { retrieve_quote: cell(correct, incorrect) } } },
      ...(generatedAt ? { generated_at: generatedAt } : {}),
    });
  const get = (url: string) => {
    const res = fakeRes();
    createRunsHandler(runs)({ url }, res);
    return res as { statusCode: number; body: unknown };
  };

  beforeAll(() => {
    root = fs.mkdtempSync(path.join(os.tmpdir(), "named-panel-"));
    runs = path.join(root, "runs");
    // The committed archive: runs/haiku/base/... (the default panel).
    const old = path.join(runs, "haiku", "base", "islam", "native", "population", "prompt-native");
    fs.mkdirSync(old, { recursive: true });
    fs.writeFileSync(path.join(old, "summary.json"), summary("haiku", 1, 9, "2026-11-01T00:00:00+00:00"));
    fs.writeFileSync(path.join(old, "scores.jsonl"), '{"question_id":"old-q"}\n');
    fs.writeFileSync(path.join(runs, "haiku", "model.json"), '{"panel_id":"haiku"}');
    // The rerun: runs/rerun-2026-11-03/<model>/base/..., two models, no summary of its own.
    for (const [model, correct] of [["haiku", 8], ["opus", 9]] as const) {
      const dir = path.join(runs, "rerun-2026-11-03", model, "base", "islam", "native", "population", "prompt-native");
      fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(path.join(dir, "summary.json"), summary(model, correct, 10 - correct, "2026-11-03T12:00:00+00:00"));
      fs.writeFileSync(path.join(dir, "scores.jsonl"), `{"question_id":"q-native","model_id":"${model}"}\n`);
    }
    fs.writeFileSync(path.join(runs, "rerun-2026-11-03", "haiku", "model.json"), '{"panel_id":"haiku","rerun":true}');
    // An unfinished file in the rerun: answers, no summary, one roster row unsaved.
    const open = path.join(runs, "rerun-2026-11-03", "haiku", "base", "islam", "english", "population");
    fs.mkdirSync(open, { recursive: true });
    fs.writeFileSync(path.join(open, "answers.jsonl"), '{"question_id":"q-e1","answer":"text"}\n');
    // The roster, resolved from the segments after base whatever the prefix depth.
    const items = path.join(root, "items", "for-test", "islam");
    fs.mkdirSync(path.join(items, "native", "population", "prompt-native"), { recursive: true });
    fs.writeFileSync(
      path.join(items, "native", "population", "prompt-native", "questions.jsonl"),
      '{"id":"q-native","task":"retrieve_quote","source":{"tradition":["Islam"],"citation":"1:1"}}\n',
    );
    fs.mkdirSync(path.join(items, "english", "population"), { recursive: true });
    fs.writeFileSync(
      path.join(items, "english", "population", "questions.jsonl"),
      '{"id":"q-e1","task":"retrieve_quote","source":{"tradition":["Islam"],"citation":"1:1"}}\n' +
        '{"id":"q-e2","task":"retrieve_quote","source":{"tradition":["Islam"],"citation":"1:2"}}\n',
    );
    // Not named panels: a real run with its own summary, and a folder with no model/base.
    fs.mkdirSync(path.join(runs, "real-run", "haiku", "base", "islam"), { recursive: true });
    // Dated before the rerun. Undated, it sorts by mtime and beats the rerun once the clock passes the rerun's date.
    fs.writeFileSync(path.join(runs, "real-run", "summary.json"), '{"models":{},"generated_at":"2026-11-02T00:00:00+00:00"}');
    fs.writeFileSync(path.join(runs, "real-run", "haiku", "base", "islam", "summary.json"), summary("haiku", 5, 5));
    fs.mkdirSync(path.join(runs, "empty-rerun", "haiku"), { recursive: true });
  });

  afterAll(() => {
    fs.rmSync(root, { recursive: true, force: true });
  });

  it("lists runs/<name>/ as run <name>, newest panel first, beside the default panel", () => {
    const index = listRuns(runs);
    const ids = index.map((r) => r.id);
    expect(ids[0]).toBe("rerun-2026-11-03");
    expect(ids).toEqual(expect.arrayContaining(["panel", "real-run"]));
    expect(ids).not.toContain("haiku");
    expect(ids).not.toContain("empty-rerun");
    const rerun = index.find((r) => r.id === "rerun-2026-11-03")!;
    expect(rerun.generatedAt).toBe("2026-11-03T12:00:00+00:00");
    const newest = Math.max(
      ...["haiku", "opus"].map(
        (m) =>
          fs.statSync(
            path.join(runs, "rerun-2026-11-03", m, "base", "islam", "native", "population", "prompt-native", "summary.json"),
          ).mtimeMs,
      ),
    );
    expect(rerun.mtimeMs).toBe(newest);
  });

  it("rolls up only that folder's models, and keeps them out of the default panel", () => {
    const rerun = JSON.parse(String(get("/rerun-2026-11-03/summary.json").body)) as {
      models: Record<string, { _overall: { n: number; correct: number } }>;
    };
    expect(Object.keys(rerun.models).sort()).toEqual(["haiku", "opus"]);
    expect(rerun.models.haiku!._overall).toMatchObject({ n: 10, correct: 8 });
    const panel = JSON.parse(String(get("/panel/summary.json").body)) as {
      models: Record<string, { _overall: { n: number; correct: number } }>;
    };
    expect(Object.keys(panel.models)).toEqual(["haiku"]);
    expect(panel.models.haiku!._overall).toMatchObject({ n: 10, correct: 1 });
    expect(String(get("/panel/scores.jsonl").body)).not.toContain("q-native");
    expect(String(get("/rerun-2026-11-03/scores.jsonl").body)).toContain("q-native");
  });

  it("serves the roster from items/for-test via the segments after base", () => {
    expect(String(get("/rerun-2026-11-03/questions.jsonl").body)).toContain('"id":"q-native"');
  });

  it("still serves other files under the folder as confined files", () => {
    expect(String(get("/rerun-2026-11-03/haiku/model.json").body)).toContain('"rerun":true');
    expect(get("/rerun-2026-11-03/nope.json").statusCode).toBe(404);
    expect(get("/panel/haiku/model.json").statusCode).toBe(404);
  });

  it("reports a rerun gap under the model id, with the folder in its path", () => {
    const gaps = collectGaps(runs);
    const gap = gaps.find((g) => g.file.startsWith("rerun-2026-11-03"));
    expect(gap).toMatchObject({
      model: "haiku",
      file: path.join("rerun-2026-11-03", "haiku", "base", "islam", "english", "population"),
      questions: 2,
      saved: 1,
    });
    expect(gap!.missing.map((m) => m.id)).toEqual(["q-e2"]);
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
