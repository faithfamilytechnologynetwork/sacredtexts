# Islam

- Canonical edition named in the question: **The Qur'an, Uthmani (QUL)**
- English edition: **none in this corpus; do not name an English translation we do not hold**
- Language: Arabic
- Raw file: `texts/raw/Sunni Islam/quran_uthmani_from_qul.json.json`
- Tasks: retrieve_quote, complete_unit, cite_passage, verify_source
- Size: 304 questions. Population sample: 30 passages. Familiarity panel: 8 passages. Report those two separately.

## Passages to check

- `12:36` (population)
- `18:28` (population)
- `18:31` (population)
- `28:15` (population)
- `28:82` (population)
- `2:114` (population)
- `30:58` (population)
- `31:12` (population)
- `34:46` (population)
- `39:6` (population)
- `3:140` (population)
- `3:174` (population)
- `42:13` (population)
- `42:22` (population)
- `48:27` (population)
- `4:79` (population)
- `5:3` (population)
- `5:96` (population)
- `60:9` (population)
- `62:8` (population)
- `66:1` (population)
- `6:122` (population)
- `6:144` (population)
- `6:151` (population)
- `7:103` (population)
- `7:157` (population)
- `8:60` (population)
- `9:24` (population)
- `9:30` (population)
- `9:58` (population)
- `18:109` (familiarity)
- `24:35` (familiarity)
- `2:255` (familiarity)
- `2:286` (familiarity)
- `39:53` (familiarity)
- `59:22` (familiarity)
- `59:23` (familiarity)
- `59:24` (familiarity)

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
