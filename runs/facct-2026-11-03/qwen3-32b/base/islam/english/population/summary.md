| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| qwen3-32b | 33% cov 100% (n=30; c/i/r 10/20/0; minor/major 0/20) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 8/22) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 2/28) | 80% cov 100% (n=30; c/i/r 24/6/0; minor/major 0/6) | **28%** cov 100% (c/i/r 34/86/0; minor/major 10/76) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| qwen3-32b | cite_passage | 20 | 0 | 20 | wrong_locus 20 |
| qwen3-32b | complete_unit | 30 | 8 | 22 | near_copy 1, paraphrase 6, wrong_passage 22, omission 1 |
| qwen3-32b | retrieve_quote | 30 | 2 | 28 | paraphrase 2, wrong_passage 28 |
| qwen3-32b | verify_source | 6 | 0 | 6 | wrong_verdict 6 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| qwen3-32b | Islam | 33% cov 100% (n=30; c/i/r 10/20/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 80% cov 100% (n=30; c/i/r 24/6/0) | **28%** cov 100% (n=120; c/i/r 34/86/0) |

### By text (one text = one work · version · language)

**qwen3-32b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Saheeh International (QUL), en) | 120 | 28% | 100% | 0 | — | 10 | 76 | near_copy 1, paraphrase 8, wrong_passage 50, omission 1, wrong_locus 20, wrong_verdict 6 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| qwen3-32b | 120 | 10,011 | 54,741 |
| **total** | 120 | 10,011 | 54,741 |
