| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| qwen3-32b | 14% cov 100% (n=21; c/i/r 3/18/0; minor/major 0/18) | 0% cov 100% (n=21; c/i/r 0/21/0; minor/major 0/21) | 0% cov 100% (n=21; c/i/r 0/21/0; minor/major 0/21) | 65% cov 95% (n=21; c/i/r 13/7/1; minor/major 0/7) | **19%** cov 99% (c/i/r 16/67/1; minor/major 0/67) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| qwen3-32b | cite_passage | 18 | 0 | 18 | wrong_locus 12, no_citation 6 |
| qwen3-32b | complete_unit | 21 | 0 | 21 | wrong_passage 21 |
| qwen3-32b | retrieve_quote | 21 | 0 | 21 | wrong_passage 21 |
| qwen3-32b | verify_source | 7 | 0 | 7 | wrong_verdict 7 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| qwen3-32b | Christianity | 14% cov 100% (n=21; c/i/r 3/18/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 65% cov 95% (n=21; c/i/r 13/7/1) | **19%** cov 99% (n=84; c/i/r 16/67/1) |

### By text (one text = one work · version · language)

**qwen3-32b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 19% | 99% | 1 | — | 0 | 64 | wrong_passage 40, wrong_locus 11, no_citation 6, wrong_verdict 7 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| qwen3-32b | 84 | 14,286 | 60,549 |
| **total** | 84 | 14,286 | 60,549 |
