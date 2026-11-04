| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sonnet | 7% cov 100% (n=30; c/i/r 2/28/0; minor/major 0/28) | 60% cov 100% (n=30; c/i/r 18/12/0; minor/major 3/9) | 50% cov 100% (n=30; c/i/r 15/15/0; minor/major 5/10) | 100% cov 7% (n=30; c/i/r 2/0/28; minor/major 0/0) | **40%** cov 77% (c/i/r 37/55/28; minor/major 8/47) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| sonnet | cite_passage | 28 | 0 | 28 | hedge 28 |
| sonnet | complete_unit | 12 | 3 | 9 | edition_variant 1, paraphrase 2, wrong_passage 9, addition 18 |
| sonnet | retrieve_quote | 15 | 5 | 10 | near_copy 1, paraphrase 4, wrong_passage 10, addition 13 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sonnet | Buddhism | 7% cov 100% (n=30; c/i/r 2/28/0) | 60% cov 100% (n=30; c/i/r 18/12/0) | 50% cov 100% (n=30; c/i/r 15/15/0) | 100% cov 7% (n=30; c/i/r 2/0/28) | **40%** cov 77% (n=120; c/i/r 37/55/28) |

### By text (one text = one work · version · language)

**sonnet**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Dhammapada (Chaṭṭha Saṅgāyana (VRI), pi) | 120 | 40% | 77% | 28 | — | 8 | 47 | edition_variant 1, near_copy 1, paraphrase 6, wrong_passage 19, addition 31, hedge 28 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sonnet | 120 | 20,794 | 32,071 |
| **total** | 120 | 20,794 | 32,071 |
