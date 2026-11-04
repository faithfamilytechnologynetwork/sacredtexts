| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| astra | 53% cov 100% (n=30; c/i/r 16/14/0; minor/major 0/14) | 40% cov 100% (n=30; c/i/r 12/18/0; minor/major 12/6) | 21% cov 63% (n=30; c/i/r 4/15/11; minor/major 2/13) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **57%** cov 91% (c/i/r 62/47/11; minor/major 14/33) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| astra | cite_passage | 14 | 0 | 14 | wrong_locus 14 |
| astra | complete_unit | 18 | 12 | 6 | edition_variant 2, near_copy 1, paraphrase 4, wrong_passage 6, omission 5, addition 1 |
| astra | retrieve_quote | 15 | 2 | 13 | paraphrase 2, wrong_passage 13, addition 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| astra | Judaism | 53% cov 100% (n=30; c/i/r 16/14/0) | 40% cov 100% (n=30; c/i/r 12/18/0) | 21% cov 63% (n=30; c/i/r 4/15/11) | 100% cov 100% (n=30; c/i/r 30/0/0) | **57%** cov 91% (n=120; c/i/r 62/47/11) |

### By text (one text = one work · version · language)

**astra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 57% | 91% | 11 | — | 14 | 33 | edition_variant 2, near_copy 1, paraphrase 6, wrong_passage 19, omission 5, addition 2, wrong_locus 14 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| astra | 120 | 10,488 | 49,055 |
| **total** | 120 | 10,488 | 49,055 |
