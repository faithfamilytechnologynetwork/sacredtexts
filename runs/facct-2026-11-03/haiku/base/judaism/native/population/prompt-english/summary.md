| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 4% cov 87% (n=30; c/i/r 1/25/4; minor/major 0/25) | 0% cov 43% (n=30; c/i/r 0/13/17; minor/major 0/13) | n/a cov 0% (n=30; c/i/r 0/0/30; minor/major 0/0) | 69% cov 97% (n=30; c/i/r 20/9/1; minor/major 0/9) | **31%** cov 57% (c/i/r 21/47/52; minor/major 0/47) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | cite_passage | 25 | 0 | 25 | wrong_locus 22, hedge 3 |
| haiku | complete_unit | 13 | 0 | 13 | wrong_passage 5, other_script 8 |
| haiku | verify_source | 9 | 0 | 9 | wrong_verdict 9 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Judaism | 4% cov 87% (n=30; c/i/r 1/25/4) | 0% cov 43% (n=30; c/i/r 0/13/17) | n/a cov 0% (n=30; c/i/r 0/0/30) | 69% cov 97% (n=30; c/i/r 20/9/1) | **31%** cov 57% (n=120; c/i/r 21/47/52) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 31% | 57% | 52 | — | 0 | 47 | wrong_passage 5, other_script 8, wrong_locus 22, hedge 3, wrong_verdict 9 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 120 | 19,705 | 14,692 |
| **total** | 120 | 19,705 | 14,692 |
