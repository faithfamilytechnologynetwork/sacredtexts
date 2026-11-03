import { useEffect, useMemo, useState } from "react";
import { CenteredSpinner } from "../components/Loading";

interface JudgeTradition {
  tradition: string;
  rows: number;
  coherent: number;
  incoherent: number;
  kind: Record<string, number>;
  theology: Record<string, number>;
}

interface JudgeReport {
  models: { model: string; coherent: number; incoherent: number; cost: number }[];
  traditions: JudgeTradition[];
}

const KINDS: { key: string; label: string; color: string }[] = [
  { key: "refusal", label: "Refusal", color: "#73787c" },
  { key: "requested_wording", label: "Requested wording", color: "#338060" },
  { key: "faithful_paraphrase", label: "Faithful paraphrase", color: "#4073a0" },
  { key: "meaning_change", label: "Meaning change", color: "#d99e26" },
  { key: "wrong_passage", label: "Wrong passage", color: "#b3473d" },
  { key: "neither", label: "Neither", color: "#8c66a0" },
];

const THEOLOGY: { key: string; label: string; color: string }[] = [
  { key: "accurate", label: "Accurate", color: "#338060" },
  { key: "gloss", label: "Gloss", color: "#4073a0" },
  { key: "distorted", label: "Distorted", color: "#d99e26" },
  { key: "contradicted", label: "Contradicted", color: "#b3473d" },
  { key: "no_claim", label: "No claim", color: "#73787c" },
];

interface Tip {
  tradition: string;
  label: string;
  n: number;
  share: string;
}

type State =
  | { status: "loading" }
  | { status: "failed"; message: string }
  | { status: "ready"; report: JudgeReport };

function InteractiveBars({
  title,
  rows,
  series,
  bag,
  highlight,
  pinned,
  onHover,
  onPickKind,
  onPickTradition,
}: {
  title: string;
  rows: JudgeTradition[];
  series: { key: string; label: string; color: string }[];
  bag: "kind" | "theology";
  highlight: string | null;
  pinned: string | null;
  onHover: (tip: Tip | null) => void;
  onPickKind: (key: string | null) => void;
  onPickTradition: (name: string | null) => void;
}) {
  const labelW = 148;
  const rowH = 28;
  const width = 720;
  const barW = width - labelW - 48;
  const height = rows.length * rowH + 8;
  return (
    <figure className="mt-2">
      <figcaption className="text-sm font-medium">{title}</figcaption>
      <svg viewBox={`0 0 ${width} ${height}`} className="mt-1 w-full" role="img" aria-label={title}>
        {rows.map((row, i) => {
          const counts = row[bag];
          const total = series.reduce((s, item) => s + (counts[item.key] ?? 0), 0);
          const y = i * rowH + 4;
          let x = labelW;
          return (
            <g key={row.tradition}>
              <text
                x={0}
                y={y + 14}
                fontSize={12}
                fill={pinned === row.tradition ? "#111" : "#333"}
                fontWeight={pinned === row.tradition ? 700 : 500}
                style={{ cursor: "pointer" }}
                onClick={() => onPickTradition(pinned === row.tradition ? null : row.tradition)}
              >
                {row.tradition}
              </text>
              {series.map((item) => {
                const n = counts[item.key] ?? 0;
                if (!total || !n) return null;
                const w = (barW * n) / total;
                const dim = highlight !== null && highlight !== item.key;
                const segment = (
                  <rect
                    key={item.key}
                    x={x}
                    y={y}
                    width={Math.max(w, 0.5)}
                    height={16}
                    fill={item.color}
                    opacity={dim ? 0.18 : 1}
                    role="button"
                    tabIndex={0}
                    aria-label={`${row.tradition} ${item.label} ${n}`}
                    style={{ cursor: "pointer" }}
                    onMouseEnter={() =>
                      onHover({ tradition: row.tradition, label: item.label, n, share: pct(n, total) })
                    }
                    onMouseLeave={() => onHover(null)}
                    onFocus={() =>
                      onHover({ tradition: row.tradition, label: item.label, n, share: pct(n, total) })
                    }
                    onBlur={() => onHover(null)}
                    stroke={pinned === row.tradition && highlight === item.key ? "#111" : "none"}
                    strokeWidth={1}
                    onClick={() => {
                      const next = highlight === item.key ? null : item.key;
                      const reading = { tradition: row.tradition, label: item.label, n, share: pct(n, total) };
                      onPickTradition(row.tradition);
                      onPickKind(next);
                      onHover(reading);
                    }}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        const next = highlight === item.key ? null : item.key;
                        onPickTradition(row.tradition);
                        onPickKind(next);
                        onHover({ tradition: row.tradition, label: item.label, n, share: pct(n, total) });
                      }
                    }}
                  />
                );
                x += w;
                return segment;
              })}
              <text x={labelW + barW + 8} y={y + 13} fontSize={11} fill="#666">
                n={total}
              </text>
            </g>
          );
        })}
      </svg>
    </figure>
  );
}

function pct(n: number, d: number): string {
  if (!d) return "—";
  return `${Math.round((100 * n) / d)}%`;
}

export function FindingsPage() {
  const [state, setState] = useState<State>({ status: "loading" });
  const [kind, setKind] = useState<string | null>(null);
  const [tradition, setTradition] = useState<string | null>(null);
  const [tip, setTip] = useState<Tip | null>(null);
  const [locked, setLocked] = useState<Tip | null>(null);

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
          report: {
            models: Array.isArray(report.models) ? report.models : [],
            traditions: Array.isArray(report.traditions) ? report.traditions : [],
          },
        });
      } catch (e) {
        if (live) setState({ status: "failed", message: (e as Error).message });
      }
    })();
    return () => {
      live = false;
    };
  }, []);

  const selected = useMemo(() => {
    if (state.status !== "ready" || !tradition) return null;
    return state.report.traditions.find((t) => t.tradition === tradition) ?? null;
  }, [state, tradition]);

  if (state.status === "loading") return <CenteredSpinner label="Reading findings…" />;
  if (state.status === "failed") {
    return (
      <div role="alert" className="mx-auto max-w-2xl py-16 text-center">
        <p className="font-semibold text-danger">Could not load findings</p>
        <p className="mt-1 text-sm text-default-500">{state.message}</p>
      </div>
    );
  }

  const traditions = state.report.traditions;
  const rows = traditions.reduce((s, t) => s + t.rows, 0);
  const incoherent = traditions.reduce((s, t) => s + t.incoherent, 0);
  const focus = selected ?? null;
  const kindMeta = KINDS.find((item) => item.key === kind) ?? null;
  const ordered = kindMeta
    ? [...traditions].sort((a, b) => {
        const share = (row: JudgeTradition) => {
          const total = KINDS.reduce((s, item) => s + (row.kind[item.key] ?? 0), 0);
          return total ? (row.kind[kindMeta.key] ?? 0) / total : 0;
        };
        return share(b) - share(a);
      })
    : traditions;
  const reading = tip ?? locked;

  return (
    <div>
      <h1 className="text-2xl font-semibold">Findings</h1>
      <p className="mt-1 max-w-3xl text-sm text-default-500">
        One accuracy number mixes a refusal, a wrong passage, a changed meaning, and a paraphrase that
        keeps the claim. Hover or focus a segment for its count. Click a segment to keep that category
        lit. Click a tradition name to pin its shares. Incoherent rows stay out of the bars.
      </p>
      <p className="mt-3 text-sm">
        {traditions.length === 0
          ? "No judgments-v5 files yet."
          : `${rows} judged · ${rows - incoherent} coherent · ${incoherent} incoherent`}
      </p>

      <div className="mt-4 flex flex-wrap gap-2" role="group" aria-label="Highlight a form">
        <button
          type="button"
          onClick={() => setKind(null)}
          className={`rounded-full px-3 py-1 text-sm ${kind === null ? "bg-default-200 font-semibold" : "bg-default-100"}`}
        >
          All forms
        </button>
        {KINDS.map((item) => (
          <button
            key={item.key}
            type="button"
            aria-pressed={kind === item.key}
            onClick={() => setKind(kind === item.key ? null : item.key)}
            className={`rounded-full px-3 py-1 text-sm ${kind === item.key ? "font-semibold text-foreground ring-2 ring-default-400" : "text-default-700"}`}
            style={{ backgroundColor: item.color + "33" }}
          >
            {item.label}
          </button>
        ))}
      </div>

      <p className="mt-4 min-h-6 text-sm font-medium" role="status">
        {reading
          ? `${reading.tradition} · ${reading.label} · ${reading.n} (${reading.share} of that bar)`
          : "Hover a segment. The count stays after you move on."}
      </p>
      {kindMeta && (
        <ol className="mt-2 space-y-1 text-sm">
          {ordered.map((row, index) => {
            const total = KINDS.reduce((s, item) => s + (row.kind[item.key] ?? 0), 0);
            return (
              <li key={row.tradition}>
                {index + 1}. {row.tradition} {pct(row.kind[kindMeta.key] ?? 0, total)} {kindMeta.label.toLowerCase()}
              </li>
            );
          })}
        </ol>
      )}
      <InteractiveBars
        title="Form of the answer"
        rows={ordered}
        series={KINDS}
        bag="kind"
        highlight={kind}
        pinned={tradition}
        onHover={(next) => {
          setTip(next);
          if (next) setLocked(next);
        }}
        onPickKind={setKind}
        onPickTradition={setTradition}
      />
      <InteractiveBars
        title="Claim distance, same cells"
        rows={ordered}
        series={THEOLOGY}
        bag="theology"
        highlight={null}
        pinned={tradition}
        onHover={(next) => {
          setTip(next);
          if (next) setLocked(next);
        }}
        onPickKind={() => {}}
        onPickTradition={setTradition}
      />

      {focus && (
        <section className="mt-6 rounded-md border border-default-200 p-4">
          <h2 className="text-base font-semibold">{focus.tradition}</h2>
          <p className="mt-1 text-sm text-default-500">
            {focus.coherent} coherent of {focus.rows} judged. Shares are of the coherent rows in this tradition.
          </p>
          <dl className="mt-3 grid grid-cols-2 gap-x-6 gap-y-1 text-sm sm:grid-cols-3">
            {KINDS.map((item) => (
              <div key={item.key} className={kind === item.key ? "font-semibold" : ""}>
                <dt className="inline">{item.label}</dt>
                <dd className="inline"> {pct(focus.kind[item.key] ?? 0, focus.coherent)}</dd>
              </div>
            ))}
          </dl>
          <p className="mt-3 text-sm">
            Among coherent rows, distorted or contradicted claims are{" "}
            {pct((focus.theology.distorted ?? 0) + (focus.theology.contradicted ?? 0), focus.coherent)}.
            Accurate claims are {pct(focus.theology.accurate ?? 0, focus.coherent)}.
          </p>
        </section>
      )}
    </div>
  );
}
