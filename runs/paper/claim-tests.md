# Paired claims

From 32478 scored cells across 16 models in `runs/facct-2026-11-03`. A file still being collected contributes only the cells it already has. Accuracy comparisons drop refusals. McNemar is the two-sided exact test on discordant pairs of the same citation. Fisher exact compares two independent answered sets.

## Citation, English prompt against native prompt

English-only means the English prompt was correct and the native prompt was not. Native-only is the reverse.

| model | English only | native only | pairs | p |
|---|---:|---:|---:|---:|
| deepseek-v4-pro | 17 | 5 | 22 | 0.017 |

## Quote against cite

Quote-only means the quotation was correct and the citation was not, on the same citation, both answered.

| model | quote only | cite only | pairs | p |
|---|---:|---:|---:|---:|
| luna | 2 | 159 | 161 | 8.92e-45 |
| terra | 2 | 149 | 151 | 8.04e-42 |
| kimi | 7 | 165 | 172 | 2.72e-40 |
| deepseek-v4-pro | 14 | 177 | 191 | 4.19e-37 |
| argon | 0 | 117 | 117 | 1.20e-35 |
| beam | 5 | 137 | 142 | 1.67e-34 |
| gemini-flash | 6 | 131 | 137 | 9.88e-32 |
| gemma-31b | 0 | 102 | 102 | 3.94e-31 |
| qwen3-32b | 0 | 75 | 75 | 5.29e-23 |
| astra | 0 | 69 | 69 | 3.39e-21 |
| sol | 1 | 68 | 69 | 2.37e-19 |
| opus | 3 | 66 | 69 | 1.86e-16 |
| haiku | 4 | 66 | 70 | 1.65e-15 |
| fable | 15 | 82 | 97 | 2.38e-12 |
| sonnet | 18 | 69 | 87 | 3.32e-08 |

## Verify, real passage against a fake

| model | real yes | not this edition | p |
|---|---:|---:|---:|
| argon | 253/257 | 251/252 | 0.373 |
| astra | 240/257 | 249/253 | 0.006 |
| beam | 215/255 | 245/253 | 1.12e-06 |
| deepseek-v4-pro | 185/257 | 248/253 | 1.99e-18 |
| fable | 217/234 | 240/240 | 4.53e-06 |
| gemini-flash | 231/257 | 251/253 | 1.74e-06 |
| gemma-31b | 166/250 | 241/249 | 3.66e-20 |
| gpt-oss-20b | 29/248 | 251/253 | 2.55e-106 |
| haiku | 138/187 | 208/208 | 2.71e-18 |
| kimi | 221/256 | 248/252 | 1.28e-07 |
| luna | 159/257 | 244/248 | 1.87e-28 |
| opus | 223/257 | 251/253 | 7.04e-09 |
| qwen3-32b | 160/227 | 213/236 | 7.60e-08 |
| sol | 238/257 | 246/253 | 0.025 |
| sonnet | 91/165 | 219/219 | 4.30e-33 |
| terra | 216/257 | 251/253 | 4.63e-11 |

## What a correct no is actually testing

Different script is an alphabet check (Gurmukhi, Pali, Sanskrit, Greek). The other rows are same-script judgments.

| negative | correct | wrong | refused |
|---|---:|---:|---:|
| Talmud shown the Bible | 651/687 | 36 | 33 |
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
| argon | 102/120 | 62/91 | 0.004 |
| astra | 112/120 | 44/72 | 5.98e-08 |
| beam | 66/99 | 37/93 | 2.75e-04 |
| deepseek-v4-pro | 57/120 | 40/119 | 0.035 |
| fable | 91/117 | 60/106 | 9.35e-04 |
| gemini-flash | 95/116 | 46/84 | 4.15e-05 |
| gemma-31b | 24/120 | 26/120 | 0.874 |
| gpt-oss-20b | 15/109 | 15/88 | 0.554 |
| haiku | 32/62 | 20/43 | 0.693 |
| kimi | 85/118 | 49/115 | 6.19e-06 |
| luna | 50/119 | 32/118 | 0.020 |
| opus | 105/119 | 57/88 | 7.19e-05 |
| qwen3-32b | 27/120 | 26/120 | 1.000 |
| sol | 110/120 | 46/75 | 6.15e-07 |
| sonnet | 52/98 | 35/59 | 0.508 |
| terra | 82/120 | 41/119 | 1.85e-07 |
