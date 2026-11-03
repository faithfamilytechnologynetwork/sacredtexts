| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | 67% cov 100% (n=30; c/i/r 20/10/0; minor/major 0/10) | 50% cov 100% (n=30; c/i/r 15/15/0; minor/major 4/11) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **78%** cov 100% (c/i/r 93/27/0; minor/major 4/23) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sonnet | cite_passage | 2 | 0 | 2 | hedge 2 |
| sonnet | complete_unit | 10 | 0 | 10 | wrong_passage 10, addition 20 |
| sonnet | retrieve_quote | 15 | 4 | 11 | paraphrase 4, wrong_passage 11, addition 15 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Hinduism | 93% cov 100% (n=30; c/i/r 28/2/0) | 67% cov 100% (n=30; c/i/r 20/10/0) | 50% cov 100% (n=30; c/i/r 15/15/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **78%** cov 100% (n=120; c/i/r 93/27/0) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 78% | 100% | 0 | — | 4 | 23 | paraphrase 4, wrong_passage 21, addition 35, hedge 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 120 | 16,413 | 23,889 |
| **total** | 120 | 16,413 | 23,889 |
