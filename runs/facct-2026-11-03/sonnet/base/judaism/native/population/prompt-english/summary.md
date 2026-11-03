| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 4% cov 87% (n=30; c/i/r 1/25/4; minor/major 0/25) | 4% cov 87% (n=30; c/i/r 1/25/4; minor/major 1/24) | n/a cov 0% (n=30; c/i/r 0/0/30; minor/major 0/0) | 25% cov 13% (n=30; c/i/r 1/3/26; minor/major 0/3) | **5%** cov 47% (c/i/r 3/53/64; minor/major 1/52) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sonnet | cite_passage | 25 | 0 | 25 | hedge 25 |
| sonnet | complete_unit | 25 | 1 | 24 | paraphrase 1, wrong_passage 13, other_script 11, addition 1 |
| sonnet | verify_source | 3 | 0 | 3 | wrong_verdict 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Judaism | 4% cov 87% (n=30; c/i/r 1/25/4) | 4% cov 87% (n=30; c/i/r 1/25/4) | n/a cov 0% (n=30; c/i/r 0/0/30) | 25% cov 13% (n=30; c/i/r 1/3/26) | **5%** cov 47% (n=120; c/i/r 3/53/64) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 5% | 47% | 64 | — | 1 | 52 | paraphrase 1, wrong_passage 13, other_script 11, addition 1, hedge 25, wrong_verdict 3 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 120 | 19,945 | 42,722 |
| **total** | 120 | 19,945 | 42,722 |
