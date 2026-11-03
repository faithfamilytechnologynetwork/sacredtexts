| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 89% cov 93% (n=30; c/i/r 25/3/2; minor/major 0/3) | 71% cov 93% (n=30; c/i/r 20/8/2; minor/major 2/6) | 38% cov 70% (n=30; c/i/r 8/13/9; minor/major 0/13) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **78%** cov 89% (c/i/r 83/24/13; minor/major 2/22) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | cite_passage | 3 | 0 | 3 | wrong_locus 3 |
| haiku | complete_unit | 8 | 2 | 6 | paraphrase 2, wrong_passage 6, addition 19 |
| haiku | retrieve_quote | 13 | 0 | 13 | wrong_passage 13, addition 8 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Hinduism | 89% cov 93% (n=30; c/i/r 25/3/2) | 71% cov 93% (n=30; c/i/r 20/8/2) | 38% cov 70% (n=30; c/i/r 8/13/9) | 100% cov 100% (n=30; c/i/r 30/0/0) | **78%** cov 89% (n=120; c/i/r 83/24/13) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 78% | 89% | 13 | — | 2 | 22 | paraphrase 2, wrong_passage 19, addition 27, wrong_locus 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 120 | 16,173 | 29,040 |
| **total** | 120 | 16,173 | 29,040 |
