| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| opus | 43% cov 100% (n=30; c/i/r 13/17/0; minor/major 0/17) | 28% cov 97% (n=30; c/i/r 8/21/1; minor/major 11/10) | 0% cov 17% (n=30; c/i/r 0/5/25; minor/major 2/3) | 83% cov 100% (n=30; c/i/r 25/5/0; minor/major 0/5) | **49%** cov 78% (c/i/r 46/48/26; minor/major 13/35) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| opus | cite_passage | 17 | 0 | 17 | wrong_locus 17 |
| opus | complete_unit | 21 | 11 | 10 | edition_variant 1, paraphrase 7, wrong_passage 9, other_script 1, omission 3 |
| opus | retrieve_quote | 5 | 2 | 3 | paraphrase 2, wrong_passage 3 |
| opus | verify_source | 5 | 0 | 5 | wrong_verdict 5 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| opus | Judaism | 43% cov 100% (n=30; c/i/r 13/17/0) | 28% cov 97% (n=30; c/i/r 8/21/1) | 0% cov 17% (n=30; c/i/r 0/5/25) | 83% cov 100% (n=30; c/i/r 25/5/0) | **49%** cov 78% (n=120; c/i/r 46/48/26) |

### By text (one text = one work · version · language)

**opus**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 49% | 78% | 26 | — | 13 | 35 | edition_variant 1, paraphrase 9, wrong_passage 12, other_script 1, omission 3, wrong_locus 17, wrong_verdict 5 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| opus | 120 | 17,875 | 58,150 |
| **total** | 120 | 17,875 | 58,150 |
