| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| astra | 67% cov 100% (n=30; c/i/r 20/10/0; minor/major 0/10) | 27% cov 100% (n=30; c/i/r 8/22/0; minor/major 16/6) | 11% cov 60% (n=30; c/i/r 2/16/12; minor/major 4/12) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **56%** cov 90% (c/i/r 60/48/12; minor/major 20/28) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| astra | cite_passage | 10 | 0 | 10 | wrong_locus 10 |
| astra | complete_unit | 22 | 16 | 6 | edition_variant 7, paraphrase 5, wrong_passage 6, omission 4, addition 1 |
| astra | retrieve_quote | 16 | 4 | 12 | near_copy 1, paraphrase 3, wrong_passage 12 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| astra | Judaism | 67% cov 100% (n=30; c/i/r 20/10/0) | 27% cov 100% (n=30; c/i/r 8/22/0) | 11% cov 60% (n=30; c/i/r 2/16/12) | 100% cov 100% (n=30; c/i/r 30/0/0) | **56%** cov 90% (n=120; c/i/r 60/48/12) |

### By text (one text = one work · version · language)

**astra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 56% | 90% | 12 | — | 20 | 28 | edition_variant 7, near_copy 1, paraphrase 8, wrong_passage 18, omission 4, addition 1, wrong_locus 10 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| astra | 120 | 11,478 | 53,336 |
| **total** | 120 | 11,478 | 53,336 |
