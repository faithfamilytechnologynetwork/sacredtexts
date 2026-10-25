"""sacredbench CLI — convert / validate / generate / collect / score.

Run from the repo root:

    uv --project pipelines run python -m sacredbench --help
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

import typer

from sacredbench import audit as aud
from sacredbench import catalogue as cat
from sacredbench import convert as conv
from sacredbench import export as exp
from sacredbench import generate as gen
from sacredbench import schema
from sacredbench.collect import CollectError, _existing, _panel_fingerprint
from sacredbench.collect import collect as run_collect
from sacredbench.config import ConfigError, load_config
from sacredbench.edition_index import EditionIndexError, load_edition_documents, write_export
from sacredbench.facct import FacctError, build_facct, write_card
from sacredbench.generate import generate as run_generate
from sacredbench.generate import load_questions, write_questions
from sacredbench.failure_kind import breakdown_run, format_breakdown, report_run
from sacredbench.probes import format_probe, probe_run
from sacredbench.editions import edition_run, format_editions
from sacredbench.splits import format_splits, split_run
from sacredbench.jev import JevError
from sacredbench.score import TEXT_KEY_SEP, ScoreError, score_file, summary_markdown, text_key

app = typer.Typer(add_completion=False, no_args_is_help=True, pretty_exceptions_enable=False)


def _require_catalogue(raw_root: Path) -> list[cat.Source]:
    """Discover the catalogue for the license gate, failing LOUDLY if it is absent.

    The gate must never silently no-op: a missing catalogue is a usage error
    (wrong working directory, or a bad ``--raw-root``), not a reason to skip the
    restricted-source check."""
    try:
        return cat.discover_catalogue(raw_root)
    except cat.CatalogueMissing as e:
        raise typer.BadParameter(
            f"{e} — the license gate needs the source catalogue. Run from the repo "
            f"root or pass --raw-root pointing at texts/raw."
        ) from e


@app.command()
def catalogue(
    raw_root: Path = typer.Option(cat.RAW_ROOT, help="root of the raw texts tree"),
    include_restricted: bool = typer.Option(
        False, help="include restricted (copyrighted, held-back) targets"
    ),
) -> None:
    """Validate the source catalogue and list the targets selected for convert/generate."""
    sources = cat.discover_catalogue(raw_root)
    targets = cat.select_targets(sources, include_restricted=include_restricted)
    all_t = cat.all_targets(sources)
    restricted = [t for t in all_t if t.license == "restricted"]
    typer.echo(
        f"{len(sources)} source(s), {len(all_t)} target(s); "
        f"selected {len(targets)} ({len(restricted)} restricted "
        f"{'included' if include_restricted else 'excluded'})"
    )
    for t in targets:
        typer.echo(
            f"  [{t.license}] {t.source_id} :: {t.work} [{t.version}] ({t.language}) "
            f"<- {t.payload} via {t.converter}"
        )


@app.command()
def convert(
    source: str = typer.Option(None, help="limit to one source-id, e.g. 'Protestant Christian'"),
    converter: str = typer.Option(None, help="limit to one converter, e.g. bible_flat"),
    raw_root: Path = typer.Option(cat.RAW_ROOT, help="raw texts root"),
    standardized_root: Path = typer.Option(cat.STANDARDIZED_ROOT, help="output root"),
    include_restricted: bool = typer.Option(
        False, help="include restricted targets (needs the local held-back payloads)"
    ),
) -> None:
    """Convert catalogue targets to standardized documents.

    Catalogue-driven: each selected target is converted via its registered
    converter and written under the standardized-path convention
    (``texts/standardized/<source-id>/<target-slug>/``), so license is always
    recoverable from the output path. Restricted targets are excluded unless
    ``--include-restricted``.
    """
    sources = _require_catalogue(raw_root)
    targets = cat.select_targets(sources, include_restricted=include_restricted)
    if source is not None:
        targets = [t for t in targets if t.source_id == source]
    if converter is not None:
        targets = [t for t in targets if t.converter == converter]
    if not targets:
        raise typer.BadParameter(
            "no targets selected (check --source / --converter / --include-restricted)"
        )
    total_docs = total_entries = 0
    for t in targets:
        paths = t.payload_paths(raw_root)
        docs = conv.convert_target(paths, t)
        out_dir = t.standardized_dir(standardized_root)
        out_dir.mkdir(parents=True, exist_ok=True)
        for i, d in enumerate(docs):
            if len(docs) == len(paths):
                stem = paths[i].stem  # one doc per payload file
            elif len(docs) == 1:
                stem = t.slug  # merged into one document
            else:
                stem = f"{t.slug}-{i:03d}"
            schema.write_document(d, out_dir / f"{stem}.json")
            total_entries += len(d.entries)
        total_docs += len(docs)
        typer.echo(f"  {t.source_id} :: {t.work} [{t.version}] -> {out_dir}/ ({len(docs)} doc(s))")
    typer.echo(
        f"converted {total_docs} document(s), {total_entries} entries from {len(targets)} target(s)"
    )


@app.command()
def export(
    inputs: list[Path] = typer.Argument(help="standardized doc(s)/dir(s) to assemble"),
    out: Path = typer.Option(Path("texts/interchange"), help="output directory (one file per work/version/language)"),
    raw_root: Path = typer.Option(cat.RAW_ROOT, help="raw texts root (for the license gate)"),
    standardized_root: Path = typer.Option(cat.STANDARDIZED_ROOT, help="standardized texts root (for the license gate)"),
    include_restricted: bool = typer.Option(False, help="include restricted standardized docs"),
) -> None:
    """Assemble standardized shards into the interchange document per (work, version, language)."""
    sources = _require_catalogue(raw_root)
    for p in inputs:
        if not Path(p).exists():
            raise typer.BadParameter(f"input path not found: {p} — run `convert` first")
    files = cat.expand_json(list(inputs))
    if not files:
        raise typer.BadParameter(
            f"no standardized .json documents found under {[str(p) for p in inputs]}"
        )
    kept = cat.filter_standardized_paths(
        files, sources, include_restricted=include_restricted, standardized_root=standardized_root,
    )
    if not kept:
        raise typer.BadParameter(
            "all standardized documents were restricted and excluded (pass --include-restricted)"
        )
    docs = schema.load_documents(kept)
    assembled = exp.assemble(docs)
    exp.check_filename_collisions(assembled)
    ok = exp.roundtrip_ok(docs)
    if not ok:
        typer.secho("round-trip FAILED: an assembled document does not reproduce its shards", fg="red", err=True)
        raise typer.Exit(1)
    out.mkdir(parents=True, exist_ok=True)
    for d in assembled:
        schema.write_document(d, out / exp.interchange_filename(d))
    typer.echo(
        f"assembled {len(assembled)} interchange document(s) from {len(docs)} shard(s) "
        f"-> {out}/ (round-trip ok)"
    )


@app.command()
def audit(
    inputs: list[Path] = typer.Argument(help="committed artifact(s)/dir(s) to audit"),
    raw_root: Path = typer.Option(cat.RAW_ROOT, help="raw texts root (catalogue)"),
) -> None:
    """Copyright audit: fail if any committed artifact derives from a restricted
    source (origin), or — when the held-back restricted payloads are present locally
    — contains restricted text (content)."""
    sources = cat.discover_catalogue(raw_root)
    fingerprints = aud.restricted_text_fingerprints(sources, raw_root)
    violations = aud.audit_paths(list(inputs), sources, fingerprints)
    if violations:
        typer.secho(f"COPYRIGHT AUDIT FAILED — {len(violations)} violation(s):", fg="red", err=True)
        for v in violations:
            typer.secho(f"  {v}", fg="red", err=True)
        raise typer.Exit(1)
    scan = f"origin + {len(fingerprints)} restricted text fingerprint(s)" if fingerprints else "origin only (restricted payloads absent)"
    typer.echo(f"copyright audit OK — {len(list(inputs))} path(s), {scan}")


@app.command()
def validate(inputs: list[Path] = typer.Argument(help="standard-format file(s)/director(ies)")) -> None:
    """Mechanically validate standard-format documents (fail-fast)."""
    docs = schema.load_documents(inputs)
    total = sum(len(d.entries) for d in docs)
    for d in docs:
        typer.echo(f"  ok: {d.work} [{d.version}] — {len(d.entries)} entries, tradition={d.tradition}")
    typer.echo(f"valid: {len(docs)} document(s), {total} entries")


@app.command()
def generate(
    inputs: list[Path] = typer.Argument(help="standard-format file(s)/director(ies)"),
    out: Path = typer.Option(Path("runs/questions.jsonl")),
    per_text: int = typer.Option(gen.DEFAULT_PER_TEXT, min=1, help="questions per in-pool text"),
    tasks: str = typer.Option(None, help="comma-separated task subset, e.g. 'retrieve_quote,verify_source'"),
    seed: int = typer.Option(20261010),
    negatives_share: float = typer.Option(0.5, min=0.0, max=1.0, help="verify_source negative ratio"),
    raw_root: Path = typer.Option(cat.RAW_ROOT, help="raw texts root (for the license gate)"),
    standardized_root: Path = typer.Option(
        cat.STANDARDIZED_ROOT, help="standardized texts root (for the license gate)"
    ),
    include_restricted: bool = typer.Option(
        False, help="include restricted (copyrighted, held-back) standardized docs"
    ),
) -> None:
    """Generate benchmark questions from the four working-group templates.

    Original-language-only: a text is in the pool iff language == canonical_language.
    There is no --include-translations; excluded texts are recorded in the manifest."""
    task_subset = tuple(t.strip() for t in tasks.split(",") if t.strip()) if tasks else None
    sources = _require_catalogue(raw_root)
    cat.text_metadata(sources)  # fail-fast on a cross-source metadata conflict
    for p in inputs:
        if not Path(p).exists():
            raise typer.BadParameter(
                f"input path not found: {p} — run `convert` to populate "
                f"{standardized_root} first"
            )
    files = cat.expand_json(list(inputs))
    if not files:
        raise typer.BadParameter(
            f"no standardized .json documents found under {[str(p) for p in inputs]} "
            "— run `convert` first"
        )
    kept = cat.filter_standardized_paths(
        files, sources, include_restricted=include_restricted,
        standardized_root=standardized_root,
    )
    if not kept:
        raise typer.BadParameter(
            "all standardized documents were restricted and excluded "
            "(pass --include-restricted to include them)"
        )
    # Recover each document's text metadata (requested_as / canonical_language) by path,
    # mirroring the license gate, and carry it alongside the loaded documents.
    docs: list = []
    text_meta: dict = {}
    for f in kept:
        tm = cat.metadata_for_standardized_path(f, sources, standardized_root=standardized_root)
        if tm is None:
            raise typer.BadParameter(
                f"{f}: no catalogue text metadata recoverable from path (fail-closed)"
            )
        doc = schema.load_document(f)
        key = (doc.work, doc.version, doc.language)
        if key in text_meta and text_meta[key] != tm:
            raise typer.BadParameter(
                f"{key}: documents resolve to conflicting text metadata (ambiguous)"
            )
        text_meta[key] = tm
        docs.append(doc)
    questions, excluded = run_generate(
        docs, text_meta, per_text=per_text, seed=seed, negatives_share=negatives_share,
        tasks=task_subset,
    )
    write_questions(questions, out)
    manifest = gen.build_manifest(docs, questions, excluded, seed, per_text, negatives_share,
                                  task_subset, inputs=[str(p) for p in inputs])
    mpath = gen.manifest_path(out)
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1)
        f.write("\n")
    by_task = {t: sum(1 for q in questions if q.task == t) for t in sorted({q.task for q in questions})}
    typer.echo(f"wrote {len(questions)} questions to {out} {by_task}")
    if excluded:
        typer.echo(f"excluded {len(excluded)} text(s) (language != canonical_language)")
    typer.echo(f"manifest {mpath} (digest {manifest['question_set_digest']}, corpus {manifest['corpus_hash']})")


@app.command()
def collect(
    questions: Path = typer.Argument(help="questions.jsonl from `generate`"),
    config: Path = typer.Argument(help="run config YAML (model panel)"),
    out: Path = typer.Option(Path("runs/answers.jsonl")),
) -> None:
    """Fan questions out to the configured model panel (resumable; exits non-zero on failed cells)."""
    qs = load_questions(questions)
    cfg = load_config(config)
    typer.echo(f"{len(qs)} questions x {len(cfg.models)} models (concurrency {cfg.concurrency})")
    done, failed, messages = run_collect(
        qs, cfg, out,
        on_result=lambda q, m, text: typer.echo(f"  done {q.id} x {m.id}"),
    )
    typer.echo(f"collected {done} answers -> {out}")
    if failed:
        typer.secho(f"{failed} cell(s) FAILED (still pending; re-run to retry):", fg="red", err=True)
        for msg in messages:
            typer.secho(f"  {msg}", fg="red", err=True)
        raise typer.Exit(1)


@app.command()
def score(
    answers: Path = typer.Argument(help="answers.jsonl from `collect`"),
    scores_out: Path = typer.Option(Path("runs/scores.jsonl")),
    summary_out: Path = typer.Option(Path("runs/summary.json")),
    summary_md: Path = typer.Option(None, help="also write the markdown summary (incl. tradition breakdown) here"),
    questions: Path = typer.Option(None, help="questions.jsonl — with --config, report missing/failed cells"),
    config: Path = typer.Option(None, help="run config YAML (the model panel) for the expected-cell roster"),
    evaluator: list[str] = typer.Option(
        None, "--evaluator",
        help="grader(s) for text-retrieval, comma-separated and/or repeatable "
             "(default: the deterministic set strict,containment; unknown names fail fast; "
             "paid/separate-pass graders are never default and cannot run here).",
    ),
) -> None:
    """Score all answers and write the per-model summary. Graders are selectable via --evaluator."""
    from .graders import GraderError, resolve_evaluators

    try:
        resolve_evaluators(evaluator or None)  # fail fast on an unknown/empty/non-inline selection
    except GraderError as e:
        raise typer.BadParameter(str(e))
    if questions is not None or config is not None:
        if questions is None or config is None:
            raise typer.BadParameter("--questions and --config must be given together (missing-cell roster)")
        qs = load_questions(questions)
        cfg = load_config(config)
        # Evidence-integrity: the committed panel must describe the identity the answers were
        # ACTUALLY collected under. The panel below is built purely from --config, so flipping a
        # model's tools (or provider/model/host) between collect and score would mislabel the
        # experimental arm in summary.json/standings with no error. Cross-check each configured
        # model's fingerprint against the fingerprints stamped in answers.jsonl before emitting it.
        _, _, _, ans_fps, ans_fp_missing = _existing(answers)
        for m in cfg.models:
            current = _panel_fingerprint(m)
            mismatched = ans_fps.get(m.id, set()) - {current}
            if mismatched:
                raise ScoreError(
                    f"{answers}: model id {m.id!r} was collected under panel identity "
                    f"{sorted(mismatched)} but --config now maps it to {current!r}; the committed "
                    "panel would mislabel the experimental arm — re-run collect or fix the config"
                )
            if m.id in ans_fp_missing:
                raise ScoreError(
                    f"{answers}: model id {m.id!r} has answer row(s) with no panel fingerprint, so "
                    "the committed panel cannot be verified against what was collected (a pre-Spec-3 "
                    "answers file); re-collect to a fresh file before scoring with --config"
                )
        expected = {}
        expected_tradition: dict[tuple[str, str, str], int] = {}
        expected_text: dict[tuple[str, str, str], int] = {}
        for m in cfg.models:
            for q in qs:
                expected[(m.id, q.task)] = expected.get((m.id, q.task), 0) + 1
                for trad in q.source.get("tradition", []) or []:
                    k = (m.id, trad, q.task)
                    expected_tradition[k] = expected_tradition.get(k, 0) + 1
                tkey = text_key(q.source)
                if tkey is not None:
                    xk = (m.id, TEXT_KEY_SEP.join(tkey), q.task)
                    expected_text[xk] = expected_text.get(xk, 0) + 1
        # panel snapshot for the committed artifact (no secrets: provider/model/tools/host only)
        default_host = {"anthropic": "api.anthropic.com", "openai": "api.openai.com",
                        "gemini": "generativelanguage.googleapis.com"}
        panel = {}
        for m in cfg.models:
            endpoint = urlparse(m.base_url).netloc if m.base_url else default_host.get(m.provider)
            # `tools` is a real panel field (Approach B): the viewer keys standings on
            # (provider, model, tools), so web-search-on and -off stay distinct while a
            # no-tools model keys identically to a bare run of the same model — its stale
            # row becomes supersedable. `model` is the raw API id, no marker.
            panel[m.id] = {"provider": m.provider, "model": m.model, "tools": list(m.tools),
                           "endpoint": endpoint, "max_tokens": m.max_tokens,
                           "temperature": m.temperature,
                           "price_in": m.price_in, "price_out": m.price_out}
        summary = score_file(answers, scores_out, expected, expected_tradition, panel,
                             expected_digest=gen.question_set_digest(qs), evaluators=evaluator or None,
                             expected_text=expected_text)
    else:
        summary = score_file(answers, scores_out, evaluators=evaluator or None)
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_out, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
        f.write("\n")
    md = summary_markdown(summary)
    if summary_md is not None:
        summary_md.parent.mkdir(parents=True, exist_ok=True)
        summary_md.write_text(md, encoding="utf-8")
    typer.echo(f"wrote {scores_out} and {summary_out}" + (f" and {summary_md}" if summary_md else "") + "\n")
    typer.echo(md)


@app.command("edition-index")
def edition_index_cmd(
    out: Path = typer.Option(Path("texts/edition_index.jsonl"), help="JSONL export path; a sibling .manifest.json is written beside it"),
    raw_root: Path = typer.Option(cat.RAW_ROOT, help="raw texts root"),
) -> None:
    """Export editions that share a citation (same canonical language, license != restricted).

    The shared cross-edition producer: the FAccT card reads this index in-process; issue #21
    consumes the file. Restricted editions (e.g. NABRE) are never indexed or exported. Makes
    no network call.
    """
    indexed, all_docs, excluded = load_edition_documents(raw_root)
    manifest = write_export(indexed, all_docs, excluded, out)
    typer.echo(
        f"wrote {out} and {out}.manifest.json — {manifest['row_count']} rows, "
        f"corpus_hash {manifest['corpus_hash']}, digest {manifest['digest']}, "
        f"excluded_restricted {manifest['excluded_restricted']}"
    )


# The only existing files a card write may replace are the card's own two outputs. Any OTHER
# existing file in the run dir (questions.jsonl, scores.jsonl, answers.jsonl, summary.json/md,
# README.md, …) is off-limits — the card writes only new files or re-writes itself.
_CARD_OUTPUTS = ("facct.json", "facct.md")


def _within(run_dir: Path, path: Path) -> Path:
    """Resolve ``path`` to a card output file strictly inside ``run_dir``.

    Inverse rule (so no enumeration of evidence names can go stale): the target must be a file inside
    the run dir, and if it already exists it must be one of the card's own outputs
    (``facct.json`` / ``facct.md``) **at that literal location** — any other existing file is
    rejected. Resolution follows symlinks, so a symlink at the default or an override pointing at a
    different file (e.g. a `facct.json` symlinked onto `scores.jsonl`) is rejected; the run directory
    itself and existing directories are rejected too.
    """
    run_dir = run_dir.resolve()
    target = (run_dir / path) if not path.is_absolute() else path
    resolved = target.resolve()
    if resolved == run_dir or run_dir not in resolved.parents:
        raise typer.BadParameter(f"{path} must resolve to a file inside the run directory {run_dir}")
    if resolved.is_dir():
        raise typer.BadParameter(f"{path} resolves to a directory, not a file")
    if target.exists() or target.is_symlink():
        card_paths = {run_dir / name for name in _CARD_OUTPUTS}  # literal, not symlink-followed
        if resolved not in card_paths:
            raise typer.BadParameter(
                f"{path} already exists in the run dir and is not a card output "
                f"(facct.json / facct.md); refusing to overwrite it"
            )
    return resolved


@app.command()
def facct(
    run_dir: Path = typer.Argument(help="a finished run directory (reads scores.jsonl, summary.json, answers.jsonl, manifest)"),
    json_out: Path = typer.Option(None, "--json", help="facct.json path (default: <run_dir>/facct.json)"),
    md_out: Path = typer.Option(None, "--md", help="facct.md path (default: <run_dir>/facct.md)"),
    raw_root: Path = typer.Option(cat.RAW_ROOT, help="raw texts root (catalogue + edition index)"),
) -> None:
    """Write the FAccT card — facct.json AND facct.md — for a finished run.

    Pure analysis: reads committed run evidence, never re-scores, never calls a model. Every
    number on the card is derived from scores.jsonl / summary.json. Both files are written into
    the run directory by default; an override path must stay within it. Fails fast (no partial
    write) on inconsistent evidence, and writes both files atomically (both-or-neither).
    """
    # Validate BOTH destinations (including the defaults) before doing any work.
    json_path = _within(run_dir, json_out if json_out is not None else Path("facct.json"))
    md_path = _within(run_dir, md_out if md_out is not None else Path("facct.md"))
    if json_path == md_path:
        raise typer.BadParameter("--json and --md must be different paths")

    # Build (fails fast on bad evidence) then write both files atomically: both or neither.
    report = build_facct(run_dir, raw_root)
    write_card(report, json_path, md_path)

    cf = report["edition_counterfactual"]["by_model"]
    other_edition = sum(b["numerator"] for b in cf.values())
    typer.echo(f"wrote {json_path} and {md_path} — {report['census']['n_texts']} texts, "
               f"{report['census']['n_questions']} questions, {other_edition} other_edition tag(s) "
               f"across {len(cf)} model(s)")


@app.command()
def failures(run_dir: Path = typer.Argument(..., help="a run directory with scores.jsonl and answers.jsonl")) -> None:
    """Count SacredBench failure kinds for one scored run, per text.

    Kinds do not change accuracy. ``minor`` stays on the passage that was asked for
    (near copy, paraphrase, omission, addition). ``major`` replaces it (wrong
    passage, other script, wrong locus, wrong verdict, no citation, hedge).
    Texts are not pooled into a tradition score.
    """
    if not (run_dir / "scores.jsonl").is_file() or not (run_dir / "answers.jsonl").is_file():
        raise ScoreError(f"{run_dir} needs scores.jsonl and answers.jsonl")
    report = report_run(run_dir)
    overall = report["overall"]
    typer.echo(
        "outcomes "
        + " ".join(f"{k.split(':', 1)[1]}={overall[k]}" for k in sorted(overall) if k.startswith("outcome:"))
    )
    typer.echo(
        "severity "
        + " ".join(f"{k.split(':', 1)[1]}={overall[k]}" for k in sorted(overall) if k.startswith("severity:"))
    )
    for key in sorted(overall):
        if key.startswith("kind:"):
            typer.echo(f"  {key.split(':', 1)[1]} {overall[key]}")
    typer.echo(f"{len(report['by_text'])} text(s); one text = one work, version, and language")


@app.command()
def breakdown(run_dir: Path = typer.Argument(..., help="a run directory with scores.jsonl and answers.jsonl")) -> None:
    """Accuracy and refusal by scripture, hadith, talmud, and papal encyclical.

    Also by tradition and by task. A type with no questions is printed at zero
    so an encyclical folder that was not in the run is visible."""
    if not (run_dir / "scores.jsonl").is_file() or not (run_dir / "answers.jsonl").is_file():
        raise ScoreError(f"{run_dir} needs scores.jsonl and answers.jsonl")
    groups = breakdown_run(run_dir)
    for title, key in (
        ("by document type", "document_type"),
        ("by tradition", "tradition"),
        ("by tradition and type", "tradition_and_type"),
        ("by task", "task"),
    ):
        typer.echo(title)
        typer.echo(format_breakdown(groups[key]))
        typer.echo("")


@app.command()
def probes(
    run_dir: Path = typer.Argument(..., help="a run directory with scores.jsonl and answers.jsonl"),
    kjv: Path = typer.Option(Path("texts/raw/Protestant Christian/kjv.json"), help="raw KJV JSON for the edition check"),
) -> None:
    """Stored-run checks: letter fold, clustered intervals, refusals, KJV substitution.

    Does not call a model and does not change a score."""
    if not (run_dir / "scores.jsonl").is_file() or not (run_dir / "answers.jsonl").is_file():
        raise ScoreError(f"{run_dir} needs scores.jsonl and answers.jsonl")
    if not kjv.is_file():
        raise ScoreError(f"missing edition JSON: {kjv}")
    typer.echo(format_probe(probe_run(run_dir, kjv)))


@app.command()
def splits(
    run_dir: Path = typer.Argument(..., help="a run directory with scores.jsonl and answers.jsonl"),
    quran: Path = typer.Option(
        Path("texts/raw/Sunni Islam/quran_uthmani_from_qul.json.json"),
        help="Uthmani Qur'an JSON, keys like 1:1, for citation distance",
    ),
    bible: Path = typer.Option(
        Path("texts/raw/Protestant Christian/kjv.json"),
        help="KJV JSON for whether a cited Bible verse exists",
    ),
) -> None:
    """Tables behind the manuscript: per model, refusals, gap test, distance, cutoffs.

    Does not call a model and does not change a score."""
    if not (run_dir / "scores.jsonl").is_file() or not (run_dir / "answers.jsonl").is_file():
        raise ScoreError(f"{run_dir} needs scores.jsonl and answers.jsonl")
    for label, path in (("Qur'an", quran), ("Bible", bible)):
        if not path.is_file():
            raise ScoreError(f"missing {label} JSON: {path}")
    typer.echo(format_splits(split_run(run_dir, quran, bible)))


@app.command()
def editions(
    raw_root: Path = typer.Option(cat.RAW_ROOT, help="raw texts root (catalogue + edition index)"),
) -> None:
    """Folded agreement of the public-domain English Bibles. Does not score a model.

    Builds the per-edition verse index from the Spec 32 edition index (the converter + the
    licence gate), so restricted editions are never read. Makes no network call."""
    _require_catalogue(raw_root)
    typer.echo(format_editions(edition_run(raw_root)))


@app.command()
def judge(
    answers: Path = typer.Argument(help="answers.jsonl from `collect`"),
    out: Path = typer.Option(Path("runs/judgments.jsonl"), help="sidecar judgments file (resumable)"),
    model: str = typer.Option(None, help="Decisions model id (default: the floating jev-latest alias)"),
    concurrency: int = typer.Option(4, help="parallel decision calls"),
    limit: int = typer.Option(None, help="cap cells judged this invocation (budget guard)"),
    raw_root: Path = typer.Option(Path("texts/raw"), help="catalogue root for the restricted-target guard"),
    yes: bool = typer.Option(False, "--yes", help="skip the pre-flight confirmation and judge now"),
) -> None:
    """Jev judgments (PAID, Decisions API) for already-collected answers → a sidecar. Never rescoring.

    Prints a pre-flight estimate and stops unless --yes is given, so a live pass cannot start
    unseen. Judges only text-retrieval cells; skips restricted-source cells before any send.
    """
    from sacredbench import jev

    jev_model = model or jev.JEV_MODEL
    if not answers.exists():
        raise typer.BadParameter(f"input path not found: {answers} — run `collect` first")
    rows = [json.loads(line) for line in answers.read_text(encoding="utf-8").splitlines() if line.strip()]
    sources = _require_catalogue(raw_root)
    restricted = frozenset(aud.restricted_keys(sources))

    # JevError (bad/absent manifest, build conflict, …) bubbles to main() for a clean message.
    est = jev.estimate(rows, out, restricted_keys=restricted, limit=limit)
    typer.echo(
        f"pre-flight: {est['pending']} cell(s) to judge with {jev_model} "
        f"(~${est['estimated_usd']:.4f}); {est['already_judged']} already judged, "
        f"{est['skipped_task']} non-text-retrieval skipped, "
        f"{est['skipped_restricted']} restricted-source skipped"
    )
    if est["pending"] == 0:
        typer.echo("nothing to judge.")
        return
    if not yes:
        typer.secho("PAID live pass — re-run with --yes to proceed.", fg="yellow")
        raise typer.Exit(2)

    done, failed, messages = jev.judge(
        rows, out, model=jev_model, concurrency=concurrency, limit=limit, restricted_keys=restricted,
    )
    summary = jev.summarize(out)
    typer.echo(f"judged {done} -> {out}; file has {summary['n']} row(s) {summary['kinds']}")
    typer.echo(f"total Jev spend this file: ${summary['total_cost_usd']:.6f}")
    if summary["judge_models"]:
        typer.echo("resolved judge model(s): " + ", ".join(summary["judge_models"]))
    if failed:
        typer.secho(f"{failed} cell(s) FAILED (still pending; re-run to retry):", fg="red", err=True)
        for msg in messages:
            typer.secho(f"  {msg}", fg="red", err=True)
        raise typer.Exit(1)


@app.command("judge-summary")
def judge_summary(
    out: Path = typer.Argument(help="a judgments sidecar written by `judge`"),
) -> None:
    """Counts + resolved build(s) over a finished sidecar. No network, no calls."""
    from sacredbench import jev

    if not out.exists():
        raise typer.BadParameter(f"sidecar not found: {out} — run `judge` first")
    s = jev.summarize(out)
    typer.echo(json.dumps(s, ensure_ascii=False, indent=1))


def main() -> None:
    try:
        app()
    except (
        schema.SchemaError, conv.ConvertError, cat.CatalogueError, exp.ExportError, CollectError,
        gen.GenerateError, ScoreError, aud.AuditError, ConfigError, EditionIndexError,
        FacctError, JevError,
    ) as e:
        typer.secho(f"error: {e}", fg="red", err=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
