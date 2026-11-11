import { describe, it, expect, beforeAll, afterAll } from "vitest";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { RUN_ARTIFACTS, assertPagesReady, bakeRuns, type BakeResult } from "./bakeRuns";

// The hosted review image (apps/api/Dockerfile) bakes only the runs its viewer stage names, one
// `COPY runs/<id> runs/<id>` line per run (#159). This reads that list, stages exactly those runs
// from the repo's runs/ the way the image's COPY lines do, and bakes them as `build:pages` does.
// The Pages bake of the whole runs/ is covered by bakeRuns.test.ts and is not affected.

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const dockerfile = fs.readFileSync(path.join(repo, "apps/api/Dockerfile"), "utf8");

/** Every COPY that takes something from the build context: its sources and its destination. */
function contextCopies(text: string): { sources: string[]; dest: string }[] {
  return text
    .split("\n")
    .map((line) => line.trim().split(/\s+/))
    .filter((words) => words[0] === "COPY" && !words.some((w) => w.startsWith("--from=")))
    .map((words) => {
      const args = words.slice(1).filter((w) => !w.startsWith("--"));
      return { sources: args.slice(0, -1), dest: args[args.length - 1]! };
    });
}

/** Whether a COPY source would bring in all of runs/ (or the whole context, runs/ included). */
const takesAllRuns = (src: string) => /^(\.\/?|runs\/?)$/.test(src) || (src.startsWith("runs") && /[*?[]/.test(src));

describe("the hosted image's run list (apps/api/Dockerfile)", () => {
  it("names each hosted run in its own COPY and never copies runs/ wholesale", () => {
    const copies = contextCopies(dockerfile);
    for (const { sources } of copies) {
      for (const src of sources) expect(takesAllRuns(src), `COPY ${src} takes all of runs/`).toBe(false);
    }
    const runCopies = copies.filter((c) => c.sources.some((s) => s.startsWith("runs/")));
    for (const { sources, dest } of runCopies) {
      expect(sources, "one run per COPY line").toHaveLength(1);
      expect(dest, "a run keeps its path, so its id is unchanged").toBe(sources[0]);
    }
  });

  it("hosts only the FAccT run (the owner's choice, #159)", () => {
    expect(hostedRunIds()).toEqual(["facct-2026-11-03"]);
  });
});

/** The run ids the Dockerfile names: `runs/<id>` sources. */
function hostedRunIds(): string[] {
  return contextCopies(dockerfile)
    .flatMap((c) => c.sources)
    .filter((s) => s.startsWith("runs/"))
    .map((s) => s.slice("runs/".length).replace(/\/$/, ""));
}

describe("bakeRuns over only the hosted runs", () => {
  const hosted = hostedRunIds();
  let root: string;
  let dist: string;
  let result: BakeResult;

  beforeAll(() => {
    root = fs.mkdtempSync(path.join(os.tmpdir(), "hosted-bake-"));
    for (const id of hosted) {
      fs.cpSync(path.join(repo, "runs", id), path.join(root, "runs", id), { recursive: true });
    }
    // The image copies items/for-test beside runs/; the bake reads the panel's questions there.
    fs.mkdirSync(path.join(root, "items"));
    fs.symlinkSync(path.join(repo, "items", "for-test"), path.join(root, "items", "for-test"));
    dist = path.join(root, "dist");
    fs.mkdirSync(dist);
    fs.writeFileSync(path.join(dist, "index.html"), '<!doctype html><div id="root"></div>');
    result = bakeRuns(path.join(root, "runs"), path.join(dist, "runs"));
  }, 120_000);
  afterAll(() => fs.rmSync(root, { recursive: true, force: true }));

  const read = (url: string) => JSON.parse(fs.readFileSync(path.join(dist, "runs", url), "utf8")) as unknown;

  it("indexes exactly the hosted runs: no panel, no archive", () => {
    const index = read("_index") as { id: string }[];
    expect(hosted.length).toBeGreaterThan(0);
    expect(index.map((r) => r.id).sort()).toEqual([...hosted].sort());
  });

  it("bakes all four artifacts of every hosted run, and a dist bake-runs.ts would accept", () => {
    for (const id of hosted) {
      for (const name of RUN_ARTIFACTS) {
        const url = `/${encodeURIComponent(id)}/${name}`;
        expect(result.notFound, url).not.toContain(url);
        expect(result.baked, url).toContain(url);
      }
    }
    // The checks scripts/bake-runs.ts makes before the image build can pass.
    expect(result.baked).toContain("/_index");
    expect(result.baked.length).toBeGreaterThan(2);
    expect(() => assertPagesReady(dist)).not.toThrow();
  });

  it("bakes the collections the single-run pages read", () => {
    expect(Array.isArray(read("_gaps"))).toBe(true);
    expect(Array.isArray((read("_judge") as { models: unknown }).models)).toBe(true);
  });

  it("includes the run every committed review sample was drawn from", () => {
    const samplesDir = path.join(repo, "review", "samples");
    const samples = fs.readdirSync(samplesDir).filter((f) => f.endsWith(".json"));
    expect(samples.length).toBeGreaterThan(0);
    const index = (read("_index") as { id: string }[]).map((r) => r.id);
    for (const file of samples) {
      const { source_run } = JSON.parse(fs.readFileSync(path.join(samplesDir, file), "utf8")) as { source_run: string };
      expect(source_run, file).toMatch(/^runs\//);
      expect(index, file).toContain(source_run.slice("runs/".length));
    }
  });
});
