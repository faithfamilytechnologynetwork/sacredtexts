| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 37% cov 100% (n=30; c/i/r 11/19/0; minor/major 0/19) | 7% cov 100% (n=30; c/i/r 2/28/0; minor/major 15/13) | 0% cov 47% (n=30; c/i/r 0/14/16; minor/major 1/13) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | **40%** cov 87% (c/i/r 42/62/16; minor/major 16/46) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemini-flash | cite_passage | 19 | 0 | 19 | wrong_locus 11, no_citation 8 |
| gemini-flash | complete_unit | 28 | 15 | 13 | edition_variant 5, paraphrase 8, wrong_passage 13, omission 2 |
| gemini-flash | retrieve_quote | 14 | 1 | 13 | near_copy 1, wrong_passage 12, other_script 1 |
| gemini-flash | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Judaism | 37% cov 100% (n=30; c/i/r 11/19/0) | 7% cov 100% (n=30; c/i/r 2/28/0) | 0% cov 47% (n=30; c/i/r 0/14/16) | 97% cov 100% (n=30; c/i/r 29/1/0) | **40%** cov 87% (n=120; c/i/r 42/62/16) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - Aramaic, he) | 120 | 40% | 87% | 16 | — | 16 | 46 | edition_variant 5, near_copy 1, paraphrase 8, wrong_passage 25, other_script 1, omission 2, wrong_locus 11, no_citation 8, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 11,922 | 71,320 |
| **total** | 120 | 11,922 | 71,320 |
