| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 80% cov 100% (n=30; c/i/r 24/6/0; minor/major 4/2) | 53% cov 100% (n=30; c/i/r 16/14/0; minor/major 14/0) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | **82%** cov 100% (c/i/r 99/21/0; minor/major 18/3) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| fable | complete_unit | 6 | 4 | 2 | edition_variant 1, paraphrase 3, wrong_passage 2, addition 2 |
| fable | retrieve_quote | 14 | 14 | 0 | edition_variant 7, near_copy 4, paraphrase 3, addition 1 |
| fable | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 80% cov 100% (n=30; c/i/r 24/6/0) | 53% cov 100% (n=30; c/i/r 16/14/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | **82%** cov 100% (n=120; c/i/r 99/21/0) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 82% | 100% | 0 | — | 18 | 3 | edition_variant 8, near_copy 4, paraphrase 6, wrong_passage 2, addition 3, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 120 | 11,579 | 14,502 |
| **total** | 120 | 11,579 | 14,502 |
