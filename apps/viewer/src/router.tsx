import {
  createRootRoute,
  createRoute,
  createRouter,
  type RouterHistory,
} from "@tanstack/react-router";
import { RootLayout } from "./routes/RootLayout";
import { LeaderboardPage } from "./routes/LeaderboardPage";
import { ExplorerPage } from "./routes/ExplorerPage";
import { StandingsPage } from "./routes/StandingsPage";
import { GapsPage } from "./routes/GapsPage";
import { ErrorsPage } from "./routes/ErrorsPage";
import { JudgePage } from "./routes/JudgePage";
import { FindingsPage } from "./routes/FindingsPage";
import { ReviewPage } from "./routes/ReviewPage";
import { ReviewCellPage } from "./routes/ReviewCellPage";
import { ReviewResultsPage } from "./routes/ReviewResultsPage";
import { NotFound } from "./routes/NotFound";
import { FAILURE_KINDS, type FailureKind } from "./lib/failureKind";
import { type ExplorerFilters } from "./lib/explorer";

// Code-based routing (deliberate, documented deviation from "file-based"): avoids the
// router-plugin codegen step, keeps the route tree explicit, and is fully unit-testable
// with a memory history. The tree is `/` (the leaderboard home, selecting a run via the
// `?run=<id>` search param), `/run/$runId/model/$modelId` (the error explorer, with its
// `?task=&tradition=&correct=&mode=&kind=` filter state), `/errors` (a run + model picker in front
// of the explorer, `?run=<id>`), `/standings` (the cross-run current standings), `/gaps`, plus a
// catch-all 404.

const rootRoute = createRootRoute({
  component: RootLayout,
  notFoundComponent: () => <NotFound />,
});

// The run selection lives in the URL as a bare run id (`?run=<id>`). A plain validator
// (not zod — pruned in the purge) keeps it to an optional string; an absent or non-string
// value becomes undefined, and the page falls back to the most-recent run.
const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: LeaderboardPage,
  validateSearch: (search: Record<string, unknown>): { run?: string } => ({
    run: typeof search.run === "string" ? search.run : undefined,
  }),
});

// The error explorer: `/run/$runId/model/$modelId` with composing filter state in the URL.
// A plain validator (zod stays pruned) coerces each param to its allowed values, dropping
// anything unexpected to undefined so a hand-edited URL never breaks the page.
const explorerRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/run/$runId/model/$modelId",
  component: ExplorerPage,
  validateSearch: (search: Record<string, unknown>): ExplorerFilters => ({
    task: typeof search.task === "string" && search.task ? search.task : undefined,
    tradition: typeof search.tradition === "string" && search.tradition ? search.tradition : undefined,
    correct:
      search.correct === "correct" ||
      search.correct === "incorrect" ||
      search.correct === "refused" ||
      search.correct === "missing"
        ? search.correct
        : undefined,
    mode:
      search.mode === "missing" || search.mode === "refused" || search.mode === "wrong"
        ? search.mode
        : undefined,
    kind: FAILURE_KINDS.includes(search.kind as FailureKind) ? (search.kind as FailureKind) : undefined,
  }),
});

// The cross-run current standings: `/standings`, no search state.
const standingsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/standings",
  component: StandingsPage,
});

const gapsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/gaps",
  component: GapsPage,
});

// The error-explorer picker: `/errors` lists one run's models as links into the explorer. Same
// `?run=<id>` validator as the leaderboard home; an unknown id falls back to the same default run.
const findingsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/findings",
  component: FindingsPage,
});

const judgeRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/judge",
  component: JudgePage,
});

const errorsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/errors",
  component: ErrorsPage,
  validateSearch: (search: Record<string, unknown>): { run?: string } => ({
    run: typeof search.run === "string" ? search.run : undefined,
  }),
});

// The review pages (Spec 154): the reviewer's home, their results (#157) and one cell's labelling page. A cell id carries
// `:`, so links to it go through lib/reviewLinks (the router percent-encodes the param).
const reviewRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/review",
  component: ReviewPage,
});

const reviewResultsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/review/results",
  component: ReviewResultsPage,
});

const reviewCellRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/review/cell/$cellId",
  component: ReviewCellPage,
});

const routeTree = rootRoute.addChildren([
  indexRoute,
  explorerRoute,
  standingsRoute,
  gapsRoute,
  errorsRoute,
  judgeRoute,
  findingsRoute,
  reviewRoute,
  reviewResultsRoute,
  reviewCellRoute,
]);

export function createAppRouter(history?: RouterHistory) {
  return createRouter({
    routeTree,
    defaultNotFoundComponent: () => <NotFound />,
    ...(history ? { history } : {}),
  });
}

export const router = createAppRouter();

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
