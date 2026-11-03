| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 89% cov 93% (n=30; c/i/r 25/3/2; minor/major 0/3) | 64% cov 93% (n=30; c/i/r 18/10/2; minor/major 2/8) | 33% cov 70% (n=30; c/i/r 7/14/9; minor/major 0/14) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **75%** cov 89% (c/i/r 80/27/13; minor/major 2/25) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | cite_passage | 3 | 0 | 3 | wrong_locus 3 |
| haiku | complete_unit | 10 | 2 | 8 | paraphrase 2, wrong_passage 8, addition 17 |
| haiku | retrieve_quote | 14 | 0 | 14 | wrong_passage 14, addition 7 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Hinduism | 89% cov 93% (n=30; c/i/r 25/3/2) | 64% cov 93% (n=30; c/i/r 18/10/2) | 33% cov 70% (n=30; c/i/r 7/14/9) | 100% cov 100% (n=30; c/i/r 30/0/0) | **75%** cov 89% (n=120; c/i/r 80/27/13) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 75% | 89% | 13 | — | 2 | 25 | paraphrase 2, wrong_passage 22, addition 24, wrong_locus 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 120 | 16,173 | 29,040 |
| **total** | 120 | 16,173 | 29,040 |
