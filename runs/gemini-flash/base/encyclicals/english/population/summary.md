| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gemini-flash | 50% cov 100% (n=30; c/i/r 15/15/0) | 0% cov 53% (n=30; c/i/r 0/16/14) | 0% cov 20% (n=30; c/i/r 0/6/24) | 90% cov 100% (n=30; c/i/r 27/3/0) | **51%** cov 68% (c/i/r 42/40/38) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused)._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gemini-flash | Encyclicals | 50% cov 100% (n=30; c/i/r 15/15/0) | 0% cov 53% (n=30; c/i/r 0/16/14) | 0% cov 20% (n=30; c/i/r 0/6/24) | 90% cov 100% (n=30; c/i/r 27/3/0) | **51%** cov 68% (n=120; c/i/r 42/40/38) |

### By text (one text = one work · version · language)

**gemini-flash**
| text | n | accuracy | coverage | refused | missing |
|---|---|---|---|---|---|
| Ad Petri Cathedram (Vatican English text (John XXIII, 1959-06-29), en) | 4 | 25% | 100% | 0 | — |
| Aeterni Patris (Vatican English text (Leo XIII, 1879-08-04), en) | 4 | 25% | 100% | 0 | — |
| Augustissimae Virginis Mariae (Vatican English text (Leo XIII, 1897-09-12), en) | 4 | 25% | 100% | 0 | — |
| Casti Connubii (Vatican English text (Pius XI, 1930-12-31), en) | 4 | 33% | 75% | 1 | — |
| Christi Matri (Vatican English text (Paul VI, 1966-09-15), en) | 4 | 33% | 75% | 1 | — |
| Communium Rerum (Vatican English text (Pius X, 1909-04-21), en) | 4 | 0% | 75% | 1 | — |
| Depuis le Jour (Vatican English text (Leo XIII, 1899-09-08), en) | 4 | 25% | 100% | 0 | — |
| Deus caritas est (Vatican English text (Benedict XVI, 2005-12-25), en) | 8 | 100% | 50% | 4 | — |
| Dominum et vivificantem (Vatican English text (John Paul II, 1986-05-18), en) | 4 | 100% | 50% | 2 | — |
| Ecclesiam Suam (Vatican English text (Paul VI, 1964-08-06), en) | 4 | 50% | 50% | 2 | — |
| Fides et Ratio (Vatican English text (John Paul II, 1998-09-14), en) | 4 | 50% | 50% | 2 | — |
| Fratelli tutti (Vatican English text (Francis, 2020-10-03), en) | 8 | 80% | 62% | 3 | — |
| Laudato si' (Vatican English text (Francis, 2015-05-24), en) | 4 | 67% | 75% | 1 | — |
| Meminisse Iuvat (Vatican English text (Pius XII, 1958-07-14), en) | 4 | 50% | 50% | 2 | — |
| Musicae Sacrae (Vatican English text (Pius XII, 1955-12-25), en) | 4 | 50% | 50% | 2 | — |
| Mysterium Fidei (Vatican English text (Paul VI, 1965-09-03), en) | 4 | 67% | 75% | 1 | — |
| Non Abbiamo Bisogno (Vatican English text (Pius XI, 1931-06-29), en) | 4 | 100% | 50% | 2 | — |
| Octobri Mense (Vatican English text (Leo XIII, 1891-09-22), en) | 4 | 67% | 75% | 1 | — |
| Orientales Omnes Ecclesias (Vatican English text (Pius XII, 1945-12-23), en) | 4 | 0% | 75% | 1 | — |
| Quadragesimo Anno (Vatican English text (Pius XI, 1931-05-15), en) | 8 | 80% | 62% | 3 | — |
| Quod Anniversarius (Vatican English text (Leo XIII, 1888-04-01), en) | 4 | 25% | 100% | 0 | — |
| Quod Multum (Vatican English text (Leo XIII, 1886-08-22), en) | 4 | 25% | 100% | 0 | — |
| Redemptoris Mater (Vatican English text (John Paul II, 1987-03-25), en) | 4 | 100% | 50% | 2 | — |
| Sacerdotalis Caelibatus (Vatican English text (Paul VI, 1967-06-24), en) | 8 | 40% | 62% | 3 | — |
| Ut Unum Sint (Vatican English text (John Paul II, 1995-05-25), en) | 4 | 100% | 50% | 2 | — |
| Veritatis Splendor (Vatican English text (John Paul II, 1993-08-06), en) | 4 | 100% | 50% | 2 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gemini-flash | 120 | 16,678 | 25,855 |
| **total** | 120 | 16,678 | 25,855 |
