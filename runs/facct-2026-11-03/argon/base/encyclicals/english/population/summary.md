| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| argon | 57% cov 100% (n=30; c/i/r 17/13/0; minor/major 0/13) | 52% cov 97% (n=30; c/i/r 15/14/1; minor/major 4/10) | 0% cov 7% (n=30; c/i/r 0/2/28; minor/major 0/2) | 100% cov 100% (n=30; c/i/r 30/0/0; minor/major 0/0) | **68%** cov 76% (c/i/r 62/29/29; minor/major 4/25) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| argon | cite_passage | 13 | 0 | 13 | wrong_locus 13 |
| argon | complete_unit | 14 | 4 | 10 | edition_variant 1, paraphrase 3, wrong_passage 10, addition 1 |
| argon | retrieve_quote | 2 | 0 | 2 | wrong_passage 2 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| argon | Encyclicals | 57% cov 100% (n=30; c/i/r 17/13/0) | 52% cov 97% (n=30; c/i/r 15/14/1) | 0% cov 7% (n=30; c/i/r 0/2/28) | 100% cov 100% (n=30; c/i/r 30/0/0) | **68%** cov 76% (n=120; c/i/r 62/29/29) |

### By text (one text = one work · version · language)

**argon**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Ad Petri Cathedram (Vatican English text (John XXIII, 1959-06-29), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Aeterni Patris (Vatican English text (Leo XIII, 1879-08-04), en) | 4 | 67% | 75% | 1 | — | 1 | 0 | paraphrase 1 |
| Augustissimae Virginis Mariae (Vatican English text (Leo XIII, 1897-09-12), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Casti Connubii (Vatican English text (Pius XI, 1930-12-31), en) | 4 | 100% | 75% | 1 | — | 0 | 0 | — |
| Christi Matri (Vatican English text (Paul VI, 1966-09-15), en) | 4 | 67% | 75% | 1 | — | 0 | 1 | wrong_passage 1 |
| Communium Rerum (Vatican English text (Pius X, 1909-04-21), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Depuis le Jour (Vatican English text (Leo XIII, 1899-09-08), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Deus caritas est (Vatican English text (Benedict XVI, 2005-12-25), en) | 8 | 100% | 75% | 2 | — | 0 | 0 | — |
| Dominum et vivificantem (Vatican English text (John Paul II, 1986-05-18), en) | 4 | 100% | 75% | 1 | — | 0 | 0 | — |
| Ecclesiam Suam (Vatican English text (Paul VI, 1964-08-06), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Fides et Ratio (Vatican English text (John Paul II, 1998-09-14), en) | 4 | 100% | 75% | 1 | — | 0 | 0 | — |
| Fratelli tutti (Vatican English text (Francis, 2020-10-03), en) | 8 | 100% | 75% | 2 | — | 0 | 0 | — |
| Laudato si' (Vatican English text (Francis, 2015-05-24), en) | 4 | 100% | 75% | 1 | — | 0 | 0 | — |
| Meminisse Iuvat (Vatican English text (Pius XII, 1958-07-14), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Musicae Sacrae (Vatican English text (Pius XII, 1955-12-25), en) | 4 | 67% | 75% | 1 | — | 0 | 1 | wrong_locus 1 |
| Mysterium Fidei (Vatican English text (Paul VI, 1965-09-03), en) | 4 | 100% | 75% | 1 | — | 0 | 0 | — |
| Non Abbiamo Bisogno (Vatican English text (Pius XI, 1931-06-29), en) | 4 | 33% | 75% | 1 | — | 1 | 1 | paraphrase 1, wrong_locus 1 |
| Octobri Mense (Vatican English text (Leo XIII, 1891-09-22), en) | 4 | 67% | 75% | 1 | — | 0 | 1 | wrong_passage 1 |
| Orientales Omnes Ecclesias (Vatican English text (Pius XII, 1945-12-23), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Quadragesimo Anno (Vatican English text (Pius XI, 1931-05-15), en) | 8 | 50% | 100% | 0 | — | 1 | 3 | paraphrase 1, wrong_passage 2, wrong_locus 1 |
| Quod Anniversarius (Vatican English text (Leo XIII, 1888-04-01), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Quod Multum (Vatican English text (Leo XIII, 1886-08-22), en) | 4 | 50% | 50% | 2 | — | 0 | 1 | wrong_locus 1 |
| Redemptoris Mater (Vatican English text (John Paul II, 1987-03-25), en) | 4 | 100% | 75% | 1 | — | 0 | 0 | — |
| Sacerdotalis Caelibatus (Vatican English text (Paul VI, 1967-06-24), en) | 8 | 67% | 75% | 2 | — | 1 | 1 | edition_variant 1, wrong_locus 1 |
| Ut Unum Sint (Vatican English text (John Paul II, 1995-05-25), en) | 4 | 100% | 75% | 1 | — | 0 | 0 | addition 1 |
| Veritatis Splendor (Vatican English text (John Paul II, 1993-08-06), en) | 4 | 100% | 75% | 1 | — | 0 | 0 | — |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| argon | 120 | 20,457 | 5,614 |
| **total** | 120 | 20,457 | 5,614 |
