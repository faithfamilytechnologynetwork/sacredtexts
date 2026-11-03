| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| qwen3-32b | 7% cov 100% (n=30; c/i/r 2/28/0; minor/major 0/28) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 93% (n=30; c/i/r 0/28/2; minor/major 0/28) | 67% cov 100% (n=30; c/i/r 20/10/0; minor/major 0/10) | **19%** cov 98% (c/i/r 22/96/2; minor/major 0/96) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| qwen3-32b | cite_passage | 28 | 0 | 28 | wrong_locus 28 |
| qwen3-32b | complete_unit | 30 | 0 | 30 | wrong_passage 30 |
| qwen3-32b | retrieve_quote | 28 | 0 | 28 | wrong_passage 24, other_script 4 |
| qwen3-32b | verify_source | 10 | 0 | 10 | wrong_verdict 10 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| qwen3-32b | Judaism | 7% cov 100% (n=30; c/i/r 2/28/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 93% (n=30; c/i/r 0/28/2) | 67% cov 100% (n=30; c/i/r 20/10/0) | **19%** cov 98% (n=120; c/i/r 22/96/2) |

### By text (one text = one work · version · language)

**qwen3-32b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 19% | 98% | 2 | — | 0 | 96 | wrong_passage 54, other_script 4, wrong_locus 28, wrong_verdict 10 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| qwen3-32b | 120 | 14,322 | 93,267 |
| **total** | 120 | 14,322 | 93,267 |
