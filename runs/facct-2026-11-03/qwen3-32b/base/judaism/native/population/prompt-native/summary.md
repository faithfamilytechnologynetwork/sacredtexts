| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| qwen3-32b | 7% cov 100% (n=30; c/i/r 2/28/0; minor/major 0/28) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 3/27) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 79% cov 97% (n=30; c/i/r 23/6/1; minor/major 0/6) | **21%** cov 99% (c/i/r 25/94/1; minor/major 3/91) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| qwen3-32b | cite_passage | 28 | 0 | 28 | wrong_locus 25, hedge 1, no_citation 2 |
| qwen3-32b | complete_unit | 30 | 3 | 27 | paraphrase 2, wrong_passage 26, other_script 1, omission 1 |
| qwen3-32b | retrieve_quote | 30 | 0 | 30 | wrong_passage 29, other_script 1 |
| qwen3-32b | verify_source | 6 | 0 | 6 | wrong_verdict 6 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| qwen3-32b | Judaism | 7% cov 100% (n=30; c/i/r 2/28/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 79% cov 97% (n=30; c/i/r 23/6/1) | **21%** cov 99% (n=120; c/i/r 25/94/1) |

### By text (one text = one work · version · language)

**qwen3-32b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 21% | 99% | 1 | — | 3 | 91 | paraphrase 2, wrong_passage 55, other_script 2, omission 1, wrong_locus 25, hedge 1, no_citation 2, wrong_verdict 6 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| qwen3-32b | 120 | 12,859 | 123,816 |
| **total** | 120 | 12,859 | 123,816 |
