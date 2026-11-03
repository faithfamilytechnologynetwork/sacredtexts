| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| terra | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 67% cov 100% (n=30; c/i/r 20/10/0; minor/major 7/3) | 67% cov 100% (n=30; c/i/r 20/10/0; minor/major 9/1) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **83%** cov 100% (c/i/r 100/20/0; minor/major 16/4) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| terra | complete_unit | 10 | 7 | 3 | paraphrase 5, wrong_passage 3, omission 2 |
| terra | retrieve_quote | 10 | 9 | 1 | paraphrase 9, wrong_passage 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| terra | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 67% cov 100% (n=30; c/i/r 20/10/0) | 67% cov 100% (n=30; c/i/r 20/10/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **83%** cov 100% (n=120; c/i/r 100/20/0) |

### By text (one text = one work · version · language)

**terra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 83% | 100% | 0 | — | 16 | 4 | paraphrase 14, wrong_passage 4, omission 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| terra | 120 | 9,289 | 2,669 |
| **total** | 120 | 9,289 | 2,669 |
