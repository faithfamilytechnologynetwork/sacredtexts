import { describe, it, expect, afterEach, vi } from "vitest";
import { screen, within, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderApp } from "../test/renderApp";
import { type Summary } from "../lib/localResults";

afterEach(() => vi.unstubAllGlobals());

/** A fetcher that serves `/runs/_index` and each run's `summary.json` (the picker reads only
 * summary.json); any other URL 404s. */
function errorsFetcher(index: { id: string; mtimeMs: number }[], summaries: Record<string, Summary>): typeof fetch {
  return (async (url: string) => {
    if (url === "/runs/_index") {
      return { ok: true, status: 200, text: async () => JSON.stringify(index) } as Response;
    }
    const m = url.match(/^\/runs\/([^/]+)\/summary\.json$/);
    if (m && summaries[m[1]!]) {
      return { ok: true, status: 200, text: async () => JSON.stringify(summaries[m[1]!]) } as Response;
    }
    return { ok: false, status: 404 } as Response;
  }) as unknown as typeof fetch;
}

const cell = (accuracy: number, coverage: number, refused = 0) => ({ n: 4, accuracy, coverage, refused });

// Newest-first: an experiment run (never the default), then the default benchmark run, then an older one.
const INDEX = [
  { id: "exp-newest-2026-10-30", mtimeMs: 3 },
  { id: "run-b", mtimeMs: 2 },
  { id: "run-a", mtimeMs: 1 },
];
const SUMMARIES: Record<string, Summary> = {
  "exp-newest-2026-10-30": { models: { "exp-model": { _overall: cell(1, 1) } }, by_tradition: {} },
  "run-b": {
    models: {
      haiku: { retrieve_quote: cell(0.5, 0.75, 1), _overall: cell(0.5, 0.75, 1) },
      "gemma-4": { retrieve_quote: cell(0.25, 1), _overall: cell(0.25, 1) },
    },
    by_tradition: {},
  },
  "run-a": { models: { legacy: { _overall: cell(0.1, 1) } }, by_tradition: {} },
};

describe("Errors nav link", () => {
  it("renders in the header and targets /errors", async () => {
    vi.stubGlobal("fetch", errorsFetcher([], {}));
    renderApp("/");
    const link = await screen.findByRole("link", { name: "Verses" });
    expect(link.getAttribute("href")).toBe("/errors");
  });
});

describe("ErrorsPage — the error-explorer picker", () => {
  it("lists the default run's models (the leaderboard's default: newest non-experiment run)", async () => {
    vi.stubGlobal("fetch", errorsFetcher(INDEX, SUMMARIES));
    renderApp("/errors");
    const table = await screen.findByRole("table", { name: "Models in run run-b" });
    expect((screen.getByLabelText("Run") as HTMLSelectElement).value).toBe("run-b");

    const dataRows = within(table).getAllByRole("row").slice(1); // drop header
    // ranked by overall accuracy, as on the leaderboard
    expect(dataRows.map((r) => within(r).getByRole("link").textContent)).toEqual(["haiku", "gemma-4"]);
    // the headline accuracy and coverage sit beside each model
    expect(dataRows[0]!.textContent).toContain("50% (n=4)");
    expect(dataRows[0]!.textContent).toContain("75% (1 refused)");
    // neither the experiment run's nor the older run's models leak in
    expect(screen.queryByRole("link", { name: "exp-model" })).toBeNull();
    expect(screen.queryByRole("link", { name: "legacy" })).toBeNull();
  });

  it("links each model to its error explorer", async () => {
    vi.stubGlobal("fetch", errorsFetcher(INDEX, SUMMARIES));
    renderApp("/errors");
    const link = await screen.findByRole("link", { name: "haiku" });
    expect(link.getAttribute("href")).toBe("/run/run-b/model/haiku");
  });

  it("switches run from the dropdown and writes ?run= to the URL", async () => {
    vi.stubGlobal("fetch", errorsFetcher(INDEX, SUMMARIES));
    const { router } = renderApp("/errors");
    await screen.findByRole("link", { name: "haiku" });
    await userEvent.selectOptions(screen.getByLabelText("Run"), "run-a");
    const link = await screen.findByRole("link", { name: "legacy" });
    expect(link.getAttribute("href")).toBe("/run/run-a/model/legacy");
    await waitFor(() => expect(router.state.location.search).toEqual({ run: "run-a" }));
  });

  it("never paints the previous run's models under the newly selected run id", async () => {
    // Switching runs changes the selected id during render, before the load effect resets the
    // state. A transient frame must not render run-b's models as /run/run-a/... links. A
    // MutationObserver records every href the DOM ever carries, so even a frame that React
    // replaces within the same act() is caught.
    vi.stubGlobal("fetch", errorsFetcher(INDEX, SUMMARIES));
    renderApp("/errors");
    await screen.findByRole("link", { name: "haiku" });
    const seen = new Set<string>();
    const record = (n: Node) => {
      if (n instanceof Element) {
        for (const a of [n, ...n.querySelectorAll("a")]) {
          const href = a.getAttribute("href");
          if (a.tagName === "A" && href) seen.add(href);
        }
      }
    };
    const observer = new MutationObserver((records) => {
      for (const r of records) {
        record(r.target);
        r.addedNodes.forEach(record);
      }
    });
    observer.observe(document.body, { subtree: true, childList: true, attributes: true, attributeFilter: ["href"] });
    await userEvent.selectOptions(screen.getByLabelText("Run"), "run-a");
    await screen.findByRole("link", { name: "legacy" });
    observer.disconnect();
    expect(seen).toContain("/run/run-a/model/legacy");
    expect([...seen].filter((h) => h.startsWith("/run/run-a/") && h !== "/run/run-a/model/legacy")).toEqual([]);
  });

  it("honours ?run=<id>, including an experiment run", async () => {
    vi.stubGlobal("fetch", errorsFetcher(INDEX, SUMMARIES));
    renderApp("/errors?run=exp-newest-2026-10-30");
    const link = await screen.findByRole("link", { name: "exp-model" });
    expect(link.getAttribute("href")).toBe("/run/exp-newest-2026-10-30/model/exp-model");
  });

  it("shows the page title while the selected run is still loading", async () => {
    // run-b's summary never resolves, so the page stays in its run-loading state.
    const base = errorsFetcher(INDEX, SUMMARIES);
    vi.stubGlobal("fetch", (async (url: string) =>
      url === "/runs/run-b/summary.json" ? new Promise<Response>(() => {}) : base(url)) as unknown as typeof fetch);
    renderApp("/errors");
    expect(await screen.findByText("Loading run run-b…")).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 1, name: "Verses" })).toBeInTheDocument();
    expect(screen.queryByRole("table")).toBeNull();
  });

  it("shows the empty state when there are no runs", async () => {
    vi.stubGlobal("fetch", errorsFetcher([], {}));
    renderApp("/errors");
    expect(await screen.findByText(/No runs yet/i)).toBeInTheDocument();
  });

  it("keeps the selector usable when the selected run cannot be loaded", async () => {
    vi.stubGlobal("fetch", errorsFetcher(INDEX, { "run-a": SUMMARIES["run-a"]! }));
    renderApp("/errors");
    expect(await screen.findByText(/Could not load run run-b/)).toBeInTheDocument();
    // the page title stays up in the error state, not only once a run has loaded
    expect(screen.getByRole("heading", { level: 1, name: "Verses" })).toBeInTheDocument();
    await userEvent.selectOptions(screen.getByLabelText("Run"), "run-a");
    expect(await screen.findByRole("link", { name: "legacy" })).toBeInTheDocument();
  });
});
