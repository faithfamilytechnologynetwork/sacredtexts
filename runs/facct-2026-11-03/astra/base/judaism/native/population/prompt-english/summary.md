| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| astra | 73% cov 100% (n=30; c/i/r 22/8/0; minor/major 0/8) | 37% cov 100% (n=30; c/i/r 11/19/0; minor/major 16/3) | 8% cov 40% (n=30; c/i/r 1/11/18; minor/major 2/9) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **63%** cov 85% (c/i/r 64/38/18; minor/major 18/20) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| astra | cite_passage | 8 | 0 | 8 | no_citation 8 |
| astra | complete_unit | 19 | 16 | 3 | edition_variant 6, near_copy 1, paraphrase 5, wrong_passage 3, omission 4, addition 1 |
| astra | retrieve_quote | 11 | 2 | 9 | near_copy 1, paraphrase 1, wrong_passage 9 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| astra | Judaism | 73% cov 100% (n=30; c/i/r 22/8/0) | 37% cov 100% (n=30; c/i/r 11/19/0) | 8% cov 40% (n=30; c/i/r 1/11/18) | 100% cov 100% (n=30; c/i/r 30/0/0) | **63%** cov 85% (n=120; c/i/r 64/38/18) |

### By text (one text = one work · version · language)

**astra**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 63% | 85% | 18 | — | 18 | 20 | edition_variant 6, near_copy 2, paraphrase 6, wrong_passage 12, omission 4, addition 1, no_citation 8 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| astra | 120 | 12,908 | 50,642 |
| **total** | 120 | 12,908 | 50,642 |
