| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| astra | 3% cov 100% (n=37; c/i/r 1/36/0) | 70% cov 100% (n=37; c/i/r 26/11/0) | 0% cov 89% (n=37; c/i/r 0/33/4) | 46% cov 100% (n=37; c/i/r 17/20/0) | **31%** cov 97% (c/i/r 44/100/4) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| astra | Hinduism | 3% cov 100% (n=37; c/i/r 1/36/0) | 70% cov 100% (n=37; c/i/r 26/11/0) | 0% cov 89% (n=37; c/i/r 0/33/4) | 46% cov 100% (n=37; c/i/r 17/20/0) | **31%** cov 97% (n=148; c/i/r 44/100/4) |

### By text (one text = one work · version · language)

**astra**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Bhagavad Gita (Stotra Samhita (Gita Press text), sa) | 148 | 31% | 97% | 4 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| astra | 148 | 13,066 | 16,045 |
| **total** | 148 | 13,066 | 16,045 |
