| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| terra | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | 13% cov 100% (n=30; c/i/r 4/26/0; minor/major 23/3) | 7% cov 100% (n=30; c/i/r 2/28/0; minor/major 26/2) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **55%** cov 100% (c/i/r 66/54/0; minor/major 49/5) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| terra | complete_unit | 26 | 23 | 3 | edition_variant 2, paraphrase 21, wrong_passage 3 |
| terra | retrieve_quote | 28 | 26 | 2 | near_copy 2, paraphrase 24, wrong_passage 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| terra | Hinduism | 100% cov 100% (n=30; c/i/r 30/0/0) | 13% cov 100% (n=30; c/i/r 4/26/0) | 7% cov 100% (n=30; c/i/r 2/28/0) | 100% cov 100% (n=30; c/i/r 30/0/0) | **55%** cov 100% (n=120; c/i/r 66/54/0) |

### By text (one text = one work · version · language)

**terra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 55% | 100% | 0 | — | 49 | 5 | edition_variant 2, near_copy 2, paraphrase 45, wrong_passage 5 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| terra | 120 | 7,938 | 2,258 |
| **total** | 120 | 7,938 | 2,258 |
