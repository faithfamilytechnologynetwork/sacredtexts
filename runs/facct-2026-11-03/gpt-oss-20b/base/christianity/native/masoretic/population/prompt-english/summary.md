| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 0% cov 95% (n=21; c/i/r 0/20/1; minor/major 0/20) | 0% cov 100% (n=21; c/i/r 0/21/0; minor/major 0/21) | 0% cov 100% (n=21; c/i/r 0/21/0; minor/major 0/21) | 57% cov 100% (n=21; c/i/r 12/9/0; minor/major 0/9) | **14%** cov 99% (c/i/r 12/71/1; minor/major 0/71) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gpt-oss-20b | cite_passage | 20 | 0 | 20 | wrong_locus 16, no_citation 4 |
| gpt-oss-20b | complete_unit | 21 | 0 | 21 | wrong_passage 21 |
| gpt-oss-20b | retrieve_quote | 21 | 0 | 21 | wrong_passage 21 |
| gpt-oss-20b | verify_source | 9 | 0 | 9 | wrong_verdict 9 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Christianity | 0% cov 95% (n=21; c/i/r 0/20/1) | 0% cov 100% (n=21; c/i/r 0/21/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 57% cov 100% (n=21; c/i/r 12/9/0) | **14%** cov 99% (n=84; c/i/r 12/71/1) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 2 |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 14% | 100% | 0 | — | 0 | 69 | wrong_passage 40, wrong_locus 16, no_citation 4, wrong_verdict 9 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 84 | 16,837 | 129,407 |
| **total** | 84 | 16,837 | 129,407 |
