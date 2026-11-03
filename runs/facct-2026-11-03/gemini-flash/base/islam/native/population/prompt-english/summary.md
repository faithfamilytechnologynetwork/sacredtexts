| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | 87% cov 100% (n=30; c/i/r 26/4/0; minor/major 4/0) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **96%** cov 100% (c/i/r 115/5/0; minor/major 4/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemini-flash | complete_unit | 1 | 0 | 1 | wrong_passage 1 |
| gemini-flash | retrieve_quote | 4 | 4 | 0 | near_copy 1, paraphrase 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | 87% cov 100% (n=30; c/i/r 26/4/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **96%** cov 100% (n=120; c/i/r 115/5/0) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 96% | 100% | 0 | — | 4 | 1 | near_copy 1, paraphrase 3, wrong_passage 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 16,524 | 19,060 |
| **total** | 120 | 16,524 | 19,060 |
