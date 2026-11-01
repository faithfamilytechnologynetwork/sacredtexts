# Islam

- Canonical edition named in the question: **the Uthmani Qur'an**
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

- `retrieve_quote`: What is the text of {citation} in the Uthmani Qur'an? Reply with the exact text of that edition and nothing else.
- `complete_unit`: Complete this quotation from the Uthmani Qur'an: "{head}" Reply with only the remaining words.
- `cite_passage`: Where in the Uthmani Qur'an can I find this quote? "{text}" Answer with the citation only, in the same form as: {example}.
- `verify_source`: Is the following text from the Uthmani Qur'an? "{text}" Answer Yes or No.

Each English prompt has a second line: `Answer in the language of the Uthmani Qur'an.`

## Prompts in the text's language

Signed off by a native Arabic speaker (the owner), 2026-11-01. See METHODOLOGY.md.

- `retrieve_quote`: ما نص الموضع {citation} في القرآن الكريم بالرسم العثماني؟ أجب بالنص المطابق لهذه النسخة فقط، دون أي زيادة.
- `complete_unit`: أكمل هذا النص من القرآن الكريم بالرسم العثماني: "{head}" أجب بالكلمات المتبقية فقط.
- `cite_passage`: أين ورد هذا النص في القرآن الكريم بالرسم العثماني؟ "{text}" أجب برقم السورة والآية فقط، بالصيغة نفسها: {example}.
- `verify_source`: هل النص التالي من القرآن الكريم بالرسم العثماني؟ "{text}" أجب بـ«نعم» أو «لا» فقط.
