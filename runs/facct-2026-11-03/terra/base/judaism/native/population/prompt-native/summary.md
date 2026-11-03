| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| terra | 50% cov 100% (n=30; c/i/r 15/15/0; minor/major 0/15) | 17% cov 100% (n=30; c/i/r 5/25/0; minor/major 11/14) | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 2/27) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | **42%** cov 100% (c/i/r 50/70/0; minor/major 13/57) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| terra | cite_passage | 15 | 0 | 15 | wrong_locus 15 |
| terra | complete_unit | 25 | 11 | 14 | edition_variant 2, near_copy 2, paraphrase 4, wrong_passage 14, omission 3, addition 1 |
| terra | retrieve_quote | 29 | 2 | 27 | near_copy 1, paraphrase 1, wrong_passage 27, addition 1 |
| terra | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| terra | Judaism | 50% cov 100% (n=30; c/i/r 15/15/0) | 17% cov 100% (n=30; c/i/r 5/25/0) | 3% cov 100% (n=30; c/i/r 1/29/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | **42%** cov 100% (n=120; c/i/r 50/70/0) |

### By text (one text = one work · version · language)

**terra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 42% | 100% | 0 | — | 13 | 57 | edition_variant 2, near_copy 3, paraphrase 5, wrong_passage 41, omission 3, addition 2, wrong_locus 15, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| terra | 120 | 11,478 | 11,118 |
| **total** | 120 | 11,478 | 11,118 |
