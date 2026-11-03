| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 19% cov 87% (n=30; c/i/r 5/21/4; minor/major 0/21) | 22% cov 30% (n=30; c/i/r 2/7/21; minor/major 0/7) | 33% cov 10% (n=30; c/i/r 1/2/27; minor/major 0/2) | 100% cov 80% (n=30; c/i/r 24/0/6; minor/major 0/0) | **52%** cov 52% (c/i/r 32/30/58; minor/major 0/30) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | cite_passage | 21 | 0 | 21 | wrong_locus 19, hedge 2 |
| haiku | complete_unit | 7 | 0 | 7 | wrong_passage 7, addition 2 |
| haiku | retrieve_quote | 2 | 0 | 2 | wrong_passage 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Book of Mormon | 19% cov 87% (n=30; c/i/r 5/21/4) | 22% cov 30% (n=30; c/i/r 2/7/21) | 33% cov 10% (n=30; c/i/r 1/2/27) | 100% cov 80% (n=30; c/i/r 24/0/6) | **52%** cov 52% (n=120; c/i/r 32/30/58) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Book of Mormon (2013 edition, en) | 120 | 52% | 52% | 58 | — | 0 | 30 | wrong_passage 9, addition 2, wrong_locus 19, hedge 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 120 | 13,183 | 12,301 |
| **total** | 120 | 13,183 | 12,301 |
