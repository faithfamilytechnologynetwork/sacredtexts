# Review pack

Each tradition has two samples. Report them separately.
The population sample is 30 passages, drawn uniformly (seed 20261030),
with the pre-registered familiar citations removed first.
The familiarity panel is every citation in `well_known.yaml` for that edition.
Christianity is one set of 30. The NRSV is the English edition. Hebrew Bible
verses of that set are the Masoretic text, and New Testament verses are the
Greek New Testament (Scrivener 1894). Each native passage is an English prompt
and a native-language prompt. Judaism is the same 30 in Aramaic (both prompts)
and in English. Islam and Sikhism on disk are the native edition, both prompts.
A finished non-Christian tradition adds an English edition. Each tradition is
then 360 population questions. Christianity is already 360.
The familiarity panels are different lengths on purpose (Islam 7, Christianity 4,
Sikhism 3, Judaism 1). Compare traditions on the population sample of 30.
Do not pad or cut the familiar lists to make those counts match.
The English edition can differ from the native edition.
This folder is for a person to check the edition, the citation, and the
wording of the prompts before a run.

Checked against `texts/raw` on this machine: the Bhagavad Gita and the Dhammapada
are not there. Those two folders say so and do not invent passages. Sikhism is
there (`sggs_shabados.json`).

Christianity is the NRSV. The full `nrsv.json` is gitignored. The drawn verses
are in `christianity/english/`. The Protestant folder's KJV list chose the
citations; the scored wording is NRSV. Other Christian payloads are not
separate religions here.

Native-language lines are drafts. A speaker of that language should correct them
before they are used as the scored prompt.

| Folder | In raw data? | Edition in the question | English edition, if different |
|---|---|---|---|
| `01-christianity` | questions in `christianity/english/`; full `nrsv.json` is gitignored | NRSV | same |
| `02-judaism` | yes | Talmud Bavli, William Davidson Aramaic | William Davidson English |
| `03-islam` | yes | Qur'an, Uthmani (QUL) | no English Qur'an in this corpus |
| `04-sikhism` | yes | Sri Guru Granth Sahib, Shabad OS (SGPC Shabadaarth) | no English SGGS in this corpus |
| `05-hinduism` | no | The Bhagavad Gita — edition not chosen | not in raw data |
| `06-buddhism` | no | The Dhammapada — edition not chosen | not in raw data |
