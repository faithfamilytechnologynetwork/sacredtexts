# Buddhism

- Canonical edition named in the question: **Dhammapada, Chaṭṭha Saṅgāyana (VRI)**
- English edition: **none in this corpus**
- Language: Pali (romanized)
- Raw file: `texts/raw/Buddhism/s0502m.mul.xml`
- Tasks: retrieve_quote, complete_unit, cite_passage, verify_source
- Size: population sample of 30 passages. No familiarity list in `well_known.yaml`.

## Passages to check

- `Dhammapada 184` (population)
- `Dhammapada 144` (population)
- `Dhammapada 371` (population)
- `Dhammapada 361` (population)
- `Dhammapada 142` (population)
- `Dhammapada 1` (population)
- `Dhammapada 380` (population)
- `Dhammapada 92` (population)
- `Dhammapada 127` (population)
- `Dhammapada 20` (population)
- `Dhammapada 74` (population)
- `Dhammapada 337` (population)
- `Dhammapada 177` (population)
- `Dhammapada 8` (population)
- `Dhammapada 259` (population)
- `Dhammapada 3` (population)
- `Dhammapada 76` (population)
- `Dhammapada 106` (population)
- `Dhammapada 359` (population)
- `Dhammapada 329` (population)
- `Dhammapada 84` (population)
- `Dhammapada 185` (population)
- `Dhammapada 93` (population)
- `Dhammapada 310` (population)
- `Dhammapada 108` (population)
- `Dhammapada 165` (population)
- `Dhammapada 154` (population)
- `Dhammapada 302` (population)
- `Dhammapada 306` (population)
- `Dhammapada 282` (population)

These citations are the question file. Population and familiarity are separate samples.

## Prompts in English

- `retrieve_quote`: What is the text of {citation} in {version}? Reply with the exact text of that edition and nothing else.
- `complete_unit`: Complete this quotation from {version}: "{head}" Reply with only the remaining words.
- `cite_passage`: Where in {version} can I find this quote? "{text}" Answer with the citation only, in the same form as: {example}.
- `verify_source`: Is the following text from {version}? "{text}" Answer Yes or No.

## Prompts in the text's language (draft)

A native speaker should correct these before a run.

- `retrieve_quote`: Ko {citation} pāṭho {version} potthake? Tasseva pāṭham eva vissajjehi.
- `complete_unit`: {version} ito imaṃ udāharaṇaṃ paripūrehi: "{head}" Avasiṭṭhapadāni yeva vissajjehi.
- `cite_passage`: Kattha {version} potthake ayaṃ pāṭho? "{text}" Ṭhānam eva vissajjehi, iminā ākārena: {example}.
- `verify_source`: Ayaṃ pāṭho {version} potthakato? "{text}" Āma vā no vā vissajjehi.
