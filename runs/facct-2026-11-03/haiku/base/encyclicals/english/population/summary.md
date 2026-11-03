| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| haiku | 40% cov 50% (n=30; c/i/r 6/9/15; minor/major 0/9) | 0% cov 37% (n=30; c/i/r 0/11/19; minor/major 1/10) | n/a cov 0% (n=30; c/i/r 0/0/30; minor/major 0/0) | 82% cov 57% (n=30; c/i/r 14/3/13; minor/major 0/3) | **47%** cov 36% (c/i/r 20/23/77; minor/major 1/22) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| haiku | cite_passage | 9 | 0 | 9 | wrong_locus 9 |
| haiku | complete_unit | 11 | 1 | 10 | wrong_passage 10, omission 1 |
| haiku | verify_source | 3 | 0 | 3 | wrong_verdict 3 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| haiku | Encyclicals | 40% cov 50% (n=30; c/i/r 6/9/15) | 0% cov 37% (n=30; c/i/r 0/11/19) | n/a cov 0% (n=30; c/i/r 0/0/30) | 82% cov 57% (n=30; c/i/r 14/3/13) | **47%** cov 36% (n=120; c/i/r 20/23/77) |

### By text (one text = one work · version · language)

**haiku**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Ad Petri Cathedram (Vatican English text (John XXIII, 1959-06-29), en) | 4 | 100% | 25% | 3 | — | 0 | 0 | — |
| Aeterni Patris (Vatican English text (Leo XIII, 1879-08-04), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Augustissimae Virginis Mariae (Vatican English text (Leo XIII, 1897-09-12), en) | 4 | 100% | 25% | 3 | — | 0 | 0 | — |
| Casti Connubii (Vatican English text (Pius XI, 1930-12-31), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Christi Matri (Vatican English text (Paul VI, 1966-09-15), en) | 4 | 100% | 25% | 3 | — | 0 | 0 | — |
| Communium Rerum (Vatican English text (Pius X, 1909-04-21), en) | 4 | 100% | 25% | 3 | — | 0 | 0 | — |
| Depuis le Jour (Vatican English text (Leo XIII, 1899-09-08), en) | 4 | n/a | 0% | 4 | — | 0 | 0 | — |
| Deus caritas est (Vatican English text (Benedict XVI, 2005-12-25), en) | 8 | 67% | 75% | 2 | — | 0 | 2 | wrong_passage 2 |
| Dominum et vivificantem (Vatican English text (John Paul II, 1986-05-18), en) | 4 | 50% | 50% | 2 | — | 0 | 1 | wrong_passage 1 |
| Ecclesiam Suam (Vatican English text (Paul VI, 1964-08-06), en) | 4 | 0% | 25% | 3 | — | 0 | 1 | wrong_locus 1 |
| Fides et Ratio (Vatican English text (John Paul II, 1998-09-14), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Fratelli tutti (Vatican English text (Francis, 2020-10-03), en) | 8 | 100% | 38% | 5 | — | 0 | 0 | — |
| Laudato si' (Vatican English text (Francis, 2015-05-24), en) | 4 | 100% | 50% | 2 | — | 0 | 0 | — |
| Meminisse Iuvat (Vatican English text (Pius XII, 1958-07-14), en) | 4 | 0% | 25% | 3 | — | 0 | 1 | wrong_locus 1 |
| Musicae Sacrae (Vatican English text (Pius XII, 1955-12-25), en) | 4 | 0% | 25% | 3 | — | 0 | 1 | wrong_locus 1 |
| Mysterium Fidei (Vatican English text (Paul VI, 1965-09-03), en) | 4 | 0% | 50% | 2 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Non Abbiamo Bisogno (Vatican English text (Pius XI, 1931-06-29), en) | 4 | n/a | 0% | 4 | — | 0 | 0 | — |
| Octobri Mense (Vatican English text (Leo XIII, 1891-09-22), en) | 4 | 0% | 25% | 3 | — | 0 | 1 | wrong_locus 1 |
| Orientales Omnes Ecclesias (Vatican English text (Pius XII, 1945-12-23), en) | 4 | n/a | 0% | 4 | — | 0 | 0 | — |
| Quadragesimo Anno (Vatican English text (Pius XI, 1931-05-15), en) | 8 | 0% | 38% | 5 | — | 0 | 3 | wrong_passage 1, wrong_locus 1, wrong_verdict 1 |
| Quod Anniversarius (Vatican English text (Leo XIII, 1888-04-01), en) | 4 | n/a | 0% | 4 | — | 0 | 0 | — |
| Quod Multum (Vatican English text (Leo XIII, 1886-08-22), en) | 4 | 0% | 25% | 3 | — | 0 | 1 | wrong_verdict 1 |
| Redemptoris Mater (Vatican English text (John Paul II, 1987-03-25), en) | 4 | 50% | 50% | 2 | — | 1 | 0 | omission 1 |
| Sacerdotalis Caelibatus (Vatican English text (Paul VI, 1967-06-24), en) | 8 | 0% | 12% | 7 | — | 0 | 1 | wrong_verdict 1 |
| Ut Unum Sint (Vatican English text (John Paul II, 1995-05-25), en) | 4 | 0% | 25% | 3 | — | 0 | 1 | wrong_passage 1 |
| Veritatis Splendor (Vatican English text (John Paul II, 1993-08-06), en) | 4 | 67% | 75% | 1 | — | 0 | 1 | wrong_passage 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| haiku | 120 | 25,213 | 15,540 |
| **total** | 120 | 25,213 | 15,540 |
