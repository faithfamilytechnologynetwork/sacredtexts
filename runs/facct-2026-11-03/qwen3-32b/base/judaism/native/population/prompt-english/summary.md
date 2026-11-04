| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| qwen3-32b | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 0/29) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 1/29) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 87% cov 100% (n=30; c/i/r 26/4/0; minor/major 0/4) | **22%** cov 100% (c/i/r 27/93/0; minor/major 1/92) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| qwen3-32b | cite_passage | 29 | 0 | 29 | wrong_locus 28, no_citation 1 |
| qwen3-32b | complete_unit | 30 | 1 | 29 | wrong_passage 29, omission 1 |
| qwen3-32b | retrieve_quote | 30 | 0 | 30 | wrong_passage 30 |
| qwen3-32b | verify_source | 4 | 0 | 4 | wrong_verdict 4 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| qwen3-32b | Judaism | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 87% cov 100% (n=30; c/i/r 26/4/0) | **22%** cov 100% (n=120; c/i/r 27/93/0) |

### By text (one text = one work · version · language)

**qwen3-32b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 22% | 100% | 0 | — | 1 | 92 | wrong_passage 59, omission 1, wrong_locus 28, no_citation 1, wrong_verdict 4 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| qwen3-32b | 120 | 13,482 | 102,353 |
| **total** | 120 | 13,482 | 102,353 |
