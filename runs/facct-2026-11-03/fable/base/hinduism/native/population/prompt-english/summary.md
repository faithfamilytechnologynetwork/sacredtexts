| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 73% cov 100% (n=30; c/i/r 22/8/0; minor/major 5/3) | 67% cov 100% (n=30; c/i/r 20/10/0; minor/major 9/1) | 96% cov 90% (n=30; c/i/r 26/1/3; minor/major 0/1) | **84%** cov 98% (c/i/r 98/19/3; minor/major 14/5) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| fable | complete_unit | 8 | 5 | 3 | paraphrase 5, wrong_passage 3, addition 1 |
| fable | retrieve_quote | 10 | 9 | 1 | edition_variant 2, paraphrase 7, wrong_passage 1, addition 1 |
| fable | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 73% cov 100% (n=30; c/i/r 22/8/0) | 67% cov 100% (n=30; c/i/r 20/10/0) | 96% cov 90% (n=30; c/i/r 26/1/3) | **84%** cov 98% (n=120; c/i/r 98/19/3) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 84% | 98% | 3 | — | 14 | 5 | edition_variant 2, paraphrase 12, wrong_passage 4, addition 2, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 120 | 18,444 | 14,296 |
| **total** | 120 | 18,444 | 14,296 |
