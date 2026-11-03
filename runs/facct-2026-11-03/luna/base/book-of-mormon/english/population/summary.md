| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 57% cov 100% (n=30; c/i/r 17/13/0; minor/major 0/13) | 7% cov 97% (n=30; c/i/r 2/27/1; minor/major 10/17) | 27% cov 100% (n=30; c/i/r 8/22/0; minor/major 4/18) | 73% cov 100% (n=30; c/i/r 22/8/0; minor/major 0/8) | **41%** cov 99% (c/i/r 49/70/1; minor/major 14/56) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| luna | cite_passage | 13 | 0 | 13 | wrong_locus 13 |
| luna | complete_unit | 27 | 10 | 17 | near_copy 2, paraphrase 4, wrong_passage 17, omission 4 |
| luna | retrieve_quote | 22 | 4 | 18 | paraphrase 4, wrong_passage 18, addition 1 |
| luna | verify_source | 8 | 0 | 8 | wrong_verdict 8 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Book of Mormon | 57% cov 100% (n=30; c/i/r 17/13/0) | 7% cov 97% (n=30; c/i/r 2/27/1) | 27% cov 100% (n=30; c/i/r 8/22/0) | 73% cov 100% (n=30; c/i/r 22/8/0) | **41%** cov 99% (n=120; c/i/r 49/70/1) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Book of Mormon (2013 edition, en) | 120 | 41% | 99% | 1 | — | 14 | 56 | near_copy 2, paraphrase 8, wrong_passage 35, omission 4, addition 1, wrong_locus 13, wrong_verdict 8 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 120 | 9,378 | 8,095 |
| **total** | 120 | 9,378 | 8,095 |
