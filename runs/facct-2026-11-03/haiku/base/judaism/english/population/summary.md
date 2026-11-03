| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 0% cov 30% (n=30; c/i/r 0/9/21; minor/major 0/9) | 0% cov 17% (n=30; c/i/r 0/5/25; minor/major 2/3) | n/a cov 0% (n=30; c/i/r 0/0/30; minor/major 0/0) | 80% cov 17% (n=30; c/i/r 4/1/25; minor/major 0/1) | **21%** cov 16% (c/i/r 4/15/101; minor/major 2/13) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | cite_passage | 9 | 0 | 9 | wrong_locus 7, hedge 2 |
| haiku | complete_unit | 5 | 2 | 3 | paraphrase 2, wrong_passage 3 |
| haiku | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Judaism | 0% cov 30% (n=30; c/i/r 0/9/21) | 0% cov 17% (n=30; c/i/r 0/5/25) | n/a cov 0% (n=30; c/i/r 0/0/30) | 80% cov 17% (n=30; c/i/r 4/1/25) | **21%** cov 16% (n=120; c/i/r 4/15/101) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - English, en) | 120 | 21% | 16% | 101 | — | 2 | 13 | paraphrase 2, wrong_passage 3, wrong_locus 7, hedge 2, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 120 | 18,727 | 22,828 |
| **total** | 120 | 18,727 | 22,828 |
