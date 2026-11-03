| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| fable | 50% cov 100% (n=30; c/i/r 15/15/0; minor/major 0/15) | 23% cov 100% (n=30; c/i/r 7/23/0; minor/major 12/11) | 12% cov 53% (n=30; c/i/r 2/14/14; minor/major 9/5) | 87% cov 100% (n=30; c/i/r 26/4/0; minor/major 0/4) | **47%** cov 88% (c/i/r 50/56/14; minor/major 21/35) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| fable | cite_passage | 15 | 0 | 15 | wrong_locus 15 |
| fable | complete_unit | 23 | 12 | 11 | edition_variant 1, near_copy 4, paraphrase 4, wrong_passage 11, omission 3 |
| fable | retrieve_quote | 14 | 9 | 5 | near_copy 6, paraphrase 2, wrong_passage 5, omission 1 |
| fable | verify_source | 4 | 0 | 4 | wrong_verdict 4 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| fable | Encyclicals | 50% cov 100% (n=30; c/i/r 15/15/0) | 23% cov 100% (n=30; c/i/r 7/23/0) | 12% cov 53% (n=30; c/i/r 2/14/14) | 87% cov 100% (n=30; c/i/r 26/4/0) | **47%** cov 88% (n=120; c/i/r 50/56/14) |

### By text (one text = one work · version · language)

**fable**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Ad Petri Cathedram (Vatican English text (John XXIII, 1959-06-29), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Aeterni Patris (Vatican English text (Leo XIII, 1879-08-04), en) | 4 | 25% | 100% | 0 | — | 2 | 1 | near_copy 1, paraphrase 1, wrong_locus 1 |
| Augustissimae Virginis Mariae (Vatican English text (Leo XIII, 1897-09-12), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Casti Connubii (Vatican English text (Pius XI, 1930-12-31), en) | 4 | 50% | 100% | 0 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Christi Matri (Vatican English text (Paul VI, 1966-09-15), en) | 4 | 67% | 75% | 1 | — | 0 | 1 | wrong_passage 1 |
| Communium Rerum (Vatican English text (Pius X, 1909-04-21), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Depuis le Jour (Vatican English text (Leo XIII, 1899-09-08), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Deus caritas est (Vatican English text (Benedict XVI, 2005-12-25), en) | 8 | 75% | 100% | 0 | — | 2 | 0 | near_copy 1, omission 1 |
| Dominum et vivificantem (Vatican English text (John Paul II, 1986-05-18), en) | 4 | 67% | 75% | 1 | — | 1 | 0 | near_copy 1 |
| Ecclesiam Suam (Vatican English text (Paul VI, 1964-08-06), en) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| Fides et Ratio (Vatican English text (John Paul II, 1998-09-14), en) | 4 | 75% | 100% | 0 | — | 1 | 0 | near_copy 1 |
| Fratelli tutti (Vatican English text (Francis, 2020-10-03), en) | 8 | 62% | 100% | 0 | — | 3 | 0 | near_copy 2, omission 1 |
| Laudato si' (Vatican English text (Francis, 2015-05-24), en) | 4 | 100% | 100% | 0 | — | 0 | 0 | — |
| Meminisse Iuvat (Vatican English text (Pius XII, 1958-07-14), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Musicae Sacrae (Vatican English text (Pius XII, 1955-12-25), en) | 4 | 33% | 75% | 1 | — | 1 | 1 | paraphrase 1, wrong_locus 1 |
| Mysterium Fidei (Vatican English text (Paul VI, 1965-09-03), en) | 4 | 50% | 100% | 0 | — | 1 | 1 | edition_variant 1, wrong_passage 1 |
| Non Abbiamo Bisogno (Vatican English text (Pius XI, 1931-06-29), en) | 4 | 0% | 75% | 1 | — | 0 | 3 | wrong_passage 1, wrong_locus 1, wrong_verdict 1 |
| Octobri Mense (Vatican English text (Leo XIII, 1891-09-22), en) | 4 | 50% | 100% | 0 | — | 0 | 2 | wrong_passage 2 |
| Orientales Omnes Ecclesias (Vatican English text (Pius XII, 1945-12-23), en) | 4 | 0% | 75% | 1 | — | 0 | 3 | wrong_passage 1, wrong_locus 1, wrong_verdict 1 |
| Quadragesimo Anno (Vatican English text (Pius XI, 1931-05-15), en) | 8 | 43% | 88% | 1 | — | 2 | 2 | near_copy 1, paraphrase 1, wrong_locus 1, wrong_verdict 1 |
| Quod Anniversarius (Vatican English text (Leo XIII, 1888-04-01), en) | 4 | 0% | 75% | 1 | — | 1 | 2 | paraphrase 1, wrong_locus 1, wrong_verdict 1 |
| Quod Multum (Vatican English text (Leo XIII, 1886-08-22), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Redemptoris Mater (Vatican English text (John Paul II, 1987-03-25), en) | 4 | 50% | 100% | 0 | — | 2 | 0 | paraphrase 1, omission 1 |
| Sacerdotalis Caelibatus (Vatican English text (Paul VI, 1967-06-24), en) | 8 | 57% | 88% | 1 | — | 2 | 1 | near_copy 2, wrong_locus 1 |
| Ut Unum Sint (Vatican English text (John Paul II, 1995-05-25), en) | 4 | 50% | 100% | 0 | — | 1 | 1 | paraphrase 1, wrong_passage 1 |
| Veritatis Splendor (Vatican English text (John Paul II, 1993-08-06), en) | 4 | 50% | 100% | 0 | — | 2 | 0 | near_copy 1, omission 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| fable | 120 | 25,453 | 48,354 |
| **total** | 120 | 25,453 | 48,354 |
