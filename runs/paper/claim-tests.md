# Paired claims

From 27264 scored cells across 16 models. A file still being collected contributes only the cells it already has. Accuracy comparisons drop refusals. McNemar is the two-sided exact test on discordant pairs of the same citation. Fisher exact compares two independent answered sets.

## Citation, English prompt against native prompt

English-only means the English prompt was correct and the native prompt was not. Native-only is the reverse.

| model | English only | native only | pairs | p |
|---|---:|---:|---:|---:|
| opus | 1 | 91 | 92 | 3.76e-26 |
| gemini-flash | 3 | 89 | 92 | 5.24e-23 |
| sonnet | 1 | 77 | 78 | 5.23e-22 |
| kimi | 0 | 68 | 68 | 6.78e-21 |
| terra | 1 | 73 | 74 | 7.94e-21 |
| astra | 0 | 66 | 66 | 2.71e-20 |
| sol | 1 | 64 | 65 | 3.58e-18 |
| argon | 1 | 48 | 49 | 1.78e-13 |
| fable | 0 | 29 | 29 | 3.73e-09 |
| luna | 21 | 5 | 26 | 0.002 |
| deepseek-v4-pro | 9 | 28 | 37 | 0.003 |
| haiku | 31 | 30 | 61 | 1.000 |

## Quote against cite

Quote-only means the quotation was correct and the citation was not, on the same citation, both answered.

| model | quote only | cite only | pairs | p |
|---|---:|---:|---:|---:|
| luna | 9 | 194 | 203 | 2.20e-46 |
| beam | 2 | 127 | 129 | 2.46e-35 |
| gemma-31b | 0 | 84 | 84 | 1.03e-25 |
| deepseek-v4-pro | 20 | 149 | 169 | 1.42e-25 |
| terra | 34 | 170 | 204 | 6.00e-23 |
| argon | 11 | 113 | 124 | 1.76e-22 |
| kimi | 23 | 116 | 139 | 3.90e-16 |
| gemini-flash | 53 | 137 | 190 | 9.26e-10 |
| qwen3-32b | 0 | 27 | 27 | 1.49e-08 |
| sonnet | 46 | 104 | 150 | 2.47e-06 |
| fable | 10 | 43 | 53 | 5.55e-06 |
| haiku | 23 | 61 | 84 | 4.08e-05 |
| opus | 41 | 76 | 117 | 0.002 |
| sol | 40 | 34 | 74 | 0.561 |
| astra | 36 | 32 | 68 | 0.716 |

## Verify, real passage against a fake

| model | real yes | not this edition | p |
|---|---:|---:|---:|
| argon | 189/236 | 239/241 | 1.38e-13 |
| astra | 136/151 | 146/148 | 0.002 |
| beam | 136/207 | 209/215 | 8.94e-19 |
| deepseek-v4-pro | 147/239 | 205/238 | 9.07e-10 |
| fable | 93/108 | 115/117 | 6.03e-04 |
| gemini-flash | 197/269 | 266/268 | 1.59e-21 |
| gemma-31b | 165/245 | 239/256 | 6.81e-14 |
| gpt-oss-20b | 20/151 | 144/144 | 1.10e-62 |
| haiku | 102/161 | 159/160 | 1.85e-19 |
| kimi | 191/226 | 207/227 | 0.032 |
| luna | 171/268 | 213/244 | 5.41e-10 |
| opus | 155/211 | 208/211 | 2.63e-15 |
| qwen3-32b | 51/85 | 67/86 | 0.013 |
| sol | 146/167 | 156/163 | 0.009 |
| sonnet | 62/164 | 185/186 | 3.40e-43 |
| terra | 214/269 | 257/263 | 5.24e-12 |

## What a correct no is actually testing

Different script is an alphabet check (Gurmukhi, Pali, Sanskrit, Greek). The other rows are same-script judgments.

| negative | correct | wrong | refused |
|---|---:|---:|---:|
| Book of Mormon shown an encyclical | 83/116 | 33 | 19 |
| Talmud shown the Bible | 579/675 | 96 | 45 |
| Encyclical shown the Book of Mormon | 124/128 | 4 | 7 |
| Qur'an shown a hadith | 627/634 | 7 | 11 |
| Other same-script negative | 450/455 | 5 | 20 |
| Different script | 913/919 | 6 | 118 |
| NRSV shown the Book of Mormon | 239/240 | 1 | 0 |

## Book of Mormon against encyclicals

Answered cells only. A model that refuses most of both sets can show a large gap in coverage and a small, non-significant gap here.

| model | Book of Mormon | Encyclicals | p |
|---|---:|---:|---:|
| argon | 95/120 | 49/96 | 2.09e-05 |
| deepseek-v4-pro | 50/120 | 34/120 | 0.042 |
| gemini-flash | 82/117 | 42/82 | 0.008 |
| gemma-31b | 19/120 | 26/120 | 0.321 |
| haiku | 11/47 | 12/36 | 0.335 |
| luna | 37/118 | 31/115 | 0.475 |
| sonnet | 35/82 | 25/75 | 0.253 |
| terra | 72/120 | 37/117 | 1.53e-05 |
