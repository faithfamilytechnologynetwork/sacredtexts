| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 7% cov 93% (n=30; c/i/r 2/26/2; minor/major 0/26) | 0% cov 97% (n=30; c/i/r 0/29/1; minor/major 0/29) | 0% cov 97% (n=30; c/i/r 0/29/1; minor/major 0/29) | 57% cov 100% (n=30; c/i/r 17/13/0; minor/major 0/13) | **16%** cov 97% (c/i/r 19/97/4; minor/major 0/97) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gpt-oss-20b | cite_passage | 26 | 0 | 26 | wrong_locus 17, hedge 1, no_citation 8 |
| gpt-oss-20b | complete_unit | 29 | 0 | 29 | wrong_passage 29 |
| gpt-oss-20b | retrieve_quote | 29 | 0 | 29 | wrong_passage 26, other_script 3 |
| gpt-oss-20b | verify_source | 13 | 0 | 13 | wrong_verdict 13 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Islam | 7% cov 93% (n=30; c/i/r 2/26/2) | 0% cov 97% (n=30; c/i/r 0/29/1) | 0% cov 97% (n=30; c/i/r 0/29/1) | 57% cov 100% (n=30; c/i/r 17/13/0) | **16%** cov 97% (n=120; c/i/r 19/97/4) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Uthmani (QUL), ar) | 120 | 16% | 97% | 4 | — | 0 | 97 | wrong_passage 55, other_script 3, wrong_locus 17, hedge 1, no_citation 8, wrong_verdict 13 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 120 | 25,782 | 106,900 |
| **total** | 120 | 25,782 | 106,900 |
