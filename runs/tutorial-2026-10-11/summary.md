| model | retrieve_quote | overall |
|---|---|---|
| opus | 100% cov 66% (n=100; c/i/r 66/0/34) | **100%** cov 66% (c/i/r 66/0/34) |
| opus-search | 92% cov 80% (n=100; c/i/r 74/6/20) | **92%** cov 80% (c/i/r 74/6/20) |
| haiku-search | 79% cov 66% (n=100; c/i/r 52/14/34) | **79%** cov 66% (c/i/r 52/14/34) |
| haiku | 71% cov 66% (n=100; c/i/r 47/19/34) | **71%** cov 66% (c/i/r 47/19/34) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | retrieve_quote | overall |
|---|---|---|---|
| haiku | Judaism | n/a cov 0% (n=34; c/i/r 0/0/34) | **n/a** cov 0% (n=34; c/i/r 0/0/34) |
| haiku | Protestant Christian | 85% cov 100% (n=33; c/i/r 28/5/0) | **85%** cov 100% (n=33; c/i/r 28/5/0) |
| haiku | Sunni Islam | 58% cov 100% (n=33; c/i/r 19/14/0) | **58%** cov 100% (n=33; c/i/r 19/14/0) |
| haiku-search | Judaism | n/a cov 0% (n=34; c/i/r 0/0/34) | **n/a** cov 0% (n=34; c/i/r 0/0/34) |
| haiku-search | Protestant Christian | 85% cov 100% (n=33; c/i/r 28/5/0) | **85%** cov 100% (n=33; c/i/r 28/5/0) |
| haiku-search | Sunni Islam | 73% cov 100% (n=33; c/i/r 24/9/0) | **73%** cov 100% (n=33; c/i/r 24/9/0) |
| opus | Judaism | n/a cov 0% (n=34; c/i/r 0/0/34) | **n/a** cov 0% (n=34; c/i/r 0/0/34) |
| opus | Protestant Christian | 100% cov 100% (n=33; c/i/r 33/0/0) | **100%** cov 100% (n=33; c/i/r 33/0/0) |
| opus | Sunni Islam | 100% cov 100% (n=33; c/i/r 33/0/0) | **100%** cov 100% (n=33; c/i/r 33/0/0) |
| opus-search | Judaism | 57% cov 41% (n=34; c/i/r 8/6/20) | **57%** cov 41% (n=34; c/i/r 8/6/20) |
| opus-search | Protestant Christian | 100% cov 100% (n=33; c/i/r 33/0/0) | **100%** cov 100% (n=33; c/i/r 33/0/0) |
| opus-search | Sunni Islam | 100% cov 100% (n=33; c/i/r 33/0/0) | **100%** cov 100% (n=33; c/i/r 33/0/0) |

### Panel composition (committed-artifact proof — provider / model / tools / endpoint, no secrets)
| model_id | provider | model | tools | endpoint | served_by |
|---|---|---|---|---|---|
| haiku | anthropic | claude-haiku-5-5 | — | api.anthropic.com | — |
| haiku-search | anthropic | claude-haiku-5-5 | web_search | api.anthropic.com | — |
| opus | anthropic | claude-opus-5-5 | — | api.anthropic.com | — |
| opus-search | anthropic | claude-opus-5-5 | web_search | api.anthropic.com | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 100 | 5,166 | 44,375 |
| haiku-search | 100 | 1,460,684 | 80,986 |
| opus | 100 | 5,166 | 39,954 |
| opus-search | 100 | 2,772,157 | 83,210 |
| **total** | 400 | 4,243,173 | 248,525 |
