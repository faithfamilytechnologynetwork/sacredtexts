| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 80% cov 100% (n=30; c/i/r 24/6/0; minor/major 0/6) | 4% cov 83% (n=30; c/i/r 1/24/5; minor/major 3/21) | 0% cov 23% (n=30; c/i/r 0/7/23; minor/major 6/1) | 80% cov 83% (n=30; c/i/r 20/5/5; minor/major 0/5) | **52%** cov 72% (c/i/r 45/42/33; minor/major 9/33) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sonnet | cite_passage | 6 | 0 | 6 | hedge 6 |
| sonnet | complete_unit | 24 | 3 | 21 | paraphrase 3, wrong_passage 21, addition 1 |
| sonnet | retrieve_quote | 7 | 6 | 1 | edition_variant 1, paraphrase 5, wrong_passage 1 |
| sonnet | verify_source | 5 | 0 | 5 | wrong_verdict 5 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Hinduism | 80% cov 100% (n=30; c/i/r 24/6/0) | 4% cov 83% (n=30; c/i/r 1/24/5) | 0% cov 23% (n=30; c/i/r 0/7/23) | 80% cov 83% (n=30; c/i/r 20/5/5) | **52%** cov 72% (n=120; c/i/r 45/42/33) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 52% | 72% | 33 | — | 9 | 33 | edition_variant 1, paraphrase 8, wrong_passage 22, addition 1, hedge 6, wrong_verdict 5 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 120 | 11,579 | 22,378 |
| **total** | 120 | 11,579 | 22,378 |
