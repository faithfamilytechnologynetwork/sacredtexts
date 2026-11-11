import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, it, expect } from "vitest";
import {
  fetchCsrf,
  getDraft,
  getSample,
  isCsrfError,
  listDrafts,
  login,
  logout,
  me,
  putDraft,
  REVIEW_BODY_MAX_BYTES,
  ReviewApiError,
  ReviewUnavailableError,
  setReviewFetch,
} from "./reviewApi";
import { SampleFormatError } from "./reviewSample";

const json = (obj: unknown, status = 200) =>
  new Response(JSON.stringify(obj), { status, headers: { "content-type": "application/json; charset=utf-8" } });
const html = (status = 200) =>
  new Response("<!doctype html><title>viewer</title>", { status, headers: { "content-type": "text/html" } });

type Seen = { path: string; method: string; headers: Headers; body?: string };

function recordingFetch(respond: (path: string, method: string) => Response) {
  const seen: Seen[] = [];
  const impl = (async (input: RequestInfo | URL, init?: RequestInit) => {
    const path = new URL(String(input), "http://x").pathname;
    const method = init?.method ?? "GET";
    seen.push({ path, method, headers: new Headers(init?.headers), body: init?.body as string | undefined });
    return respond(path, method);
  }) as unknown as typeof fetch;
  return { impl, seen };
}

const sampleText = readFileSync(resolve(process.cwd(), "../../fixtures/review_sample.json"), "utf8");

describe("reviewApi: telling 'no review service' from 'signed out'", () => {
  it("a non-JSON 200 (the static build's index.html) is unavailable, not signed out", async () => {
    setReviewFetch(recordingFetch(() => html()).impl);
    await expect(me()).rejects.toBeInstanceOf(ReviewUnavailableError);
    await expect(fetchCsrf()).rejects.toThrow("review service unavailable");
    await expect(getSample()).rejects.toBeInstanceOf(ReviewUnavailableError);
  });

  it("a non-JSON 404 is unavailable too", async () => {
    setReviewFetch(recordingFetch(() => html(404)).impl);
    await expect(getDraft("S")).rejects.toBeInstanceOf(ReviewUnavailableError);
  });

  it("a JSON 401 from /me is signed out", async () => {
    setReviewFetch(recordingFetch(() => json({ error: "unauthorized" }, 401)).impl);
    expect(await me()).toBeNull();
  });

  it("a 5xx is a service error with the server's message when it sent one", async () => {
    setReviewFetch(recordingFetch(() => json({ error: "database down" }, 503)).impl);
    await expect(me()).rejects.toMatchObject({ status: 503, message: "database down" });
    setReviewFetch(recordingFetch(() => new Response("Bad Gateway", { status: 502, headers: { "content-type": "text/html" } })).impl);
    await expect(me()).rejects.toMatchObject({ status: 502, message: "review service error" });
  });

  it("a plain-text 413 (hono's bodyLimit, or a proxy) is 'too large', not unavailable", async () => {
    setReviewFetch(recordingFetch(() => new Response("Payload Too Large", { status: 413 })).impl);
    const err = await putDraft("S", { texts: [] }, 1).catch((e) => e);
    expect(err).toBeInstanceOf(ReviewApiError);
    expect(err).toMatchObject({ status: 413, message: "this change is too large to save" });
  });
});

describe("reviewApi: requests", () => {
  it("mutations echo the CSRF token; reads don't need it", async () => {
    const api = recordingFetch((path, method) => {
      if (path === "/api/auth/csrf") return json({ csrfToken: "tok-1" });
      if (method === "PUT") return json({ version: 4 });
      return json({ state: null, version: 0 });
    });
    setReviewFetch(api.impl);
    await fetchCsrf();
    await getDraft("S");
    expect(await putDraft("S", { texts: ["x"] }, 3)).toEqual({ ok: true, version: 4 });
    const put = api.seen.find((s) => s.method === "PUT")!;
    expect(put.headers.get("X-CSRF-Token")).toBe("tok-1");
    expect(put.headers.get("Content-Type")).toBe("application/json");
    expect(JSON.parse(put.body!)).toEqual({ state: { texts: ["x"] }, version: 3 });
    expect(api.seen.find((s) => s.method === "GET" && s.path === "/api/review/S")!.headers.get("X-CSRF-Token")).toBeNull();
  });

  it("encodes the sample id in the path", async () => {
    const api = recordingFetch(() => json({ state: null, version: 0 }));
    setReviewFetch(api.impl);
    await getDraft("a/b c");
    expect(api.seen[0]!.path).toBe("/api/review/a%2Fb%20c");
  });

  it("a 409 returns the server's draft for reconciling", async () => {
    setReviewFetch(recordingFetch(() => json({ error: "conflict", state: { texts: ["y"] }, version: 9 }, 409)).impl);
    expect(await putDraft("S", { texts: ["x"] }, 3)).toEqual({ ok: false, conflict: { state: { texts: ["y"] }, version: 9 } });
  });

  it("the list is keyed by sample id", async () => {
    setReviewFetch(
      recordingFetch(() => json({ drafts: [{ sampleId: "S", state: { texts: [] }, version: 2 }, { sampleId: "T", version: 1 }] }))
        .impl,
    );
    expect(await listDrafts()).toEqual([
      { sampleId: "S", state: { texts: [] }, version: 2 },
      { sampleId: "T", state: null, version: 1 },
    ]);
  });
});

describe("reviewApi: logout", () => {
  it("clears the CSRF token on success", async () => {
    const rec = recordingFetch((path) =>
      path === "/api/auth/login" ? json({ reviewer: { id: "r" }, csrfToken: "tok" }) : json({ ok: true }),
    );
    setReviewFetch(rec.impl);
    await login("a@b.c", "password1");
    await logout();
    await logout(); // the second one goes out with no token: the first cleared it
    const posts = rec.seen.filter((r) => r.path === "/api/auth/logout");
    expect(posts.map((r) => r.headers.get("X-CSRF-Token"))).toEqual(["tok", null]);
  });

  it("throws on a refused sign-out instead of reporting success", async () => {
    setReviewFetch(recordingFetch(() => json({ error: "csrf" }, 403)).impl);
    const err = await logout().catch((e: unknown) => e);
    expect(err).toBeInstanceOf(ReviewApiError);
    expect(isCsrfError(err)).toBe(true);

    setReviewFetch(recordingFetch(() => json({ error: "nope" }, 400)).impl);
    await expect(logout()).rejects.toMatchObject({ status: 400, message: "nope" });
  });
});

describe("reviewApi: the byte guard", () => {
  it("mirrors the API's body cap exactly", () => {
    const apiSource = readFileSync(resolve(process.cwd(), "../api/src/routes/review.ts"), "utf8");
    const match = apiSource.match(/export const REVIEW_BODY_MAX_BYTES = ([\d\s*]+);/);
    expect(match).not.toBeNull();
    const apiCap = match![1]!.split("*").reduce((product, factor) => product * Number(factor.trim()), 1);
    expect(REVIEW_BODY_MAX_BYTES).toBe(apiCap);
  });

  it("refuses a body over the cap without sending it", async () => {
    const api = recordingFetch(() => json({ version: 1 }));
    setReviewFetch(api.impl);
    // ~4.2M Gurmukhi characters at 3 UTF-8 bytes each: under the cap in UTF-16 units, over it in bytes.
    const notes = "ਸ".repeat(Math.ceil(REVIEW_BODY_MAX_BYTES / 2));
    expect(notes.length).toBeLessThan(REVIEW_BODY_MAX_BYTES);
    await expect(putDraft("S", { texts: [], labels: { c: { notes } } }, 0)).rejects.toMatchObject({
      status: 413,
      message: "this change is too large to save",
    });
    expect(api.seen).toEqual([]);
  });

  it("sends a body exactly at the cap", async () => {
    const api = recordingFetch(() => json({ version: 1 }));
    setReviewFetch(api.impl);
    const overhead = JSON.stringify({ state: { n: "" }, version: 0 }).length;
    const result = await putDraft("S", { n: "x".repeat(REVIEW_BODY_MAX_BYTES - overhead) }, 0);
    expect(result).toEqual({ ok: true, version: 1 });
    expect(new TextEncoder().encode(api.seen[0]!.body!).length).toBe(REVIEW_BODY_MAX_BYTES);
  });
});

describe("reviewApi: getSample", () => {
  it("parses the served sample strictly", async () => {
    setReviewFetch(
      recordingFetch(() => new Response(sampleText, { headers: { "content-type": "application/json; charset=utf-8" } })).impl,
    );
    const sample = await getSample();
    expect(sample.sample_id).toBe("review_sample");
    expect(sample.cells).toHaveLength(10);
  });

  it("a 401 is unauthorized", async () => {
    setReviewFetch(recordingFetch(() => json({ error: "unauthorized" }, 401)).impl);
    await expect(getSample()).rejects.toMatchObject({ status: 401 });
  });

  it("a malformed sample fails loudly", async () => {
    setReviewFetch(recordingFetch(() => json({ format: 2 })).impl);
    await expect(getSample()).rejects.toBeInstanceOf(SampleFormatError);
  });
});
