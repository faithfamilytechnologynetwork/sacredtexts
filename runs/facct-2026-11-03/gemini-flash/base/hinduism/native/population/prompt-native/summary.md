| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | 73% cov 100% (n=30; c/i/r 22/8/0; minor/major 7/1) | 60% cov 100% (n=30; c/i/r 18/12/0; minor/major 4/8) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **82%** cov 100% (c/i/r 99/21/0; minor/major 11/10) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemini-flash | cite_passage | 1 | 0 | 1 | wrong_locus 1 |
| gemini-flash | complete_unit | 8 | 7 | 1 | paraphrase 7, wrong_passage 1, addition 6 |
| gemini-flash | retrieve_quote | 12 | 4 | 8 | paraphrase 4, wrong_passage 8, addition 18 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Hinduism | 97% cov 100% (n=30; c/i/r 29/1/0) | 73% cov 100% (n=30; c/i/r 22/8/0) | 60% cov 100% (n=30; c/i/r 18/12/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **82%** cov 100% (n=120; c/i/r 99/21/0) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 82% | 100% | 0 | — | 11 | 10 | paraphrase 11, wrong_passage 9, addition 24, wrong_locus 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 7,157 | 9,437 |
| **total** | 120 | 7,157 | 9,437 |
