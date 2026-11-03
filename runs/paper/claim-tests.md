# Paired claims

From 32637 scored cells across 16 models in `runs/facct-2026-11-03`. A file still being collected contributes only the cells it already has. Accuracy comparisons drop refusals. McNemar is the two-sided exact test on discordant pairs of the same citation. Fisher exact compares two independent answered sets.

## Citation, English prompt against native prompt

English-only means the English prompt was correct and the native prompt was not. Native-only is the reverse.

| model | English only | native only | pairs | p |
|---|---:|---:|---:|---:|
| deepseek-v4-pro | 18 | 7 | 25 | 0.043 |
| fable | 13 | 9 | 22 | 0.523 |

## Quote against cite

Quote-only means the quotation was correct and the citation was not, on the same citation, both answered.

| model | quote only | cite only | pairs | p |
|---|---:|---:|---:|---:|
| terra | 3 | 175 | 178 | 4.91e-48 |
| luna | 1 | 161 | 162 | 5.58e-47 |
| deepseek-v4-pro | 13 | 186 | 199 | 2.21e-40 |
| kimi | 7 | 164 | 171 | 5.23e-40 |
| argon | 0 | 127 | 127 | 1.18e-38 |
| gemini-flash | 6 | 146 | 152 | 5.66e-36 |
| beam | 5 | 141 | 146 | 1.20e-35 |
| gemma-31b | 0 | 102 | 102 | 3.94e-31 |
| astra | 1 | 85 | 86 | 2.25e-24 |
| sol | 1 | 85 | 86 | 2.25e-24 |
| qwen3-32b | 0 | 79 | 79 | 3.31e-24 |
| opus | 3 | 73 | 76 | 1.94e-18 |
| haiku | 3 | 67 | 70 | 9.69e-17 |
| fable | 20 | 105 | 125 | 4.13e-15 |
| sonnet | 18 | 75 | 93 | 1.92e-09 |

## Verify, real passage against a fake

| model | real yes | not this edition | p |
|---|---:|---:|---:|
| argon | 255/257 | 251/252 | 1.000 |
| astra | 241/257 | 249/253 | 0.010 |
| beam | 217/255 | 245/253 | 3.59e-06 |
| deepseek-v4-pro | 177/257 | 248/253 | 3.21e-21 |
| fable | 222/238 | 241/241 | 1.06e-05 |
| gemini-flash | 241/257 | 251/253 | 0.001 |
| gemma-31b | 158/249 | 241/249 | 1.09e-22 |
| gpt-oss-20b | 31/248 | 251/253 | 2.13e-104 |
| haiku | 131/183 | 207/207 | 9.25e-20 |
| kimi | 222/256 | 248/252 | 2.45e-07 |
| luna | 165/256 | 244/248 | 8.91e-26 |
| opus | 231/257 | 251/253 | 1.74e-06 |
| qwen3-32b | 159/233 | 212/236 | 7.54e-09 |
| sol | 238/257 | 248/253 | 0.005 |
| sonnet | 87/163 | 217/217 | 2.58e-34 |
| terra | 230/257 | 251/253 | 8.86e-07 |

## What a correct no is actually testing

Different script is an alphabet check (Gurmukhi, Pali, Sanskrit, Greek). The other rows are same-script judgments.

| negative | correct | wrong | refused |
|---|---:|---:|---:|
| Talmud shown the Bible | 650/685 | 35 | 35 |
| Qur'an shown a hadith | 687/708 | 21 | 12 |
| Encyclical shown the Book of Mormon | 232/237 | 5 | 3 |
| Other same-script negative | 549/556 | 7 | 4 |
| NRSV shown the Book of Mormon | 238/239 | 1 | 1 |
| Different script | 1259/1261 | 2 | 67 |
| Book of Mormon shown an encyclical | 240/240 | 0 | 0 |

## Book of Mormon against encyclicals

Answered cells only. A model that refuses most of both sets can show a large gap in coverage and a small, non-significant gap here.

| model | Book of Mormon | Encyclicals | p |
|---|---:|---:|---:|
| argon | 102/120 | 51/91 | 4.56e-06 |
| astra | 112/120 | 44/72 | 5.98e-08 |
| beam | 63/99 | 34/93 | 2.84e-04 |
| deepseek-v4-pro | 57/120 | 36/119 | 0.008 |
| fable | 91/117 | 50/106 | 3.55e-06 |
| gemini-flash | 93/116 | 44/84 | 5.02e-05 |
| gemma-31b | 24/120 | 26/120 | 0.874 |
| gpt-oss-20b | 15/109 | 15/88 | 0.554 |
| haiku | 32/62 | 20/43 | 0.693 |
| kimi | 83/118 | 45/115 | 1.92e-06 |
| luna | 49/119 | 29/118 | 0.008 |
| opus | 105/119 | 48/88 | 6.37e-08 |
| qwen3-32b | 27/120 | 26/120 | 1.000 |
| sol | 110/120 | 45/75 | 2.76e-07 |
| sonnet | 48/98 | 29/59 | 1.000 |
| terra | 81/120 | 38/119 | 4.29e-08 |
