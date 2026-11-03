| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 90% cov 100% (n=21; c/i/r 19/2/0; minor/major 0/2) | 76% cov 100% (n=21; c/i/r 16/5/0; minor/major 1/4) | 52% cov 100% (n=21; c/i/r 11/10/0; minor/major 8/2) | 52% cov 100% (n=21; c/i/r 11/10/0; minor/major 0/10) | **68%** cov 100% (c/i/r 57/27/0; minor/major 9/18) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sonnet | cite_passage | 2 | 0 | 2 | wrong_locus 1, hedge 1 |
| sonnet | complete_unit | 5 | 1 | 4 | edition_variant 1, wrong_passage 4, addition 13 |
| sonnet | retrieve_quote | 10 | 8 | 2 | edition_variant 2, paraphrase 6, wrong_passage 2, addition 7 |
| sonnet | verify_source | 10 | 0 | 10 | wrong_verdict 10 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Christianity | 90% cov 100% (n=21; c/i/r 19/2/0) | 76% cov 100% (n=21; c/i/r 16/5/0) | 52% cov 100% (n=21; c/i/r 11/10/0) | 52% cov 100% (n=21; c/i/r 11/10/0) | **68%** cov 100% (n=84; c/i/r 57/27/0) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 50% | 100% | 0 | — | 1 | 1 | paraphrase 1, wrong_passage 1 |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 69% | 100% | 0 | — | 8 | 17 | edition_variant 3, paraphrase 5, wrong_passage 5, addition 20, wrong_locus 1, hedge 1, wrong_verdict 10 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 84 | 13,563 | 24,375 |
| **total** | 84 | 13,563 | 24,375 |
