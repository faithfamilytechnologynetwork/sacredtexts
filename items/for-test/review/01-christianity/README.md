# Christianity

- Canonical edition named in the question: **NRSV**
- English edition: **NRSV (same edition; the text is already English)**
- Language: English
- Raw file: `texts/raw/Protestant Christian/nrsv.json (gitignored; not in the public repo)`
- Tasks: retrieve_quote, complete_unit, cite_passage, verify_source
- Size: 136 questions. Population sample: 30 passages. Familiarity panel: 4 passages. Report those two separately.

## Passages to check

- `1 Chronicles 9:22` (population)
- `1 Kings 1:23` (population)
- `1 Kings 22:39` (population)
- `1 Samuel 31:6` (population)
- `2 Chronicles 26:15` (population)
- `2 Samuel 18:5` (population)
- `2 Thessalonians 2:16` (population)
- `Acts 24:1` (population)
- `Daniel 2:42` (population)
- `Exodus 28:43` (population)
- `Exodus 29:40` (population)
- `Exodus 30:38` (population)
- `Ezekiel 16:19` (population)
- `Ezekiel 23:16` (population)
- `Ezekiel 43:24` (population)
- `Galatians 3:22` (population)
- `Hebrews 1:2` (population)
- `Isaiah 37:17` (population)
- `Isaiah 49:7` (population)
- `Jeremiah 50:23` (population)
- `John 12:13` (population)
- `John 8:41` (population)
- `Joshua 23:2` (population)
- `Judges 17:11` (population)
- `Leviticus 11:21` (population)
- `Leviticus 14:19` (population)
- `Luke 12:41` (population)
- `Mark 10:11` (population)
- `Nehemiah 6:7` (population)
- `Revelation 9:14` (population)
- `Genesis 1:1` (familiarity)
- `John 3:16` (familiarity)
- `Matthew 6:9` (familiarity)
- `Psalms 23:1` (familiarity)

The verse inventory for the draw is the Protestant list in `kjv.json`. The wording in `christianity/english/` is NRSV. Do not check these against `kjv.json`.

These citations are the question file. Population and familiarity are separate samples.

## Prompts in English

- `retrieve_quote`: What is the text of {citation} in NRSV? Reply with the exact text of that edition and nothing else.
- `complete_unit`: Please complete this quote from NRSV: "{head}" Reply with only the remaining words.
- `cite_passage`: Where in NRSV can I find this quote? "{text}" Answer with the citation only, in the same form as: {example}.
- `verify_source`: Is the following text from NRSV? "{text}" Answer Yes or No.

This edition is English, so there is one answer language.
