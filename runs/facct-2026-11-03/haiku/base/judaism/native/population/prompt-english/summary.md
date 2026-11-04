| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 7% cov 100% (n=30; c/i/r 2/28/0; minor/major 0/28) | 0% cov 67% (n=30; c/i/r 0/20/10; minor/major 0/20) | n/a cov 0% (n=30; c/i/r 0/0/30; minor/major 0/0) | 77% cov 100% (n=30; c/i/r 23/7/0; minor/major 0/7) | **31%** cov 67% (c/i/r 25/55/40; minor/major 0/55) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | cite_passage | 28 | 0 | 28 | wrong_locus 25, hedge 3 |
| haiku | complete_unit | 20 | 0 | 20 | wrong_passage 6, other_script 14 |
| haiku | verify_source | 7 | 0 | 7 | wrong_verdict 7 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Judaism | 7% cov 100% (n=30; c/i/r 2/28/0) | 0% cov 67% (n=30; c/i/r 0/20/10) | n/a cov 0% (n=30; c/i/r 0/0/30) | 77% cov 100% (n=30; c/i/r 23/7/0) | **31%** cov 67% (n=120; c/i/r 25/55/40) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 31% | 67% | 40 | — | 0 | 55 | wrong_passage 6, other_script 14, wrong_locus 25, hedge 3, wrong_verdict 7 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 120 | 17,635 | 15,528 |
| **total** | 120 | 17,635 | 15,528 |
