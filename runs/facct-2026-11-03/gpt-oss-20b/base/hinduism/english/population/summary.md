| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 2/28) | 0% cov 10% (n=30; c/i/r 0/3/27; minor/major 0/3) | 50% cov 100% (n=30; c/i/r 15/15/0; minor/major 0/15) | **16%** cov 78% (c/i/r 15/78/27; minor/major 2/76) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gpt-oss-20b | cite_passage | 30 | 0 | 30 | wrong_locus 20, no_citation 10 |
| gpt-oss-20b | complete_unit | 30 | 2 | 28 | paraphrase 2, wrong_passage 28 |
| gpt-oss-20b | retrieve_quote | 3 | 0 | 3 | wrong_passage 3 |
| gpt-oss-20b | verify_source | 15 | 0 | 15 | wrong_verdict 15 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Hinduism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 10% (n=30; c/i/r 0/3/27) | 50% cov 100% (n=30; c/i/r 15/15/0) | **16%** cov 78% (n=120; c/i/r 15/78/27) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 16% | 78% | 27 | — | 2 | 76 | paraphrase 2, wrong_passage 31, wrong_locus 20, no_citation 10, wrong_verdict 15 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 120 | 15,231 | 18,444 |
| **total** | 120 | 15,231 | 18,444 |
