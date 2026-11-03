| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| luna | 33% cov 100% (n=30; c/i/r 10/20/0; minor/major 0/20) | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 6/24) | 0% cov 93% (n=30; c/i/r 0/28/2; minor/major 2/26) | 63% cov 100% (n=30; c/i/r 19/11/0; minor/major 0/11) | **25%** cov 98% (c/i/r 29/89/2; minor/major 8/81) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| luna | cite_passage | 20 | 0 | 20 | wrong_locus 20 |
| luna | complete_unit | 30 | 6 | 24 | near_copy 1, paraphrase 3, wrong_passage 24, omission 2 |
| luna | retrieve_quote | 28 | 2 | 26 | paraphrase 2, wrong_passage 26 |
| luna | verify_source | 11 | 0 | 11 | wrong_verdict 11 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| luna | Encyclicals | 33% cov 100% (n=30; c/i/r 10/20/0) | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 93% (n=30; c/i/r 0/28/2) | 63% cov 100% (n=30; c/i/r 19/11/0) | **25%** cov 98% (n=120; c/i/r 29/89/2) |

### By text (one text = one work · version · language)

**luna**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Ad Petri Cathedram (Vatican English text (John XXIII, 1959-06-29), en) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| Aeterni Patris (Vatican English text (Leo XIII, 1879-08-04), en) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| Augustissimae Virginis Mariae (Vatican English text (Leo XIII, 1897-09-12), en) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| Casti Connubii (Vatican English text (Pius XI, 1930-12-31), en) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| Christi Matri (Vatican English text (Paul VI, 1966-09-15), en) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| Communium Rerum (Vatican English text (Pius X, 1909-04-21), en) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| Depuis le Jour (Vatican English text (Leo XIII, 1899-09-08), en) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| Deus caritas est (Vatican English text (Benedict XVI, 2005-12-25), en) | 8 | 50% | 100% | 0 | — | 2 | 2 | near_copy 1, paraphrase 1, wrong_passage 2 |
| Dominum et vivificantem (Vatican English text (John Paul II, 1986-05-18), en) | 4 | 50% | 100% | 0 | — | 0 | 2 | wrong_passage 2 |
| Ecclesiam Suam (Vatican English text (Paul VI, 1964-08-06), en) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| Fides et Ratio (Vatican English text (John Paul II, 1998-09-14), en) | 4 | 50% | 100% | 0 | — | 0 | 2 | wrong_passage 2 |
| Fratelli tutti (Vatican English text (Francis, 2020-10-03), en) | 8 | 38% | 100% | 0 | — | 2 | 3 | paraphrase 1, wrong_passage 2, omission 1, wrong_locus 1 |
| Laudato si' (Vatican English text (Francis, 2015-05-24), en) | 4 | 50% | 100% | 0 | — | 1 | 1 | paraphrase 1, wrong_passage 1 |
| Meminisse Iuvat (Vatican English text (Pius XII, 1958-07-14), en) | 4 | 0% | 100% | 0 | — | 1 | 3 | paraphrase 1, wrong_passage 1, wrong_locus 1, wrong_verdict 1 |
| Musicae Sacrae (Vatican English text (Pius XII, 1955-12-25), en) | 4 | 0% | 100% | 0 | — | 0 | 4 | wrong_passage 2, wrong_locus 1, wrong_verdict 1 |
| Mysterium Fidei (Vatican English text (Paul VI, 1965-09-03), en) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| Non Abbiamo Bisogno (Vatican English text (Pius XI, 1931-06-29), en) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_locus 1 |
| Octobri Mense (Vatican English text (Leo XIII, 1891-09-22), en) | 4 | 0% | 100% | 0 | — | 0 | 4 | wrong_passage 2, wrong_locus 1, wrong_verdict 1 |
| Orientales Omnes Ecclesias (Vatican English text (Pius XII, 1945-12-23), en) | 4 | 0% | 100% | 0 | — | 0 | 4 | wrong_passage 2, wrong_locus 1, wrong_verdict 1 |
| Quadragesimo Anno (Vatican English text (Pius XI, 1931-05-15), en) | 8 | 12% | 100% | 0 | — | 0 | 7 | wrong_passage 4, wrong_locus 2, wrong_verdict 1 |
| Quod Anniversarius (Vatican English text (Leo XIII, 1888-04-01), en) | 4 | 0% | 75% | 1 | — | 0 | 3 | wrong_passage 1, wrong_locus 1, wrong_verdict 1 |
| Quod Multum (Vatican English text (Leo XIII, 1886-08-22), en) | 4 | 0% | 75% | 1 | — | 0 | 3 | wrong_passage 1, wrong_locus 1, wrong_verdict 1 |
| Redemptoris Mater (Vatican English text (John Paul II, 1987-03-25), en) | 4 | 50% | 100% | 0 | — | 1 | 1 | wrong_passage 1, omission 1 |
| Sacerdotalis Caelibatus (Vatican English text (Paul VI, 1967-06-24), en) | 8 | 12% | 100% | 0 | — | 0 | 7 | wrong_passage 4, wrong_locus 1, wrong_verdict 2 |
| Ut Unum Sint (Vatican English text (John Paul II, 1995-05-25), en) | 4 | 25% | 100% | 0 | — | 0 | 3 | wrong_passage 2, wrong_verdict 1 |
| Veritatis Splendor (Vatican English text (John Paul II, 1993-08-06), en) | 4 | 25% | 100% | 0 | — | 1 | 2 | paraphrase 1, wrong_passage 1, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| luna | 120 | 17,055 | 8,154 |
| **total** | 120 | 17,055 | 8,154 |
