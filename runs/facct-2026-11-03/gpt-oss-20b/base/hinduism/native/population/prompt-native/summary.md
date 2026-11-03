| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 23% (n=30; c/i/r 0/7/23; minor/major 0/7) | 53% cov 100% (n=30; c/i/r 16/14/0; minor/major 0/14) | **16%** cov 81% (c/i/r 16/81/23; minor/major 0/81) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gpt-oss-20b | cite_passage | 30 | 0 | 30 | wrong_locus 28, no_citation 2 |
| gpt-oss-20b | complete_unit | 30 | 0 | 30 | wrong_passage 30 |
| gpt-oss-20b | retrieve_quote | 7 | 0 | 7 | wrong_passage 7 |
| gpt-oss-20b | verify_source | 14 | 0 | 14 | wrong_verdict 14 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Hinduism | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 23% (n=30; c/i/r 0/7/23) | 53% cov 100% (n=30; c/i/r 16/14/0) | **16%** cov 81% (n=120; c/i/r 16/81/23) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 16% | 81% | 23 | — | 0 | 81 | wrong_passage 37, wrong_locus 28, no_citation 2, wrong_verdict 14 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 120 | 16,603 | 51,964 |
| **total** | 120 | 16,603 | 51,964 |
