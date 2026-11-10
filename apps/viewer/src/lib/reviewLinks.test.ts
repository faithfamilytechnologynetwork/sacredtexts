import { describe, it, expect } from "vitest";
import { createMemoryHistory } from "@tanstack/react-router";
import { createAppRouter } from "../router";
import { CELL_ROUTE, cellHref, cellIdFromParam, cellLink } from "./reviewLinks";

const IDS = [
  "facct-2026-11-03:qwen3-32b:05f737b9d36571be", // the real shape: `:` separators
  "run:vendor/model:q1", // a `/` would otherwise split the segment
  "run:model 50%:q#2?x=1", // space, `%`, `#`, `?`
  "run:מודל:ש1", // non-ASCII
];

/** The `$cellId` param the real router matches for a URL. */
function matchedParam(url: string): string | undefined {
  const router = createAppRouter(createMemoryHistory({ initialEntries: ["/"] }));
  const matches = router.matchRoutes(url);
  const leaf = matches[matches.length - 1];
  if (leaf?.routeId !== CELL_ROUTE) return undefined;
  return (leaf.params as { cellId?: string }).cellId;
}

describe("review cell links", () => {
  it("percent-encodes the id into one path segment", () => {
    expect(cellHref("facct-2026-11-03:haiku:0c83124520583c65")).toBe(
      "/review/cell/facct-2026-11-03%3Ahaiku%3A0c83124520583c65",
    );
    for (const id of IDS) {
      const segment = cellHref(id).slice("/review/cell/".length);
      expect(segment).not.toMatch(/[:/ #?]/);
      expect(decodeURIComponent(segment)).toBe(id);
    }
  });

  it("cellHref is the URL the router builds for cellLink", () => {
    const router = createAppRouter(createMemoryHistory({ initialEntries: ["/"] }));
    for (const id of IDS) expect(router.buildLocation(cellLink(id)).href).toBe(cellHref(id));
  });

  it("an id round-trips through the link and the route's param", () => {
    for (const id of IDS) {
      const param = matchedParam(cellHref(id));
      expect(param).toBeDefined();
      expect(cellIdFromParam(param!)).toBe(id);
    }
  });
});
