| model | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|
| gpt-oss-20b | 0% cov 100% (n=30; c/i/r 0/30/0; minor/major 0/30) | 0% cov 90% (n=30; c/i/r 0/27/3; minor/major 3/24) | 0% cov 3% (n=30; c/i/r 0/1/29; minor/major 0/1) | 50% cov 100% (n=30; c/i/r 15/15/0; minor/major 0/15) | **17%** cov 73% (c/i/r 15/73/32; minor/major 3/70) |

_Cells: accuracy cov coverage (n answered; c/i/r = correct/incorrect/refused). accuracy = correct/(correct+incorrect) — refusals excluded; coverage = (correct+incorrect)/n; refused_rate = refused/n. `−N` = roster cells that produced no answer (distinct from refused). minor/major splits incorrect by failure kind: minor stays on the passage asked for, major replaces it._

### Failure kinds (per task)
| model | task | incorrect | minor | major | kinds |
|---|---|---|---|---|---|
| gpt-oss-20b | cite_passage | 30 | 0 | 30 | wrong_locus 27, no_citation 3 |
| gpt-oss-20b | complete_unit | 27 | 3 | 24 | paraphrase 1, wrong_passage 24, omission 2 |
| gpt-oss-20b | retrieve_quote | 1 | 0 | 1 | wrong_passage 1 |
| gpt-oss-20b | verify_source | 15 | 0 | 15 | wrong_verdict 15 |

_A near copy (token-F1 ≥ 0.85) is split by base-letter token edits: diacritic_only (none — only vowel signs, accents or pointing differ), edition_variant (1–2 tokens — another edition or spelling), near_copy (more). addition is a correct quote that runs past the reference._

### By tradition (each observation counts once per listed tradition)
| model | tradition | cite_passage | complete_unit | retrieve_quote | verify_source | overall |
|---|---|---|---|---|---|---|
| gpt-oss-20b | Encyclicals | 0% cov 100% (n=30; c/i/r 0/30/0) | 0% cov 90% (n=30; c/i/r 0/27/3) | 0% cov 3% (n=30; c/i/r 0/1/29) | 50% cov 100% (n=30; c/i/r 15/15/0) | **17%** cov 73% (n=120; c/i/r 15/73/32) |

### By text (one text = one work · version · language)

**gpt-oss-20b**
| text | n | accuracy | coverage | refused | missing | minor | major | kinds |
|---|---|---|---|---|---|---|---|---|
| Ad Petri Cathedram (Vatican English text (John XXIII, 1959-06-29), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Aeterni Patris (Vatican English text (Leo XIII, 1879-08-04), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Augustissimae Virginis Mariae (Vatican English text (Leo XIII, 1897-09-12), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Casti Connubii (Vatican English text (Pius XI, 1930-12-31), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Christi Matri (Vatican English text (Paul VI, 1966-09-15), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Communium Rerum (Vatican English text (Pius X, 1909-04-21), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Depuis le Jour (Vatican English text (Leo XIII, 1899-09-08), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Deus caritas est (Vatican English text (Benedict XVI, 2005-12-25), en) | 8 | 40% | 62% | 3 | — | 0 | 3 | wrong_passage 1, wrong_locus 1, no_citation 1 |
| Dominum et vivificantem (Vatican English text (John Paul II, 1986-05-18), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Ecclesiam Suam (Vatican English text (Paul VI, 1964-08-06), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Fides et Ratio (Vatican English text (John Paul II, 1998-09-14), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, wrong_locus 1 |
| Fratelli tutti (Vatican English text (Francis, 2020-10-03), en) | 8 | 40% | 62% | 3 | — | 0 | 3 | wrong_passage 1, wrong_locus 1, no_citation 1 |
| Laudato si' (Vatican English text (Francis, 2015-05-24), en) | 4 | 33% | 75% | 1 | — | 0 | 2 | wrong_passage 1, no_citation 1 |
| Meminisse Iuvat (Vatican English text (Pius XII, 1958-07-14), en) | 4 | 0% | 75% | 1 | — | 0 | 3 | wrong_passage 1, wrong_locus 1, wrong_verdict 1 |
| Musicae Sacrae (Vatican English text (Pius XII, 1955-12-25), en) | 4 | 0% | 50% | 2 | — | 0 | 2 | wrong_locus 1, wrong_verdict 1 |
| Mysterium Fidei (Vatican English text (Paul VI, 1965-09-03), en) | 4 | 0% | 75% | 1 | — | 0 | 3 | wrong_passage 1, wrong_locus 1, wrong_verdict 1 |
| Non Abbiamo Bisogno (Vatican English text (Pius XI, 1931-06-29), en) | 4 | 0% | 75% | 1 | — | 0 | 3 | wrong_passage 1, wrong_locus 1, wrong_verdict 1 |
| Octobri Mense (Vatican English text (Leo XIII, 1891-09-22), en) | 4 | 0% | 75% | 1 | — | 0 | 3 | wrong_passage 1, wrong_locus 1, wrong_verdict 1 |
| Orientales Omnes Ecclesias (Vatican English text (Pius XII, 1945-12-23), en) | 4 | 0% | 75% | 1 | — | 0 | 3 | wrong_passage 1, wrong_locus 1, wrong_verdict 1 |
| Quadragesimo Anno (Vatican English text (Pius XI, 1931-05-15), en) | 8 | 0% | 75% | 2 | — | 0 | 6 | wrong_passage 2, wrong_locus 2, wrong_verdict 2 |
| Quod Anniversarius (Vatican English text (Leo XIII, 1888-04-01), en) | 4 | 0% | 75% | 1 | — | 1 | 2 | paraphrase 1, wrong_locus 1, wrong_verdict 1 |
| Quod Multum (Vatican English text (Leo XIII, 1886-08-22), en) | 4 | 0% | 75% | 1 | — | 0 | 3 | wrong_passage 1, wrong_locus 1, wrong_verdict 1 |
| Redemptoris Mater (Vatican English text (John Paul II, 1987-03-25), en) | 4 | 0% | 75% | 1 | — | 1 | 2 | omission 1, wrong_locus 1, wrong_verdict 1 |
| Sacerdotalis Caelibatus (Vatican English text (Paul VI, 1967-06-24), en) | 8 | 0% | 75% | 2 | — | 0 | 6 | wrong_passage 2, wrong_locus 2, wrong_verdict 2 |
| Ut Unum Sint (Vatican English text (John Paul II, 1995-05-25), en) | 4 | 0% | 75% | 1 | — | 0 | 3 | wrong_passage 1, wrong_locus 1, wrong_verdict 1 |
| Veritatis Splendor (Vatican English text (John Paul II, 1993-08-06), en) | 4 | 0% | 100% | 0 | — | 1 | 3 | wrong_passage 1, omission 1, wrong_locus 1, wrong_verdict 1 |

### Token usage
| model_id | calls | in | out |
|---|---|---|---|
| gpt-oss-20b | 120 | 24,598 | 8,339 |
| **total** | 120 | 24,598 | 8,339 |
