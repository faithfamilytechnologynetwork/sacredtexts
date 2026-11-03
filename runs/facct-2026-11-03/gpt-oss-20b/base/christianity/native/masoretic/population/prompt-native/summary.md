| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 0% cov 100% (n=21; c/i/r 0/21/0; minor/major 0/21) | 0% cov 81% (n=21; c/i/r 0/17/4; minor/major 0/17) | 0% cov 100% (n=21; c/i/r 0/21/0; minor/major 0/21) | 71% cov 100% (n=21; c/i/r 15/6/0; minor/major 0/6) | **19%** cov 95% (c/i/r 15/65/4; minor/major 0/65) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gpt-oss-20b | cite_passage | 21 | 0 | 21 | wrong_locus 19, no_citation 2 |
| gpt-oss-20b | complete_unit | 17 | 0 | 17 | wrong_passage 17 |
| gpt-oss-20b | retrieve_quote | 21 | 0 | 21 | wrong_passage 19, other_script 2 |
| gpt-oss-20b | verify_source | 6 | 0 | 6 | wrong_verdict 6 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Christianity | 0% cov 100% (n=21; c/i/r 0/21/0) | 0% cov 81% (n=21; c/i/r 0/17/4) | 0% cov 100% (n=21; c/i/r 0/21/0) | 71% cov 100% (n=21; c/i/r 15/6/0) | **19%** cov 95% (n=84; c/i/r 15/65/4) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 18% | 95% | 4 | — | 0 | 62 | wrong_passage 34, other_script 2, wrong_locus 18, no_citation 2, wrong_verdict 6 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 84 | 14,906 | 108,672 |
| **total** | 84 | 14,906 | 108,672 |
