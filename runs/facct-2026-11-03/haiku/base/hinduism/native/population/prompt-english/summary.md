| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | 55% cov 97% (n=30; c/i/r 16/13/1; minor/major 9/4) | 100% cov 23% (n=30; c/i/r 7/0/23; minor/major 0/0) | 77% cov 73% (n=30; c/i/r 17/5/8; minor/major 0/5) | **78%** cov 73% (c/i/r 69/19/32; minor/major 9/10) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | cite_passage | 1 | 0 | 1 | wrong_locus 1 |
| haiku | complete_unit | 13 | 9 | 4 | edition_variant 1, paraphrase 7, wrong_passage 4, omission 1, addition 10 |
| haiku | retrieve_quote | 0 | 0 | 0 | addition 7 |
| haiku | verify_source | 5 | 0 | 5 | wrong_verdict 5 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Hinduism | 97% cov 100% (n=30; c/i/r 29/1/0) | 55% cov 97% (n=30; c/i/r 16/13/1) | 100% cov 23% (n=30; c/i/r 7/0/23) | 77% cov 73% (n=30; c/i/r 17/5/8) | **78%** cov 73% (n=120; c/i/r 69/19/32) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 78% | 73% | 32 | — | 9 | 10 | edition_variant 1, paraphrase 7, wrong_passage 4, omission 1, addition 17, wrong_locus 1, wrong_verdict 5 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 120 | 18,204 | 13,594 |
| **total** | 120 | 18,204 | 13,594 |
