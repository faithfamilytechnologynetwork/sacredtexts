# Review pack

Each tradition has two samples. Report them separately.
The population sample is 30 passages, drawn uniformly (seed 20261030),
with the pre-registered familiar citations removed first.
The familiarity panel is every citation in `well_known.yaml` for that edition.
Christianity is one set of 30. The NRSV is the English edition. Hebrew Bible
verses of that set are the Masoretic text, and New Testament verses are the
Greek New Testament (Scrivener 1894). Each native passage is an English prompt
and a native-language prompt. Judaism is the same 30 in Aramaic (both prompts)
and in English. Islam is the Uthmani Qur'an in both prompt languages, plus the
Saheeh International English edition. Sikhism and Buddhism are the native edition
only, and Buddhism's Pali is asked with the English prompt only (#113). Hinduism is
Sanskrit and Besant's English. Christianity, Judaism, Islam, and Hinduism are 360
population questions. Sikhism is 240 and Buddhism is 120.
The familiarity panels are different lengths on purpose (Islam 8, Christianity 4,
Hinduism 4, Buddhism 4, Sikhism 3, Judaism 1). Compare traditions on the population sample of 30.
Do not pad or cut the familiar lists to make those counts match.
The English edition can differ from the native edition.
This folder is for a person to check the edition, the citation, and the
wording of the prompts before a run.

Checked against `texts/raw`: the Bhagavad Gita, the Dhammapada, and Sikhism
(`sggs_shabados.json`) are in the corpus. The Gita and the Dhammapada review
pages were written by `build_remaining.py` and are left in place.

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
| `03-islam` | yes | the Uthmani Qur'an (catalogue version `Uthmani (QUL)`) | Saheeh International, same citations |
| `04-sikhism` | yes | Sri Guru Granth Sahib, Shabad OS (SGPC Shabadaarth) | no English SGGS in this corpus |
| `05-hinduism` | yes | Bhagavad Gita, Stotra Samhita (Gita Press text) | Annie Besant (1922) |
| `06-buddhism` | yes | Dhammapada, Chaṭṭha Saṅgāyana (VRI) | no English Dhammapada in this corpus |
