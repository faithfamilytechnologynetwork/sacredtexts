| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemma-31b | 10% cov 100% (n=30; c/i/r 3/27/0; minor/major 0/27) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 2/28) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 97% cov 100% (n=30; c/i/r 29/1/0; minor/major 0/1) | **27%** cov 100% (c/i/r 32/88/0; minor/major 2/86) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gemma-31b | cite_passage | 27 | 0 | 27 | wrong_locus 26, no_citation 1 |
| gemma-31b | complete_unit | 30 | 2 | 28 | paraphrase 2, wrong_passage 28 |
| gemma-31b | retrieve_quote | 30 | 0 | 30 | wrong_passage 30 |
| gemma-31b | verify_source | 1 | 0 | 1 | wrong_verdict 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemma-31b | Hinduism | 10% cov 100% (n=30; c/i/r 3/27/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 97% cov 100% (n=30; c/i/r 29/1/0) | **27%** cov 100% (n=120; c/i/r 32/88/0) |

### By text (one text = one work · version · language)

**gemma-31b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Bhagavad Gita (Annie Besant (1922), en) | 120 | 27% | 100% | 0 | — | 2 | 86 | paraphrase 2, wrong_passage 58, wrong_locus 26, no_citation 1, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemma-31b | 120 | 8,913 | 1,661 |
| **total** | 120 | 8,913 | 1,661 |
