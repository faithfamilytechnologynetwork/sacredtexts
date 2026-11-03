| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| kimi | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | 31% cov 97% (n=30; c/i/r 9/20/1; minor/major 13/7) | 0% cov 87% (n=30; c/i/r 0/26/4; minor/major 11/15) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **59%** cov 96% (c/i/r 68/47/5; minor/major 24/23) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| kimi | cite_passage | 1 | 0 | 1 | wrong_locus 1 |
| kimi | complete_unit | 20 | 13 | 7 | edition_variant 2, near_copy 1, paraphrase 10, wrong_passage 7, addition 2 |
| kimi | retrieve_quote | 26 | 11 | 15 | paraphrase 11, wrong_passage 15 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| kimi | Hinduism | 97% cov 100% (n=30; c/i/r 29/1/0) | 31% cov 97% (n=30; c/i/r 9/20/1) | 0% cov 87% (n=30; c/i/r 0/26/4) | 100% cov 100% (n=30; c/i/r 30/0/0) | **59%** cov 96% (n=120; c/i/r 68/47/5) |

### By text (one text = one work · version · language)

**kimi**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 59% | 96% | 5 | — | 24 | 23 | edition_variant 2, near_copy 1, paraphrase 21, wrong_passage 22, addition 2, wrong_locus 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| kimi | 120 | 9,547 | 7,280 |
| **total** | 120 | 9,547 | 7,280 |
