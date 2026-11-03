| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 0% cov 97% (n=30; c/i/r 0/29/1; minor/major 0/29) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 90% (n=30; c/i/r 0/27/3; minor/major 0/27) | 57% cov 100% (n=30; c/i/r 17/13/0; minor/major 0/13) | **15%** cov 97% (c/i/r 17/99/4; minor/major 0/99) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gpt-oss-20b | cite_passage | 29 | 0 | 29 | wrong_locus 19, no_citation 10 |
| gpt-oss-20b | complete_unit | 30 | 0 | 30 | wrong_passage 29, other_script 1 |
| gpt-oss-20b | retrieve_quote | 27 | 0 | 27 | wrong_passage 27 |
| gpt-oss-20b | verify_source | 13 | 0 | 13 | wrong_verdict 13 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Islam | 0% cov 97% (n=30; c/i/r 0/29/1) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 90% (n=30; c/i/r 0/27/3) | 57% cov 100% (n=30; c/i/r 17/13/0) | **15%** cov 97% (n=120; c/i/r 17/99/4) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 15% | 97% | 4 | — | 0 | 99 | wrong_passage 56, other_script 1, wrong_locus 19, no_citation 10, wrong_verdict 13 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 120 | 24,390 | 153,925 |
| **total** | 120 | 24,390 | 153,925 |
