import { useEffect, useState } from "react";
import { CenteredSpinner } from "../components/Loading";

interface GapItem {
  id: string;
  task: string;
  tradition: string;
  citation: string;
}

interface GapFile {
  model: string;
  file: string;
  questions: number;
  saved: number;
  missing: GapItem[];
  empty: GapItem[];
}

type State =
  | { status: "loading" }
  | { status: "failed"; message: string }
  | { status: "ready"; files: GapFile[] };

export function GapsPage() {
  const [state, setState] = useState<State>({ status: "loading" });

  useEffect(() => {
    let live = true;
    (async () => {
      try {
        const res = await fetch("/runs/_gaps");
        const text = await res.text();
        if (!live) return;
        if (!res.ok || text.trimStart().startsWith("<")) {
          setState({ status: "failed", message: "The run server did not return a gap list." });
          return;
        }
        const files = JSON.parse(text) as GapFile[];
        setState({ status: "ready", files: Array.isArray(files) ? files : [] });
      } catch (e) {
        if (live) setState({ status: "failed", message: (e as Error).message });
      }
    })();
    return () => {
      live = false;
    };
  }, []);

  if (state.status === "loading") return <CenteredSpinner label="Checking unsaved questions…" />;
  if (state.status === "failed") {
    return (
      <div role="alert" className="mx-auto max-w-2xl py-16 text-center">
        <p className="font-semibold text-danger">Could not load gaps</p>
        <p className="mt-1 text-sm text-default-500">{state.message}</p>
      </div>
    );
  }

  const missingN = state.files.reduce((n, f) => n + f.missing.length, 0);
  const emptyN = state.files.reduce((n, f) => n + f.empty.length, 0);

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <h1 className="text-2xl font-semibold">Unsaved and empty</h1>
      <p className="mt-1 text-sm text-default-500">
        A question is listed when its file has answers but no summary, so the collect did not finish,
        and that question has no saved row. A finished short run, such as the first nine Buddhism
        questions, is not listed. An empty row is a saved answer with no text.
      </p>
      <p className="mt-3 text-sm">
        {state.files.length === 0
          ? "No unfinished files and no empty answers."
          : `${state.files.length} files · ${missingN} unsaved questions shown · ${emptyN} empty answers`}
      </p>
      <div className="mt-4 space-y-6">
        {state.files.map((file) => (
          <section key={file.file}>
            <h2 className="text-base font-semibold">
              {file.model}{" "}
              <span className="font-normal text-default-500">
                {file.saved} saved of {file.questions} · {file.file}
              </span>
            </h2>
            {file.missing.length > 0 && (
              <table className="mt-2 w-full border-collapse text-sm">
                <caption className="mb-1 text-left text-xs text-default-500">Not saved</caption>
                <thead>
                  <tr className="border-b text-left">
                    <th className="py-1 pr-4">task</th>
                    <th className="py-1 pr-4">tradition</th>
                    <th className="py-1 pr-4">citation</th>
                    <th className="py-1 pr-4">id</th>
                  </tr>
                </thead>
                <tbody>
                  {file.missing.map((row) => (
                    <tr key={row.id} className="border-b">
                      <td className="py-1 pr-4">{row.task}</td>
                      <td className="py-1 pr-4">{row.tradition}</td>
                      <td className="py-1 pr-4">{row.citation}</td>
                      <td className="py-1 pr-4 font-mono text-xs">{row.id}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
            {file.empty.length > 0 && (
              <table className="mt-2 w-full border-collapse text-sm">
                <caption className="mb-1 text-left text-xs text-default-500">Empty answer</caption>
                <thead>
                  <tr className="border-b text-left">
                    <th className="py-1 pr-4">task</th>
                    <th className="py-1 pr-4">citation</th>
                    <th className="py-1 pr-4">id</th>
                  </tr>
                </thead>
                <tbody>
                  {file.empty.map((row) => (
                    <tr key={`e-${row.id}`} className="border-b">
                      <td className="py-1 pr-4">{row.task}</td>
                      <td className="py-1 pr-4">{row.citation}</td>
                      <td className="py-1 pr-4 font-mono text-xs">{row.id}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>
        ))}
      </div>
    </div>
  );
}
