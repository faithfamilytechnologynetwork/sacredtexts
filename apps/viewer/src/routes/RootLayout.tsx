import { useEffect, useRef } from "react";
import { Link, Outlet, useRouterState } from "@tanstack/react-router";

const NAV = [
  { to: "/", label: "Scores" },
  { to: "/errors", label: "Verses" },
  { to: "/findings", label: "Findings" },
  { to: "/standings", label: "Standings" },
  { to: "/judge", label: "Judge" },
  { to: "/gaps", label: "Gaps" },
] as const;

export function RootLayout() {
  // `main` is the app's scroll container (h-dvh shell) — its scrollTop would otherwise persist across
  // route changes. Reset it to the top on every pathname change.
  const mainRef = useRef<HTMLElement>(null);
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  useEffect(() => { if (mainRef.current) mainRef.current.scrollTop = 0; }, [pathname]);
  return (
    // Viewport-height app shell: the header is fixed; the scroll lives INSIDE (main for normal pages).
    // So `document` never overflows — a page fits one screen; the inner scroll does the rest.
    <div className="flex h-dvh flex-col bg-background text-foreground">
      <header className="shrink-0 border-b border-default-200">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-x-6 gap-y-2 px-4 py-3">
          <Link to="/" className="text-lg font-semibold">
            SacredBench
          </Link>
          <nav aria-label="Primary" className="flex flex-wrap items-center gap-1 text-sm">
            {NAV.map((item) => (
              <Link
                key={item.to}
                to={item.to}
                activeOptions={{ exact: true }}
                className="rounded-md px-2.5 py-1 text-default-600 hover:bg-default-100 hover:text-foreground [&.active]:bg-default-100 [&.active]:font-semibold [&.active]:text-foreground"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <main ref={mainRef} className="mx-auto min-h-0 w-full max-w-6xl flex-1 overflow-y-auto px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
