| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| qwen3-32b | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 0/29) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 1/29) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 83% cov 77% (n=30; c/i/r 19/4/7; minor/major 0/4) | **18%** cov 94% (c/i/r 20/93/7; minor/major 1/92) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| qwen3-32b | cite_passage | 29 | 0 | 29 | wrong_locus 29 |
| qwen3-32b | complete_unit | 30 | 1 | 29 | paraphrase 1, wrong_passage 29 |
| qwen3-32b | retrieve_quote | 30 | 0 | 30 | wrong_passage 30 |
| qwen3-32b | verify_source | 4 | 0 | 4 | wrong_verdict 4 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| qwen3-32b | Judaism | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 83% cov 77% (n=30; c/i/r 19/4/7) | **18%** cov 94% (n=120; c/i/r 20/93/7) |

### By text (one text = one work · version · language)

**qwen3-32b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 18% | 94% | 7 | — | 1 | 92 | paraphrase 1, wrong_passage 59, wrong_locus 29, wrong_verdict 4 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| qwen3-32b | 120 | 11,719 | 132,014 |
| **total** | 120 | 11,719 | 132,014 |
