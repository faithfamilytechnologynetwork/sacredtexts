| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| qwen3-32b | 13% cov 100% (n=30; c/i/r 4/26/0; minor/major 0/26) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 77% cov 100% (n=30; c/i/r 23/7/0; minor/major 0/7) | **22%** cov 100% (c/i/r 27/93/0; minor/major 0/93) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| qwen3-32b | cite_passage | 26 | 0 | 26 | wrong_locus 25, no_citation 1 |
| qwen3-32b | complete_unit | 30 | 0 | 30 | wrong_passage 30 |
| qwen3-32b | retrieve_quote | 30 | 0 | 30 | wrong_passage 30 |
| qwen3-32b | verify_source | 7 | 0 | 7 | wrong_verdict 7 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| qwen3-32b | Hinduism | 13% cov 100% (n=30; c/i/r 4/26/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 77% cov 100% (n=30; c/i/r 23/7/0) | **22%** cov 100% (n=120; c/i/r 27/93/0) |

### By text (one text = one work · version · language)

**qwen3-32b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 120 | 22% | 100% | 0 | — | 0 | 93 | wrong_passage 60, wrong_locus 25, no_citation 1, wrong_verdict 7 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| qwen3-32b | 120 | 15,800 | 56,735 |
| **total** | 120 | 15,800 | 56,735 |
