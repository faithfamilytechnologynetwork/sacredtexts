# Hinduism

- Canonical edition named in the question: **Bhagavad Gita, Stotra Samhita (Gita Press text)**
- English edition: **Annie Besant (1922), same 30 citations**
- Language: Sanskrit, then English
- Raw file: `texts/raw/Hinduism/gita_stotrasamhita.json and gita_besant.json`
- Tasks: retrieve_quote, complete_unit, cite_passage, verify_source
- Size: population sample of 30 passages. No familiarity list in `well_known.yaml`.

## Passages to check

- `10:36` (population)
- `17:13` (population)
- `4:39` (population)
- `2:14` (population)
- `6:10` (population)
- `11:26` (population)
- `16:10` (population)
- `12:4` (population)
- `16:7` (population)
- `17:24` (population)
- `5:21` (population)
- `7:1` (population)
- `18:71` (population)
- `11:30` (population)
- `16:20` (population)
- `12:18` (population)
- `10:3` (population)
- `12:7` (population)
- `15:1` (population)
- `16:18` (population)
- `9:13` (population)
- `6:33` (population)
- `13:27` (population)
- `15:16` (population)
- `12:6` (population)
- `7:8` (population)
- `17:26` (population)
- `5:2` (population)
- `8:28` (population)
- `9:24` (population)

These citations are the question file. Population and familiarity are separate samples.

## Prompts in English

- `retrieve_quote`: What is the text of {citation} in {version}? Reply with the exact text of that edition and nothing else.
- `complete_unit`: Complete this quotation from {version}: "{head}" Reply with only the remaining words.
- `cite_passage`: Where in {version} can I find this quote? "{text}" Answer with the citation only, in the same form as: {example}.
- `verify_source`: Is the following text from {version}? "{text}" Answer Yes or No.

## Prompts in the text's language (draft)

A native speaker should correct these before a run.

- `retrieve_quote`: {citation} का पाठ {version} में क्या है? केवल उसी संस्करण का पाठ लिखें।
- `complete_unit`: {version} से यह उद्धरण पूरा करें: "{head}" केवल शेष शब्द लिखें।
- `cite_passage`: {version} में यह उद्धरण कहाँ है? "{text}" केवल संकेत लिखें, इस रूप में: {example}।
- `verify_source`: क्या यह पाठ {version} से है? "{text}" हाँ या नहीं लिखें।
