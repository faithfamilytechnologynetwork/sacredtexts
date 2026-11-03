import { describe, it, expect, afterEach, vi } from "vitest";
import { screen } from "@testing-library/react";
import { renderApp } from "../test/renderApp";

afterEach(() => vi.unstubAllGlobals());

describe("Judge page", () => {
  it("renders coherent counts and keeps the incoherent total separate", async () => {
    vi.stubGlobal(
      "fetch",
      (async (url: string) => {
        if (String(url).endsWith("/_judge")) {
          return {
            ok: true,
            status: 200,
            text: async () =>
              JSON.stringify({
                file: "judgments-v5.jsonl",
                models: [
                  {
                    model: "argon",
                    rows: 3,
                    coherent: 2,
                    incoherent: 1,
                    cost: 0.003,
                    kind: { refusal: 1, requested_wording: 1 },
                    theology: { accurate: 1, no_claim: 1 },
                  },
                ],
              }),
          };
        }
        return { ok: true, status: 200, text: async () => "[]" };
      }) as unknown as typeof fetch,
    );
    renderApp("/judge");
    expect(await screen.findByRole("heading", { name: "Judge" })).toBeInTheDocument();
    expect(screen.getByText(/2 coherent of 3 judged/)).toBeInTheDocument();
    expect(screen.getByText("argon")).toBeInTheDocument();
  });
});
