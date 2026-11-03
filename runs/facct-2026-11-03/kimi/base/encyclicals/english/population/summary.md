| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| kimi | 30% cov 100% (n=30; c/i/r 9/21/0; minor/major 0/21) | 13% cov 100% (n=30; c/i/r 4/26/0; minor/major 9/17) | 8% cov 83% (n=30; c/i/r 2/23/5; minor/major 3/20) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **39%** cov 96% (c/i/r 45/70/5; minor/major 12/58) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| kimi | cite_passage | 21 | 0 | 21 | wrong_locus 21 |
| kimi | complete_unit | 26 | 9 | 17 | edition_variant 2, paraphrase 3, wrong_passage 17, omission 4 |
| kimi | retrieve_quote | 23 | 3 | 20 | edition_variant 1, paraphrase 2, wrong_passage 20 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| kimi | Encyclicals | 30% cov 100% (n=30; c/i/r 9/21/0) | 13% cov 100% (n=30; c/i/r 4/26/0) | 8% cov 83% (n=30; c/i/r 2/23/5) | 100% cov 100% (n=30; c/i/r 30/0/0) | **39%** cov 96% (n=120; c/i/r 45/70/5) |

### By text (one text = one work · version · language)

**kimi**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Ad Petri Cathedram (Vatican English text (John XXIII, 1959-06-29), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Aeterni Patris (Vatican English text (Leo XIII, 1879-08-04), en) | 4 | 25% | 100% | 0 | — | 1 | 2 | paraphrase 1, wrong_passage 1, wrong_locus 1 |
| Augustissimae Virginis Mariae (Vatican English text (Leo XIII, 1897-09-12), en) | 4 | 50% | 100% | 0 | — | 0 | 2 | wrong_passage 2 |
| Casti Connubii (Vatican English text (Pius XI, 1930-12-31), en) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| Christi Matri (Vatican English text (Paul VI, 1966-09-15), en) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| Communium Rerum (Vatican English text (Pius X, 1909-04-21), en) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| Depuis le Jour (Vatican English text (Leo XIII, 1899-09-08), en) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| Deus caritas est (Vatican English text (Benedict XVI, 2005-12-25), en) | 8 | 88% | 100% | 0 | — | 1 | 0 | omission 1 |
| Dominum et vivificantem (Vatican English text (John Paul II, 1986-05-18), en) | 4 | 25% | 100% | 0 | — | 1 | 2 | paraphrase 1, wrong_passage 1, wrong_locus 1 |
| Ecclesiam Suam (Vatican English text (Paul VI, 1964-08-06), en) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| Fides et Ratio (Vatican English text (John Paul II, 1998-09-14), en) | 4 | 50% | 100% | 0 | — | 0 | 2 | wrong_passage 2 |
| Fratelli tutti (Vatican English text (Francis, 2020-10-03), en) | 8 | 62% | 100% | 0 | — | 2 | 1 | edition_variant 1, wrong_passage 1, omission 1 |
| Laudato si' (Vatican English text (Francis, 2015-05-24), en) | 4 | 100% | 75% | 1 | — | 0 | 0 | — |
| Meminisse Iuvat (Vatican English text (Pius XII, 1958-07-14), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Musicae Sacrae (Vatican English text (Pius XII, 1955-12-25), en) | 4 | 50% | 100% | 0 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Mysterium Fidei (Vatican English text (Paul VI, 1965-09-03), en) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| Non Abbiamo Bisogno (Vatican English text (Pius XI, 1931-06-29), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Octobri Mense (Vatican English text (Leo XIII, 1891-09-22), en) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| Orientales Omnes Ecclesias (Vatican English text (Pius XII, 1945-12-23), en) | 4 | 33% | 75% | 1 | — | 1 | 1 | paraphrase 1, wrong_locus 1 |
| Quadragesimo Anno (Vatican English text (Pius XI, 1931-05-15), en) | 8 | 25% | 100% | 0 | — | 1 | 5 | wrong_passage 3, omission 1, wrong_locus 2 |
| Quod Anniversarius (Vatican English text (Leo XIII, 1888-04-01), en) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| Quod Multum (Vatican English text (Leo XIII, 1886-08-22), en) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| Redemptoris Mater (Vatican English text (John Paul II, 1987-03-25), en) | 4 | 50% | 100% | 0 | — | 1 | 1 | edition_variant 1, wrong_passage 1 |
| Sacerdotalis Caelibatus (Vatican English text (Paul VI, 1967-06-24), en) | 8 | 25% | 100% | 0 | — | 1 | 5 | wrong_passage 3, omission 1, wrong_locus 2 |
| Ut Unum Sint (Vatican English text (John Paul II, 1995-05-25), en) | 4 | 25% | 100% | 0 | — | 1 | 2 | paraphrase 1, wrong_passage 1, wrong_locus 1 |
| Veritatis Splendor (Vatican English text (John Paul II, 1993-08-06), en) | 4 | 50% | 100% | 0 | — | 2 | 0 | edition_variant 1, paraphrase 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| kimi | 120 | 18,794 | 16,091 |
| **total** | 120 | 18,794 | 16,091 |
