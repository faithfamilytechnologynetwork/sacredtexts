| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| deepseek-v4-pro | 21% cov 97% (n=30; c/i/r 6/23/1; minor/major 0/23) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 7/23) | 0% cov 73% (n=30; c/i/r 0/22/8; minor/major 1/21) | 53% cov 100% (n=30; c/i/r 16/14/0; minor/major 0/14) | **20%** cov 92% (c/i/r 22/89/9; minor/major 8/81) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| deepseek-v4-pro | cite_passage | 23 | 0 | 23 | wrong_locus 22, no_citation 1 |
| deepseek-v4-pro | complete_unit | 30 | 7 | 23 | paraphrase 3, wrong_passage 23, omission 4 |
| deepseek-v4-pro | retrieve_quote | 22 | 1 | 21 | paraphrase 1, wrong_passage 20, other_script 1 |
| deepseek-v4-pro | verify_source | 14 | 0 | 14 | wrong_verdict 14 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | Judaism | 21% cov 97% (n=30; c/i/r 6/23/1) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 73% (n=30; c/i/r 0/22/8) | 53% cov 100% (n=30; c/i/r 16/14/0) | **20%** cov 92% (n=120; c/i/r 22/89/9) |

### By text (one text = one work · version · language)

**deepseek-v4-pro**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 20% | 92% | 9 | — | 8 | 81 | paraphrase 4, wrong_passage 43, other_script 1, omission 4, wrong_locus 22, no_citation 1, wrong_verdict 14 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| deepseek-v4-pro | 120 | 12,406 | 6,828 |
| **total** | 120 | 12,406 | 6,828 |
