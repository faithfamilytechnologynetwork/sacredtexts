| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| kimi | 10% cov 100% (n=30; c/i/r 3/27/0; minor/major 0/27) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 5/25) | 0% cov 93% (n=30; c/i/r 0/28/2; minor/major 0/28) | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | **26%** cov 98% (c/i/r 31/87/2; minor/major 5/82) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| kimi | cite_passage | 27 | 0 | 27 | wrong_locus 22, no_citation 5 |
| kimi | complete_unit | 30 | 5 | 25 | paraphrase 4, wrong_passage 24, other_script 1, omission 1 |
| kimi | retrieve_quote | 28 | 0 | 28 | wrong_passage 28 |
| kimi | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| kimi | Judaism | 10% cov 100% (n=30; c/i/r 3/27/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 93% (n=30; c/i/r 0/28/2) | 93% cov 100% (n=30; c/i/r 28/2/0) | **26%** cov 98% (n=120; c/i/r 31/87/2) |

### By text (one text = one work · version · language)

**kimi**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 26% | 98% | 2 | — | 5 | 82 | paraphrase 4, wrong_passage 52, other_script 1, omission 1, wrong_locus 22, no_citation 5, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| kimi | 120 | 16,514 | 42,488 |
| **total** | 120 | 16,514 | 42,488 |
