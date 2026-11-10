import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { act, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderApp } from "../test/renderApp";
import {
  draftOf,
  GOLD_FIXTURE,
  goldFixtureLabels,
  installFakeReviewApi,
  json,
  SAMPLE_ID,
} from "../test/reviewHarness";
import { flushReviewSaves, resetReviewStore, setReviewFetch } from "../lib/review";
import { cellHref } from "../lib/reviewLinks";

const ISLAM_PASS = [
  "fixture-run:model-b:df788ade727db3cf",
  "fixture-run:model-b:aeaa707307175fdb",
  "fixture-run:model-a:12e45dddc647beb6",
  "fixture-run:model-a:aeaa707307175fdb",
  "fixture-run:model-a:7c41160f85999097",
];
const HINDU_PASS = [
  "fixture-run:model-b:e84250807e983aef",
  "fixture-run:model-a:f713b30ff8deb19b",
  "fixture-run:model-a:44fef84fa1aef80b",
  "fixture-run:model-b:1e33ec77e1ed0b3f",
  "fixture-run:model-a:b9bdeb4400fc2a64",
];
/** Both texts, in sample order (the cells interleave). */
const BOTH_PASS = [
  "fixture-run:model-b:df788ade727db3cf",
  ...HINDU_PASS,
  "fixture-run:model-b:aeaa707307175fdb",
  "fixture-run:model-a:12e45dddc647beb6",
  "fixture-run:model-a:aeaa707307175fdb",
  "fixture-run:model-a:7c41160f85999097",
];

const html = () => new Response("<!doctype html><html><body></body></html>", { status: 200, headers: { "content-type": "text/html" } });

// jsdom has no object URLs. The download hands its Blob to createObjectURL; keep the last one, and
// leave both functions installed for the whole file (the revoke runs on a timer after the click).
let lastBlob: Blob | null = null;
Object.defineProperty(URL, "createObjectURL", {
  configurable: true,
  writable: true,
  value: (blob: Blob) => {
    lastBlob = blob;
    return "blob:gold";
  },
});
Object.defineProperty(URL, "revokeObjectURL", { configurable: true, writable: true, value: () => {} });

/** jsdom's Blob has no `text()`; read it as UTF-8 the old way. */
function readBlob(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(reader.error);
    reader.readAsText(blob);
  });
}

beforeEach(() => resetReviewStore());
afterEach(() => vi.restoreAllMocks());

const passHrefs = () =>
  within(screen.getByTestId("pass-list"))
    .getAllByRole("link")
    .map((a) => a.getAttribute("href"));

const textBox = (name: RegExp) => screen.getByRole("checkbox", { name });

describe("/review: the auth gate", () => {
  it("shows the sign-in form when signed out", async () => {
    installFakeReviewApi({ signedIn: false });
    renderApp("/review");
    expect(await screen.findByTestId("review-auth-form")).toBeInTheDocument();
    expect(screen.queryByTestId("review-page")).toBeNull();
  });

  it("shows 'review service unavailable', not a sign-in form, when the origin answers with HTML", async () => {
    // The static Cloudflare Pages build answers every /api/* path with its index.html.
    setReviewFetch((async () => html()) as typeof fetch);
    renderApp("/review");
    expect(await screen.findByRole("heading", { name: /review service unavailable/i })).toBeInTheDocument();
    expect(screen.queryByTestId("review-auth-form")).toBeNull();
  });

  it("shows 'review service unavailable' when the sample request gets a non-JSON answer", async () => {
    const api = installFakeReviewApi();
    api.override((path) => (path === "/api/sample" ? html() : undefined));
    renderApp("/review");
    expect(await screen.findByRole("heading", { name: /review service unavailable/i })).toBeInTheDocument();
  });

  it("signs the reviewer out when the sample request finds the session expired", async () => {
    const api = installFakeReviewApi();
    api.override((path) => (path === "/api/sample" ? json({ error: "unauthorized" }, 401) : undefined));
    renderApp("/review");
    expect(await screen.findByTestId("review-auth-form")).toBeInTheDocument();
    expect(screen.getByTestId("review-service-error")).toHaveTextContent("your session expired");
  });

  it("fetches the sample once per session, not once per page", async () => {
    const api = installFakeReviewApi({ drafts: draftOf(["islam/native"]) });
    let sampleRequests = 0;
    api.override((path) => {
      if (path === "/api/sample") sampleRequests += 1;
      return undefined;
    });
    renderApp("/review");
    await userEvent.click((await screen.findAllByTestId("pass-item"))[0]!);
    await userEvent.click(await screen.findByRole("link", { name: "Next cell" }));
    await userEvent.click(screen.getByRole("link", { name: "← Your pass" }));
    expect(await screen.findByTestId("pass-list")).toBeInTheDocument();
    expect(sampleRequests).toBe(1);

    // Signing out starts a new session: the next reviewer's pages fetch it afresh.
    await userEvent.click(screen.getByRole("button", { name: "Sign out" }));
    await userEvent.type(await screen.findByLabelText("Email"), "b@example.com");
    await userEvent.type(screen.getByLabelText("Password"), "password123");
    await userEvent.click(screen.getByRole("button", { name: "Sign in" }));
    expect(await screen.findByTestId("pass-list")).toBeInTheDocument();
    expect(sampleRequests).toBe(2);
  });

  it("shows a failed sample load with a retry that loads it", async () => {
    const api = installFakeReviewApi();
    api.override((path) => (path === "/api/sample" ? json({ error: "boom" }, 503) : undefined));
    renderApp("/review");
    expect(await screen.findByTestId("sample-error")).toHaveTextContent("boom");
    api.override(() => undefined);
    await userEvent.click(screen.getByRole("button", { name: "Try again" }));
    expect(await screen.findByTestId("review-page")).toBeInTheDocument();
  });
});

describe("/review: the text picker", () => {
  it("prompts the reviewer to choose, listing every text with its cell count", async () => {
    installFakeReviewApi();
    renderApp("/review");
    expect(await screen.findByTestId("choose-texts")).toBeInTheDocument();
    expect(screen.queryByTestId("pass-list")).toBeNull();
    expect(textBox(/The Qur'an — Uthmani \(QUL\)/)).toBeInTheDocument();
    expect(textBox(/Qur'an/).closest("label")).toHaveTextContent("The Qur'an — Uthmani (QUL) (5 cells)");
    expect(textBox(/Talmud/).closest("label")).toHaveTextContent("Talmud Bavli — Aramaic (2 cells)");
    expect(screen.getAllByRole("checkbox")).toHaveLength(4);
    expect(screen.getByTestId("sample-meta")).toHaveTextContent(`Sample ${SAMPLE_ID} · 13 cells from runs/fixture-run`);
  });

  it("filters the pass to the chosen texts, in sample order, and saves the choice", async () => {
    const api = installFakeReviewApi();
    renderApp("/review");
    await waitFor(() => expect(textBox(/Qur'an/)).toBeEnabled());

    await userEvent.click(textBox(/Qur'an/));
    expect(passHrefs()).toEqual(ISLAM_PASS.map(cellHref));
    expect(screen.queryByTestId("choose-texts")).toBeNull();

    await userEvent.click(textBox(/Bhagavad Gita/));
    expect(passHrefs()).toEqual(BOTH_PASS.map(cellHref));

    await act(() => flushReviewSaves());
    // Saved in the sample's text order, whatever the click order.
    expect(api.drafts.get(SAMPLE_ID)?.state).toMatchObject({ texts: ["hinduism/english", "islam/native"] });

    await userEvent.click(textBox(/Qur'an/));
    expect(passHrefs()).toEqual(HINDU_PASS.map(cellHref));
  });

  it("restores the choice from the saved draft (a reload or a second device)", async () => {
    installFakeReviewApi({ drafts: draftOf(["islam/native"]) });
    renderApp("/review");
    await waitFor(() => expect(textBox(/Qur'an/)).toBeChecked());
    expect(textBox(/Bhagavad Gita/)).not.toBeChecked();
    expect(passHrefs()).toEqual(ISLAM_PASS.map(cellHref));
  });

  it("keeps the picker off until the saved draft loads", async () => {
    const api = installFakeReviewApi({ drafts: draftOf(["islam/native"]) });
    let release!: () => void;
    const gate = new Promise<void>((r) => (release = r));
    api.override((path, method) =>
      path === `/api/review/${SAMPLE_ID}` && method === "GET"
        ? gate.then(() => json({ state: { texts: ["islam/native"], labels: {} }, version: 1 }))
        : undefined,
    );
    renderApp("/review");
    expect(await screen.findByTestId("review-page")).toBeInTheDocument();
    expect(textBox(/Qur'an/)).toBeDisabled();
    expect(screen.getByRole("button", { name: "Download gold set" })).toBeDisabled();
    release();
    await waitFor(() => expect(textBox(/Qur'an/)).toBeEnabled());
    expect(textBox(/Qur'an/)).toBeChecked();
  });
});

describe("/review: progress and the pass", () => {
  it("counts labelled / in pass per text and overall, and shows each cell's label state", async () => {
    const labels = goldFixtureLabels();
    const one = { [ISLAM_PASS[2]!]: labels[ISLAM_PASS[2]!]! }; // incorrect
    const flagged = { [HINDU_PASS[3]!]: labels[HINDU_PASS[3]!]! }; // correct, defect
    const pending = { [HINDU_PASS[0]!]: { ...labels[HINDU_PASS[0]!]!, outcome: null } }; // no outcome yet
    installFakeReviewApi({ drafts: draftOf(["hinduism/english", "islam/native"], { ...one, ...flagged, ...pending }) });
    renderApp("/review");
    await screen.findByTestId("pass-list");

    expect(screen.getByRole("progressbar", { name: "Overall progress" })).toHaveAttribute("aria-valuenow", "2");
    expect(screen.getByRole("progressbar", { name: "Overall progress" })).toHaveAttribute("aria-valuemax", "10");
    const perText = screen.getAllByTestId("text-progress").map((li) => li.textContent);
    expect(perText).toEqual([
      "Bhagavad Gita — Annie Besant (1922)1 / 5 labelled",
      "The Qur'an — Uthmani (QUL)1 / 5 labelled",
    ]);

    const states = screen.getAllByTestId("label-state").map((s) => s.textContent);
    expect(states).toEqual([
      "not labelled",
      "not labelled", // an outcome-less label isn't a judgement
      "not labelled",
      "not labelled",
      "Correct · defect",
      "not labelled",
      "not labelled",
      "Incorrect",
      "not labelled",
      "not labelled",
    ]);
    // "Continue" goes to the first cell in pass order without an outcome.
    expect(screen.getByTestId("continue-link")).toHaveAttribute("href", cellHref(BOTH_PASS[0]!));
  });

  it("opens a cell's labelling page from its pass item", async () => {
    installFakeReviewApi({ drafts: draftOf(["islam/native"]) });
    renderApp("/review");
    const items = await screen.findAllByTestId("pass-item");
    await userEvent.click(items[2]!);
    expect(await screen.findByTestId("review-cell-page")).toBeInTheDocument();
    expect(screen.getByTestId("pass-position")).toHaveTextContent("cell 3 of 5 in your pass");
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("3:140");
  });
});

describe("/review: the gold-set download", () => {
  function captureDownloads() {
    const files: Array<{ name: string; href: string; blob: Blob }> = [];
    lastBlob = null;
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(function (this: HTMLAnchorElement) {
      files.push({ name: this.download, href: this.getAttribute("href") ?? "", blob: lastBlob! });
    });
    return files;
  }

  it("saves gold-<sample_id>.jsonl byte-identical to the fixture, the same both times", async () => {
    const files = captureDownloads();
    installFakeReviewApi({ drafts: draftOf(["islam/native"], goldFixtureLabels()) });
    renderApp("/review");
    const button = await screen.findByRole("button", { name: "Download gold set" });
    await waitFor(() => expect(button).toBeEnabled());
    expect(screen.getByText(/You have 10 labelled cells/)).toBeInTheDocument();

    await userEvent.click(button);
    await userEvent.click(button);

    expect(files.map((f) => f.name)).toEqual([`gold-${SAMPLE_ID}.jsonl`, `gold-${SAMPLE_ID}.jsonl`]);
    expect(files.every((f) => f.href === "blob:gold")).toBe(true);
    const [first, second] = await Promise.all(files.map((f) => readBlob(f.blob)));
    expect(first).toBe(GOLD_FIXTURE);
    expect(second).toBe(first);
  });

  it("is off until a cell has an outcome", async () => {
    installFakeReviewApi({ drafts: draftOf(["islam/native"]) });
    renderApp("/review");
    await screen.findByTestId("pass-list");
    expect(screen.getByRole("button", { name: "Download gold set" })).toBeDisabled();
    expect(screen.getByText(/You have 0 labelled cells/)).toBeInTheDocument();
  });

  it("shows why a gold set can't be written instead of saving a bad file", async () => {
    const files = captureDownloads();
    const stale = { "fixture-run:model-z:not-in-sample": { ...goldFixtureLabels()[ISLAM_PASS[0]!]! } };
    installFakeReviewApi({ drafts: draftOf(["islam/native"], stale) });
    renderApp("/review");
    const button = await screen.findByRole("button", { name: "Download gold set" });
    await waitFor(() => expect(button).toBeEnabled());
    await userEvent.click(button);
    expect(screen.getByTestId("download-error")).toHaveTextContent(/not in sample review_sample/);
    expect(files).toEqual([]);
  });
});
