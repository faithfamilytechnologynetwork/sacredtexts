# Judaism

- Canonical edition named in the question: **the Talmud Bavli (Vilna text)**
- English edition: **the William Davidson English edition of the Babylonian Talmud (same citations, a separate file)**
- Language: Aramaic / Hebrew
- Raw file: `texts/raw/Judaism/Talmud Bavli/`
- Tasks: retrieve_quote, complete_unit, cite_passage, verify_source
- Size: 372 questions. Population sample: 30 passages. Familiarity panel: 1 passages. Report those two separately.

## Passages to check

- `Bava Batra 32a:1` (population)
- `Bava Batra 60b:2` (population)
- `Bava Batra 61a:1` (population)
- `Bava Batra 64a:1` (population)
- `Bava Batra 8a:1` (population)
- `Bava Kamma 111b:1` (population)
- `Bava Kamma 78b:2` (population)
- `Bava Metzia 89b:1` (population)
- `Bekhorot 2a:1` (population)
- `Bekhorot 4a:1` (population)
- `Bekhorot 60a:1` (population)
- `Berakhot 56b:1` (population)
- `Chullin 56a:1` (population)
- `Eruvin 14b:1` (population)
- `Eruvin 61a:7` (population)
- `Eruvin 91a:1` (population)
- `Gittin 40a:1` (population)
- `Gittin 41a:1` (population)
- `Megillah 10b:2` (population)
- `Megillah 23b:3` (population)
- `Nedarim 52b:2` (population)
- `Pesachim 98a:4` (population)
- `Rosh Hashanah 11a:2` (population)
- `Rosh Hashanah 21a:2` (population)
- `Sanhedrin 60a:1` (population)
- `Sanhedrin 88b:2` (population)
- `Shabbat 96a:1` (population)
- `Sotah 32a:2` (population)
- `Yevamot 67b:1` (population)
- `Yoma 78b:1` (population)
- `Berakhot 2a:1` (familiarity)
- The Aramaic and English Davidson files are different wording (CC-BY-NC).
- The Aramaic prompts name the Vilna text, not the Davidson edition (#147).
- Aramaic cite_passage expects the daf+amud; retrieve_quote asks for the beginning of the amud (#147).

These citations are the question file. Population and familiarity are separate samples.

## Prompts in English

- `retrieve_quote`: What is the text at the beginning of {amud} in the Talmud Bavli (Vilna text)? Reply with the exact text of that edition and nothing else.
- `complete_unit`: Complete this quotation from the Talmud Bavli (Vilna text): "{head}" Reply with only the remaining words.
- `cite_passage`: Where in the Talmud Bavli (Vilna text) can I find this quote? "{text}" Answer with the citation only, in the same form as: {example}.
- `verify_source`: Is the following text from the Talmud Bavli (Vilna text)? "{text}" Answer Yes or No.

Each English prompt has a second line: `Answer in the language of the Talmud Bavli (Vilna text).`

## Prompts in the text's language (draft)

A native speaker should correct these before a run.

- `retrieve_quote`: מהו הנוסח בתחילת {amud} בתלמוד הבבלי (נוסח וילנא)? ענה בנוסח אותה מהדורה בלבד.
- `complete_unit`: השלם ציטוט זה מהתלמוד הבבלי (נוסח וילנא): "{head}" ענה במילים הנותרות בלבד.
- `cite_passage`: היכן בתלמוד הבבלי (נוסח וילנא) נמצא הטקסט הזה? "{text}" ענה בציון המקום בלבד, בצורה: {example}.
- `verify_source`: האם הטקסט הבא מן התלמוד הבבלי (נוסח וילנא)? "{text}" ענה כן או לא.
