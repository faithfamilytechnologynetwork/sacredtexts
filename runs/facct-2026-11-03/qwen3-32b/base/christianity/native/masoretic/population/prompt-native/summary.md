| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| qwen3-32b | 29% cov 100% (n=21; c/i/r 6/15/0; minor/major 0/15) | 0% cov 100% (n=21; c/i/r 0/21/0; minor/major 3/18) | 0% cov 100% (n=21; c/i/r 0/21/0; minor/major 0/21) | 58% cov 90% (n=21; c/i/r 11/8/2; minor/major 0/8) | **21%** cov 98% (c/i/r 17/65/2; minor/major 3/62) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| qwen3-32b | cite_passage | 15 | 0 | 15 | wrong_locus 15 |
| qwen3-32b | complete_unit | 21 | 3 | 18 | paraphrase 2, wrong_passage 18, omission 1 |
| qwen3-32b | retrieve_quote | 21 | 0 | 21 | wrong_passage 21 |
| qwen3-32b | verify_source | 8 | 0 | 8 | wrong_verdict 8 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| qwen3-32b | Christianity | 29% cov 100% (n=21; c/i/r 6/15/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 0% cov 100% (n=21; c/i/r 0/21/0) | 58% cov 90% (n=21; c/i/r 11/8/2) | **21%** cov 98% (n=84; c/i/r 17/65/2) |

### By text (one text = one work · version · language)

**qwen3-32b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Bible (the Masoretic Text (Westminster Leningrad Codex), arc) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| The Bible (the Masoretic Text (Westminster Leningrad Codex), he) | 80 | 21% | 98% | 2 | — | 3 | 59 | paraphrase 2, wrong_passage 37, omission 1, wrong_locus 14, wrong_verdict 8 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| qwen3-32b | 84 | 12,324 | 72,725 |
| **total** | 84 | 12,324 | 72,725 |
