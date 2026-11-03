| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 53% cov 50% (n=30; c/i/r 8/7/15; minor/major 6/1) | 47% cov 63% (n=30; c/i/r 9/10/11; minor/major 10/0) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **82%** cov 78% (c/i/r 77/17/26; minor/major 16/1) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemini-flash | complete_unit | 7 | 6 | 1 | edition_variant 3, near_copy 1, paraphrase 2, wrong_passage 1 |
| gemini-flash | retrieve_quote | 10 | 10 | 0 | edition_variant 4, near_copy 6 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 53% cov 50% (n=30; c/i/r 8/7/15) | 47% cov 63% (n=30; c/i/r 9/10/11) | 100% cov 100% (n=30; c/i/r 30/0/0) | **82%** cov 78% (n=120; c/i/r 77/17/26) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Saheeh International (QUL), en) | 120 | 82% | 78% | 26 | — | 16 | 1 | edition_variant 7, near_copy 7, paraphrase 2, wrong_passage 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 8,656 | 14,284 |
| **total** | 120 | 8,656 | 14,284 |
