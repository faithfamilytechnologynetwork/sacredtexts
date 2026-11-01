# texts/ — corpora (two-tier: raw → standardized)

- **`raw/`** — source data exactly as obtained, organised by tradition. Seeded
  from the working group's Box folder ("Phase I / raw JSON", downloaded
  2026-10-10). Two subsets are **held back from this public repo** pending
  licensing and exist only locally (see `.gitignore`):
  - `raw/Roman Catholic/nabre.json` — NABRE is a copyrighted translation
    (Confraternity of Christian Doctrine / USCCB).
  - `raw/Protestant Christian/nrsv.json` — NRSV is a copyrighted translation
    (National Council of the Churches of Christ in the USA, 1989).
  - `raw/Greek Orthodox/` — direct extracts of the licensed TLG corpus
    (and the underlying Rahlfs Septuagint / Nestle-Aland editions are
    themselves copyrighted).
- **`standardized/`** — the working group's standard flat-format documents,
  produced from `raw/` by `sacredbench convert` (see `pipelines/README.md`).
  Rebuilt locally; corpora derived from copyrighted sources are not committed.

## Obtaining the held-back sources

Both held-back sources live in the working group's access-controlled Box folder
— **"Phase I / raw JSON"** (<https://byu.app.box.com/s/pgptf0ntvthlgabpn85m5kn5o73r3sy3>,
BYU Box login + group membership required). After downloading, place them so the
layout matches the committed tree:

- **NABRE** → download `Roman Catholic/nabre.json` from Box and save it as
  `texts/raw/Roman Catholic/nabre.json`. Alternatively rebuild it from
  [`Religion-at-Notre-Dame/catholic_text_json`](https://github.com/Religion-at-Notre-Dame/catholic_text_json)
  (the upstream source of the group's copy).
- **NRSV** → place a copy you are allowed to hold at
  `texts/raw/Protestant Christian/nrsv.json`, in the same `{book, chapter, verse, text}`
  shape as `kjv.json`. The National Council of Churches holds the copyright;
  this repo does not redistribute the text.
The Christian test set does not use those TLG files. Its original-language verses are a Masoretic excerpt (Westminster Leningrad Codex) and a Greek New Testament excerpt (Scrivener 1894), stored with the questions under `items/for-test/christianity/`.

- **Greek Orthodox (TLG)** → download the whole `Greek Orthodox/` folder from
  Box and save it as `texts/raw/Greek Orthodox/`. These files are extracts of
  the licensed [TLG](https://stephanus.tlg.uci.edu/) corpus — you (or your
  institution) must hold TLG access rights to use them.

Both paths are gitignored, so a local copy never ends up in a commit. The
pipeline treats them as **restricted** sources: they are excluded from
conversion and benchmark generation unless explicitly enabled with
`--include-restricted` (see the catalogue section in `pipelines/README.md`), and
committed benchmark artifacts must never embed their text. Each restricted
source still carries a committed `source.yaml` (with its payload held back) so
the catalogue stays complete and auditable.

`raw/Sikhism/sggs_shabados.json` is a verbatim, filtered extract of the Shabad OS
database (the Sri Guru Granth Sahib's lines only — the full database is 603 MB of
TOML). `raw/Sikhism/build_extract.py` rebuilds it byte for byte from a checkout of
`shabados/shabados` at the commit recorded in the file's `upstream` header.

`raw/Buddhism/s0502m.mul.xml` is the Vipassana Research Institute's romanized Dhammapada,
committed exactly as published (UTF-16 TEI). `raw/Buddhism/source.yaml` records its commit and
SHA-256, and VRI's non-commercial terms.

`raw/Hinduism/gita_stotrasamhita.json` is a verbatim, verses-only extract of `gita.tex` from
`stotrasamhita/gita`. `raw/Hinduism/build_extract.py` rebuilds it byte for byte from that file at
the commit recorded in the `upstream` header. The source has no licence file: see
`raw/Hinduism/source.yaml` and the spec. `raw/Hinduism/gita_besant.json` is Annie Besant's 1922
English, and `raw/Hinduism/build_besant.py` rebuilds it from the Wikisource page revisions recorded
in its header.

Per-source provenance metadata lives in each `texts/raw/<tradition>/source.yaml`
(a targets manifest — provenance, converter, and a `license` field per target;
see `pipelines/sacredbench/catalogue.py`).
