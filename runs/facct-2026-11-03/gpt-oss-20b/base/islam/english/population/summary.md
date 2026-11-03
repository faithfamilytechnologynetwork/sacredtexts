| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 10% cov 97% (n=30; c/i/r 3/26/1; minor/major 0/26) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 1/29) | 0% cov 93% (n=30; c/i/r 0/28/2; minor/major 1/27) | 60% cov 100% (n=30; c/i/r 18/12/0; minor/major 0/12) | **18%** cov 98% (c/i/r 21/96/3; minor/major 2/94) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gpt-oss-20b | cite_passage | 26 | 0 | 26 | wrong_locus 26 |
| gpt-oss-20b | complete_unit | 30 | 1 | 29 | paraphrase 1, wrong_passage 29 |
| gpt-oss-20b | retrieve_quote | 28 | 1 | 27 | paraphrase 1, wrong_passage 27 |
| gpt-oss-20b | verify_source | 12 | 0 | 12 | wrong_verdict 12 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Islam | 10% cov 97% (n=30; c/i/r 3/26/1) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 93% (n=30; c/i/r 0/28/2) | 60% cov 100% (n=30; c/i/r 18/12/0) | **18%** cov 98% (n=120; c/i/r 21/96/3) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Saheeh International (QUL), en) | 120 | 18% | 98% | 3 | — | 2 | 94 | paraphrase 2, wrong_passage 56, wrong_locus 26, wrong_verdict 12 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 120 | 16,687 | 41,844 |
| **total** | 120 | 16,687 | 41,844 |
