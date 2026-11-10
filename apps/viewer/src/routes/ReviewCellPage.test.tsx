import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { act, cleanup, fireEvent, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderApp } from "../test/renderApp";
import { draftOf, installFakeReviewApi, json, multiScriptSample, ODD_CELL_ID, SAMPLE_ID } from "../test/reviewHarness";
import { flushReviewSaves, NOTES_MAX_CHARS, resetReviewStore } from "../lib/review";
import { cellHref } from "../lib/reviewLinks";
import { RUBRIC, RUBRIC_VERSION } from "../lib/rubric";

const ISLAM_QUOTE = "fixture-run:model-a:7c41160f85999097"; // retrieve_quote, matcher correct via containment
const ISLAM_CITE = "fixture-run:model-a:12e45dddc647beb6";
const HEBREW = "fixture-run:model-a:he0001";
const GURMUKHI = "fixture-run:model-a:pa0001";
const HINDU_FIRST = "fixture-run:model-b:e84250807e983aef";
/** hinduism/english + islam/native, in sample order. */
const BOTH_PASS = [
  "fixture-run:model-b:df788ade727db3cf",
  "fixture-run:model-b:e84250807e983aef",
  "fixture-run:model-a:f713b30ff8deb19b",
  "fixture-run:model-a:44fef84fa1aef80b",
  "fixture-run:model-b:1e33ec77e1ed0b3f",
  "fixture-run:model-a:b9bdeb4400fc2a64",
  "fixture-run:model-b:aeaa707307175fdb",
  "fixture-run:model-a:12e45dddc647beb6",
  "fixture-run:model-a:aeaa707307175fdb",
  "fixture-run:model-a:7c41160f85999097",
];

const SAMPLE = multiScriptSample();
const cellOf = (id: string) => SAMPLE.cells.find((c: { cell_id: string }) => c.cell_id === id);
/** Testing Library collapses whitespace in the DOM text, not in a string matcher: collapse it here. */
const collapsed = (text: string) => text.replace(/\s+/g, " ").trim();

beforeEach(() => resetReviewStore());
afterEach(() => vi.restoreAllMocks());

const outcomeButton = (name: string) => screen.getByRole("button", { name });
const whenEditable = () => waitFor(() => expect(outcomeButton("Incorrect")).toBeEnabled());

describe("/review/cell/$cellId: what the reviewer sees", () => {
  it("shows the explorer's card, the matcher's verdict, every submetric and the grader path", async () => {
    installFakeReviewApi({ drafts: draftOf(["islam/native"]) });
    renderApp(cellHref(ISLAM_QUOTE));
    expect(await screen.findByTestId("review-cell-page")).toBeInTheDocument();

    const heading = screen.getByRole("heading", { level: 1 });
    expect(heading).toHaveTextContent("The Qur'an — Uthmani (QUL)");
    expect(heading).toHaveTextContent("28:82");
    expect(screen.getByText("model-a", { selector: "span" })).toBeInTheDocument();
    expect(screen.getByText(ISLAM_QUOTE)).toBeInTheDocument();

    const card = screen.getByTestId("question-card");
    expect(within(card).getByText(collapsed(cellOf(ISLAM_QUOTE).prompt))).toBeInTheDocument();
    expect(within(card).getByText("exact")).toBeInTheDocument();

    const verdict = screen.getByTestId("matcher-verdict");
    expect(within(verdict).getByTestId("matcher-outcome")).toHaveTextContent("correct");
    expect(within(verdict).getByTestId("grader-path")).toHaveTextContent("contained");
    const metrics = Object.fromEntries(
      within(verdict)
        .getAllByRole("term")
        .map((dt) => [dt.textContent, dt.nextElementSibling?.textContent]),
    );
    expect(metrics).toEqual({
      contains_reference: "1",
      correct: "1",
      exact: "0",
      normalized: "0",
      token_f1: "0.5778",
      token_f1_base: "0.5778",
    });
  });

  it("shows the rubric of the cell's own task, with its version", async () => {
    installFakeReviewApi({ drafts: draftOf(["hinduism/english", "islam/native"]) });
    const byTask = new Map<string, string>();
    for (const c of SAMPLE.cells) if (!byTask.has(c.task)) byTask.set(c.task, c.cell_id);
    expect([...byTask.keys()].sort()).toEqual(["cite_passage", "complete_unit", "retrieve_quote", "verify_source"]);

    for (const [task, id] of byTask) {
      const { unmount } = renderApp(cellHref(id));
      const rubric = await screen.findByTestId("rubric");
      expect(rubric).toHaveTextContent(`Rubric: ${task}`);
      expect(within(rubric).getByTestId("rubric-version")).toHaveTextContent(`version ${RUBRIC_VERSION}`);
      for (const rule of RUBRIC[task as keyof typeof RUBRIC].rules) expect(rubric).toHaveTextContent(rule.text);
      const tolerances = task === "retrieve_quote" || task === "complete_unit";
      expect(within(rubric).queryByText("Ignore:") !== null).toBe(tolerances);
      expect(rubric).toHaveTextContent("Use can't judge when you can't tell");
      unmount();
    }
  });

  it.each([
    ["Arabic", ISLAM_QUOTE, "ar"],
    ["Hebrew", HEBREW, "he"],
    ["Gurmukhi", GURMUKHI, "pa"],
  ])("renders %s with dir=auto, its lang and the script font", async (_name, id, lang) => {
    installFakeReviewApi({ drafts: draftOf(["islam/native", "judaism/native", "sikhism/native"]) });
    renderApp(cellHref(id));
    const card = await screen.findByTestId("question-card");
    const cell = cellOf(id);
    for (const text of [cell.prompt, cell.expected.text, cell.answer]) {
      const el = within(card).getByText(collapsed(text));
      expect(el).toHaveAttribute("dir", "auto");
      expect(el).toHaveAttribute("lang", lang);
      expect(el).toHaveClass("script-text");
    }
  });

  it("shows a not-found message for a cell id that isn't in the sample", async () => {
    installFakeReviewApi();
    renderApp(cellHref("fixture-run:model-a:not-a-cell"));
    const alert = await screen.findByTestId("cell-not-found");
    expect(alert).toHaveTextContent("fixture-run:model-a:not-a-cell isn’t in the review sample review_sample");
    expect(within(alert).getByRole("link", { name: /Back to your pass/ })).toHaveAttribute("href", "/review");
  });

  it("notes a cell outside the chosen texts, and still lets the reviewer label it", async () => {
    installFakeReviewApi({ drafts: draftOf(["islam/native"]) });
    renderApp(cellHref(HINDU_FIRST));
    expect(await screen.findByTestId("outside-pass")).toBeInTheDocument();
    expect(screen.queryByTestId("pass-position")).toBeNull();
    await whenEditable();
  });
});

describe("/review/cell/$cellId: labelling", () => {
  it("records outcome, defect and notes in the store, and the pass's progress follows", async () => {
    const api = installFakeReviewApi({ drafts: draftOf(["islam/native"]) });
    renderApp(cellHref(ISLAM_CITE));
    await whenEditable();

    await userEvent.click(outcomeButton("Incorrect"));
    expect(outcomeButton("Incorrect")).toHaveAttribute("aria-pressed", "true");
    expect(outcomeButton("Correct")).toHaveAttribute("aria-pressed", "false");
    await userEvent.click(screen.getByRole("checkbox", { name: /Question defect/ }));
    await userEvent.type(screen.getByRole("textbox", { name: /Notes/ }), "Two locations.");
    expect(screen.getByTestId("notes-counter")).toHaveTextContent(`14 / ${NOTES_MAX_CHARS}`);

    await act(() => flushReviewSaves());
    const saved = (api.drafts.get(SAMPLE_ID)?.state as any).labels[ISLAM_CITE];
    expect(saved).toMatchObject({ outcome: "incorrect", defect: true, notes: "Two locations.", rubric_version: RUBRIC_VERSION });
    expect(Number.isNaN(Date.parse(saved.labelled_at))).toBe(false);

    await userEvent.click(screen.getByRole("link", { name: "← Your pass" }));
    expect(await screen.findByRole("progressbar", { name: "Overall progress" })).toHaveAttribute("aria-valuenow", "1");
    expect(screen.getAllByTestId("label-state")[2]).toHaveTextContent("Incorrect · defect");
  });

  it("clears the outcome when the chosen one is clicked again", async () => {
    installFakeReviewApi({ drafts: draftOf(["islam/native"]) });
    renderApp(cellHref(ISLAM_CITE));
    await whenEditable();
    await userEvent.click(outcomeButton("Can't judge"));
    expect(outcomeButton("Can't judge")).toHaveAttribute("aria-pressed", "true");
    await userEvent.click(outcomeButton("Can't judge"));
    expect(outcomeButton("Can't judge")).toHaveAttribute("aria-pressed", "false");
  });

  it("caps notes at NOTES_MAX_CHARS and says an outcome is still needed", async () => {
    installFakeReviewApi({ drafts: draftOf(["islam/native"]) });
    renderApp(cellHref(ISLAM_CITE));
    await whenEditable();
    const notes = screen.getByRole("textbox", { name: /Notes/ });
    expect(notes).toHaveAttribute("maxLength", String(NOTES_MAX_CHARS));
    expect(notes).toHaveAttribute("dir", "auto");
    fireEvent.change(notes, { target: { value: "ن".repeat(NOTES_MAX_CHARS + 5) } });
    expect(screen.getByTestId("notes-counter")).toHaveTextContent(`${NOTES_MAX_CHARS} / ${NOTES_MAX_CHARS}`);
    expect(screen.getByTestId("label-needs-outcome")).toBeInTheDocument();
  });

  it("keeps editing off until the saved labels load, and offers a retry when the load fails", async () => {
    const api = installFakeReviewApi({ drafts: draftOf(["islam/native"]) });
    api.override((path, method) =>
      path === `/api/review/${SAMPLE_ID}` && method === "GET" ? json({ error: "db down" }, 503) : undefined,
    );
    renderApp(cellHref(ISLAM_CITE));
    // The page's own load state (which shows the retry button) settles a tick after the store's error.
    const retry = await screen.findByRole("button", { name: "Try loading your labels again" });
    expect(screen.getByTestId("review-save-status")).toHaveTextContent(
      "Couldn't load your saved labels (db down). Editing stays off until they load.",
    );
    for (const name of ["Correct", "Incorrect", "Refused", "Can't judge"]) expect(outcomeButton(name)).toBeDisabled();
    expect(screen.getByRole("checkbox", { name: /Question defect/ })).toBeDisabled();
    expect(screen.getByRole("textbox", { name: /Notes/ })).toBeDisabled();
    // The chosen texts are unknown, not empty: no false "outside your texts" note, no pass position.
    expect(screen.queryByTestId("outside-pass")).toBeNull();
    expect(screen.queryByTestId("pass-position")).toBeNull();

    api.override(() => undefined);
    await userEvent.click(retry);
    await whenEditable();
    expect(screen.queryByTestId("review-save-status")).toBeNull();
    expect(screen.getByTestId("pass-position")).toHaveTextContent("cell 3 of 5 in your pass");
  });

  it("claims nothing about the pass while the saved labels are still loading", async () => {
    const api = installFakeReviewApi({ drafts: draftOf(["islam/native"]) });
    let release!: () => void;
    const gate = new Promise<void>((r) => (release = r));
    api.override((path, method) =>
      path === `/api/review/${SAMPLE_ID}` && method === "GET"
        ? gate.then(() => json({ state: { texts: ["islam/native"], labels: {} }, version: 1 }))
        : undefined,
    );
    renderApp(cellHref(ISLAM_CITE));
    expect(await screen.findByTestId("review-cell-page")).toBeInTheDocument();
    expect(outcomeButton("Incorrect")).toBeDisabled();
    expect(screen.queryByTestId("outside-pass")).toBeNull();
    expect(screen.queryByTestId("pass-position")).toBeNull();
    release();
    await whenEditable();
    expect(screen.getByTestId("pass-position")).toHaveTextContent("cell 3 of 5 in your pass");
    expect(screen.queryByTestId("outside-pass")).toBeNull();
  });

  it("shows a save the server refuses for good as 'Not saved', with no promise of a retry", async () => {
    const api = installFakeReviewApi({ drafts: draftOf(["islam/native"]) });
    renderApp(cellHref(ISLAM_CITE));
    await whenEditable();
    api.override((path, method) =>
      path === `/api/review/${SAMPLE_ID}` && method === "PUT" ? json({ error: "invalid draft" }, 400) : undefined,
    );
    await userEvent.click(outcomeButton("Refused"));
    await act(() => flushReviewSaves());
    const status = screen.getByTestId("review-save-status");
    expect(status).toHaveTextContent("Not saved: invalid draft.");
    expect(status).not.toHaveTextContent(/retry/i);
    expect(outcomeButton("Refused")).toHaveAttribute("aria-pressed", "true"); // the label stays on this device
  });
});

describe("/review/cell/$cellId: moving through the pass", () => {
  it("previous / next follow the pass order", async () => {
    installFakeReviewApi({ drafts: draftOf(["hinduism/english", "islam/native"]) });
    const { router } = renderApp(cellHref(BOTH_PASS[0]!));
    expect(await screen.findByTestId("pass-position")).toHaveTextContent("cell 1 of 10 in your pass");
    expect(screen.queryByRole("link", { name: "Previous cell" })).toBeNull();

    for (let i = 1; i < BOTH_PASS.length; i++) {
      await userEvent.click(screen.getByRole("link", { name: "Next cell" }));
      await waitFor(() => expect(router.state.location.pathname).toBe(cellHref(BOTH_PASS[i]!)));
      expect(screen.getByTestId("pass-position")).toHaveTextContent(`cell ${i + 1} of 10 in your pass`);
      expect(screen.getByText(BOTH_PASS[i]!)).toBeInTheDocument();
    }
    expect(screen.queryByRole("link", { name: "Next cell" })).toBeNull();

    await userEvent.click(screen.getByRole("link", { name: "Previous cell" }));
    await waitFor(() => expect(router.state.location.pathname).toBe(cellHref(BOTH_PASS[8]!)));
  });

  it("round-trips a cell id with `:`, `/`, `%` and a space through the link and the route", async () => {
    installFakeReviewApi({ drafts: draftOf(["judaism/native"]) });
    renderApp("/review");
    const items = await screen.findAllByTestId("pass-item");
    expect(items.map((a) => a.getAttribute("href"))).toEqual([cellHref(HEBREW), cellHref(ODD_CELL_ID)]);

    await userEvent.click(items[1]!);
    expect(await screen.findByTestId("review-cell-page")).toBeInTheDocument();
    expect(screen.getByText(ODD_CELL_ID)).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Berakhot 2a:2");
    expect(screen.getByTestId("pass-position")).toHaveTextContent("cell 2 of 2 in your pass");
    cleanup();

    // And straight from the URL, as a reload or a pasted link would arrive.
    renderApp(cellHref(ODD_CELL_ID));
    expect(await screen.findByText(ODD_CELL_ID)).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Berakhot 2a:2");
  });
});
