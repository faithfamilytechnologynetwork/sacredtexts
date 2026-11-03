| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| opus | 27% cov 100% (n=30; c/i/r 8/22/0; minor/major 0/22) | 10% cov 97% (n=30; c/i/r 3/26/1; minor/major 16/10) | 0% cov 10% (n=30; c/i/r 0/3/27; minor/major 2/1) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | **43%** cov 77% (c/i/r 40/52/28; minor/major 18/34) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| opus | cite_passage | 22 | 0 | 22 | wrong_locus 17, no_citation 5 |
| opus | complete_unit | 26 | 16 | 10 | edition_variant 5, near_copy 1, paraphrase 5, wrong_passage 10, omission 5 |
| opus | retrieve_quote | 3 | 2 | 1 | edition_variant 1, paraphrase 1, wrong_passage 1 |
| opus | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| opus | Judaism | 27% cov 100% (n=30; c/i/r 8/22/0) | 10% cov 97% (n=30; c/i/r 3/26/1) | 0% cov 10% (n=30; c/i/r 0/3/27) | 97% cov 100% (n=30; c/i/r 29/1/0) | **43%** cov 77% (n=120; c/i/r 40/52/28) |

### By text (one text = one work · version · language)

**opus**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 43% | 77% | 28 | — | 18 | 34 | edition_variant 6, near_copy 1, paraphrase 6, wrong_passage 11, omission 5, wrong_locus 17, no_citation 5, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| opus | 120 | 19,945 | 58,804 |
| **total** | 120 | 19,945 | 58,804 |
