| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| qwen3-32b | 7% cov 100% (n=30; c/i/r 2/28/0; minor/major 0/28) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 3/27) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 80% cov 100% (n=30; c/i/r 24/6/0; minor/major 0/6) | **22%** cov 100% (c/i/r 26/94/0; minor/major 3/91) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| qwen3-32b | cite_passage | 28 | 0 | 28 | wrong_locus 27, no_citation 1 |
| qwen3-32b | complete_unit | 30 | 3 | 27 | paraphrase 2, wrong_passage 27, omission 1 |
| qwen3-32b | retrieve_quote | 30 | 0 | 30 | wrong_passage 30 |
| qwen3-32b | verify_source | 6 | 0 | 6 | wrong_verdict 6 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| qwen3-32b | Judaism | 7% cov 100% (n=30; c/i/r 2/28/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 80% cov 100% (n=30; c/i/r 24/6/0) | **22%** cov 100% (n=120; c/i/r 26/94/0) |

### By text (one text = one work · version · language)

**qwen3-32b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - English, en) | 120 | 22% | 100% | 0 | — | 3 | 91 | paraphrase 2, wrong_passage 57, omission 1, wrong_locus 27, no_citation 1, wrong_verdict 6 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| qwen3-32b | 120 | 13,900 | 52,531 |
| **total** | 120 | 13,900 | 52,531 |
