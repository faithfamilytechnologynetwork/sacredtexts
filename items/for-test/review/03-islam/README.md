# Islam

- Canonical edition named in the question: **The Qur'an, Uthmani (QUL)**
- English edition: **none in this corpus; do not name an English translation we do not hold**
- Language: Arabic
- Raw file: `texts/raw/Sunni Islam/quran_uthmani_from_qul.json.json`
- Tasks: retrieve_quote, complete_unit, cite_passage, verify_source
- Size: 148 questions. Population sample: 30 passages. Familiarity panel: 7 passages. Report those two separately.

## Passages to check

- `12:36` (population)
- `16:93` (population)
- `18:22` (population)
- `20:77` (population)
- `27:24` (population)
- `2:120` (population)
- `31:16` (population)
- `33:60` (population)
- `34:39` (population)
- `34:54` (population)
- `3:145` (population)
- `3:167` (population)
- `3:195` (population)
- `40:5` (population)
- `41:12` (population)
- `4:170` (population)
- `4:92` (population)
- `57:15` (population)
- `59:24` (population)
- `5:20` (population)
- `5:96` (population)
- `6:111` (population)
- `6:54` (population)
- `6:7` (population)
- `6:71` (population)
- `7:123` (population)
- `7:129` (population)
- `7:152` (population)
- `8:34` (population)
- `9:61` (population)
- `112:1` (familiarity)
- `1:1` (familiarity)
- `1:2` (familiarity)
- `24:35` (familiarity)
- `2:255` (familiarity)
- `2:286` (familiarity)
- `67:1` (familiarity)

These citations are the question file. Population and familiarity are separate samples.

## Prompts in English

- `retrieve_quote`: What is the text of {citation} in The Qur'an, Uthmani (QUL)? Reply with the exact text of that edition and nothing else.
- `complete_unit`: Please complete this quote from The Qur'an, Uthmani (QUL): "{head}" Reply with only the remaining words.
- `cite_passage`: Where in The Qur'an, Uthmani (QUL) can I find this quote? "{text}" Answer with the citation only, in the same form as: {example}.
- `verify_source`: Is the following text from The Qur'an, Uthmani (QUL)? "{text}" Answer Yes or No.

## Prompts in the text's language (draft)

A native speaker should correct these before a run.

- `retrieve_quote`: ما نص {citation} من القرآن في طبعة عثماني (QUL)؟ أجب بنص تلك الطبعة فقط.
- `complete_unit`: أكمل هذا الاقتباس من القرآن، طبعة عثماني (QUL): "{head}" أجب بالكلمات المتبقية فقط.
- `cite_passage`: أين أجد هذا النص في القرآن، طبعة عثماني (QUL)؟ "{text}" أجب بالاستشهاد فقط.
- `verify_source`: هل النص التالي من القرآن، طبعة عثماني (QUL)؟ "{text}" أجب بنعم أو لا.
