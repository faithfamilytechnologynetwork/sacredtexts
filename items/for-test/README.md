# Items for test

This folder is the test set for the six traditions. Start with the methodology, then the population folders below.

| File | What it is |
|---|---|
| `METHODOLOGY.md` | How the sample was drawn, and what to report |
| `christianity/english/population/` | The 30 NRSV passages that run |
| `christianity/masoretic/population/` | Those of the 30 whose original is the Hebrew Bible |
| `christianity/greek/population/` | Those of the 30 whose original is the New Testament |
| `judaism/native/population/prompt-english/` and `prompt-native/` | The same 30 Aramaic passages, two prompts |
| `judaism/english/population/` | Those 30 again, English edition |
| `islam/native/population/prompt-english/` and `prompt-native/` | The same 30 Arabic passages, two prompts |
| `sikhism/native/population/prompt-english/` and `prompt-native/` | The same 30 Gurmukhi passages. Not collected |
| `*/familiarity/` | The pre-registered list. Not in the run |
| `cost.py` | Cost calculator. Writes `COST.md` from OpenRouter's prices |
| `models/openrouter.yaml` | List A: 16 OpenRouter models, search off |
| `models/openrouter-subset.yaml` | List B: 7 of those models |
| `review/` | Check pages only. The questions themselves are in the tradition folders |

## Passage files

Each `passages.json` is the scored wording for that tradition and language.
A verify question can quote some other tradition; those quotes are not copied here.

| Field | Meaning |
|---|---|
| `tradition` | Christianity, Judaism, Islam, or Sikhism |
| `citation` | The passage, in the form the scorer expects |
| `sample` | `population` (the headline 30) or `familiarity` (the pre-registered list) |
| `version` | The edition that question asks for. An English file names the English edition |
| `run` | On the file, not each passage. True only in `population/` |
| `text.native` | The native-edition wording. Omitted when the edition is already English |
| `text.english` | The English wording. Omitted when this corpus has no English edition |

`notice` holds the NRSV copyright line and the Talmud CC-BY-NC line.

## Counts

The run is the `population/` folder. `passages.json` there is the 30 passages, and `run` is true. The `familiarity/` folder is not collected with the run (Christianity 4, Judaism 1, Islam 7, Sikhism 3).

A native edition is the same passages asked twice: `prompt-english/` and `prompt-native/`. Christianity's native text is not a second draw and not two full Bibles. The same 30 citations are split by original language: Hebrew Bible verses in `masoretic/`, New Testament verses in `greek/`. The NRSV file is the English edition of all 30.

| Tradition | Questions in the run | Population | Familiarity | File |
|---|---|---|---|---|
| Christianity (NRSV, then original language) | 120 + 240 | 30 | 4, not in the run | `christianity/english/population/`, `masoretic/`, `greek/` |
| Judaism (Aramaic, two prompts, then English) | 120 + 120 + 120 | 30 | 1, not in the run | `judaism/native/population/prompt-english/`, `prompt-native/`, `judaism/english/population/` |
| Islam (Arabic, two prompts) | 120 + 120 | 30 | 7, not in the run | `islam/native/population/prompt-english/`, `prompt-native/` |
| Sikhism (Gurmukhi, two prompts) | 240, not collected | 30 | 3, not in the run | `sikhism/native/population/prompt-english/`, `prompt-native/` |
| Hinduism | 0 | — | — | no Bhagavad Gita in `texts/raw` |
| Buddhism | 0 | — | — | no Dhammapada in `texts/raw` |

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

A cite prompt shows one other citation from the same edition, so the answer has a form to follow (`in the same form as: …`). Within each sample, half of the verify prompts quote a real passage from a different tradition and expect `no`.

## How a prompt is built

The edition is named inside the prompt. The model call has no language field.

**English edition, already English** (the NRSV file). One line. It names that edition and asks for the answer in English.

The same 30 citations are also in `christianity/masoretic/` (Hebrew Bible, including Aramaic Daniel 2) and `christianity/greek/` (New Testament). Those use the two-call native form below. Together they are one set of 30, not a second draw.

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

Islam and Sikhism do not have this third prompt. This corpus has no English edition of either, so those questions are the native-answer form only.

## Run the panel

The run joins the population question files in `RUNNING.md`. Sikhism stays out because `collect` refuses a Gurmukhi question while scoring still drops Gurmukhi vowel signs. `review/` has check pages and does not keep a second copy of the questions.

List A is `models/openrouter.yaml` (16 models), and that is the run. List B is `models/openrouter-subset.yaml` (7 models). Both go through OpenRouter with temperature 0. One `OPENROUTER_API_KEY` covers every model. No Anthropic, OpenAI, or Gemini key. The reference file `configs/models.openrouter.yaml` is the old three-model run and is not this panel.

Search is the `search` key at the top of the panel file. It is `false`, which strips `web_search` from every model, so nothing in this run uses search. Set it to `true` to turn search on for every model, or `both` to run each model twice (the plain id, and `<id>-search`) where OpenRouter can forward that provider's own search. Google, DeepSeek, Moonshot, Reflection, and Qwen are not forwarded, so `true` fails on this panel and `both` leaves those models search-off.

OpenRouter has no language field. The prompt already names the edition and the answer language. One collect writes every model in the chosen file into the same answers file; each row is marked with its `model_id`.

`COST.md` prices List A. Christianity and Judaism are 360 population questions each. Islam on disk is the native 240. Familiarity lists are not in that total. Refresh with `python items/for-test/cost.py`.

`complete_unit` scores the remaining words of that passage. An answer that then continues into later verses still counts as correct, because the remainder is contained in the answer. A cite task that asks for a passage from the wrong edition is not in this run.

How to run, pause, and resume is in `RUNNING.md` at the top of the repo. A pilot collects `christianity/english/population/questions.jsonl` with `--model haiku` into its own answers file. Finished answers are kept if you stop midway.
