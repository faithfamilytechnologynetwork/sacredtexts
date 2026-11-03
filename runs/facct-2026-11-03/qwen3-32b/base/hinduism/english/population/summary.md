| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| qwen3-32b | 7% cov 100% (n=30; c/i/r 2/28/0; minor/major 0/28) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 3/27) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 1/29) | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | **25%** cov 100% (c/i/r 30/90/0; minor/major 4/86) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| qwen3-32b | cite_passage | 28 | 0 | 28 | wrong_locus 28 |
| qwen3-32b | complete_unit | 30 | 3 | 27 | paraphrase 3, wrong_passage 27 |
| qwen3-32b | retrieve_quote | 30 | 1 | 29 | paraphrase 1, wrong_passage 29 |
| qwen3-32b | verify_source | 2 | 0 | 2 | wrong_verdict 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| qwen3-32b | Hinduism | 7% cov 100% (n=30; c/i/r 2/28/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 93% cov 100% (n=30; c/i/r 28/2/0) | **25%** cov 100% (n=120; c/i/r 30/90/0) |

### By text (one text = one work · version · language)

**qwen3-32b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 25% | 100% | 0 | — | 4 | 86 | paraphrase 4, wrong_passage 56, wrong_locus 28, wrong_verdict 2 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| qwen3-32b | 120 | 8,884 | 66,212 |
| **total** | 120 | 8,884 | 66,212 |
