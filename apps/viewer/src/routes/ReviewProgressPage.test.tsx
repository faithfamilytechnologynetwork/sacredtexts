import { describe, it, expect, beforeEach } from "vitest";
import { act, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderApp } from "../test/renderApp";
import { draftOf, installFakeReviewApi, json, SAMPLE_ID } from "../test/reviewHarness";
import { resetReviewStore } from "../lib/review";

const PROGRESS = {
  sampleId: SAMPLE_ID,
  reviewers: [
    {
      name: "Amira",
      texts: ["islam/native"],
      labelledCellIds: ["fixture-run:model-b:df788ade727db3cf", "fixture-run:model-a:f713b30ff8deb19b", "fixture-run:model-a:12e45dddc647beb6"],
      submissions: 0,
      updatedAt: "2026-11-17T22:05:00.000Z",
    },
    { name: "Ben", texts: [], labelledCellIds: [], submissions: 0, updatedAt: "2026-11-18T08:00:00.000Z" },
  ],
};

beforeEach(() => resetReviewStore());

function serveProgress(reply: () => Response) {
  const api = installFakeReviewApi({ drafts: draftOf(["islam/native"]) });
  api.override((path) => (path === "/api/progress" ? reply() : undefined));
}

describe("/review/progress", () => {
  it("shows every reviewer's labels per text and how much of each text anyone has labelled", async () => {
    serveProgress(() => json(PROGRESS));
    renderApp("/review/progress");
    const rows = await screen.findAllByTestId("reviewer-row");
    expect(rows).toHaveLength(2);
    const amira = within(rows[0]!);
    expect(amira.getByText("Amira")).toBeInTheDocument();
    expect(amira.getAllByTestId("reviewer-text").map((li) => li.textContent)).toEqual([
      "Bhagavad Gita — Annie Besant (1922) (not chosen)1 / 5 labelled",
      "The Qur'an — Uthmani (QUL)2 / 5 labelled",
    ]);
    expect(amira.getByTestId("reviewer-labelled")).toHaveTextContent("3");
    expect(amira.getByText("2026-11-17")).toHaveAttribute("datetime", "2026-11-17T22:05:00.000Z");
    expect(within(rows[1]!).getByText("No texts chosen yet")).toBeInTheDocument();
    expect(within(rows[1]!).getByTestId("reviewer-labelled")).toHaveTextContent("0");

    expect(screen.getByRole("progressbar", { name: "Overall coverage" })).toHaveAttribute("aria-valuenow", "3");
    expect(within(screen.getByTestId("coverage")).getAllByRole("listitem").map((li) => li.textContent)).toEqual([
      "Bhagavad Gita — Annie Besant (1922)1 / 5 labelled",
      "The Qur'an — Uthmani (QUL)2 / 5 labelled",
      "Talmud Bavli — Aramaic0 / 2 labelled",
      "Sri Guru Granth Sahib0 / 1 labelled",
    ]);
  });

  it("says so when no one has started", async () => {
    serveProgress(() => json({ sampleId: SAMPLE_ID, reviewers: [] }));
    renderApp("/review/progress");
    expect(await screen.findByTestId("no-reviewers")).toBeInTheDocument();
    expect(screen.getByRole("progressbar", { name: "Overall coverage" })).toHaveAttribute("aria-valuemax", "13");
  });

  it("shows a failed load and loads again on retry", async () => {
    let fail = true;
    serveProgress(() => (fail ? json({ error: "boom" }, 400) : json(PROGRESS)));
    renderApp("/review/progress");
    expect(await screen.findByRole("alert")).toHaveTextContent("Couldn’t load the progress: boom");
    fail = false;
    await userEvent.click(screen.getByRole("button", { name: "Try again" }));
    expect(await screen.findAllByTestId("reviewer-row")).toHaveLength(2);
  });

  it("refuses progress for a different sample than the one loaded", async () => {
    serveProgress(() => json({ ...PROGRESS, sampleId: "another-sample" }));
    renderApp("/review/progress");
    expect(await screen.findByRole("alert")).toHaveTextContent(`the progress is for sample another-sample, not ${SAMPLE_ID}`);
  });

  it("is linked from /review", async () => {
    serveProgress(() => json(PROGRESS));
    const { router } = renderApp("/review");
    expect(await screen.findByTestId("progress-link")).toHaveAttribute("href", "/review/progress");
    await act(() => router.navigate({ to: "/review/progress" }));
    expect(await screen.findByTestId("review-progress-page")).toBeInTheDocument();
  });
});
