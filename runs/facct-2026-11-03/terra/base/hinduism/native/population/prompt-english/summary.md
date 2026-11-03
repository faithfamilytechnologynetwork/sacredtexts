| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| terra | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | 70% cov 100% (n=30; c/i/r 21/9/0; minor/major 7/2) | 43% cov 100% (n=30; c/i/r 13/17/0; minor/major 15/2) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **78%** cov 100% (c/i/r 93/27/0; minor/major 22/5) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| terra | cite_passage | 1 | 0 | 1 | wrong_locus 1 |
| terra | complete_unit | 9 | 7 | 2 | edition_variant 1, paraphrase 6, wrong_passage 2, addition 1 |
| terra | retrieve_quote | 17 | 15 | 2 | edition_variant 4, paraphrase 11, wrong_passage 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| terra | Hinduism | 97% cov 100% (n=30; c/i/r 29/1/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 43% cov 100% (n=30; c/i/r 13/17/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **78%** cov 100% (n=120; c/i/r 93/27/0) |

### By text (one text = one work · version · language)

**terra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 78% | 100% | 0 | — | 22 | 5 | edition_variant 5, paraphrase 17, wrong_passage 4, addition 1, wrong_locus 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| terra | 120 | 11,832 | 2,782 |
| **total** | 120 | 11,832 | 2,782 |
