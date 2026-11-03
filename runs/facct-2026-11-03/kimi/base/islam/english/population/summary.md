| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| kimi | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 53% cov 100% (n=30; c/i/r 16/14/0; minor/major 12/2) | 54% cov 87% (n=30; c/i/r 14/12/4; minor/major 8/4) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **78%** cov 97% (c/i/r 90/26/4; minor/major 20/6) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| kimi | complete_unit | 14 | 12 | 2 | edition_variant 5, near_copy 5, paraphrase 1, wrong_passage 2, omission 1, addition 1 |
| kimi | retrieve_quote | 12 | 8 | 4 | edition_variant 2, near_copy 5, paraphrase 1, wrong_passage 4 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| kimi | Islam | 100% cov 100% (n=30; c/i/r 30/0/0) | 53% cov 100% (n=30; c/i/r 16/14/0) | 54% cov 87% (n=30; c/i/r 14/12/4) | 100% cov 100% (n=30; c/i/r 30/0/0) | **78%** cov 97% (n=120; c/i/r 90/26/4) |

### By text (one text = one work · version · language)

**kimi**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Saheeh International (QUL), en) | 120 | 78% | 97% | 4 | — | 20 | 6 | edition_variant 7, near_copy 10, paraphrase 2, wrong_passage 6, omission 1, addition 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| kimi | 120 | 10,895 | 4,745 |
| **total** | 120 | 10,895 | 4,745 |
