| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| qwen3-32b | 37% cov 100% (n=30; c/i/r 11/19/0; minor/major 0/19) | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 4/25) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 84% cov 83% (n=30; c/i/r 21/4/5; minor/major 0/4) | **29%** cov 96% (c/i/r 33/82/5; minor/major 4/78) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| qwen3-32b | cite_passage | 19 | 0 | 19 | wrong_locus 19 |
| qwen3-32b | complete_unit | 29 | 4 | 25 | paraphrase 2, wrong_passage 25, omission 2 |
| qwen3-32b | retrieve_quote | 30 | 0 | 30 | wrong_passage 30 |
| qwen3-32b | verify_source | 4 | 0 | 4 | wrong_verdict 4 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| qwen3-32b | Islam | 37% cov 100% (n=30; c/i/r 11/19/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 84% cov 83% (n=30; c/i/r 21/4/5) | **29%** cov 96% (n=120; c/i/r 33/82/5) |

### By text (one text = one work · version · language)

**qwen3-32b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 29% | 96% | 5 | — | 4 | 78 | paraphrase 2, wrong_passage 55, omission 2, wrong_locus 19, wrong_verdict 4 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| qwen3-32b | 120 | 23,263 | 60,903 |
| **total** | 120 | 23,263 | 60,903 |
