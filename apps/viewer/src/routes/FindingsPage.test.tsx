import { describe, it, expect, afterEach, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderApp } from "../test/renderApp";

afterEach(() => vi.unstubAllGlobals());

const REPORT = {
  models: [],
  traditions: [
    {
      tradition: "Judaism",
      rows: 10,
      coherent: 8,
      incoherent: 2,
      kind: { refusal: 2, wrong_passage: 4, faithful_paraphrase: 1, meaning_change: 1 },
      theology: { distorted: 5, accurate: 1, no_claim: 2 },
    },
  ],
};

describe("Findings page", () => {
  it("highlights a form and opens a tradition", async () => {
    vi.stubGlobal(
      "fetch",
      (async () => ({ ok: true, status: 200, text: async () => JSON.stringify(REPORT) })) as unknown as typeof fetch,
    );
    renderApp("/findings");
    expect(await screen.findByRole("heading", { name: "Findings" })).toBeInTheDocument();
    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Judaism Wrong passage 4" }));
    expect(screen.getByRole("heading", { name: "Judaism" })).toBeInTheDocument();
    expect(screen.getByText(/distorted or contradicted claims are 63%/)).toBeInTheDocument();
  });
});
