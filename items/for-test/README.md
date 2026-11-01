# Items for test

This folder is the test set for the six traditions. The population sample is 30 passages. A native edition is asked twice, an English prompt and a prompt in the text's language. An English edition, when this corpus has one, is a third file. Sampling is in `METHODOLOGY.md`.

| Tradition | Native text | English prompt | Native prompt | English text | Missing |
|---|---|---|---|---|---|
| Christianity | Yes | Yes | Yes | Yes | Nothing on the main 30. Supplemental, not in the run: English only, 15 Book of Mormon verses and 15 papal encyclical paragraphs |
| Judaism | Yes | Yes | Yes | Yes | — |
| Islam | Yes | Yes | Yes | No | English text |
| Sikhism | Yes | Yes | Yes | No | English text |
| Hinduism | Yes | Yes | Yes | Yes | — |
| Buddhism | Yes | Yes | Yes | No | English text |

`*/familiarity/` is the pre-registered list and is not in the run (Christianity 4, Judaism 1, Islam 7, Sikhism 3; Hinduism and Buddhism have none). `cost.py` writes `COST.md`. `models/openrouter.yaml` is the 16-model run and `models/openrouter-subset.yaml` is 7 of those models. `review/` is check pages only.

## Before a run

No pull request is open. These issues are still open and the work is not already on `main`.

| Issue | Still to do | Blocks |
|---|---|---|
| #60 | Arabic fold still skips hamza-alef `ءَا` ↔ alef-madda `آ`, and `ىٰ` ↔ maqsura. #52 did not cover these | Nothing. Islam can run; a few answers stay under-credited |
| #37 | Septuagint is not in the repo. The test set has a Masoretic excerpt and Scrivener 1894, not a full Tanakh and not Nestle-Aland | The catalogue copies of those witnesses. The excerpt already in this folder can run |
| #43 | Qur'an, Latter-day Saint, and NRSV license terms | Releasing questions, not collecting them |

Already done, so not on that list: #50's scoring half (`normalize()` keeps Gurmukhi, Devanagari, and Pali vowel signs; the Guru Granth Sahib text landed in #51), #63 (Dhammapada, closed), #64 (Gita text landed in #66; the issue is still open and should be closed), #52 (main Arabic fold, closed). #54's harness merged in #59; the live search run has not been done, and it is a separate experiment.

Safe to collect now: Christianity (NRSV, Masoretic, Greek), Judaism (Aramaic and English), Islam, Sikhism, the Sanskrit and English Gita, and the Pali Dhammapada. The Christian supplemental set waits until after the main 30.

## Passage files

Each `passages.json` is the scored wording for that tradition and language.
A verify question can quote some other tradition; those quotes are not copied here.

| Field | Meaning |
|---|---|
| `tradition` | One of the six: Christianity, Judaism, Islam, Sikhism, Hinduism, Buddhism. The Christian supplemental files name the Book of Mormon and the encyclical instead |
| `citation` | The passage, in the form the scorer expects |
| `sample` | `population` (the headline 30), `familiarity` (the pre-registered list), or `supplemental` (the Christian modern set, not in the run) |
| `version` | The edition that question asks for. An English file names the English edition |
| `run` | On the file, not each passage. True only in `population/` |
| `text.native` | The native-edition wording. Omitted when the edition is already English |
| `text.english` | The English wording. Omitted when this corpus has no English edition |

`notice` holds the NRSV copyright line and the Talmud CC-BY-NC line.

## Counts

The run is the `population/` folder. `passages.json` there is the 30 passages, and `run` is true. The `familiarity/` folder is not collected with the run (Christianity 4, Judaism 1, Islam 7, Sikhism 3).

A native edition is the same passages asked twice: `prompt-english/` and `prompt-native/`. Christianity's native text is not a second draw and not two full Bibles. The same 30 citations are split by original language: Hebrew Bible verses in `native/masoretic/`, New Testament verses in `native/greek/`. The NRSV file is the English edition of all 30.

| Tradition | Questions in the run | Population | Familiarity | File |
|---|---|---|---|---|
| Christianity (NRSV, then original language) | 120 + 240 | 30 | 4, not in the run | `christianity/english/population/`, `native/masoretic/`, `native/greek/` |
| Judaism (Aramaic, two prompts, then English) | 120 + 120 + 120 | 30 | 1, not in the run | `judaism/native/population/prompt-english/`, `prompt-native/`, `judaism/english/population/` |
| Islam (Arabic, two prompts) | 120 + 120 | 30 | 7, not in the run | `islam/native/population/prompt-english/`, `prompt-native/` |
| Sikhism (Gurmukhi, two prompts) | 240 | 30 | 3, not in the run | `sikhism/native/population/prompt-english/`, `prompt-native/` |
| Hinduism (Sanskrit, two prompts, then English) | 120 + 120 + 120 | 30 | none listed | `hinduism/native/population/`, `hinduism/english/population/` |
| Buddhism (Pali, two prompts) | 120 + 120 | 30 | none listed | `buddhism/native/population/` |

Report the population sample and the familiarity panel separately. The reason
is in `METHODOLOGY.md`.

## The four prompts

Each passage is asked once as each task. `expected` is what `score_answer` reads.

| Task | The model is asked to | `expected` |
|---|---|---|
| `retrieve_quote` | Give the exact text of a citation | `text`: the whole passage |
| `complete_unit` | Finish a quotation after the first half of its words | `text`: the remaining words |
| `cite_passage` | Name where a quotation appears | `citation`: the citation only |
| `verify_source` | Say whether a quotation is from the named edition | `answer`: `yes` or `no` |

A cite prompt shows one other citation from the same edition, so the answer has a form to follow (`in the same form as: …`). Within each sample, half of the verify prompts quote a real passage from a different work in the same language and expect `no`. Where this corpus has only one work in that language, the donor is another tradition, and the script differs. The rule is in `METHODOLOGY.md`.

## How a prompt is built

The edition is named inside the prompt. The model call has no language field.

**English edition, already English** (the NRSV file). One line. It names that edition and asks for the answer in English.

The same 30 citations are also in `christianity/native/masoretic/` (Hebrew Bible, including Aramaic Daniel 2) and `christianity/native/greek/` (New Testament). Those use the two-call native form below. Together they are one set of 30, not a second draw.

```
What is the text of Exodus 28:43 in the New Revised Standard Version (NRSV)? Reply with the exact text of that edition and nothing else.
```

**Native edition, two calls** (Islam, Sikhism, and the Aramaic half of Judaism). The same question is not stacked in one prompt. `prompt-english/` is the English question plus one line saying which language to answer in. `prompt-native/` is only the question in the text's language. Those native lines are drafts for a native speaker.

```
What is the text of 34:54 in the Uthmani (QUL) edition? Reply with the exact text of that edition and nothing else.
Answer in the language of the Uthmani (QUL) edition.
```

```
ما نص 34:54 من القرآن في طبعة عثماني (QUL)؟ أجب بنص تلك الطبعة فقط.
```

**English edition of a non-English work** (Judaism). One English line, the same shape as Christianity. It names the English edition. It does not repeat the question in Hebrew, and it does not warn that the translation can differ.

Judaism's native edition is one text, the Aramaic Davidson edition. Hebrew and Aramaic are mixed in that text; they are not two scored languages. The English Davidson edition is a second scored answer. `complete_unit` cuts each edition at half of its own words (`split_quote` in `generate.py`, the same cut the main generator uses). The two remainders are the same fraction of each wording. They are not the same point in the passage, because the translation is not the same length.

Islam, Sikhism, and Buddhism do not have this third prompt. This corpus has no English edition of those works, so those questions are the native-answer form only. Hinduism does: the same 30 verses are asked in Besant's English as well as in Sanskrit.

## Run the panel

The run joins the population question files in `RUNNING.md`. `review/` has check pages and does not keep a second copy of the questions.

List A is `models/openrouter.yaml` (16 models), and that is the run. List B is `models/openrouter-subset.yaml` (7 models). Both go through OpenRouter with temperature 0. One `OPENROUTER_API_KEY` covers every model. No Anthropic, OpenAI, or Gemini key. The reference file `configs/models.openrouter.yaml` is the old three-model run and is not this panel.

Search is the `search` key at the top of the panel file. It is `false`, which strips `web_search` from every model, so nothing in this run uses search. Set it to `true` to turn search on for every model, or `both` to run each model twice (the plain id, and `<id>-search`) where OpenRouter can forward that provider's own search. Google, DeepSeek, Moonshot, Reflection, and Qwen are not forwarded, so `true` fails on this panel and `both` leaves those models search-off.

OpenRouter has no language field. The prompt already names the edition and the answer language. One collect writes every model in the chosen file into the same answers file; each row is marked with its `model_id`.

`COST.md` prices List A. Christianity, Judaism, and Hinduism are 360 population questions each (native two prompts, plus an English edition). Islam, Sikhism, and Buddhism are 240 (native only). Familiarity lists and `christianity/modern/` are not in that total. Refresh with `python items/for-test/cost.py`.

`complete_unit` scores the remaining words of that passage. An answer that then continues into later verses still counts as correct, because the remainder is contained in the answer. A cite task that asks for a passage from the wrong edition is not in this run.

How to run, pause, and resume is in `RUNNING.md` at the top of the repo. A pilot collects `christianity/english/population/questions.jsonl` with `--model haiku` into its own answers file. Finished answers are kept if you stop midway.
