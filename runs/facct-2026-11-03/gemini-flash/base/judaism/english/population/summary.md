| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 47% cov 100% (n=30; c/i/r 14/16/0; minor/major 0/16) | 0% cov 7% (n=30; c/i/r 0/2/28; minor/major 2/0) | 0% cov 7% (n=30; c/i/r 0/2/28; minor/major 0/2) | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | **66%** cov 53% (c/i/r 42/22/56; minor/major 2/20) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemini-flash | cite_passage | 16 | 0 | 16 | wrong_locus 16 |
| gemini-flash | complete_unit | 2 | 2 | 0 | paraphrase 1, omission 1 |
| gemini-flash | retrieve_quote | 2 | 0 | 2 | wrong_passage 2 |
| gemini-flash | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Judaism | 47% cov 100% (n=30; c/i/r 14/16/0) | 0% cov 7% (n=30; c/i/r 0/2/28) | 0% cov 7% (n=30; c/i/r 0/2/28) | 93% cov 100% (n=30; c/i/r 28/2/0) | **66%** cov 53% (n=120; c/i/r 42/22/56) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Talmud Bavli (William Davidson Edition - English, en) | 120 | 66% | 53% | 56 | — | 2 | 20 | paraphrase 1, wrong_passage 2, omission 1, wrong_locus 16, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 11,897 | 33,757 |
| **total** | 120 | 11,897 | 33,757 |
