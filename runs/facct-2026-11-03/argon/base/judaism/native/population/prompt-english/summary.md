| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 30% cov 100% (n=30; c/i/r 9/21/0; minor/major 0/21) | 10% cov 100% (n=30; c/i/r 3/27/0; minor/major 15/12) | 0% cov 57% (n=30; c/i/r 0/17/13; minor/major 1/16) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **39%** cov 89% (c/i/r 42/65/13; minor/major 16/49) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| argon | cite_passage | 21 | 0 | 21 | wrong_locus 17, no_citation 4 |
| argon | complete_unit | 27 | 15 | 12 | edition_variant 4, near_copy 1, paraphrase 8, wrong_passage 12, omission 2, addition 1 |
| argon | retrieve_quote | 17 | 1 | 16 | paraphrase 1, wrong_passage 16 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Judaism | 30% cov 100% (n=30; c/i/r 9/21/0) | 10% cov 100% (n=30; c/i/r 3/27/0) | 0% cov 57% (n=30; c/i/r 0/17/13) | 100% cov 100% (n=30; c/i/r 30/0/0) | **39%** cov 89% (n=120; c/i/r 42/65/13) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 39% | 89% | 13 | — | 16 | 49 | edition_variant 4, near_copy 1, paraphrase 9, wrong_passage 28, omission 2, addition 1, wrong_locus 17, no_citation 4 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 120 | 23,583 | 10,373 |
| **total** | 120 | 23,583 | 10,373 |
