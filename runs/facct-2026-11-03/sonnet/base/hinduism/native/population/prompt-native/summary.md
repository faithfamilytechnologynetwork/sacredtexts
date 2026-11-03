| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | 73% cov 100% (n=30; c/i/r 22/8/0; minor/major 0/8) | 60% cov 100% (n=30; c/i/r 18/12/0; minor/major 3/9) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **82%** cov 100% (c/i/r 98/22/0; minor/major 3/19) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sonnet | cite_passage | 2 | 0 | 2 | hedge 2 |
| sonnet | complete_unit | 8 | 0 | 8 | wrong_passage 8, addition 22 |
| sonnet | retrieve_quote | 12 | 3 | 9 | paraphrase 3, wrong_passage 9, addition 17 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Hinduism | 93% cov 100% (n=30; c/i/r 28/2/0) | 73% cov 100% (n=30; c/i/r 22/8/0) | 60% cov 100% (n=30; c/i/r 18/12/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **82%** cov 100% (n=120; c/i/r 98/22/0) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 82% | 100% | 0 | — | 3 | 19 | paraphrase 3, wrong_passage 17, addition 39, hedge 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 120 | 16,413 | 23,889 |
| **total** | 120 | 16,413 | 23,889 |
