| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| beam | 17% cov 97% (n=30; c/i/r 5/24/1; minor/major 0/24) | 0% cov 87% (n=30; c/i/r 0/26/4; minor/major 6/20) | n/a cov 0% (n=30; c/i/r 0/0/30; minor/major 0/0) | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | **39%** cov 71% (c/i/r 33/52/35; minor/major 6/46) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| beam | cite_passage | 24 | 0 | 24 | wrong_locus 23, no_citation 1 |
| beam | complete_unit | 26 | 6 | 20 | paraphrase 4, wrong_passage 18, other_script 2, omission 2 |
| beam | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| beam | Judaism | 17% cov 97% (n=30; c/i/r 5/24/1) | 0% cov 87% (n=30; c/i/r 0/26/4) | n/a cov 0% (n=30; c/i/r 0/0/30) | 93% cov 100% (n=30; c/i/r 28/2/0) | **39%** cov 71% (n=120; c/i/r 33/52/35) |

### By text (one text = one work · version · language)

**beam**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 39% | 71% | 35 | — | 6 | 46 | paraphrase 4, wrong_passage 18, other_script 2, omission 2, wrong_locus 23, no_citation 1, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| beam | 120 | 17,005 | 134,695 |
| **total** | 120 | 17,005 | 134,695 |
