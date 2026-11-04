| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| opus | 38% cov 97% (n=30; c/i/r 11/18/1; minor/major 0/18) | 36% cov 73% (n=30; c/i/r 8/14/8; minor/major 8/6) | 50% cov 7% (n=30; c/i/r 1/1/28; minor/major 1/0) | 80% cov 100% (n=30; c/i/r 24/6/0; minor/major 0/6) | **53%** cov 69% (c/i/r 44/39/37; minor/major 9/30) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| opus | cite_passage | 18 | 0 | 18 | wrong_locus 18 |
| opus | complete_unit | 14 | 8 | 6 | edition_variant 2, paraphrase 3, wrong_passage 6, omission 3 |
| opus | retrieve_quote | 1 | 1 | 0 | paraphrase 1, addition 1 |
| opus | verify_source | 6 | 0 | 6 | wrong_verdict 6 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| opus | Judaism | 38% cov 97% (n=30; c/i/r 11/18/1) | 36% cov 73% (n=30; c/i/r 8/14/8) | 50% cov 7% (n=30; c/i/r 1/1/28) | 80% cov 100% (n=30; c/i/r 24/6/0) | **53%** cov 69% (n=120; c/i/r 44/39/37) |

### By text (one text = one work · version · language)

**opus**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 53% | 69% | 37 | — | 9 | 30 | edition_variant 2, paraphrase 4, wrong_passage 6, omission 3, addition 1, wrong_locus 18, wrong_verdict 6 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| opus | 120 | 16,527 | 66,624 |
| **total** | 120 | 16,527 | 66,624 |
