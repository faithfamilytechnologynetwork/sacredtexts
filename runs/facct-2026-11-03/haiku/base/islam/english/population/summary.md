| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 93% cov 100% (n=30; c/i/r 28/2/0; minor/major 0/2) | 15% cov 67% (n=30; c/i/r 3/17/10; minor/major 9/8) | n/a cov 0% (n=30; c/i/r 0/0/30; minor/major 0/0) | 100% cov 37% (n=30; c/i/r 11/0/19; minor/major 0/0) | **69%** cov 51% (c/i/r 42/19/59; minor/major 9/10) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | cite_passage | 2 | 0 | 2 | wrong_locus 1, hedge 1 |
| haiku | complete_unit | 17 | 9 | 8 | near_copy 3, paraphrase 5, wrong_passage 8, omission 1, addition 1 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Islam | 93% cov 100% (n=30; c/i/r 28/2/0) | 15% cov 67% (n=30; c/i/r 3/17/10) | n/a cov 0% (n=30; c/i/r 0/0/30) | 100% cov 37% (n=30; c/i/r 11/0/19) | **69%** cov 51% (n=120; c/i/r 42/19/59) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| The Qur'an (Saheeh International (QUL), en) | 120 | 69% | 51% | 59 | — | 9 | 10 | near_copy 3, paraphrase 5, wrong_passage 8, omission 1, addition 1, wrong_locus 1, hedge 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 120 | 12,893 | 10,436 |
| **total** | 120 | 12,893 | 10,436 |
