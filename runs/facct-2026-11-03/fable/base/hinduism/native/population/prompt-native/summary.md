| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | 70% cov 100% (n=30; c/i/r 21/9/0; minor/major 4/5) | 57% cov 100% (n=30; c/i/r 17/13/0; minor/major 4/9) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **81%** cov 100% (c/i/r 97/23/0; minor/major 8/15) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| fable | cite_passage | 1 | 0 | 1 | wrong_locus 1 |
| fable | complete_unit | 9 | 4 | 5 | paraphrase 4, wrong_passage 5, addition 13 |
| fable | retrieve_quote | 13 | 4 | 9 | paraphrase 4, wrong_passage 9, addition 17 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Hinduism | 97% cov 100% (n=30; c/i/r 29/1/0) | 70% cov 100% (n=30; c/i/r 21/9/0) | 57% cov 100% (n=30; c/i/r 17/13/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **81%** cov 100% (n=120; c/i/r 97/23/0) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 81% | 100% | 0 | — | 8 | 15 | paraphrase 8, wrong_passage 14, addition 30, wrong_locus 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 120 | 16,413 | 24,679 |
| **total** | 120 | 16,413 | 24,679 |
