// Shared harness for the review page tests (Spec 154): the committed fixture sample extended with
// Hebrew and Gurmukhi cells, the fixture gold set's labels, and an in-memory fake of the review
// service (auth, the sample, drafts with optimistic-concurrency versions). Every JSON response carries
// `content-type: application/json`: reviewApi reads anything else as "review service unavailable".

import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { setReviewFetch, type CellLabel } from "../lib/review";

const readFixture = (rel: string) => readFileSync(resolve(process.cwd(), "../../fixtures", rel), "utf8");

export const SAMPLE_ID = "review_sample";
export const REVIEWER = { id: "3f2b8c1e-5d4a-4e6f-9b7c-1a2d3e4f5a6b", email: "rev@example.com", name: "Test Reviewer" };

/** The committed gold-set fixture's bytes (written from the fixture sample's labels). */
export const GOLD_FIXTURE = readFixture("review_gold_set.jsonl");

/** The labels the gold-set fixture was written from, keyed by cell id. */
export function goldFixtureLabels(): Record<string, CellLabel> {
  const labels: Record<string, CellLabel> = {};
  for (const line of GOLD_FIXTURE.trim().split("\n")) {
    const row = JSON.parse(line);
    labels[row.cell_id] = { ...row.label, rubric_version: row.rubric_version, labelled_at: row.labelled_at };
  }
  return labels;
}

/** A cell id with characters a path segment can't carry raw (`:`, `/`, `%`, a space). */
export const ODD_CELL_ID = "fixture-run:vendor/model 50%:q-odd";

/**
 * The fixture sample (texts `hinduism/english` and `islam/native`, 10 cells) plus a Hebrew and a
 * Gurmukhi text with one retrieve_quote cell each, and one cell whose id needs percent-encoding.
 */
export function multiScriptSample(): any {
  const sample = JSON.parse(readFixture("review_sample.json"));
  const quote = sample.cells.find((c: any) => c.task === "retrieve_quote" && c.text === "islam/native");
  const cell = (over: { model_id: string; question_id: string; text: string; source: object; prompt: string; expected: string; answer: string }) => ({
    ...quote,
    cell_id: `fixture-run:${over.model_id}:${over.question_id}`,
    model_id: over.model_id,
    question_id: over.question_id,
    text: over.text,
    prompt: over.prompt,
    expected: { text: over.expected },
    answer: over.answer,
    source: { ...quote.source, ...over.source },
  });
  sample.texts.push(
    { id: "judaism/native", label: "Talmud Bavli — Aramaic", drawn: 2 },
    { id: "sikhism/native", label: "Sri Guru Granth Sahib", drawn: 1 },
  );
  sample.cells.push(
    cell({
      model_id: "model-a",
      question_id: "he0001",
      text: "judaism/native",
      source: { language: "he", tradition: ["Judaism"], citation: "Berakhot 2a:1" },
      prompt: "What is the beginning of Berakhot 2a in the Talmud Bavli (Vilna text)?",
      expected: "מֵאֵימָתַי קוֹרִין אֶת שְׁמַע בְּעַרְבִין",
      answer: "מאימתי קורין את שמע בערבין",
    }),
    cell({
      model_id: "model-a",
      question_id: "pa0001",
      text: "sikhism/native",
      source: { language: "pa", tradition: ["Sikhism"], citation: "Ang 1" },
      prompt: "What is the text of Ang 1 of the Sri Guru Granth Sahib?",
      expected: "ੴ ਸਤਿ ਨਾਮੁ ਕਰਤਾ ਪੁਰਖੁ",
      answer: "ੴ ਸਤਿ ਨਾਮੁ ਕਰਤਾ ਪੁਰਖੁ ਨਿਰਭਉ",
    }),
    cell({
      model_id: "vendor/model 50%",
      question_id: "q-odd",
      text: "judaism/native",
      source: { language: "he", tradition: ["Judaism"], citation: "Berakhot 2a:2" },
      prompt: "What is the text of Berakhot 2a:2?",
      expected: "מִשָּׁעָה שֶׁהַכֹּהֲנִים נִכְנָסִים",
      answer: "משעה שהכהנים נכנסים",
    }),
  );
  return sample;
}

type Draft = { state: unknown; version: number };
type Reply = Response | Promise<Response>;

export const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

export interface FakeReviewApi {
  drafts: Map<string, Draft>;
  /** The body of every draft PUT, in order. */
  puts: Array<{ sid: string; state: any; version: number }>;
  /** Override a route: return a Response (or a promise of one) to answer it, or undefined to fall through. */
  override: (fn: (path: string, method: string) => Reply | undefined) => void;
}

/**
 * Install a fake review service as the review API's fetch. Signed in as REVIEWER unless
 * `signedIn: false`. `drafts` seeds the saved drafts by sample id.
 */
export function installFakeReviewApi(
  opts: { sample?: unknown; drafts?: Record<string, Draft>; signedIn?: boolean } = {},
): FakeReviewApi {
  const sample = opts.sample ?? multiScriptSample();
  const drafts = new Map(Object.entries(opts.drafts ?? {}));
  const puts: FakeReviewApi["puts"] = [];
  let overrideFn: ((path: string, method: string) => Reply | undefined) | null = null;
  let signedIn = opts.signedIn ?? true;

  const impl = (async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    const path = new URL(String(input), "http://x").pathname;
    const method = init?.method ?? "GET";
    const overridden = overrideFn?.(path, method);
    if (overridden) return overridden;
    if (path === "/api/auth/csrf") return json({ csrfToken: "t" });
    if (path === "/api/auth/me") return signedIn ? json({ reviewer: REVIEWER }) : json({ error: "unauthorized" }, 401);
    if (path === "/api/auth/login" || path === "/api/auth/signup") {
      signedIn = true;
      return json({ reviewer: REVIEWER, csrfToken: "t" });
    }
    if (path === "/api/auth/logout") {
      signedIn = false;
      return json({ ok: true });
    }
    if (!signedIn) return json({ error: "unauthorized" }, 401);
    if (path === "/api/sample") return json(sample);
    if (path === "/api/review") {
      return json({ drafts: [...drafts.entries()].map(([sampleId, d]) => ({ sampleId, ...d })) });
    }
    if (path.startsWith("/api/review/")) {
      const sid = decodeURIComponent(path.slice("/api/review/".length));
      if (method === "GET") return json(drafts.get(sid) ?? { state: null, version: 0 });
      if (method === "DELETE") {
        drafts.delete(sid);
        return json({ ok: true });
      }
      if (method === "PUT") {
        const body = JSON.parse(String(init?.body ?? "{}"));
        puts.push({ sid, state: body.state, version: body.version });
        const cur = drafts.get(sid)?.version ?? 0;
        if (body.version !== cur) return json({ error: "conflict", ...drafts.get(sid) }, 409);
        drafts.set(sid, { state: body.state, version: cur + 1 });
        return json({ version: cur + 1 });
      }
    }
    return json({ error: "not found" }, 404);
  }) as typeof fetch;

  setReviewFetch(impl);
  return {
    drafts,
    puts,
    override: (fn) => {
      overrideFn = fn;
    },
  };
}

/** A saved draft for the fixture sample. */
export function draftOf(texts: string[], labels: Record<string, CellLabel> = {}, version = 1): Record<string, Draft> {
  return { [SAMPLE_ID]: { state: { texts, labels }, version } };
}
