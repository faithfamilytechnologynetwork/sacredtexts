| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| sol-search | 50% cov 100% (n=14; c/i/r 7/7/0) | 93% cov 100% (n=14; c/i/r 13/1/0) | 21% cov 100% (n=14; c/i/r 3/11/0) | 100% cov 100% (n=14; c/i/r 14/0/0) | **66%** cov 100% (c/i/r 37/19/0) |
| sonnet | 50% cov 100% (n=14; c/i/r 7/7/0) | 64% cov 100% (n=14; c/i/r 9/5/0) | 0% cov 57% (n=14; c/i/r 0/8/6) | 100% cov 100% (n=14; c/i/r 14/0/0) | **60%** cov 89% (c/i/r 30/20/6) |
| sol | 50% cov 100% (n=14; c/i/r 7/7/0) | 64% cov 100% (n=14; c/i/r 9/5/0) | 14% cov 100% (n=14; c/i/r 2/12/0) | 100% cov 100% (n=14; c/i/r 14/0/0) | **57%** cov 100% (c/i/r 32/24/0) |
| sonnet-search | 50% cov 100% (n=14; c/i/r 7/7/0) | 57% cov 100% (n=14; c/i/r 8/6/0) | 0% cov 71% (n=14; c/i/r 0/10/4) | 100% cov 100% (n=14; c/i/r 14/0/0) | **56%** cov 93% (c/i/r 29/23/4) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| sol | Sunni Islam | 50% cov 100% (n=14; c/i/r 7/7/0) | 64% cov 100% (n=14; c/i/r 9/5/0) | 14% cov 100% (n=14; c/i/r 2/12/0) | 100% cov 100% (n=14; c/i/r 14/0/0) | **57%** cov 100% (n=56; c/i/r 32/24/0) |
| sol-search | Sunni Islam | 50% cov 100% (n=14; c/i/r 7/7/0) | 93% cov 100% (n=14; c/i/r 13/1/0) | 21% cov 100% (n=14; c/i/r 3/11/0) | 100% cov 100% (n=14; c/i/r 14/0/0) | **66%** cov 100% (n=56; c/i/r 37/19/0) |
| sonnet | Sunni Islam | 50% cov 100% (n=14; c/i/r 7/7/0) | 64% cov 100% (n=14; c/i/r 9/5/0) | 0% cov 57% (n=14; c/i/r 0/8/6) | 100% cov 100% (n=14; c/i/r 14/0/0) | **60%** cov 89% (n=56; c/i/r 30/20/6) |
| sonnet-search | Sunni Islam | 50% cov 100% (n=14; c/i/r 7/7/0) | 57% cov 100% (n=14; c/i/r 8/6/0) | 0% cov 71% (n=14; c/i/r 0/10/4) | 100% cov 100% (n=14; c/i/r 14/0/0) | **56%** cov 93% (n=56; c/i/r 29/23/4) |

### By text (one text = one work · version · language)

**sol**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Sahih al-Bukhari (sunnah.com Arabic, ar) | 28 | 36% | 100% | 0 | — |
| The Qur'an (Uthmani (QUL), ar) | 28 | 79% | 100% | 0 | — |

**sol-search**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Sahih al-Bukhari (sunnah.com Arabic, ar) | 28 | 46% | 100% | 0 | — |
| The Qur'an (Uthmani (QUL), ar) | 28 | 86% | 100% | 0 | — |

**sonnet**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Sahih al-Bukhari (sunnah.com Arabic, ar) | 28 | 41% | 79% | 6 | — |
| The Qur'an (Uthmani (QUL), ar) | 28 | 75% | 100% | 0 | — |

**sonnet-search**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Sahih al-Bukhari (sunnah.com Arabic, ar) | 28 | 33% | 86% | 4 | — |
| The Qur'an (Uthmani (QUL), ar) | 28 | 75% | 100% | 0 | — |

### Panel composition (committed-artifact proof — provider / model / tools / endpoint, no secrets)
| model_id | provider | model | tools | endpoint | max_tokens | temperature | served_by |
|---|---|---|---|---|---|---|---|
| sol | openai | openai/gpt-6.1-sol | — | openrouter.ai | 4096 | 0.0 | OpenAI |
| sol-search | openai | openai/gpt-6.1-sol | web_search | openrouter.ai | 4096 | 0.0 | OpenAI |
| sonnet | openai | anthropic/claude-sonnet-5.5 | — | openrouter.ai | 4096 | 0.0 | Claude Platform on AWS |
| sonnet-search | openai | anthropic/claude-sonnet-5.5 | web_search | openrouter.ai | 4096 | 0.0 | Claude Platform on AWS |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| sol | 56 | 9,540 | 23,610 |
| sol-search | 56 | 502,026 | 9,755 |
| sonnet | 56 | 14,694 | 26,167 |
| sonnet-search | 56 | 674,282 | 28,834 |
| **total** | 224 | 1,200,542 | 88,366 |
