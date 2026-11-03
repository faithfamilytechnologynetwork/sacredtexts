# Findings

From 32637 scored answers in finished files in `runs/facct-2026-11-03`. A file still being collected is not here.

## Takeaway

One accuracy number ranks the wrong thing. It mixes three different facts: a habit of saying no, a prompt language that turns quoting and citing on and off, and a scorer that reads only Western digits. A model can reject every fake, quote a verse it cannot name, and write the right citation in Arabic digits, and the leaderboard will call the first knowledge and the third a miss.

## The story

A leaderboard of theological accuracy will rank the wrong thing.

The careful model refuses. Refusal is removed from accuracy, so the model that declines the hard verse outranks the model that answers it and is wrong. On verify, the easy point is saying no to a passage from somewhere else. The hard point is recognizing the real verse. gpt-oss-20b takes every easy point in the finished file and misses most of the real ones. Published as one accuracy, that is knowledge. It is a preference for no.

The fluent model can quote a verse it cannot cite, or cite a verse it cannot quote. Gemini Flash, given the Qur'an in Arabic, does both. Given the same verses in English, it still quotes them and almost never names them. Given the Hebrew text in Hebrew, it names every verse and quotes none. The prompt language is choosing which skill is visible. A single Christianity number averages those into a tradition the model does not have.

And the score itself has a script. A citation written with Arabic digits is the right verse and a wrong answer. The benchmark then reports that the model does not know where the verse is. The finding and the instrument have to be read together, or the paper ranks a refusal policy, a prompt language, and a Latin-digit rule.

The negative item is not one test either. A Guru Granth Sahib question shown Arabic, or a Pali verse shown Gurmukhi, is an alphabet check. A Talmud question shown the Bible, and a Book of Mormon question shown a papal encyclical, are canon checks. One verify accuracy gives the alphabet check and the canon check the same weight.

## Models believe a fake more easily than the real text

On verify, a correct `no` means the model rejected a passage that is not from the named edition. A correct `yes` means it recognized a passage that is. Refusals are counted separately.

| model | real text (`yes`) | not from the edition (`no`) |
|---|---:|---:|
| argon | 99% of 257, refused 0 | 100% of 252, refused 1 |
| astra | 94% of 257, refused 0 | 98% of 253, refused 0 |
| beam | 85% of 255, refused 2 | 97% of 253, refused 0 |
| deepseek-v4-pro | 69% of 257, refused 0 | 98% of 253, refused 0 |
| fable | 93% of 238, refused 19 | 100% of 241, refused 12 |
| gemini-flash | 94% of 257, refused 0 | 99% of 253, refused 0 |
| gemma-31b | 63% of 249, refused 8 | 97% of 249, refused 4 |
| gpt-oss-20b | 12% of 248, refused 9 | 99% of 253, refused 0 |
| haiku | 72% of 183, refused 74 | 100% of 207, refused 46 |
| kimi | 87% of 256, refused 1 | 98% of 252, refused 1 |
| luna | 64% of 256, refused 1 | 98% of 248, refused 5 |
| opus | 90% of 257, refused 0 | 99% of 253, refused 0 |
| qwen3-32b | 68% of 233, refused 24 | 90% of 236, refused 17 |
| sol | 93% of 257, refused 0 | 98% of 253, refused 0 |
| sonnet | 53% of 163, refused 94 | 100% of 217, refused 36 |
| terra | 89% of 257, refused 0 | 99% of 253, refused 0 |

A model that is sure about fakes and unsure about the real text will look accurate on a set that is half `no`. That accuracy is not recognition.

## The negative item is an alphabet check for some traditions

A correct `no` is not the same question in every file. Sikhism, the Sanskrit Gita, the Pali Dhammapada, and the Greek New Testament are shown a passage in another script, because this corpus has no second work in Gurmukhi, Devanagari, Pali, or Greek. Islam is shown a hadith. The Talmud is shown the Bible. The Book of Mormon is shown a papal encyclical, and the encyclical is shown the Book of Mormon. Refusals are out of the percent.

| negative the model was shown | correct no | wrong yes | refused |
|---|---:|---:|---:|
| Different script | 100% (1259/1261) | 2 | 67 |
| NRSV shown the Book of Mormon | 100% (238/239) | 1 | 1 |
| Qur'an shown a hadith | 97% (687/708) | 21 | 12 |
| Encyclical shown the Book of Mormon | 98% (232/237) | 5 | 3 |
| Other same-script negative | 99% (549/556) | 7 | 4 |
| Talmud shown the Bible | 95% (650/685) | 35 | 35 |
| Book of Mormon shown an encyclical | 100% (240/240) | 0 | 0 |

Saying no to a different alphabet is nearly automatic. Saying no to the Bible when the question names the Talmud, and saying no to an encyclical when the question names the Book of Mormon, is where the errors are. The reverse pair is not the same: shown a Book of Mormon verse and asked if it is the encyclical, models almost always say no. A verify accuracy that averages these items ranks a tradition by how its negative was built.

## Quoting and citing are different skills

Each finished file, retrieve against cite. A wide gap means the model can do one and not the other. Refusals are out of the percent and shown beside it.

| model | file | retrieve | cite |
|---|---|---:|---:|
| luna | `hinduism/english/population` | 0% (0/13, refused 17) | 100% (30/30, refused 0) |
| haiku | `christianity/native/greek/population/prompt-english` | 0% (0/9, refused 0) | 100% (9/9, refused 0) |
| kimi | `hinduism/english/population` | 0% (0/26, refused 4) | 97% (29/30, refused 0) |
| beam | `hinduism/english/population` | 0% (0/23, refused 7) | 97% (29/30, refused 0) |
| terra | `hinduism/english/population` | 7% (2/30, refused 0) | 100% (30/30, refused 0) |
| luna | `hinduism/native/population/prompt-english` | 7% (2/28, refused 2) | 100% (30/30, refused 0) |
| sonnet | `hinduism/english/population` | 0% (0/7, refused 23) | 80% (24/30, refused 0) |
| haiku | `buddhism/native/population/prompt-english` | 0% (0/4, refused 26) | 80% (24/30, refused 0) |
| kimi | `hinduism/native/population/prompt-english` | 23% (7/30, refused 0) | 100% (30/30, refused 0) |
| gemini-flash | `hinduism/english/population` | 23% (7/30, refused 0) | 100% (30/30, refused 0) |
| deepseek-v4-pro | `islam/english/population` | 23% (7/30, refused 0) | 100% (30/30, refused 0) |
| argon | `hinduism/english/population` | 24% (7/29, refused 1) | 100% (30/30, refused 0) |
| gemma-31b | `islam/native/population/prompt-native` | 0% (0/30, refused 0) | 73% (22/30, refused 0) |
| luna | `hinduism/native/population/prompt-native` | 27% (6/22, refused 8) | 100% (30/30, refused 0) |
| gemini-flash | `buddhism/native/population/prompt-english` | 30% (9/30, refused 0) | 100% (30/30, refused 0) |
| deepseek-v4-pro | `hinduism/english/population` | 0% (0/28, refused 2) | 70% (21/30, refused 0) |
| deepseek-v4-pro | `buddhism/native/population/prompt-english` | 20% (6/30, refused 0) | 90% (27/30, refused 0) |
| deepseek-v4-pro | `hinduism/native/population/prompt-english` | 30% (9/30, refused 0) | 97% (29/30, refused 0) |
| luna | `christianity/native/greek/population/prompt-native` | 33% (3/9, refused 0) | 100% (9/9, refused 0) |
| kimi | `christianity/native/greek/population/prompt-native` | 33% (3/9, refused 0) | 100% (9/9, refused 0) |
| deepseek-v4-pro | `christianity/native/greek/population/prompt-english` | 33% (3/9, refused 0) | 100% (9/9, refused 0) |
| astra | `hinduism/english/population` | 33% (10/30, refused 0) | 100% (30/30, refused 0) |
| sonnet | `islam/english/population` | 35% (8/23, refused 7) | 100% (30/30, refused 0) |
| astra | `judaism/native/population/prompt-english` | 8% (1/12, refused 18) | 73% (22/30, refused 0) |
| haiku | `christianity/english/population` | 22% (2/9, refused 21) | 86% (25/29, refused 1) |
| kimi | `hinduism/native/population/prompt-native` | 35% (7/20, refused 10) | 97% (29/30, refused 0) |
| beam | `buddhism/native/population/prompt-english` | 25% (7/28, refused 2) | 87% (26/30, refused 0) |
| sol | `hinduism/english/population` | 37% (11/30, refused 0) | 97% (29/30, refused 0) |
| gemma-31b | `islam/native/population/prompt-english` | 3% (1/30, refused 0) | 63% (19/30, refused 0) |
| kimi | `buddhism/native/population/prompt-english` | 34% (10/29, refused 1) | 93% (28/30, refused 0) |
| haiku | `christianity/native/masoretic/population/prompt-english` | 14% (3/21, refused 0) | 71% (15/21, refused 0) |
| beam | `christianity/native/masoretic/population/prompt-native` | 43% (9/21, refused 0) | 100% (21/21, refused 0) |
| sol | `encyclicals/english/population` | 0% (0/4, refused 26) | 57% (17/30, refused 0) |
| qwen3-32b | `christianity/english/population` | 0% (0/30, refused 0) | 57% (17/30, refused 0) |
| luna | `islam/native/population/prompt-native` | 43% (13/30, refused 0) | 100% (30/30, refused 0) |
| gemma-31b | `islam/english/population` | 0% (0/30, refused 0) | 57% (17/30, refused 0) |
| argon | `encyclicals/english/population` | 0% (0/2, refused 28) | 57% (17/30, refused 0) |
| haiku | `hinduism/native/population/prompt-native` | 33% (7/21, refused 9) | 89% (25/28, refused 2) |
| beam | `christianity/native/greek/population/prompt-english` | 44% (4/9, refused 0) | 100% (9/9, refused 0) |
| astra | `judaism/native/population/prompt-native` | 11% (2/18, refused 12) | 67% (20/30, refused 0) |
| kimi | `christianity/native/greek/population/prompt-english` | 33% (3/9, refused 0) | 89% (8/9, refused 0) |
| haiku | `christianity/native/masoretic/population/prompt-native` | 10% (2/21, refused 0) | 65% (13/20, refused 1) |
| sol | `judaism/native/population/prompt-english` | 6% (1/17, refused 13) | 60% (18/30, refused 0) |
| terra | `hinduism/native/population/prompt-english` | 43% (13/30, refused 0) | 97% (29/30, refused 0) |
| luna | `buddhism/native/population/prompt-english` | 33% (10/30, refused 0) | 87% (26/30, refused 0) |
| fable | `judaism/english/population` | 0% (0/11, refused 19) | 53% (16/30, refused 0) |
| luna | `christianity/english/population` | 40% (4/10, refused 20) | 93% (28/30, refused 0) |
| gemini-flash | `islam/english/population` | 47% (9/19, refused 11) | 100% (30/30, refused 0) |
| deepseek-v4-pro | `hinduism/native/population/prompt-native` | 47% (14/30, refused 0) | 97% (29/30, refused 0) |
| opus | `hinduism/native/population/prompt-native` | 50% (15/30, refused 0) | 100% (30/30, refused 0) |
| gemini-flash | `encyclicals/english/population` | 0% (0/12, refused 18) | 50% (15/30, refused 0) |
| astra | `encyclicals/english/population` | 0% (0/1, refused 29) | 50% (15/30, refused 0) |
| argon | `hinduism/native/population/prompt-english` | 50% (15/30, refused 0) | 100% (30/30, refused 0) |
| terra | `buddhism/native/population/prompt-english` | 50% (15/30, refused 0) | 97% (29/30, refused 0) |
| gemini-flash | `hinduism/native/population/prompt-native` | 50% (15/30, refused 0) | 97% (29/30, refused 0) |
| terra | `judaism/native/population/prompt-native` | 3% (1/30, refused 0) | 50% (15/30, refused 0) |
| sonnet | `hinduism/native/population/prompt-english` | 53% (16/30, refused 0) | 100% (30/30, refused 0) |
| sol | `hinduism/native/population/prompt-native` | 53% (16/30, refused 0) | 100% (30/30, refused 0) |
| sol | `hinduism/native/population/prompt-english` | 53% (16/30, refused 0) | 100% (30/30, refused 0) |
| gemini-flash | `judaism/english/population` | 0% (0/2, refused 28) | 47% (14/30, refused 0) |
| gemini-flash | `hinduism/native/population/prompt-english` | 53% (16/30, refused 0) | 100% (30/30, refused 0) |
| fable | `hinduism/english/population` | 53% (16/30, refused 0) | 100% (30/30, refused 0) |
| astra | `hinduism/native/population/prompt-native` | 53% (16/30, refused 0) | 100% (30/30, refused 0) |
| argon | `hinduism/native/population/prompt-native` | 53% (16/30, refused 0) | 100% (30/30, refused 0) |
| kimi | `islam/english/population` | 54% (14/26, refused 4) | 100% (30/30, refused 0) |
| sol | `judaism/native/population/prompt-native` | 5% (1/20, refused 10) | 50% (15/30, refused 0) |
| beam | `hinduism/native/population/prompt-english` | 52% (15/29, refused 1) | 97% (29/30, refused 0) |
| terra | `christianity/native/greek/population/prompt-native` | 56% (5/9, refused 0) | 100% (9/9, refused 0) |
| sonnet | `christianity/native/greek/population/prompt-native` | 56% (5/9, refused 0) | 100% (9/9, refused 0) |
| sonnet | `christianity/native/greek/population/prompt-english` | 56% (5/9, refused 0) | 100% (9/9, refused 0) |
| deepseek-v4-pro | `christianity/native/greek/population/prompt-native` | 56% (5/9, refused 0) | 100% (9/9, refused 0) |
| terra | `hinduism/native/population/prompt-native` | 57% (17/30, refused 0) | 100% (30/30, refused 0) |
| sonnet | `buddhism/native/population/prompt-english` | 50% (15/30, refused 0) | 7% (2/30, refused 0) |
| opus | `hinduism/native/population/prompt-english` | 57% (17/30, refused 0) | 100% (30/30, refused 0) |
| fable | `hinduism/native/population/prompt-english` | 57% (17/30, refused 0) | 100% (30/30, refused 0) |
| astra | `hinduism/native/population/prompt-english` | 57% (17/30, refused 0) | 100% (30/30, refused 0) |
| argon | `buddhism/native/population/prompt-english` | 53% (16/30, refused 0) | 97% (29/30, refused 0) |
| sonnet | `hinduism/native/population/prompt-native` | 50% (15/30, refused 0) | 93% (28/30, refused 0) |
| luna | `christianity/native/masoretic/population/prompt-native` | 52% (11/21, refused 0) | 95% (20/21, refused 0) |
| beam | `christianity/native/masoretic/population/prompt-english` | 52% (11/21, refused 0) | 95% (20/21, refused 0) |
| beam | `hinduism/native/population/prompt-native` | 59% (17/29, refused 1) | 100% (30/30, refused 0) |
| fable | `hinduism/native/population/prompt-native` | 57% (17/30, refused 0) | 97% (29/30, refused 0) |
| terra | `judaism/native/population/prompt-english` | 0% (0/30, refused 0) | 40% (12/30, refused 0) |
| terra | `judaism/english/population` | 0% (0/25, refused 5) | 40% (12/30, refused 0) |
| terra | `encyclicals/english/population` | 0% (0/29, refused 1) | 40% (12/30, refused 0) |
| kimi | `islam/native/population/prompt-native` | 60% (18/30, refused 0) | 100% (30/30, refused 0) |
| kimi | `islam/native/population/prompt-english` | 60% (18/30, refused 0) | 100% (30/30, refused 0) |
| gemma-31b | `christianity/english/population` | 0% (0/30, refused 0) | 40% (12/30, refused 0) |
| gemini-flash | `judaism/native/population/prompt-native` | 0% (0/30, refused 0) | 40% (12/30, refused 0) |
| deepseek-v4-pro | `islam/native/population/prompt-native` | 17% (5/30, refused 0) | 57% (17/30, refused 0) |
| beam | `christianity/english/population` | 60% (18/30, refused 0) | 100% (30/30, refused 0) |
| opus | `judaism/native/population/prompt-native` | 0% (0/2, refused 28) | 39% (11/28, refused 2) |
| opus | `hinduism/english/population` | 61% (14/23, refused 7) | 100% (30/30, refused 0) |
| sonnet | `christianity/native/masoretic/population/prompt-native` | 52% (11/21, refused 0) | 90% (19/21, refused 0) |
| terra | `christianity/native/masoretic/population/prompt-english` | 57% (12/21, refused 0) | 95% (20/21, refused 0) |
| luna | `christianity/native/masoretic/population/prompt-english` | 57% (12/21, refused 0) | 95% (20/21, refused 0) |
| argon | `christianity/native/masoretic/population/prompt-native` | 62% (13/21, refused 0) | 100% (21/21, refused 0) |
| fable | `encyclicals/english/population` | 12% (2/16, refused 14) | 50% (15/30, refused 0) |
| luna | `islam/english/population` | 63% (12/19, refused 11) | 100% (30/30, refused 0) |
| qwen3-32b | `islam/native/population/prompt-english` | 0% (0/30, refused 0) | 37% (11/30, refused 0) |
| gemini-flash | `judaism/native/population/prompt-english` | 0% (0/14, refused 16) | 37% (11/30, refused 0) |
| beam | `islam/native/population/prompt-native` | 63% (19/30, refused 0) | 100% (30/30, refused 0) |
| astra | `sikhism/native/population/prompt-english` | 0% (0/3, refused 27) | 37% (11/30, refused 0) |
| argon | `judaism/native/population/prompt-native` | 0% (0/15, refused 15) | 37% (11/30, refused 0) |
| fable | `judaism/native/population/prompt-english` | 4% (1/27, refused 3) | 40% (12/30, refused 0) |
| beam | `islam/english/population` | 65% (17/26, refused 4) | 100% (30/30, refused 0) |
| terra | `christianity/native/masoretic/population/prompt-native` | 62% (13/21, refused 0) | 95% (20/21, refused 0) |
| sol | `sikhism/native/population/prompt-english` | 0% (0/3, refused 27) | 33% (10/30, refused 0) |
| qwen3-32b | `islam/english/population` | 0% (0/30, refused 0) | 33% (10/30, refused 0) |
| qwen3-32b | `christianity/native/greek/population/prompt-native` | 0% (0/9, refused 0) | 33% (3/9, refused 0) |
| luna | `encyclicals/english/population` | 0% (0/28, refused 2) | 33% (10/30, refused 0) |
| kimi | `christianity/native/masoretic/population/prompt-english` | 57% (12/21, refused 0) | 90% (19/21, refused 0) |
| gemma-31b | `christianity/native/greek/population/prompt-native` | 0% (0/9, refused 0) | 33% (3/9, refused 0) |
| gemma-31b | `christianity/native/greek/population/prompt-english` | 0% (0/9, refused 0) | 33% (3/9, refused 0) |
| deepseek-v4-pro | `encyclicals/english/population` | 0% (0/29, refused 1) | 33% (10/30, refused 0) |
| argon | `book-of-mormon/english/population` | 63% (19/30, refused 0) | 97% (29/30, refused 0) |
| terra | `christianity/native/greek/population/prompt-english` | 67% (6/9, refused 0) | 100% (9/9, refused 0) |
| opus | `islam/english/population` | 67% (20/30, refused 0) | 100% (30/30, refused 0) |
| luna | `christianity/native/greek/population/prompt-english` | 67% (6/9, refused 0) | 100% (9/9, refused 0) |
| deepseek-v4-pro | `christianity/native/masoretic/population/prompt-native` | 67% (14/21, refused 0) | 100% (21/21, refused 0) |
| beam | `christianity/native/greek/population/prompt-native` | 56% (5/9, refused 0) | 89% (8/9, refused 0) |
| argon | `christianity/native/greek/population/prompt-english` | 67% (6/9, refused 0) | 100% (9/9, refused 0) |
| terra | `islam/english/population` | 70% (21/30, refused 0) | 100% (30/30, refused 0) |
| sol | `sikhism/native/population/prompt-native` | 0% (0/8, refused 22) | 30% (9/30, refused 0) |
| kimi | `judaism/english/population` | 0% (0/16, refused 14) | 30% (9/30, refused 0) |
| haiku | `islam/native/population/prompt-native` | 67% (20/30, refused 0) | 97% (29/30, refused 0) |
| beam | `islam/native/population/prompt-english` | 70% (21/30, refused 0) | 100% (30/30, refused 0) |
| argon | `judaism/native/population/prompt-english` | 0% (0/17, refused 13) | 30% (9/30, refused 0) |
| luna | `book-of-mormon/english/population` | 27% (8/30, refused 0) | 57% (17/30, refused 0) |
| qwen3-32b | `christianity/native/masoretic/population/prompt-native` | 0% (0/21, refused 0) | 29% (6/21, refused 0) |
| argon | `christianity/english/population` | 73% (22/30, refused 0) | 100% (30/30, refused 0) |
| qwen3-32b | `islam/native/population/prompt-native` | 0% (0/30, refused 0) | 27% (8/30, refused 0) |
| opus | `judaism/native/population/prompt-english` | 0% (0/3, refused 27) | 27% (8/30, refused 0) |
| luna | `judaism/native/population/prompt-english` | 0% (0/25, refused 5) | 27% (8/30, refused 0) |
| gemma-31b | `hinduism/native/population/prompt-native` | 0% (0/30, refused 0) | 27% (8/30, refused 0) |
| gemma-31b | `hinduism/native/population/prompt-english` | 0% (0/30, refused 0) | 27% (8/30, refused 0) |
| terra | `book-of-mormon/english/population` | 47% (14/30, refused 0) | 73% (22/30, refused 0) |
| terra | `christianity/english/population` | 67% (18/27, refused 3) | 93% (28/30, refused 0) |
| gemini-flash | `book-of-mormon/english/population` | 61% (17/28, refused 2) | 87% (26/30, refused 0) |
| gemini-flash | `christianity/native/masoretic/population/prompt-native` | 71% (15/21, refused 0) | 95% (20/21, refused 0) |
| sonnet | `christianity/native/masoretic/population/prompt-english` | 57% (12/21, refused 0) | 81% (17/21, refused 0) |
| fable | `sikhism/native/population/prompt-native` | 0% (0/12, refused 18) | 23% (7/30, refused 0) |
| deepseek-v4-pro | `judaism/native/population/prompt-english` | 0% (0/30, refused 0) | 23% (7/30, refused 0) |
| beam | `judaism/english/population` | 0% (0/1, refused 29) | 23% (7/30, refused 0) |
| argon | `islam/english/population` | 77% (23/30, refused 0) | 100% (30/30, refused 0) |
| sol | `christianity/native/greek/population/prompt-native` | 78% (7/9, refused 0) | 100% (9/9, refused 0) |
| sol | `christianity/native/greek/population/prompt-english` | 78% (7/9, refused 0) | 100% (9/9, refused 0) |
| argon | `christianity/native/greek/population/prompt-native` | 78% (7/9, refused 0) | 100% (9/9, refused 0) |
| qwen3-32b | `christianity/native/greek/population/prompt-english` | 0% (0/9, refused 0) | 22% (2/9, refused 0) |
| kimi | `encyclicals/english/population` | 8% (2/25, refused 5) | 30% (9/30, refused 0) |
| fable | `judaism/native/population/prompt-native` | 5% (1/19, refused 11) | 27% (8/30, refused 0) |
| gemini-flash | `christianity/english/population` | 79% (23/29, refused 1) | 100% (30/30, refused 0) |
| deepseek-v4-pro | `judaism/native/population/prompt-native` | 0% (0/22, refused 8) | 21% (6/29, refused 1) |
| qwen3-32b | `hinduism/native/population/prompt-native` | 0% (0/30, refused 0) | 20% (6/30, refused 0) |
| luna | `judaism/native/population/prompt-native` | 0% (0/20, refused 10) | 20% (6/30, refused 0) |
| deepseek-v4-pro | `judaism/english/population` | 0% (0/27, refused 3) | 20% (6/30, refused 0) |
| deepseek-v4-pro | `islam/native/population/prompt-english` | 77% (23/30, refused 0) | 97% (29/30, refused 0) |
| deepseek-v4-pro | `book-of-mormon/english/population` | 33% (10/30, refused 0) | 53% (16/30, refused 0) |
| astra | `sikhism/native/population/prompt-native` | 0% (0/7, refused 23) | 20% (6/30, refused 0) |
| argon | `sikhism/native/population/prompt-english` | 0% (0/21, refused 9) | 20% (6/30, refused 0) |
| sol | `christianity/native/masoretic/population/prompt-english` | 81% (17/21, refused 0) | 100% (21/21, refused 0) |
| kimi | `christianity/native/masoretic/population/prompt-native` | 71% (15/21, refused 0) | 90% (19/21, refused 0) |
| gemini-flash | `christianity/native/masoretic/population/prompt-english` | 76% (16/21, refused 0) | 95% (20/21, refused 0) |
| deepseek-v4-pro | `christianity/native/masoretic/population/prompt-english` | 71% (15/21, refused 0) | 90% (19/21, refused 0) |
| sol | `buddhism/native/population/prompt-english` | 83% (25/30, refused 0) | 100% (30/30, refused 0) |
| opus | `buddhism/native/population/prompt-english` | 83% (25/30, refused 0) | 100% (30/30, refused 0) |
| fable | `islam/english/population` | 83% (25/30, refused 0) | 100% (30/30, refused 0) |
| astra | `buddhism/native/population/prompt-english` | 83% (25/30, refused 0) | 100% (30/30, refused 0) |
| kimi | `judaism/native/population/prompt-native` | 0% (0/27, refused 3) | 17% (5/30, refused 0) |
| argon | `sikhism/native/population/prompt-native` | 0% (0/22, refused 8) | 17% (5/30, refused 0) |
| kimi | `christianity/english/population` | 77% (17/22, refused 8) | 93% (28/30, refused 0) |
| opus | `encyclicals/english/population` | 43% (3/7, refused 23) | 59% (17/29, refused 1) |
| sol | `christianity/native/masoretic/population/prompt-native` | 86% (18/21, refused 0) | 100% (21/21, refused 0) |
| opus | `christianity/native/masoretic/population/prompt-native` | 86% (18/21, refused 0) | 100% (21/21, refused 0) |
| astra | `christianity/native/masoretic/population/prompt-native` | 86% (18/21, refused 0) | 100% (21/21, refused 0) |
| astra | `christianity/native/masoretic/population/prompt-english` | 86% (18/21, refused 0) | 100% (21/21, refused 0) |
| argon | `christianity/native/masoretic/population/prompt-english` | 86% (18/21, refused 0) | 100% (21/21, refused 0) |
| sonnet | `judaism/native/population/prompt-native` | 0% (0/3, refused 27) | 14% (3/21, refused 9) |
| qwen3-32b | `christianity/native/masoretic/population/prompt-english` | 0% (0/21, refused 0) | 14% (3/21, refused 0) |
| opus | `sikhism/native/population/prompt-native` | 0% (0/1, refused 29) | 14% (3/21, refused 9) |
| gemma-31b | `christianity/native/masoretic/population/prompt-native` | 0% (0/21, refused 0) | 14% (3/21, refused 0) |
| haiku | `book-of-mormon/english/population` | 33% (1/3, refused 27) | 19% (5/26, refused 4) |
| terra | `sikhism/native/population/prompt-english` | 0% (0/30, refused 0) | 13% (4/30, refused 0) |
| qwen3-32b | `hinduism/native/population/prompt-english` | 0% (0/30, refused 0) | 13% (4/30, refused 0) |
| gemini-flash | `sikhism/native/population/prompt-native` | 0% (0/30, refused 0) | 13% (4/30, refused 0) |
| gemini-flash | `islam/native/population/prompt-english` | 87% (26/30, refused 0) | 100% (30/30, refused 0) |
| opus | `christianity/native/greek/population/prompt-native` | 89% (8/9, refused 0) | 100% (9/9, refused 0) |
| gemini-flash | `christianity/native/greek/population/prompt-native` | 89% (8/9, refused 0) | 100% (9/9, refused 0) |
| gemini-flash | `christianity/native/greek/population/prompt-english` | 89% (8/9, refused 0) | 100% (9/9, refused 0) |
| fable | `christianity/native/greek/population/prompt-english` | 89% (8/9, refused 0) | 100% (9/9, refused 0) |
| astra | `christianity/native/greek/population/prompt-native` | 89% (8/9, refused 0) | 100% (9/9, refused 0) |
| astra | `christianity/native/greek/population/prompt-english` | 89% (8/9, refused 0) | 100% (9/9, refused 0) |
| fable | `sikhism/native/population/prompt-english` | 12% (3/24, refused 6) | 23% (7/30, refused 0) |
| gpt-oss-20b | `islam/english/population` | 0% (0/28, refused 2) | 10% (3/29, refused 1) |
| terra | `sikhism/native/population/prompt-native` | 0% (0/30, refused 0) | 10% (3/30, refused 0) |
| luna | `islam/native/population/prompt-english` | 90% (27/30, refused 0) | 100% (30/30, refused 0) |
| kimi | `judaism/native/population/prompt-english` | 0% (0/28, refused 2) | 10% (3/30, refused 0) |
| gemma-31b | `hinduism/english/population` | 0% (0/30, refused 0) | 10% (3/30, refused 0) |
| gemini-flash | `sikhism/native/population/prompt-english` | 0% (0/30, refused 0) | 10% (3/30, refused 0) |
| gemini-flash | `islam/native/population/prompt-native` | 90% (27/30, refused 0) | 100% (30/30, refused 0) |
| astra | `book-of-mormon/english/population` | 90% (27/30, refused 0) | 100% (30/30, refused 0) |
| fable | `christianity/native/masoretic/population/prompt-native` | 86% (18/21, refused 0) | 95% (20/21, refused 0) |
| gemma-31b | `christianity/native/masoretic/population/prompt-english` | 0% (0/21, refused 0) | 10% (2/21, refused 0) |
| opus | `christianity/native/masoretic/population/prompt-english` | 90% (19/21, refused 0) | 100% (21/21, refused 0) |
| haiku | `islam/native/population/prompt-english` | 81% (22/27, refused 3) | 90% (27/30, refused 0) |
| gpt-oss-20b | `islam/native/population/prompt-english` | 0% (0/29, refused 1) | 7% (2/28, refused 2) |
| fable | `islam/native/population/prompt-english` | 93% (27/29, refused 0) | 100% (30/30, refused 0) |
| sonnet | `christianity/english/population` | 83% (15/18, refused 12) | 90% (27/30, refused 0) |
| opus | `islam/native/population/prompt-english` | 93% (28/30, refused 0) | 100% (30/30, refused 0) |
| fable | `islam/native/population/prompt-native` | 93% (28/30, refused 0) | 100% (30/30, refused 0) |
| deepseek-v4-pro | `christianity/english/population` | 83% (25/30, refused 0) | 90% (27/30, refused 0) |
| beam | `encyclicals/english/population` | 33% (1/3, refused 27) | 27% (8/30, refused 0) |
| qwen3-32b | `judaism/native/population/prompt-native` | 0% (0/30, refused 0) | 7% (2/30, refused 0) |
| qwen3-32b | `judaism/native/population/prompt-english` | 0% (0/28, refused 2) | 7% (2/30, refused 0) |
| qwen3-32b | `judaism/english/population` | 0% (0/30, refused 0) | 7% (2/30, refused 0) |
| qwen3-32b | `hinduism/english/population` | 0% (0/30, refused 0) | 7% (2/30, refused 0) |
| luna | `sikhism/native/population/prompt-english` | 0% (0/6, refused 24) | 7% (2/30, refused 0) |
| gemma-31b | `book-of-mormon/english/population` | 0% (0/30, refused 0) | 7% (2/30, refused 0) |
| kimi | `book-of-mormon/english/population` | 61% (17/28, refused 2) | 67% (20/30, refused 0) |
| sonnet | `sikhism/native/population/prompt-native` | 0% (0/5, refused 25) | 6% (1/18, refused 12) |
| fable | `christianity/native/masoretic/population/prompt-english` | 95% (20/21, refused 0) | 90% (19/21, refused 0) |
| qwen3-32b | `book-of-mormon/english/population` | 0% (0/30, refused 0) | 3% (1/30, refused 0) |
| gpt-oss-20b | `christianity/english/population` | 0% (0/28, refused 2) | 3% (1/30, refused 0) |
| gemma-31b | `buddhism/native/population/prompt-english` | 0% (0/30, refused 0) | 3% (1/30, refused 0) |
| opus | `islam/native/population/prompt-native` | 97% (29/30, refused 0) | 100% (30/30, refused 0) |
| opus | `christianity/english/population` | 97% (29/30, refused 0) | 100% (30/30, refused 0) |
| opus | `book-of-mormon/english/population` | 93% (28/30, refused 0) | 90% (27/30, refused 0) |
| haiku | `hinduism/native/population/prompt-english` | 100% (7/7, refused 23) | 97% (29/30, refused 0) |
| fable | `christianity/english/population` | 100% (29/29, refused 1) | 97% (29/30, refused 0) |
| fable | `buddhism/native/population/prompt-english` | 90% (27/30, refused 0) | 93% (28/30, refused 0) |
| fable | `book-of-mormon/english/population` | 70% (21/30, refused 0) | 67% (20/30, refused 0) |
| astra | `islam/native/population/prompt-english` | 97% (29/30, refused 0) | 100% (30/30, refused 0) |
| argon | `islam/native/population/prompt-english` | 97% (29/30, refused 0) | 100% (30/30, refused 0) |
| sonnet | `book-of-mormon/english/population` | 35% (6/17, refused 13) | 32% (9/28, refused 2) |
| terra | `islam/native/population/prompt-native` | 100% (30/30, refused 0) | 100% (30/30, refused 0) |
| terra | `islam/native/population/prompt-english` | 100% (30/30, refused 0) | 100% (30/30, refused 0) |
| sonnet | `sikhism/native/population/prompt-english` | 0% (0/2, refused 28) | 0% (0/20, refused 10) |
| sonnet | `islam/native/population/prompt-native` | 100% (30/30, refused 0) | 100% (30/30, refused 0) |
| sonnet | `islam/native/population/prompt-english` | 100% (30/30, refused 0) | 100% (30/30, refused 0) |
| sol | `islam/native/population/prompt-native` | 100% (30/30, refused 0) | 100% (30/30, refused 0) |
| sol | `islam/native/population/prompt-english` | 100% (30/30, refused 0) | 100% (30/30, refused 0) |
| sol | `book-of-mormon/english/population` | 93% (28/30, refused 0) | 93% (28/30, refused 0) |
| qwen3-32b | `sikhism/native/population/prompt-native` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| qwen3-32b | `sikhism/native/population/prompt-english` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| qwen3-32b | `encyclicals/english/population` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| qwen3-32b | `buddhism/native/population/prompt-english` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| opus | `christianity/native/greek/population/prompt-english` | 100% (9/9, refused 0) | 100% (9/9, refused 0) |
| luna | `sikhism/native/population/prompt-native` | 0% (0/26, refused 4) | 0% (0/30, refused 0) |
| kimi | `sikhism/native/population/prompt-native` | 0% (0/28, refused 2) | 0% (0/30, refused 0) |
| kimi | `sikhism/native/population/prompt-english` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| haiku | `sikhism/native/population/prompt-native` | 0% (0/15, refused 15) | 0% (0/15, refused 15) |
| gpt-oss-20b | `sikhism/native/population/prompt-native` | 0% (0/20, refused 10) | 0% (0/30, refused 0) |
| gpt-oss-20b | `sikhism/native/population/prompt-english` | 0% (0/1, refused 29) | 0% (0/30, refused 0) |
| gpt-oss-20b | `judaism/native/population/prompt-native` | 0% (0/20, refused 10) | 0% (0/30, refused 0) |
| gpt-oss-20b | `islam/native/population/prompt-native` | 0% (0/27, refused 3) | 0% (0/29, refused 1) |
| gpt-oss-20b | `hinduism/native/population/prompt-native` | 0% (0/7, refused 23) | 0% (0/30, refused 0) |
| gpt-oss-20b | `hinduism/english/population` | 0% (0/3, refused 27) | 0% (0/30, refused 0) |
| gpt-oss-20b | `encyclicals/english/population` | 0% (0/1, refused 29) | 0% (0/30, refused 0) |
| gpt-oss-20b | `christianity/native/masoretic/population/prompt-native` | 0% (0/21, refused 0) | 0% (0/21, refused 0) |
| gpt-oss-20b | `christianity/native/masoretic/population/prompt-english` | 0% (0/21, refused 0) | 0% (0/20, refused 1) |
| gpt-oss-20b | `christianity/native/greek/population/prompt-native` | 0% (0/9, refused 0) | 0% (0/9, refused 0) |
| gpt-oss-20b | `christianity/native/greek/population/prompt-english` | 0% (0/9, refused 0) | 0% (0/9, refused 0) |
| gpt-oss-20b | `buddhism/native/population/prompt-english` | 0% (0/13, refused 17) | 0% (0/30, refused 0) |
| gpt-oss-20b | `book-of-mormon/english/population` | 0% (0/20, refused 10) | 0% (0/30, refused 0) |
| gemma-31b | `sikhism/native/population/prompt-native` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| gemma-31b | `sikhism/native/population/prompt-english` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| gemma-31b | `judaism/native/population/prompt-native` | 0% (0/28, refused 2) | 0% (0/30, refused 0) |
| gemma-31b | `judaism/native/population/prompt-english` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| gemma-31b | `judaism/english/population` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| gemma-31b | `encyclicals/english/population` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| fable | `christianity/native/greek/population/prompt-native` | 100% (9/9, refused 0) | 100% (9/9, refused 0) |
| deepseek-v4-pro | `sikhism/native/population/prompt-native` | 0% (0/26, refused 4) | 0% (0/30, refused 0) |
| deepseek-v4-pro | `sikhism/native/population/prompt-english` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| beam | `sikhism/native/population/prompt-native` | 0% (0/4, refused 26) | 0% (0/9, refused 21) |
| beam | `book-of-mormon/english/population` | 67% (6/9, refused 21) | 67% (20/30, refused 0) |
| astra | `islam/native/population/prompt-native` | 100% (30/30, refused 0) | 100% (30/30, refused 0) |
| argon | `islam/native/population/prompt-native` | 100% (30/30, refused 0) | 100% (30/30, refused 0) |

The flip is inside one model, on the same verses. Gemini Flash, Qur'an prompted in Arabic: quotation 28/30 and citation 30/30. The same file prompted in English: quotation 28/30 and citation 1/30. Hebrew Masoretic text prompted in Hebrew: citation 21/21, quotation 0/21. Prompted in English: citation 0/21 and quotation 0/21. Greek prompted in English: quotation 8/9, citation 0/9. Naming the verse and producing its words come apart, and the prompt language decides which one is available.

## Close wording that still scores incorrect

1611 incorrect answers still have token F1 of at least 0.70. The strict score is doing what it was built for: a near miss is not a hit. Most of them are Gemini Flash completions.

- beam, retrieve_quote: 98
- terra, retrieve_quote: 97
- gemini-flash, retrieve_quote: 90
- argon, retrieve_quote: 85
- argon, complete_unit: 82
- luna, complete_unit: 80
- beam, complete_unit: 79
- kimi, complete_unit: 75
- terra, complete_unit: 71
- kimi, retrieve_quote: 63
- sol, retrieve_quote: 62
- gemini-flash, complete_unit: 61
- deepseek-v4-pro, retrieve_quote: 59
- opus, complete_unit: 59
- astra, retrieve_quote: 57
- astra, complete_unit: 54
- fable, retrieve_quote: 52
- deepseek-v4-pro, complete_unit: 47
- fable, complete_unit: 46
- luna, retrieve_quote: 46
- sol, complete_unit: 43
- sonnet, retrieve_quote: 41
- haiku, complete_unit: 39
- opus, retrieve_quote: 39
- haiku, retrieve_quote: 37
- sonnet, complete_unit: 17
- qwen3-32b, complete_unit: 12
- gemma-31b, complete_unit: 6
- qwen3-32b, retrieve_quote: 6
- gemma-31b, retrieve_quote: 4
- gpt-oss-20b, retrieve_quote: 2
- gpt-oss-20b, complete_unit: 2

## A right citation in Arabic digits is scored wrong

61 incorrect citations are the right verse once Arabic-Indic digits are read as Western digits. 3074 wrong citations stay wrong after that fold.

- sonnet: 42
- fable: 5
- gpt-oss-20b: 5
- gemma-31b: 3
- haiku: 3
- qwen3-32b: 3

Examples:
- fable: expected `2 Nephi 17:17`, answered `This is Isaiah 7:17, quoted in the Book of Mormon as 2 Nephi 17:17.`
- fable: expected `Alma 3:17`, answered `2 Nephi 5:23... wait, let me verify. The quote "And again, I say he that departeth from thee shall no more be called thy seed; and I will bless thee, and whomsoever shall be called thy seed, henceforth and forever; and these were the promises of the Lord unto Nephi and to his seed" is found in Alma 3:17.`
- fable: expected `2 Nephi 15:18`, answered `This is from Isaiah 5:18, quoted in 2 Nephi 15:18.`

The cite score asks for the same characters as the Latin citation in the question file. A model that answers in the digits of the Qur'an is counted as naming a different book. That is the benchmark under-crediting a correct location, which is the failure the scorer was built to avoid.

## Another canon, accepted as this one

A verify `yes` on a `no` item means the model took a passage from somewhere else as the named edition. Across the finished files that happened twice.

**argon.** Asked whether this is the named edition, and said yes. The passage is Psalms 23:1 (Christianity, NRSV).

> The Lord is my shepherd, I shall not want.

Answer: Yes

**astra.** Asked whether this is the named edition, and said yes. The passage is Psalms 23:1 (Christianity, NRSV).

> The Lord is my shepherd, I shall not want.

Answer: Yes.

**astra.** Asked whether this is the named edition, and said yes. The passage is Daniel 2:42 (Christianity, NRSV).

> As the toes of the feet were part iron and part clay, so the kingdom shall be partly strong and partly brittle.

Answer: Yes.

**astra.** Asked whether this is the named edition, and said yes. The passage is 1 Kings 22:39 (Christianity, NRSV).

> Now the rest of the acts of Ahab, and all that he did, and the ivory house that he built, and all the cities that he built, are they not written in the Book of the Annals of the Ki

Answer: Yes.

**astra.** Asked whether this is the named edition, and said yes. The passage is 1 Chronicles 9:22 (Christianity, NRSV).

> All these, who were chosen as gatekeepers at the thresholds, were two hundred twelve. They were enrolled by genealogies in their villages. David and the seer Samuel established the

Answer: Yes.

**beam.** Asked whether this is the named edition, and said yes. The passage is Eruvin 61a:7 (Judaism, William Davidson Edition - Aramaic).

> מאן דתני אנשי לא משתבש דמוקים לה בנותן ומאן דתני אין אנשי לא משתבש דמוקים לה במודד

Answer: כן.

**beam.** Asked whether this is the named edition, and said yes. The passage is Ether 12:19 (Book of Mormon, 2013 edition).

> And there were many whose faith was so exceedingly strong, even before Christ came, who could not be kept from within the veil, but truly saw with their eyes the things which they 

Answer: Yes

**beam.** Asked whether this is the named edition, and said yes. The passage is 3 Nephi 22:13 (Book of Mormon, 2013 edition).

> And all thy children shall be taught of the Lord; and great shall be the peace of thy children.

Answer: Yes

**beam.** Asked whether this is the named edition, and said yes. The passage is Alma 60:7 (Book of Mormon, 2013 edition).

> Can you think to sit upon your thrones in a state of thoughtless stupor, while your enemies are spreading the work of death around you? Yea, while they are murdering thousands of y

Answer: Yes.

**beam.** Asked whether this is the named edition, and said yes. The passage is Sunan an-Nasa'i 3403 (Islam, sunnah.com English).

> Tell him to take her back, then divorce her while she is pure (not menstruating) or pregnant.

Answer: Yes

**beam.** Asked whether this is the named edition, and said yes. The passage is Sunan Ibn Majah 3628 (Islam, sunnah.com English).

> Whoever unexpectedly comes across a person suffering a calamity, and says: Al-hamdu Lillahil-ladhi ‘afani mim-mabtalaka bihi, wa faddalani ‘ala kathirin mimman khalaqa tafdila (Pra

Answer: Yes

**beam.** Asked whether this is the named edition, and said yes. The passage is Psalms 23:1 (Christianity, NRSV).

> The Lord is my shepherd, I shall not want.

Answer: Yes

**beam.** Asked whether this is the named edition, and said yes. The passage is Daniel 2:42 (Christianity, NRSV).

> As the toes of the feet were part iron and part clay, so the kingdom shall be partly strong and partly brittle.

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Sunan an-Nasa'i 1302 (Islam, sunnah.com English).

> I was sitting with the Messenger of Allah (ﷺ) and a man was standing and praying. When he bowed, prostrated and recited the tashahhud, he supplicated, and in his supplication he sa

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Sunan an-Nasa'i 3403 (Islam, sunnah.com English).

> Tell him to take her back, then divorce her while she is pure (not menstruating) or pregnant.

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Sunan Ibn Majah 3628 (Islam, sunnah.com English).

> Whoever unexpectedly comes across a person suffering a calamity, and says: Al-hamdu Lillahil-ladhi ‘afani mim-mabtalaka bihi, wa faddalani ‘ala kathirin mimman khalaqa tafdila (Pra

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Sunan Ibn Majah 1258 (Islam, sunnah.com English).

> The leader of the hypocrites in Al- Madinah died, and left instructions that the Prophet (ﷺ) should offer the funeral prayer for him and shroud him in his shirt. He offered the fun

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Sunan an-Nasa'i 3510 (Islam, sunnah.com Arabic).

> لاَ يَحِلُّ لاِمْرَأَةٍ تُؤْمِنُ بِاللَّهِ وَالْيَوْمِ الآخِرِ تَحِدُّ عَلَى مَيِّتٍ أَكْثَرَ مِنْ ثَلاَثَةِ أَيَّامٍ إِلاَّ عَلَى زَوْجٍ فَإِنَّهَا تَحِدُّ عَلَيْهِ أَرْبَعَةَ أَش

Answer: نعم

**gemini-flash.** Asked whether this is the named edition, and said yes. The passage is Ezekiel 16:19 (Christianity, NRSV).

> Also my bread that I gave you—I fed you with choice flour and oil and honey—you set it before them as a pleasing odor; and so it was, says the Lord God .

Answer: **Yes**

**gemini-flash.** Asked whether this is the named edition, and said yes. The passage is Exodus 29:40 (Christianity, NRSV).

> and with the first lamb one-tenth of a measure of choice flour mixed with one-fourth of a hin of beaten oil, and one-fourth of a hin of wine for a drink offering.

Answer: **Yes** (specifically, this is the translation of the biblical verse Exodus 29:40 as it appears within the text of the William Davidson Talmud, e.g., in tractates such as Menachot).

**gemma-31b.** Asked whether this is the named edition, and said yes. The passage is Alma 60:7 (Book of Mormon, 2013 edition).

> Can you think to sit upon your thrones in a state of thoughtless stupor, while your enemies are spreading the work of death around you? Yea, while they are murdering thousands of y

Answer: Yes

**gemma-31b.** Asked whether this is the named edition, and said yes. The passage is Sahih al-Bukhari 307 (Islam, sunnah.com English).

> One of the wives of Allah's Messenger (ﷺ) joined him in I`tikaf and she noticed blood and yellowish discharge (from her private parts) and put a dish under her when she prayed.

Answer: Yes

**gemma-31b.** Asked whether this is the named edition, and said yes. The passage is 2 Chronicles 26:15 (Christianity, NRSV).

> In Jerusalem he set up machines, invented by skilled workers, on the towers and the corners for shooting arrows and large stones. And his fame spread far, for he was marvelously he

Answer: Yes

**gemma-31b.** Asked whether this is the named edition, and said yes. The passage is Leviticus 11:21 (Christianity, NRSV).

> But among the winged insects that walk on all fours you may eat those that have jointed legs above their feet, with which to leap on the ground.

Answer: Yes

**gemma-31b.** Asked whether this is the named edition, and said yes. The passage is Judges 17:11 (Christianity, NRSV).

> The Levite agreed to stay with the man; and the young man became to him like one of his sons.

Answer: Yes

**gemma-31b.** Asked whether this is the named edition, and said yes. The passage is Exodus 30:38 (Christianity, NRSV).

> Whoever makes any like it to use as perfume shall be cut off from the people.

Answer: Yes

**gemma-31b.** Asked whether this is the named edition, and said yes. The passage is 1 Kings 1:23 (Christianity, NRSV).

> The king was told, 'Here is the prophet Nathan.' When he came in before the king, he did obeisance to the king, with his face to the ground.

Answer: Yes

**gemma-31b.** Asked whether this is the named edition, and said yes. The passage is Exodus 29:40 (Christianity, NRSV).

> and with the first lamb one-tenth of a measure of choice flour mixed with one-fourth of a hin of beaten oil, and one-fourth of a hin of wine for a drink offering.

Answer: Yes

**gpt-oss-20b.** Asked whether this is the named edition, and said yes. The passage is 1 Nephi 4:29 (Book of Mormon, 2013 edition).

> And it came to pass that I called after them, and they did hear me; wherefore they did cease to flee from my presence.

Answer: Yes.

**gpt-oss-20b.** Asked whether this is the named edition, and said yes. The passage is Yevamot 67b:1 (Judaism, William Davidson Edition - Aramaic).

> אין חוששין למיעוטא ואיבעית אימא לעולם קסבר חוששין למיעוטא דעבדינן ליה תקנתא כרב נחמן אמר שמואל

Answer: כן.

**kimi.** Asked whether this is the named edition, and said yes. The passage is Ezekiel 16:19 (Christianity, NRSV).

> Also my bread that I gave you—I fed you with choice flour and oil and honey—you set it before them as a pleasing odor; and so it was, says the Lord God .

Answer: Yes

**kimi.** Asked whether this is the named edition, and said yes. The passage is Exodus 30:38 (Christianity, NRSV).

> Whoever makes any like it to use as perfume shall be cut off from the people.

Answer: Yes

**kimi.** Asked whether this is the named edition, and said yes. The passage is 1 Kings 1:23 (Christianity, NRSV).

> The king was told, 'Here is the prophet Nathan.' When he came in before the king, he did obeisance to the king, with his face to the ground.

Answer: Yes

**kimi.** Asked whether this is the named edition, and said yes. The passage is Exodus 29:40 (Christianity, NRSV).

> and with the first lamb one-tenth of a measure of choice flour mixed with one-fourth of a hin of beaten oil, and one-fourth of a hin of wine for a drink offering.

Answer: Yes

**luna.** Asked whether this is the named edition, and said yes. The passage is Jami` at-Tirmidhi 2249 (Islam, sunnah.com Arabic).

> وَالَّذِي نَفْسِي بِيَدِهِ لاَ تَقُومُ السَّاعَةُ حَتَّى تُكَلِّمَ السِّبَاعُ الإِنْسَ وَحَتَّى تُكَلِّمَ الرَّجُلَ عَذَبَةُ سَوْطِهِ وَشِرَاكُ نَعْلِهِ وَتُخْبِرَهُ فَخِذُهُ بِمَا

Answer: نَعَمْ

**luna.** Asked whether this is the named edition, and said yes. The passage is Daniel 2:42 (Christianity, NRSV).

> As the toes of the feet were part iron and part clay, so the kingdom shall be partly strong and partly brittle.

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is Exodus 30:38 (Christianity, NRSV).

> Whoever makes any like it to use as perfume shall be cut off from the people.

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is 1 Kings 1:23 (Christianity, NRSV).

> The king was told, 'Here is the prophet Nathan.' When he came in before the king, he did obeisance to the king, with his face to the ground.

Answer: Yes.

**opus.** Asked whether this is the named edition, and said yes. The passage is Ezekiel 16:19 (Christianity, NRSV).

> Also my bread that I gave you—I fed you with choice flour and oil and honey—you set it before them as a pleasing odor; and so it was, says the Lord God .

Answer: **Yes.** I'm not fully certain, though. The verse is Ezekiel 16:19, which the Talmud quotes in Berakhot 32a. The wording doesn't match standard Tanakh translations like the JPS 1917 or 1985, but it does fit the adapted style the William Dav

**opus.** Asked whether this is the named edition, and said yes. The passage is Leviticus 14:19 (Christianity, NRSV).

> the priest shall offer the sin offering, to make atonement for the one to be cleansed from his uncleanness. Afterward he shall slaughter the burnt offering;

Answer: **Yes.** This appears to be the William Davidson edition's rendering of Leviticus 14:19, which the Talmud quotes in discussions of the order of offerings (for example, in tractate Zevachim). I can't verify the exact page, though. The wordin

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Bava Batra 32a:1 (Judaism, William Davidson Edition - Aramaic).

> ורבן שמעון בן גמליאל סבר ערער תרי והאמר רבי יוחנן דברי הכל אין ערער פחות משנים

Answer: כן.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Nedarim 52b:2 (Judaism, William Davidson Edition - Aramaic).

> לא קשיא מר כי אתריה ומר כי אתריה באתרא דרבנן קרו לחלבא חלבא ולקומא קומא באתריה דרבי יוסי לקומא נמי קרו ליה קומא דחלבא

Answer: כן, הטקסט שציינת הוא מן המסורה, ובעיקר מה kodeks Leningradensis (לנינגרד), שהוא המanuscript העברי המוקדם ביותר ששרד, ומכיל את מסכת ברכות, מסכת שבועות, וחלקים נוספים מהמסכתות. הטקסט שאתה מציין הוא מסורת מילולית או תקנית, כלומר הוא מתייחס לפר

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Alma 24:10 (Book of Mormon, 2013 edition).

> And I also thank my God, yea, my great God, that he hath granted unto us that we might repent of these things, and also that he hath forgiven us of those our many sins and murders 

Answer: Yes.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Dhammapada 165 (Buddhism, Chaṭṭha Saṅgāyana (VRI)).

> Attanā hi kataṃ pāpaṃ, attanā saṃkilissati; Attanā akataṃ pāpaṃ, attanāva visujjhati; Suddhī asuddhi paccattaṃ, nāñño aññaṃ visodhaye.

Answer: हाँ।

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Dhammapada 380 (Buddhism, Chaṭṭha Saṅgāyana (VRI)).

> Attā hi attano nātho, ko hi nātho paro siyā Attā hi attano gati; Tasmā saṃyamamattānaṃ , assaṃ bhadraṃva vāṇijo.

Answer: हाँ।

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Sunan an-Nasa'i 1366 (Islam, sunnah.com English).

> We fasted Ramadan with the Messenger of Allah (ﷺ), and the Prophet (ﷺ) did not lead us in Qiyam until there were seven days left of the month, then he led us in Qiyam until one-thi

Answer: Yes.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Sahih al-Bukhari 307 (Islam, sunnah.com English).

> One of the wives of Allah's Messenger (ﷺ) joined him in I`tikaf and she noticed blood and yellowish discharge (from her private parts) and put a dish under her when she prayed.

Answer: Yes.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Sunan Ibn Majah 634 (Islam, sunnah.com English).

> The Messenger of Allah (ﷺ) used to teach us the Tashah-hud as he used to teach us a Surah of the Qur’an. He used to say: ‘At-Tahiyyatul-Mubarakatus salawatut-tayyibatu lillah; As-s

Answer: Yes.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Sahih al-Bukhari 4671 (Islam, sunnah.com Arabic).

> جَنَّتَانِ مِنْ فِضَّةٍ، آنِيَتُهُمَا وَمَا فِيهِمَا وَجَنَّتَانِ مِنْ ذَهَبٍ آنِيَتُهُمَا وَمَا فِيهِمَا، وَمَا بَيْنَ الْقَوْمِ وَبَيْنَ أَنْ يَنْظُرُوا إِلَى رَبِّهِمْ إِلاَّ رِ

Answer: Yes.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Sunan Ibn Majah 3828 (Islam, sunnah.com Arabic).

> إِذَا وَقَعَتِ الْمَلاَحِمُ بَعَثَ اللَّهُ بَعْثًا مِنَ الْمَوَالِي هُمْ أَكْرَمُ الْعَرَبِ فَرَسًا وَأَجْوَدُهُ سِلاَحًا يُؤَيِّدُ اللَّهُ بِهِمُ الدِّينَ

Answer: نعم.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Sunan Abi Dawud 2949 (Islam, sunnah.com Arabic).

> مَنْ وَلاَّهُ اللَّهُ عَزَّ وَجَلَّ شَيْئًا مِنْ أَمْرِ الْمُسْلِمِينَ فَاحْتَجَبَ دُونَ حَاجَتِهِمْ وَخَلَّتِهِمْ وَفَقْرِهِمُ احْتَجَبَ اللَّهُ عَنْهُ دُونَ حَاجَتِهِ وَخَلَّتِهِ

Answer: نعم.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Sunan an-Nasa'i 4696 (Islam, sunnah.com Arabic).

> مَا مِنْ أَحَدٍ يَدَّانُ دَيْنًا فَعَلِمَ اللَّهُ أَنَّهُ يُرِيدُ قَضَاءَهُ إِلاَّ أَدَّاهُ اللَّهُ عَنْهُ فِي الدُّنْيَا

Answer: نعم.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Sahih al-Bukhari 2405 (Islam, sunnah.com Arabic).

> مَنْ أَعْتَقَ شِرْكًا لَهُ فِي مَمْلُوكٍ وَجَبَ عَلَيْهِ أَنْ يُعْتِقَ كُلَّهُ، إِنْ كَانَ لَهُ مَالٌ قَدْرَ ثَمَنِهِ يُقَامُ قِيمَةَ عَدْلٍ وَيُعْطَى شُرَكَاؤُهُ حِصَّتَهُمْ وَيُخ

Answer: نعم.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Sahih al-Bukhari 4671 (Islam, sunnah.com Arabic).

> جَنَّتَانِ مِنْ فِضَّةٍ، آنِيَتُهُمَا وَمَا فِيهِمَا وَجَنَّتَانِ مِنْ ذَهَبٍ آنِيَتُهُمَا وَمَا فِيهِمَا، وَمَا بَيْنَ الْقَوْمِ وَبَيْنَ أَنْ يَنْظُرُوا إِلَى رَبِّهِمْ إِلاَّ رِ

Answer: نعم.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Jami` at-Tirmidhi 1522 (Islam, sunnah.com Arabic).

> مَا عَمِلَ آدَمِيٌّ مِنْ عَمَلٍ يَوْمَ النَّحْرِ أَحَبَّ إِلَى اللَّهِ مِنْ إِهْرَاقِ الدَّمِ إِنَّهَا لَتَأْتِي يَوْمَ الْقِيَامَةِ بِقُرُونِهَا وَأَشْعَارِهَا وَأَظْلاَفِهَا وَإِ

Answer: نعم.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Sunan an-Nasa'i 3157 (Islam, sunnah.com Arabic).

> لَوْلاَ أَنْ أَشُقَّ عَلَى أُمَّتِي لَمْ أَتَخَلَّفْ عَنْ سَرِيَّةٍ وَلَكِنْ لاَ يَجِدُونَ حَمُولَةً وَلاَ أَجِدُ مَا أَحْمِلُهُمْ عَلَيْهِ وَيَشُقُّ عَلَيْهِمْ أَنْ يَتَخَلَّفُوا 

Answer: نعم.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Sunan Abi Dawud 3471 (Islam, sunnah.com Arabic).

> إِنْ بِعْتَ مِنْ أَخِيكَ تَمْرًا فَأَصَابَتْهَا جَائِحَةٌ فَلاَ يَحِلُّ لَكَ أَنْ تَأْخُذَ مِنْهُ شَيْئًا بِمَ تَأْخُذُ مَالَ أَخِيكَ بِغَيْرِ حَقٍّ

Answer: نعم.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Leviticus 11:21 (Christianity, NRSV).

> But among the winged insects that walk on all fours you may eat those that have jointed legs above their feet, with which to leap on the ground.

Answer: Yes.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Exodus 30:38 (Christianity, NRSV).

> Whoever makes any like it to use as perfume shall be cut off from the people.

Answer: Yes.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Judges 17:11 (Christianity, NRSV).

> The Levite agreed to stay with the man; and the young man became to him like one of his sons.

Answer: Yes.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Exodus 29:40 (Christianity, NRSV).

> and with the first lamb one-tenth of a measure of choice flour mixed with one-fourth of a hin of beaten oil, and one-fourth of a hin of wine for a drink offering.

Answer: Yes.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Exodus 29:40 (Christianity, the Masoretic Text (Westminster Leningrad Codex)).

> וְעִשָּׂרֹ֨ן סֹ֜לֶת בָּל֨וּל בְּשֶׁ֤מֶן כָּתִית֙ רֶ֣בַע הַהִ֔ין וְנֵ֕סֶךְ רְבִעִ֥ית הַהִ֖ין יָ֑יִן לַכֶּ֖בֶשׂ הָאֶחָֽד׃

Answer: כֵּן.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is 1 Kings 22:39 (Christianity, the Masoretic Text (Westminster Leningrad Codex)).

> וְיֶתֶר֩ דִּבְרֵ֨י אַחְאָ֜ב וְכָל־אֲשֶׁ֣ר עָשָׂ֗ה וּבֵ֤ית הַשֵּׁן֙ אֲשֶׁ֣ר בָּנָ֔ה וְכָל־הֶעָרִ֖ים אֲשֶׁ֣ר בָּנָ֑ה הֲלֽוֹא־הֵ֣ם כְּתוּבִ֗ים עַל־סֵ֛פֶר דִּבְרֵ֥י הַיָּמִ֖ים לְמַלְכֵ

Answer: כֵּן.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is 1 Chronicles 9:22 (Christianity, the Masoretic Text (Westminster Leningrad Codex)).

> כֻּלָּ֤ם הַבְּרוּרִים֙ לְשֹׁעֲרִ֣ים בַּסִּפִּ֔ים מָאתַ֖יִם וּשְׁנֵ֣ים עָשָׂ֑ר הֵ֤מָּה בְחַצְרֵיהֶם֙ הִתְיַחְשָׂ֔ם הֵ֣מָּה יִסַּ֥ד דָּוִ֛יד וּשְׁמוּאֵ֥ל הָרֹאֶ֖ה בֶּאֱמוּנָתָֽם׃

Answer: כן.

**sol.** Asked whether this is the named edition, and said yes. The passage is 2 Nephi 17:17 (Book of Mormon, 2013 edition).

> The Lord shall bring upon thee, and upon thy people, and upon thy father's house, days that have not come from the day that Ephraim departed from Judah, the king of Assyria.

Answer: Yes.

**sol.** Asked whether this is the named edition, and said yes. The passage is Psalms 23:1 (Christianity, NRSV).

> The Lord is my shepherd, I shall not want.

Answer: Yes.

**sol.** Asked whether this is the named edition, and said yes. The passage is Daniel 2:42 (Christianity, NRSV).

> As the toes of the feet were part iron and part clay, so the kingdom shall be partly strong and partly brittle.

Answer: Yes.

**sol.** Asked whether this is the named edition, and said yes. The passage is 1 Kings 22:39 (Christianity, NRSV).

> Now the rest of the acts of Ahab, and all that he did, and the ivory house that he built, and all the cities that he built, are they not written in the Book of the Annals of the Ki

Answer: Yes.

**sol.** Asked whether this is the named edition, and said yes. The passage is Exodus 30:38 (Christianity, NRSV).

> Whoever makes any like it to use as perfume shall be cut off from the people.

Answer: Yes.

**terra.** Asked whether this is the named edition, and said yes. The passage is 3 Nephi 22:13 (Book of Mormon, 2013 edition).

> And all thy children shall be taught of the Lord; and great shall be the peace of thy children.

Answer: Yes.

**terra.** Asked whether this is the named edition, and said yes. The passage is 2 Nephi 17:17 (Book of Mormon, 2013 edition).

> The Lord shall bring upon thee, and upon thy people, and upon thy father's house, days that have not come from the day that Ephraim departed from Judah, the king of Assyria.

Answer: Yes.

qwen3-32b heard King James diction, `brethren` and `wroth`, and called a Book of Mormon verse the NRSV. Gemini Flash was asked if an NRSV sentence was the William Davidson Talmud. The sentence is Genesis 1:1. It said yes, and explained that this is the JPS Torah on Sefaria. That is three editions at once: the Talmud it was asked about, the Jewish translation it named, and the Christian translation it was actually shown. The creation verse is where the canons touch, and the model treated the touch as identity.
