import { useEffect, useState } from "react";
import { CenteredSpinner } from "../components/Loading";

interface JudgeModel {
  model: string;
  rows: number;
  coherent: number;
  incoherent: number;
  cost: number;
  kind: Record<string, number>;
  theology: Record<string, number>;
}

interface JudgeReport {
  file: string;
  models: JudgeModel[];
}

type State =
  | { status: "loading" }
  | { status: "failed"; message: string }
  | { status: "ready"; report: JudgeReport };

const KINDS: { key: string; label: string }[] = [
  { key: "refusal", label: "Refusal" },
  { key: "requested_wording", label: "Requested wording" },
  { key: "faithful_paraphrase", label: "Faithful paraphrase" },
  { key: "meaning_change", label: "Meaning change" },
  { key: "wrong_passage", label: "Wrong passage" },
  { key: "neither", label: "Neither" },
];

const THEOLOGY: { key: string; label: string }[] = [
  { key: "accurate", label: "Accurate" },
  { key: "gloss", label: "Gloss" },
  { key: "distorted", label: "Distorted" },
  { key: "contradicted", label: "Contradicted" },
  { key: "no_claim", label: "No claim" },
];

function n(model: JudgeModel, bag: "kind" | "theology", key: string): number {
  return model[bag][key] ?? 0;
}

export function JudgePage() {
  const [state, setState] = useState<State>({ status: "loading" });

  useEffect(() => {
    let live = true;
    (async () => {
      try {
        const res = await fetch("/runs/_judge");
        const text = await res.text();
        if (!live) return;
        if (!res.ok || text.trimStart().startsWith("<")) {
          setState({ status: "failed", message: "The run server did not return judge counts." });
          return;
        }
        const report = JSON.parse(text) as JudgeReport;
        setState({
          status: "ready",
          report: { file: report.file ?? "judgments-v5.jsonl", models: Array.isArray(report.models) ? report.models : [] },
        });
      } catch (e) {
        if (live) setState({ status: "failed", message: (e as Error).message });
      }
    })();
    return () => {
      live = false;
    };
  }, []);

  if (state.status === "loading") return <CenteredSpinner label="Reading judge labels…" />;
  if (state.status === "failed") {
    return (
      <div role="alert" className="mx-auto max-w-2xl py-16 text-center">
        <p className="font-semibold text-danger">Could not load judge labels</p>
        <p className="mt-1 text-sm text-default-500">{state.message}</p>
      </div>
    );
  }

  const models = state.report.models;
  const rows = models.reduce((s, m) => s + m.rows, 0);
  const coherent = models.reduce((s, m) => s + m.coherent, 0);
  const incoherent = models.reduce((s, m) => s + m.incoherent, 0);
  const cost = models.reduce((s, m) => s + m.cost, 0);

  return (
    <div>
      <h1 className="text-2xl font-semibold">Judge</h1>
      <p className="mt-1 max-w-3xl text-sm text-default-500">
        Jev labels for cells the string score did not settle. The headline accuracy stays the string
        match. Kind is the form of the answer. Theology is how far its claims sit from the requested
        wording. Spelling, accents, and vowel signs are the same claim. A quotation that drops a clause
        is not accurate. Counts below are coherent rows only. Incoherent rows stay out of those columns.
      </p>
      <p className="mt-3 text-sm">
        {models.length === 0
          ? "No judgments-v5 files yet."
          : `${models.length} models · ${coherent} coherent of ${rows} judged · ${incoherent} incoherent · $${cost.toFixed(4)}`}
      </p>
      {models.length > 0 && (
        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-default-200 text-default-500">
                <th className="py-2 pr-3 font-medium">Model</th>
                <th className="py-2 pr-3 font-medium">Coherent</th>
                {KINDS.map((k) => (
                  <th key={k.key} className="py-2 pr-3 font-medium">{k.label}</th>
                ))}
                {THEOLOGY.map((k) => (
                  <th key={k.key} className="py-2 pr-3 font-medium">{k.label}</th>
                ))}
                <th className="py-2 pr-3 font-medium">Incoherent</th>
              </tr>
            </thead>
            <tbody>
              {models.map((m) => (
                <tr key={m.model} className="border-b border-default-100">
                  <td className="py-2 pr-3 font-medium">{m.model}</td>
                  <td className="py-2 pr-3">{m.coherent}</td>
                  {KINDS.map((k) => (
                    <td key={k.key} className="py-2 pr-3">{n(m, "kind", k.key)}</td>
                  ))}
                  {THEOLOGY.map((k) => (
                    <td key={k.key} className="py-2 pr-3">{n(m, "theology", k.key)}</td>
                  ))}
                  <td className="py-2 pr-3">{m.incoherent}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
