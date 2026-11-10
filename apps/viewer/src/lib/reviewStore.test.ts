import { describe, it, expect, beforeEach } from "vitest";
import { REVIEW_BODY_MAX_BYTES, setReviewFetch } from "./reviewApi";
import {
  ensureSampleLoaded,
  flushReviewSaves,
  hasPendingRetry,
  initReview,
  loginReview,
  peekReviewState,
  peekReviewStatus,
  peekVersion,
  prefetchDrafts,
  resetReviewStore,
  updateReviewState,
  withLabel,
  withTexts,
  withoutSample,
} from "./review";

type Draft = { state: unknown; version: number };
type Handler = (path: string, method: string, init?: RequestInit) => Response | Promise<Response>;

const NOW = new Date("2026-11-10T12:00:00.000Z");
const json = (obj: unknown, status = 200) =>
  new Response(JSON.stringify(obj), { status, headers: { "content-type": "application/json" } });

/** A fake fetch: CSRF is always served; every other request goes to `handler`. */
function fakeFetch(handler: Handler): typeof fetch {
  return (async (input: RequestInfo | URL, init?: RequestInit) => {
    const path = new URL(String(input), "http://x").pathname;
    if (path === "/api/auth/csrf") return json({ csrfToken: "t" });
    return handler(path, init?.method ?? "GET", init);
  }) as unknown as typeof fetch;
}

const draftId = (path: string) => decodeURIComponent(path.slice("/api/review/".length));

/** An in-memory fake of the draft API that models optimistic-concurrency versions. */
function fakeApi(seed: Record<string, Draft> = {}) {
  const store = new Map(Object.entries(seed));
  const puts: Array<{ sid: string; version: number }> = [];
  const impl = fakeFetch((path, method, init) => {
    if (path.startsWith("/api/review/")) {
      const sid = draftId(path);
      if (method === "GET") {
        const d = store.get(sid);
        return json(d ? { state: d.state, version: d.version } : { state: null, version: 0 });
      }
      if (method === "PUT") {
        const body = JSON.parse(String(init?.body ?? "{}"));
        puts.push({ sid, version: body.version });
        const cur = store.get(sid);
        const curV = cur?.version ?? 0;
        if (body.version === curV) {
          const version = curV + 1;
          store.set(sid, { state: body.state, version });
          return json({ version });
        }
        return json({ error: "conflict", state: cur?.state ?? null, version: curV }, 409);
      }
    }
    return json({ error: "not found" }, 404);
  });
  return { impl, puts, store };
}

const label = (outcome: "correct" | "incorrect" | "refused" | "cant_judge", notes = "") =>
  ({ outcome, defect: false, notes, rubric_version: "1", labelled_at: NOW.toISOString() });

beforeEach(() => resetReviewStore());

describe("review store: async persistence", () => {
  it("saves a changed sample optimistically and advances the version", async () => {
    const api = fakeApi();
    setReviewFetch(api.impl);

    updateReviewState((s) => withTexts(s, "S", ["islam/native"]));
    // Optimistic: in memory immediately.
    expect(peekReviewState().samples.S?.texts).toEqual(["islam/native"]);

    await flushReviewSaves();
    expect(api.puts).toEqual([{ sid: "S", version: 0 }]); // a new draft
    expect(peekVersion("S")).toBe(1);

    updateReviewState((s) => withLabel(s, "S", "r:m:q1", { outcome: "correct" }, NOW));
    await flushReviewSaves();
    expect(api.puts).toEqual([
      { sid: "S", version: 0 },
      { sid: "S", version: 1 }, // an update on the advanced version
    ]);
    expect(peekVersion("S")).toBe(2);
    expect((api.store.get("S")?.state as any).labels["r:m:q1"].outcome).toBe("correct");
  });

  it("only saves the sample that actually changed (reference diff)", async () => {
    setReviewFetch(fakeApi().impl);
    updateReviewState((s) => withTexts(s, "a", ["x"]));
    await flushReviewSaves();
    const api2 = fakeApi();
    setReviewFetch(api2.impl);
    updateReviewState((s) => withTexts(s, "b", ["x"]));
    await flushReviewSaves();
    expect(api2.puts.map((p) => p.sid)).toEqual(["b"]); // "a" not re-saved
  });

  it("a no-op edit schedules no save", async () => {
    const api = fakeApi();
    setReviewFetch(api.impl);
    updateReviewState((s) => withLabel(s, "S", "c", { outcome: "refused" }, NOW));
    await flushReviewSaves();
    updateReviewState((s) => withLabel(s, "S", "c", { outcome: "refused" }, NOW));
    await flushReviewSaves();
    expect(api.puts).toHaveLength(1);
  });

  it("reconciles a genuine concurrent conflict (last-write-wins) without dropping the active edit", async () => {
    // Load first (version 1), then another device advances the server to version 2 out of band.
    const api = fakeApi({ S: { state: { texts: ["t"] }, version: 1 } });
    setReviewFetch(api.impl);
    await ensureSampleLoaded("S");
    expect(peekVersion("S")).toBe(1);
    api.store.set("S", { state: { texts: ["t"] }, version: 2 }); // a concurrent write

    updateReviewState((s) => withLabel(s, "S", "c1", { outcome: "incorrect" }, NOW));
    await flushReviewSaves();

    // PUT version 1 → 409 (the server is at 2); retry with the server's version 2 → succeeds at 3.
    expect(api.puts).toEqual([
      { sid: "S", version: 1 },
      { sid: "S", version: 2 },
    ]);
    expect(peekVersion("S")).toBe(3);
    // The active device's edit survived the reconcile.
    expect((api.store.get("S")?.state as any).labels.c1.outcome).toBe("incorrect");
    // LWW is the design, but it must not be silent.
    expect(peekReviewStatus().reconciled).toBe("S");
  });

  it("adopts the server draft (server-wins) when the last-write-wins retry conflicts again", async () => {
    let putCount = 0;
    const server = { texts: ["t"], labels: { c9: label("correct", "OTHER DEVICE") } };
    setReviewFetch(
      fakeFetch((_path, method) => {
        if (method === "GET") return json({ state: { texts: [] }, version: 1 });
        putCount += 1; // every PUT loses to a third writer
        return json({ error: "conflict", state: server, version: 10 + putCount }, 409);
      }),
    );
    await ensureSampleLoaded("S");
    updateReviewState((s) => withLabel(s, "S", "c1", { outcome: "incorrect" }, NOW));
    await flushReviewSaves();

    expect(putCount).toBe(2);
    expect(peekReviewState().samples.S?.labels.c9?.notes).toBe("OTHER DEVICE");
    expect(peekReviewState().samples.S?.labels.c1).toBeUndefined();
    expect(peekVersion("S")).toBe(12);
    expect(peekReviewStatus().reconciled).toBe("S");
  });

  it("does NOT overwrite a saved server draft when the initial load fails", async () => {
    // The server has a real saved draft (version 3). GET fails (network), but the reviewer edits.
    const server = new Map<string, Draft>([["S", { state: { labels: { c: label("correct", "server work") } }, version: 3 }]]);
    const puts: number[] = [];
    setReviewFetch(
      fakeFetch((_path, method) => {
        if (method === "GET") throw new Error("network down"); // the draft load fails
        if (method === "PUT") {
          puts.push(1);
          return json({ version: 4 });
        }
        return json({}, 404);
      }),
    );

    updateReviewState((s) => withLabel(s, "S", "c", { outcome: "refused" }, NOW));
    await flushReviewSaves();

    // The save was HELD (no PUT) because the load failed, so the server draft is intact.
    expect(puts).toEqual([]);
    expect(server.get("S")?.version).toBe(3);
    expect(peekReviewStatus().error).toBeTruthy();
    expect(peekReviewStatus().errorKind).toBe("load");
  });

  it("adopts the server draft (not the blip edit) when a load fails then recovers", async () => {
    // GET fails once, the reviewer edits during the failure, then GET recovers with the saved draft.
    // The pre-load edit sat on a blank base, so the server draft wins (+ reconciled).
    let getFails = true;
    const server = { texts: ["islam/native"], labels: { c9: label("correct", "SERVER") } };
    setReviewFetch(
      fakeFetch((_path, method) => {
        if (method === "GET") {
          if (getFails) {
            getFails = false;
            throw new Error("blip");
          }
          return json({ state: server, version: 7 });
        }
        if (method === "PUT") return json({ version: 8 });
        return json({}, 404);
      }),
    );

    expect(await ensureSampleLoaded("S")).toBe(false);
    updateReviewState((s) => withLabel(s, "S", "c1", { outcome: "incorrect" }, NOW));
    await flushReviewSaves();

    expect(peekReviewState().samples.S?.texts).toEqual(["islam/native"]);
    expect(peekReviewState().samples.S?.labels.c9?.notes).toBe("SERVER");
    expect(peekReviewState().samples.S?.labels.c1).toBeUndefined();
    expect(peekReviewStatus().reconciled).toBe("S");
  });

  it("retries a failed save on the next flush", async () => {
    let failNext = true;
    const saved = new Map<string, Draft>();
    setReviewFetch(
      fakeFetch((_path, method, init) => {
        if (method === "GET") return json({ state: null, version: 0 });
        if (method === "PUT") {
          if (failNext) {
            failNext = false;
            throw new Error("network blip");
          }
          const b = JSON.parse(String(init?.body ?? "{}"));
          saved.set("S", { state: b.state, version: (saved.get("S")?.version ?? 0) + 1 });
          return json({ version: saved.get("S")!.version });
        }
        return json({}, 404);
      }),
    );

    updateReviewState((s) => withTexts(s, "S", ["t"]));
    await flushReviewSaves(); // the first attempt throws → held dirty, a retry armed, error shown
    expect(saved.has("S")).toBe(false);
    expect(peekReviewStatus().errorKind).toBe("save");
    expect(hasPendingRetry("S")).toBe(true);

    await flushReviewSaves(); // the retry succeeds
    expect(saved.get("S")?.version).toBe(1);
    expect(peekReviewStatus().error).toBeNull();
  });

  it("start over deletes the server draft", async () => {
    const server = new Map<string, Draft>([["S", { state: { texts: ["t"] }, version: 2 }]]);
    let deleted = false;
    setReviewFetch(
      fakeFetch((_path, method) => {
        if (method === "GET") return json(server.get("S") ?? { state: null, version: 0 });
        if (method === "DELETE") {
          deleted = true;
          server.delete("S");
          return json({ ok: true });
        }
        return json({}, 404);
      }),
    );

    await ensureSampleLoaded("S");
    updateReviewState((s) => withoutSample(s, "S")); // "start over"
    await flushReviewSaves();
    expect(deleted).toBe(true);
    expect(server.has("S")).toBe(false);
  });

  it("serializes a start-over delete before a fresh save so the fresh draft wins", async () => {
    const server = new Map<string, Draft>([["S", { state: { texts: ["old"] }, version: 4 }]]);
    const ops: string[] = [];
    setReviewFetch(
      fakeFetch((_path, method, init) => {
        if (method === "GET") return json(server.get("S") ?? { state: null, version: 0 });
        if (method === "DELETE") {
          ops.push("del");
          server.delete("S");
          return json({ ok: true });
        }
        if (method === "PUT") {
          ops.push("put");
          const b = JSON.parse(String(init?.body ?? "{}"));
          const cv = server.get("S")?.version ?? 0;
          if (b.version === cv) {
            server.set("S", { state: b.state, version: cv + 1 });
            return json({ version: cv + 1 });
          }
          return json({ error: "conflict", state: server.get("S")?.state ?? null, version: cv }, 409);
        }
        return json({}, 404);
      }),
    );

    await ensureSampleLoaded("S");
    updateReviewState((s) => withoutSample(s, "S")); // start over → delete
    updateReviewState((s) => withTexts(s, "S", ["new"])); // a fresh choice → save
    await flushReviewSaves();

    expect(ops).toEqual(["del", "put"]); // the delete ran first, then the fresh save
    expect(server.get("S")?.version).toBe(1);
    expect((server.get("S")?.state as any).texts).toEqual(["new"]);
  });

  it("clears pendingDeletes on success so a later flush can't delete a recreated draft", async () => {
    const server = new Map<string, Draft>([["S", { state: { texts: ["old"] }, version: 3 }]]);
    const ops: string[] = [];
    setReviewFetch(
      fakeFetch((_path, method, init) => {
        if (method === "GET") return json(server.get("S") ?? { state: null, version: 0 });
        if (method === "DELETE") {
          ops.push("del");
          server.delete("S");
          return json({ ok: true });
        }
        if (method === "PUT") {
          ops.push("put");
          const b = JSON.parse(String(init?.body ?? "{}"));
          const cv = server.get("S")?.version ?? 0;
          server.set("S", { state: b.state, version: cv + 1 });
          return json({ version: cv + 1 });
        }
        return json({}, 404);
      }),
    );

    await ensureSampleLoaded("S");
    updateReviewState((s) => withoutSample(s, "S"));
    await flushReviewSaves();
    expect(peekReviewStatus().saving).toBe(false); // not stuck "saving"

    // Recreate the sample, then flush AGAIN: the stale pendingDeletes must NOT re-delete it.
    updateReviewState((s) => withTexts(s, "S", ["new"]));
    await flushReviewSaves();
    expect(ops).toEqual(["del", "put"]);
    expect(server.get("S")?.state).toBeTruthy();
  });

  it("loads an existing draft from the API tolerantly", async () => {
    const api = fakeApi({
      S: { state: { texts: ["t"], labels: { c: { outcome: "correct", notes: "ok", bogus: 1 } } }, version: 5 },
    });
    setReviewFetch(api.impl);
    await ensureSampleLoaded("S");
    const r = peekReviewState().samples.S;
    expect(r?.texts).toEqual(["t"]);
    expect(r?.labels.c).toEqual({ outcome: "correct", defect: false, notes: "ok", rubric_version: "", labelled_at: "" });
    expect(peekVersion("S")).toBe(5);
  });
});

describe("review store: the editing gate", () => {
  it("ensureSampleLoaded resolves true only once the draft GET succeeds, and coalesces callers", async () => {
    let releaseGet!: () => void;
    const getGate = new Promise<void>((r) => (releaseGet = r));
    let gets = 0;
    setReviewFetch(
      fakeFetch(async (_path, method) => {
        if (method === "GET") {
          gets += 1;
          await getGate; // hold the draft load
          return json({ state: { texts: ["t"] }, version: 2 });
        }
        return json({}, 404);
      }),
    );

    let settled: boolean | null = null;
    const first = ensureSampleLoaded("S").then((ok) => (settled = ok));
    const second = ensureSampleLoaded("S");
    await Promise.resolve();
    expect(settled).toBeNull(); // still loading: the page keeps editing disabled
    releaseGet();
    await first;
    expect(settled).toBe(true);
    expect(await second).toBe(true);
    expect(gets).toBe(1);
    expect(await ensureSampleLoaded("S")).toBe(true); // loaded: no second request
    expect(gets).toBe(1);
  });

  it("ensureSampleLoaded resolves false on a failed load, and a later call retries", async () => {
    let fail = true;
    setReviewFetch(
      fakeFetch((_path, method) => {
        if (method === "GET") {
          if (fail) {
            fail = false;
            return json({ error: "boom" }, 500);
          }
          return json({ state: null, version: 0 });
        }
        return json({}, 404);
      }),
    );
    expect(await ensureSampleLoaded("S")).toBe(false);
    expect(peekReviewStatus().errorKind).toBe("load");
    expect(await ensureSampleLoaded("S")).toBe(true);
  });
});

describe("review store: the prefetch", () => {
  it("adopts the server draft when a blank-based local entry exists", async () => {
    const server = { texts: ["islam/native"], labels: { c9: label("correct", "SERVER") } };
    let getFails = true;
    setReviewFetch(
      fakeFetch((path, method) => {
        if (path === "/api/review") return json({ drafts: [{ sampleId: "S", state: server, version: 9 }] });
        if (method === "GET") {
          if (getFails) {
            getFails = false;
            throw new Error("blip");
          }
          return json({ state: server, version: 9 });
        }
        if (method === "PUT") return json({ version: 10 });
        return json({}, 404);
      }),
    );

    // A failed load, then an edit on a blank base.
    expect(await ensureSampleLoaded("S")).toBe(false);
    updateReviewState((s) => withLabel(s, "S", "c1", { outcome: "incorrect" }, NOW));
    // The prefetch must ADOPT the server draft, not just mark it loaded.
    await prefetchDrafts();
    expect(peekReviewState().samples.S?.texts).toEqual(["islam/native"]);
    expect(peekReviewState().samples.S?.labels.c1).toBeUndefined(); // the blip edit is discarded
    expect(peekReviewStatus().reconciled).toBe("S");
  });

  it("SKIPS a sample already loaded via its own GET (no clobber of post-load edits)", async () => {
    // The race: a sample's GET resolves first (loadState "ok"), the reviewer edits, then the slower
    // LIST resolves. It must not re-adopt the server copy over the edit, nor overwrite the version.
    const server = { texts: ["t"], labels: {} };
    let releaseList!: () => void;
    const listGate = new Promise<void>((r) => (releaseList = r));
    setReviewFetch(
      fakeFetch(async (path, method) => {
        if (path === "/api/review") {
          await listGate; // the LIST lands AFTER the fast GET and the reviewer's edit
          return json({ drafts: [{ sampleId: "S", state: server, version: 5 }] });
        }
        if (method === "GET") return json({ state: server, version: 5 });
        if (method === "PUT") return json({ version: 6 });
        return json({}, 404);
      }),
    );

    expect(await ensureSampleLoaded("S")).toBe(true);
    expect(peekVersion("S")).toBe(5);
    const pf = prefetchDrafts(); // in flight, parked on the list gate
    updateReviewState((s) => withLabel(s, "S", "c1", { outcome: "refused", notes: "MY EDIT" }, NOW));
    releaseList();
    await pf;

    expect(peekReviewState().samples.S?.labels.c1?.notes).toBe("MY EDIT");
    expect(peekVersion("S")).toBe(5); // not overwritten by the LIST
    expect(peekReviewStatus().reconciled).toBeNull();
  });

  it("loads every draft, so progress shows without opening each sample", async () => {
    setReviewFetch(
      fakeFetch((path) => {
        if (path === "/api/review") {
          return json({
            drafts: [
              { sampleId: "A", state: { texts: ["x"] }, version: 2 },
              { sampleId: "B", state: { texts: ["y"] }, version: 4 },
            ],
          });
        }
        return json({}, 404);
      }),
    );
    await prefetchDrafts();
    expect(peekReviewState().samples.A?.texts).toEqual(["x"]);
    expect(peekVersion("B")).toBe(4);
    expect(await ensureSampleLoaded("B")).toBe(true); // already loaded: no GET needed
  });
});

describe("review store: auth and isolation", () => {
  it("clears all cached labels when the session expires (no cross-reviewer leak)", async () => {
    setReviewFetch(
      fakeFetch((_path, method) => {
        if (method === "GET") return json({ state: { texts: ["t"], labels: { c: label("correct", "A") } }, version: 2 });
        if (method === "PUT") return json({ error: "unauthorized" }, 401); // the session expired mid-save
        return json({}, 404);
      }),
    );

    await ensureSampleLoaded("S"); // reviewer A's draft is in memory
    expect(peekReviewState().samples.S?.labels.c?.notes).toBe("A");
    updateReviewState((s) => withLabel(s, "S", "c", { outcome: "incorrect" }, NOW));
    await flushReviewSaves(); // PUT → 401

    expect(peekReviewState().samples).toEqual({});
    expect(peekVersion("S")).toBe(0);
    expect(peekReviewStatus().auth).toBe("out");
  });

  it("a different reviewer signing in wipes the previous reviewer's labels", async () => {
    const reviewerA = { id: "a", email: "a@example.com", name: "A" };
    const reviewerB = { id: "b", email: "b@example.com", name: "B" };
    let next = reviewerA;
    setReviewFetch(
      fakeFetch((path, method) => {
        if (path === "/api/auth/login") return json({ reviewer: next, csrfToken: "t" });
        if (method === "GET") return json({ state: { texts: ["t"], labels: { c: label("correct", "A's note") } }, version: 3 });
        return json({}, 404);
      }),
    );

    await loginReview("a@example.com", "password1");
    await ensureSampleLoaded("S");
    expect(peekReviewState().samples.S?.labels.c?.notes).toBe("A's note");

    next = reviewerB;
    await loginReview("b@example.com", "password2");
    expect(peekReviewState().samples).toEqual({});
    expect(peekVersion("S")).toBe(0);
    expect(peekReviewStatus().reviewer?.id).toBe("b");
  });

  it("the same reviewer signing in again keeps their labels", async () => {
    const reviewer = { id: "a", email: "a@example.com", name: "A" };
    setReviewFetch(
      fakeFetch((path) => {
        if (path === "/api/auth/login") return json({ reviewer, csrfToken: "t" });
        return json({}, 404);
      }),
    );
    await loginReview("a@example.com", "password1");
    updateReviewState((s) => withTexts(s, "S", ["t"]));
    await loginReview("a@example.com", "password1");
    expect(peekReviewState().samples.S?.texts).toEqual(["t"]);
  });

  it("fails visibly (signed out, with an error) when the service is unreachable", async () => {
    setReviewFetch((async () => {
      throw new Error("offline");
    }) as unknown as typeof fetch);
    await initReview();
    const st = peekReviewStatus();
    expect(st.auth).toBe("out");
    expect(st.error).toMatch(/couldn't reach the review service/);
  });

  it("a non-JSON answer (the static viewer build) is 'unavailable', not signed out", async () => {
    setReviewFetch((async () =>
      new Response("<!doctype html><title>viewer</title>", {
        status: 200,
        headers: { "content-type": "text/html; charset=utf-8" },
      })) as unknown as typeof fetch);
    await initReview();
    expect(peekReviewStatus().auth).toBe("unavailable");
    expect(peekReviewStatus().error).toBe("review service unavailable");
  });

  it("signs in from an existing session", async () => {
    const reviewer = { id: "a", email: "a@example.com", name: "A" };
    setReviewFetch(fakeFetch((path) => (path === "/api/auth/me" ? json({ reviewer }) : json({}, 404))));
    await initReview();
    expect(peekReviewStatus().auth).toBe("in");
    expect(peekReviewStatus().reviewer?.id).toBe("a");
  });

  it("is signed out when there is no session", async () => {
    setReviewFetch(fakeFetch(() => json({ error: "unauthorized" }, 401)));
    await initReview();
    expect(peekReviewStatus().auth).toBe("out");
    expect(peekReviewStatus().error).toBeNull();
  });
});

describe("review store: CSRF and terminal saves", () => {
  it("a CSRF 403 refreshes the token, and the retry carries the fresh one", async () => {
    let token = "stale";
    let csrfFetches = 0;
    const sentTokens: Array<string | null> = [];
    let saved = false;
    setReviewFetch((async (input: RequestInfo | URL, init?: RequestInit) => {
      const path = new URL(String(input), "http://x").pathname;
      const method = init?.method ?? "GET";
      if (path === "/api/auth/csrf") {
        csrfFetches += 1;
        return json({ csrfToken: token });
      }
      if (method === "GET") return json({ state: null, version: 0 });
      if (method === "PUT") {
        const sent = new Headers(init?.headers).get("X-CSRF-Token");
        sentTokens.push(sent);
        if (sent !== "fresh") return json({ error: "csrf" }, 403);
        saved = true;
        return json({ version: 1 });
      }
      return json({}, 404);
    }) as unknown as typeof fetch);

    await initReview(); // fetches the (stale) token
    token = "fresh"; // the server rotated it
    updateReviewState((s) => withTexts(s, "S", ["t"]));
    await flushReviewSaves(); // PUT with "stale" → 403 csrf → refresh; a retry is armed
    expect(saved).toBe(false);
    expect(csrfFetches).toBe(2);
    expect(peekReviewStatus().errorKind).toBe("save");
    expect(hasPendingRetry("S")).toBe(true);

    await flushReviewSaves(); // the retry carries the fresh token
    expect(sentTokens).toEqual(["stale", "fresh"]);
    expect(saved).toBe(true);
    expect(peekReviewStatus().error).toBeNull();
  });

  it("a 413 is terminal: no retry, the error is visible, and the label stays in memory", async () => {
    let puts = 0;
    setReviewFetch(
      fakeFetch((_path, method) => {
        if (method === "GET") return json({ state: null, version: 0 });
        if (method === "PUT") {
          puts += 1;
          // hono's bodyLimit answers in plain text.
          return new Response("Payload Too Large", { status: 413, headers: { "content-type": "text/plain" } });
        }
        return json({}, 404);
      }),
    );

    updateReviewState((s) => withLabel(s, "S", "c1", { outcome: "incorrect", notes: "keep me" }, NOW));
    await flushReviewSaves();
    expect(puts).toBe(1);
    expect(peekReviewStatus().errorKind).toBe("rejected");
    expect(peekReviewStatus().error).toBe("this change is too large to save");
    expect(peekReviewStatus().saving).toBe(false);
    expect(hasPendingRetry("S")).toBe(false);
    expect(peekReviewState().samples.S?.labels.c1?.notes).toBe("keep me");

    await flushReviewSaves(); // a flush (navigation, page-hide) doesn't retry it either
    expect(puts).toBe(1);

    updateReviewState((s) => withLabel(s, "S", "c2", { outcome: "correct" }, NOW));
    await flushReviewSaves(); // the next real edit tries again
    expect(puts).toBe(2);
  });

  it("any other 4xx is terminal too, with the server's message", async () => {
    let puts = 0;
    setReviewFetch(
      fakeFetch((_path, method) => {
        if (method === "GET") return json({ state: null, version: 0 });
        if (method === "PUT") {
          puts += 1;
          return json({ error: "unknown sample" }, 404);
        }
        return json({}, 404);
      }),
    );
    updateReviewState((s) => withTexts(s, "old-sample", ["t"]));
    await flushReviewSaves();
    expect(peekReviewStatus().errorKind).toBe("rejected");
    expect(peekReviewStatus().error).toBe("unknown sample");
    expect(hasPendingRetry("old-sample")).toBe(false);
    expect(puts).toBe(1);
  });

  it("a 403 that isn't a CSRF failure is terminal, not a token refresh", async () => {
    let csrfFetches = 0;
    setReviewFetch((async (input: RequestInfo | URL, init?: RequestInit) => {
      const path = new URL(String(input), "http://x").pathname;
      if (path === "/api/auth/csrf") {
        csrfFetches += 1;
        return json({ csrfToken: "t" });
      }
      if ((init?.method ?? "GET") === "GET") return json({ state: null, version: 0 });
      return json({ error: "forbidden" }, 403);
    }) as unknown as typeof fetch);
    updateReviewState((s) => withTexts(s, "S", ["t"]));
    await flushReviewSaves();
    expect(peekReviewStatus().errorKind).toBe("rejected");
    expect(csrfFetches).toBe(0);
    expect(hasPendingRetry("S")).toBe(false);
  });

  it("a 5xx is not terminal: it retries", async () => {
    setReviewFetch(
      fakeFetch((_path, method) => {
        if (method === "GET") return json({ state: null, version: 0 });
        return new Response("Internal Server Error", { status: 500, headers: { "content-type": "text/plain" } });
      }),
    );
    updateReviewState((s) => withTexts(s, "S", ["t"]));
    await flushReviewSaves();
    expect(peekReviewStatus().errorKind).toBe("save");
    expect(hasPendingRetry("S")).toBe(true);
  });

  it("the byte guard stops an oversized draft without a request", async () => {
    let puts = 0;
    setReviewFetch(
      fakeFetch((_path, method) => {
        if (method === "GET") return json({ state: null, version: 0 });
        if (method === "PUT") puts += 1;
        return json({ version: 1 });
      }),
    );
    const huge = "x".repeat(REVIEW_BODY_MAX_BYTES);
    updateReviewState((s) => withLabel(s, "S", "c1", { outcome: "incorrect", notes: huge }, NOW));
    await flushReviewSaves();
    expect(puts).toBe(0);
    expect(peekReviewStatus().errorKind).toBe("rejected");
    expect(peekReviewStatus().error).toBe("this change is too large to save");
    expect(hasPendingRetry("S")).toBe(false);
    expect(peekReviewState().samples.S?.labels.c1?.notes).toHaveLength(REVIEW_BODY_MAX_BYTES);
  });
});
