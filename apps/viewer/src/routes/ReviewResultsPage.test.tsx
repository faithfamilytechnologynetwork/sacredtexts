import { describe, it, expect, beforeEach } from "vitest";
import { act, screen, within } from "@testing-library/react";
import { renderApp } from "../test/renderApp";
import { draftOf, goldFixtureLabels, installFakeReviewApi, SAMPLE_ID } from "../test/reviewHarness";
import { resetReviewStore, updateReviewState, withLabel } from "../lib/review";
import { cellHref } from "../lib/reviewLinks";

const AR_RETRIEVE = "fixture-run:model-a:7c41160f85999097"; // matcher correct, human incorrect
const EN_RETRIEVE = "fixture-run:model-a:b9bdeb4400fc2a64"; // matcher incorrect, human correct

beforeEach(() => resetReviewStore());

describe("/review/results", () => {
  it("shows agreement overall and per group, the exclusions, and links each disagreement to its cell", async () => {
    installFakeReviewApi({ drafts: draftOf(["islam/native"], goldFixtureLabels()) });
    renderApp("/review/results");
    expect(await screen.findByTestId("results-overall")).toHaveTextContent("Overall: 6 / 8 (75.0%)");
    expect(screen.getByTestId("results-excluded")).toHaveTextContent(
      "10 labelled; 8 judged. Not counted: 2 (can’t judge 1, question defect 1, both 0).",
    );
    const byTask = within(screen.getByRole("region", { name: "By task" }));
    expect(byTask.getByText("retrieve_quote").nextSibling).toHaveTextContent("0 / 2 (0.0%)");
    expect(within(screen.getByRole("region", { name: "By grader path" })).getByText("none").nextSibling).toHaveTextContent("1 / 2 (50.0%)");
    const links = within(screen.getByTestId("disagreements")).getAllByRole("link");
    expect(links.map((a) => a.getAttribute("href"))).toEqual([cellHref(AR_RETRIEVE), cellHref(EN_RETRIEVE)]);
    expect(links[0]).toHaveTextContent("you: incorrect · matcher: correct");
  });

  it("follows label edits", async () => {
    installFakeReviewApi({ drafts: draftOf(["islam/native"], goldFixtureLabels()) });
    renderApp("/review/results");
    await screen.findByTestId("results-overall");
    act(() => updateReviewState((s) => withLabel(s, SAMPLE_ID, EN_RETRIEVE, { outcome: "incorrect" }, new Date())));
    expect(screen.getByTestId("results-overall")).toHaveTextContent("Overall: 7 / 8 (87.5%)");
    expect(within(screen.getByTestId("disagreements")).getAllByRole("link")).toHaveLength(1);
  });

  it("says so when nothing is labelled, and /review links here", async () => {
    installFakeReviewApi({ drafts: draftOf(["islam/native"]) });
    const { router } = renderApp("/review");
    expect(await screen.findByTestId("results-link")).toHaveAttribute("href", "/review/results");
    await act(() => router.navigate({ to: "/review/results" }));
    expect(await screen.findByTestId("no-results")).toBeInTheDocument();
  });
});
