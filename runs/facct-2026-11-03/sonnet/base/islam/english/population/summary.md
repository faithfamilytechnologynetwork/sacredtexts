| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 60% cov 100% (n=30; c/i/r 18/12/0; minor/major 10/2) | 35% cov 77% (n=30; c/i/r 8/15/7; minor/major 14/1) | 88% cov 87% (n=30; c/i/r 23/3/4; minor/major 0/3) | **72%** cov 91% (c/i/r 79/30/11; minor/major 24/6) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sonnet | complete_unit | 12 | 10 | 2 | near_copy 1, paraphrase 9, wrong_passage 2, addition 13 |
| sonnet | retrieve_quote | 15 | 14 | 1 | near_copy 7, paraphrase 7, wrong_passage 1, addition 6 |
| sonnet | verify_source | 3 | 0 | 3 | wrong_verdict 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 60% cov 100% (n=30; c/i/r 18/12/0) | 35% cov 77% (n=30; c/i/r 8/15/7) | 88% cov 87% (n=30; c/i/r 23/3/4) | **72%** cov 91% (n=120; c/i/r 79/30/11) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Saheeh International (QUL), en) | 120 | 72% | 91% | 11 | — | 24 | 6 | near_copy 8, paraphrase 16, wrong_passage 3, addition 19, wrong_verdict 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 120 | 13,133 | 14,763 |
| **total** | 120 | 13,133 | 14,763 |
