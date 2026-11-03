| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| opus | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 77% cov 100% (n=30; c/i/r 23/7/0; minor/major 5/2) | 60% cov 100% (n=30; c/i/r 18/12/0; minor/major 0/12) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **84%** cov 100% (c/i/r 101/19/0; minor/major 5/14) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| opus | complete_unit | 7 | 5 | 2 | paraphrase 5, wrong_passage 2, addition 1 |
| opus | retrieve_quote | 12 | 0 | 12 | wrong_passage 12, addition 18 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| opus | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 77% cov 100% (n=30; c/i/r 23/7/0) | 60% cov 100% (n=30; c/i/r 18/12/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **84%** cov 100% (n=120; c/i/r 101/19/0) |

### By text (one text = one work · version · language)

**opus**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 84% | 100% | 0 | — | 5 | 14 | paraphrase 5, wrong_passage 14, addition 19 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| opus | 120 | 16,413 | 34,923 |
| **total** | 120 | 16,413 | 34,923 |
