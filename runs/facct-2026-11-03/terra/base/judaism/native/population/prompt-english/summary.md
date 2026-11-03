| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| terra | 40% cov 100% (n=30; c/i/r 12/18/0; minor/major 0/18) | 17% cov 100% (n=30; c/i/r 5/25/0; minor/major 13/12) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 2/28) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | **38%** cov 100% (c/i/r 46/74/0; minor/major 15/59) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| terra | cite_passage | 18 | 0 | 18 | wrong_locus 12, no_citation 6 |
| terra | complete_unit | 25 | 13 | 12 | edition_variant 1, paraphrase 8, wrong_passage 12, omission 4, addition 1 |
| terra | retrieve_quote | 30 | 2 | 28 | edition_variant 1, near_copy 1, wrong_passage 28 |
| terra | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| terra | Judaism | 40% cov 100% (n=30; c/i/r 12/18/0) | 17% cov 100% (n=30; c/i/r 5/25/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | **38%** cov 100% (n=120; c/i/r 46/74/0) |

### By text (one text = one work · version · language)

**terra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 38% | 100% | 0 | — | 15 | 59 | edition_variant 2, near_copy 1, paraphrase 8, wrong_passage 40, omission 4, addition 1, wrong_locus 12, no_citation 6, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| terra | 120 | 12,908 | 8,608 |
| **total** | 120 | 12,908 | 8,608 |
