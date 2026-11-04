| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 0% cov 53% (n=30; c/i/r 0/16/14; minor/major 0/16) | 0% cov 87% (n=30; c/i/r 0/26/4; minor/major 0/26) | 0% cov 10% (n=30; c/i/r 0/3/27; minor/major 0/3) | 69% cov 97% (n=30; c/i/r 20/9/1; minor/major 0/9) | **27%** cov 62% (c/i/r 20/54/46; minor/major 0/54) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | cite_passage | 16 | 0 | 16 | wrong_locus 8, hedge 7, no_citation 1 |
| haiku | complete_unit | 26 | 0 | 26 | wrong_passage 25, other_script 1 |
| haiku | retrieve_quote | 3 | 0 | 3 | wrong_passage 3 |
| haiku | verify_source | 9 | 0 | 9 | wrong_verdict 9 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Judaism | 0% cov 53% (n=30; c/i/r 0/16/14) | 0% cov 87% (n=30; c/i/r 0/26/4) | 0% cov 10% (n=30; c/i/r 0/3/27) | 69% cov 97% (n=30; c/i/r 20/9/1) | **27%** cov 62% (n=120; c/i/r 20/54/46) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 27% | 62% | 46 | — | 0 | 54 | wrong_passage 28, other_script 1, wrong_locus 8, hedge 7, no_citation 1, wrong_verdict 9 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 120 | 16,287 | 42,119 |
| **total** | 120 | 16,287 | 42,119 |
