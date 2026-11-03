| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 3% cov 100% (n=30; c/i/r 1/29/0; minor/major 0/29) | 3% cov 97% (n=30; c/i/r 1/28/1; minor/major 2/26) | 0% cov 93% (n=30; c/i/r 0/28/2; minor/major 2/26) | 73% cov 100% (n=30; c/i/r 22/8/0; minor/major 0/8) | **21%** cov 98% (c/i/r 24/93/3; minor/major 4/89) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gpt-oss-20b | cite_passage | 29 | 0 | 29 | wrong_locus 27, no_citation 2 |
| gpt-oss-20b | complete_unit | 28 | 2 | 26 | paraphrase 2, wrong_passage 26 |
| gpt-oss-20b | retrieve_quote | 28 | 2 | 26 | near_copy 1, paraphrase 1, wrong_passage 26 |
| gpt-oss-20b | verify_source | 8 | 0 | 8 | wrong_verdict 8 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Christianity | 3% cov 100% (n=30; c/i/r 1/29/0) | 3% cov 97% (n=30; c/i/r 1/28/1) | 0% cov 93% (n=30; c/i/r 0/28/2) | 73% cov 100% (n=30; c/i/r 22/8/0) | **21%** cov 98% (n=120; c/i/r 24/93/3) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (NRSV, en) | 120 | 21% | 98% | 3 | — | 4 | 89 | near_copy 1, paraphrase 3, wrong_passage 52, wrong_locus 27, no_citation 2, wrong_verdict 8 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 120 | 14,167 | 61,782 |
| **total** | 120 | 14,167 | 61,782 |
