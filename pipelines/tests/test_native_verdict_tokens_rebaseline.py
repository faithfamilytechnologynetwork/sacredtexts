"""Issue #115: verify_source reads more native verdict words and Devanagari "Answer:" labels. This
test checks that the change moves exactly the pre-registered cells, and only out of ``refused``.

Before the fix these were scored ``refused`` although each is a clear one-word verdict: Sanskrit
``आम्`` (yes), Hebrew ``הן`` and Aramaic ``הין`` (yes), Hindi/Pali ``nahi`` / ``nahiṃ`` in Latin script
(no, read on ``pi``/``sa`` cells only, like every Latin word), the Pali reply ``नो हेतं`` ("not so"),
and a ``उत्तर:`` / ``उत्तरम्:`` label ahead of the verdict. The native labels (Arabic included) are now
stripped on every cell, and ``_stands_alone`` skips a zero-width non-joiner after the word
(``आम्`` + U+200C). Each word must still stand alone: the leading-stance contract is unchanged.

The registered set was derived by running the pre-#115 and #115 parsers over every scored answer and
is pinned here by identity:

- 22 cells in committed ``runs/``, all ``refused`` there: 20 → correct, 2 → incorrect. The bare ``आम`` is
  never a verdict (Hindi "common"/"mango"; the virama is kept in matching), so gemini-flash's
  ``आम (Yes)`` stays ``refused``.
  ``runs/archive``: none.
- 134 cells in the untracked ``runs/rerun-2026-11-03`` (scored with #95): 133 → correct, 1 → incorrect
  (gemma's ``**Nahi**`` on an expected yes). Only the 14 models whose collection was complete are pinned;
  qwen3-32b and gpt-oss-20b were still collecting. The rerun is a witness, not a gate: each folder skips
  when absent.

No committed ``scores.jsonl`` is rewritten. The "nothing else moves, nothing moves into ``refused``"
scan is the one in ``test_cross_language_verdict_rebaseline.py`` (git-tracked score files only), which
accepts the cells registered here. Read-only. Skips cleanly if the run evidence is absent.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

from sacredbench.score import parse_yes_no, score_answer

RUNS = Path(__file__).resolve().parents[2] / "runs"


@pytest.mark.parametrize(
    "answer, language, verdict",
    [
        ("आम्", "sa", "yes"),
        ("आम्।", "sa", "yes"),
        ("**आम्।** अयं श्लोकः", "sa", "yes"),
        ("आम्\u200c।", "sa", "yes"),
        ("हाँ\u200c।", "sa", "yes"),     # a zero-width non-joiner after a word that was already listed
        ("הן", "he", "yes"),
        ("הן.", "he", "yes"),
        ("הין", "he", "yes"),
        ("Nahi", "pi", "no"),
        ("Nahi", "sa", "no"),
        ("**Nahi**, ayaṃ pāṭho na hoti.", "pi", "no"),
        ("Nahiṁ, ayaṁ pāṭho na hoti.", "pi", "no"),
        ("Nahīṃ, yaha pāṭha Dhammapada kā nahīṃ hai.", "pi", "no"),
        ("नो हेतं.", "pi", "no"),
        ("**नो हेतं** (न)।", "pi", "no"),
        ("नो।", "pi", "no"),
        ("उत्तर: हाँ", "sa", "yes"),
        ("उत्तर: **हाँ**", "sa", "yes"),
        ("उत्तरम्: आम्\u200c (हाँ)।", "sa", "yes"),
        ("उत्तरम्: **आम्\u200c।**", "sa", "yes"),
        ("उत्तर: नहीं", "en", "no"),     # the labels are read on every cell
        ("الجواب: لا", "en", "no"),
    ],
)
def test_verdict_is_read(answer, language, verdict):
    assert parse_yes_no(answer, language) == verdict


@pytest.mark.parametrize(
    "answer, language",
    [
        ("आम् इति न", "sa"),           # a following word: not a stand-alone verdict
        ("आम-तौर पर यह श्लोक नहीं है", "sa"),  # bare आम ("common") is never a verdict, even before a hyphen
        ("आम।", "sa"),
        ("आम (Yes)", "sa"),
        ("आम्\u200cइति", "sa"),
        ("הן לא", "he"),
        ("הין לא", "he"),
        ("nahi jānāmi", "pi"),
        ("नो जानामि", "pi"),
        ("उत्तर: हाँ कहना कठिन है", "sa"),
        ("उत्तर हाँ", "sa"),           # no colon: not a label
        ("Nahi", "en"),                # Latin words stay on their own language's cell
    ],
)
def test_word_that_does_not_stand_alone_is_not_a_verdict(answer, language):
    assert parse_yes_no(answer, language) is None


# answers folder (relative to runs/) -> {question_id: outcome under #115}
FLIPS: dict[str, dict[str, str]] = {
    "argon/base/judaism/native/population/prompt-english": {
        "104f6f2dcc356ab7": "correct",
    },
    "astra/base/judaism/native/population/prompt-english": {
        "253a91c24af287ee": "correct",
    },
    "beam/base/buddhism/native/population/prompt-english": {
        "227c87bb0a734f40": "correct", "f09abdf191b1e4bf": "correct",
    },
    "beam/base/judaism/native/population/prompt-english": {
        "0d9a38c5c17e376a": "correct", "253a91c24af287ee": "correct", "322a7708ee6499ab": "correct",
        "35b058fb8cf731a2": "correct", "3c94f2e8a8150c23": "correct", "42db23be5ed58b5a": "correct",
    },
    "deepseek-v4-pro/base/hinduism/native/population/prompt-english": {
        "1bf456e20feaa9ee": "correct", "1c7778747163ad02": "correct", "42dc0d16da558321": "correct",
    },
    "gemini-flash/base/hinduism/native/population/prompt-english": {
        "0b1497819e8787de": "correct",
    },
    "gemma-31b/base/buddhism/native/population/prompt-english": {
        "f0062121ba12ba06": "incorrect",
    },
    "gemma-31b/base/buddhism/native/population/prompt-native": {
        "04d77928dac7cc46": "correct", "83023f40e326c14b": "incorrect", "cb19706ec80a892a": "correct",
    },
    "rerun-2026-11-03/argon/base/buddhism/native/population/prompt-english": {
        "96f3c22bf9ab9c2e": "correct",
    },
    "rerun-2026-11-03/argon/base/hinduism/native/population/prompt-english": {
        "0589c8e453aa4eba": "correct", "40c80bf0f2e77465": "correct", "42a036c2d35997c5": "correct",
        "43756f2b68f8975c": "correct", "54c5474e9ca17426": "correct", "571cd582c9769d06": "correct",
        "670a8f73e63af90c": "correct", "95fc8931bc95c37e": "correct", "ae63380674766933": "correct",
        "afac31a7253cf2e1": "correct", "ba01abb626d109c9": "correct", "df09eb678500c4c5": "correct",
        "e1d083cadf0a1d16": "correct", "ef2171c87321c566": "correct", "ffccefa5f2fe1ef3": "correct",
    },
    "rerun-2026-11-03/astra/base/hinduism/native/population/prompt-english": {
        "0589c8e453aa4eba": "correct", "40c80bf0f2e77465": "correct", "42a036c2d35997c5": "correct",
        "43756f2b68f8975c": "correct", "54c5474e9ca17426": "correct", "571cd582c9769d06": "correct",
        "670a8f73e63af90c": "correct", "95fc8931bc95c37e": "correct", "ae63380674766933": "correct",
        "afac31a7253cf2e1": "correct", "ba01abb626d109c9": "correct", "df09eb678500c4c5": "correct",
        "e1d083cadf0a1d16": "correct", "ef2171c87321c566": "correct", "ffccefa5f2fe1ef3": "correct",
    },
    "rerun-2026-11-03/beam/base/buddhism/native/population/prompt-english": {
        "3fb1e190b55d2ade": "correct", "b0d72836bb18cc8a": "correct", "e6d1a46768d3ca7c": "correct",
    },
    "rerun-2026-11-03/beam/base/hinduism/native/population/prompt-english": {
        "0589c8e453aa4eba": "correct", "40c80bf0f2e77465": "correct", "42a036c2d35997c5": "correct",
        "43756f2b68f8975c": "correct", "54c5474e9ca17426": "correct", "670a8f73e63af90c": "correct",
        "95fc8931bc95c37e": "correct", "ae63380674766933": "correct", "afac31a7253cf2e1": "correct",
        "ba01abb626d109c9": "correct", "e1d083cadf0a1d16": "correct", "ffccefa5f2fe1ef3": "correct",
    },
    "rerun-2026-11-03/beam/base/judaism/native/population/prompt-english": {
        "1ad8e0e1134339f5": "correct", "39ddd585d08cd19b": "correct", "bedcb00dd5028f6d": "correct",
        "cd45bd9156cb42c2": "correct",
    },
    "rerun-2026-11-03/deepseek-v4-pro/base/buddhism/native/population/prompt-native": {
        "1ce1f9a920f74d13": "correct",
    },
    "rerun-2026-11-03/deepseek-v4-pro/base/hinduism/native/population/prompt-english": {
        "40c80bf0f2e77465": "correct", "43756f2b68f8975c": "correct", "571cd582c9769d06": "correct",
        "670a8f73e63af90c": "correct", "afac31a7253cf2e1": "correct", "e1d083cadf0a1d16": "correct",
    },
    "rerun-2026-11-03/fable/base/hinduism/native/population/prompt-english": {
        "0589c8e453aa4eba": "correct", "40c80bf0f2e77465": "correct", "42a036c2d35997c5": "correct",
        "43756f2b68f8975c": "correct", "54c5474e9ca17426": "correct", "670a8f73e63af90c": "correct",
        "ae63380674766933": "correct", "afac31a7253cf2e1": "correct", "ba01abb626d109c9": "correct",
        "df09eb678500c4c5": "correct", "ef2171c87321c566": "correct", "ffccefa5f2fe1ef3": "correct",
    },
    "rerun-2026-11-03/gemini-flash/base/hinduism/native/population/prompt-english": {
        "0589c8e453aa4eba": "correct", "40c80bf0f2e77465": "correct", "42a036c2d35997c5": "correct",
        "43756f2b68f8975c": "correct", "54c5474e9ca17426": "correct", "571cd582c9769d06": "correct",
        "670a8f73e63af90c": "correct", "95fc8931bc95c37e": "correct", "ae63380674766933": "correct",
        "afac31a7253cf2e1": "correct", "ba01abb626d109c9": "correct", "df09eb678500c4c5": "correct",
        "e1d083cadf0a1d16": "correct", "ef2171c87321c566": "correct", "ffccefa5f2fe1ef3": "correct",
    },
    "rerun-2026-11-03/gemini-flash/base/judaism/native/population/prompt-english": {
        "5d6047f35a5f3b58": "correct", "6a6131a6b4ff3b96": "correct", "a1fd261266f105a1": "correct",
        "ce050718836c09fb": "correct", "d64e1773d5e5a8e3": "correct",
    },
    "rerun-2026-11-03/gemma-31b/base/buddhism/native/population/prompt-native": {
        "1ce1f9a920f74d13": "correct", "7d07a712c650e5bf": "incorrect",
    },
    "rerun-2026-11-03/gemma-31b/base/hinduism/native/population/prompt-english": {
        "43756f2b68f8975c": "correct", "df09eb678500c4c5": "correct",
    },
    "rerun-2026-11-03/haiku/base/buddhism/native/population/prompt-native": {
        "0cc27297653e8b4f": "correct", "fd1bc47cab2e0399": "correct",
    },
    "rerun-2026-11-03/haiku/base/hinduism/native/population/prompt-english": {
        "0be36a7c8205b3cb": "correct",
    },
    "rerun-2026-11-03/kimi/base/hinduism/native/population/prompt-english": {
        "afac31a7253cf2e1": "correct",
    },
    "rerun-2026-11-03/opus/base/buddhism/native/population/prompt-english": {
        "b0d72836bb18cc8a": "correct",
    },
    "rerun-2026-11-03/opus/base/hinduism/native/population/prompt-english": {
        "0589c8e453aa4eba": "correct", "40c80bf0f2e77465": "correct", "42a036c2d35997c5": "correct",
        "43756f2b68f8975c": "correct", "54c5474e9ca17426": "correct", "571cd582c9769d06": "correct",
        "670a8f73e63af90c": "correct", "95fc8931bc95c37e": "correct", "ae63380674766933": "correct",
        "afac31a7253cf2e1": "correct", "ba01abb626d109c9": "correct", "df09eb678500c4c5": "correct",
        "e1d083cadf0a1d16": "correct", "ef2171c87321c566": "correct", "ffccefa5f2fe1ef3": "correct",
    },
    "rerun-2026-11-03/sol/base/hinduism/native/population/prompt-english": {
        "0589c8e453aa4eba": "correct", "40c80bf0f2e77465": "correct", "42a036c2d35997c5": "correct",
        "43756f2b68f8975c": "correct", "571cd582c9769d06": "correct", "95fc8931bc95c37e": "correct",
        "ae63380674766933": "correct", "afac31a7253cf2e1": "correct", "ba01abb626d109c9": "correct",
        "ef2171c87321c566": "correct", "ffccefa5f2fe1ef3": "correct",
    },
    "rerun-2026-11-03/sonnet/base/hinduism/native/population/prompt-english": {
        "0589c8e453aa4eba": "correct", "54c5474e9ca17426": "correct", "571cd582c9769d06": "correct",
        "670a8f73e63af90c": "correct", "e1d083cadf0a1d16": "correct",
    },
    "rerun-2026-11-03/terra/base/hinduism/native/population/prompt-english": {
        "40c80bf0f2e77465": "correct",
    },
    "rerun-2026-11-03/terra/base/judaism/native/population/prompt-english": {
        "39ddd585d08cd19b": "correct", "99bc3590cea6d244": "correct", "a2f15831fd97d359": "correct",
        "bedcb00dd5028f6d": "correct",
    },
    "sol/base/hinduism/native/population/prompt-english": {
        "a9ccd5c6a893ff1a": "correct",
    },
    "terra/base/judaism/native/population/prompt-english": {
        "194b9ceddcd819f7": "correct", "253a91c24af287ee": "correct", "42db23be5ed58b5a": "correct",
    },
}


# The rerun models whose collection was complete when the registry was derived. qwen3-32b and gpt-oss-20b
# were still collecting, so they are not pinned, and the counts below cannot drift with them.
RERUN_COMPLETE_MODELS = frozenset({
    "argon", "astra", "beam", "deepseek-v4-pro", "fable", "gemini-flash", "gemma-31b", "haiku", "kimi", "luna",
    "opus", "sol", "sonnet", "terra",
})


def test_registered_set_size():
    assert {f.split("/")[1] for f in FLIPS if f.startswith("rerun-")} <= RERUN_COMPLETE_MODELS

    def outcomes(rerun: bool) -> Counter:
        return Counter(
            o for folder, cells in FLIPS.items() if folder.startswith("rerun-") == rerun for o in cells.values()
        )

    assert outcomes(rerun=False) == {"correct": 20, "incorrect": 2}
    assert outcomes(rerun=True) == {"correct": 133, "incorrect": 1}


@pytest.mark.parametrize("folder", sorted(FLIPS))
def test_registered_cells_are_graded_as_registered(folder):
    path = RUNS / folder / "answers.jsonl"
    if not path.exists():
        pytest.skip(f"{folder} evidence not present")
    rows = (json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    answers = {d["question_id"]: d for d in rows if d["task"] == "verify_source"}
    for qid, outcome in FLIPS[folder].items():
        assert qid in answers, f"{folder}: registered cell {qid} has no verify_source answer"
        q = answers[qid]["question"]
        metrics = score_answer(
            "verify_source", answers[qid]["answer"] or "", q["expected"], language=q["source"]["language"]
        )
        assert metrics["outcome"] == outcome, (folder, qid, metrics)
