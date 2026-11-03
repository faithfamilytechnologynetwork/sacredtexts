| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 73% cov 100% (n=30; c/i/r 22/8/0; minor/major 1/7) | 63% cov 100% (n=30; c/i/r 19/11/0; minor/major 7/4) | 100% cov 67% (n=30; c/i/r 20/0/10; minor/major 0/0) | **83%** cov 92% (c/i/r 91/19/10; minor/major 8/11) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sonnet | complete_unit | 8 | 1 | 7 | paraphrase 1, wrong_passage 7, addition 18 |
| sonnet | retrieve_quote | 11 | 7 | 4 | edition_variant 1, paraphrase 6, wrong_passage 4, addition 6 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 73% cov 100% (n=30; c/i/r 22/8/0) | 63% cov 100% (n=30; c/i/r 19/11/0) | 100% cov 67% (n=30; c/i/r 20/0/10) | **83%** cov 92% (n=120; c/i/r 91/19/10) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 83% | 92% | 10 | — | 8 | 11 | edition_variant 1, paraphrase 7, wrong_passage 11, addition 24 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 120 | 18,444 | 16,280 |
| **total** | 120 | 18,444 | 16,280 |
