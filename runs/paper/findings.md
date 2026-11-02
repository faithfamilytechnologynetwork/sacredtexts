# Findings

From 27144 scored answers in finished files. A file still being collected is not here.

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
| argon | 80% of 236, refused 6 | 99% of 241, refused 1 |
| astra | 90% of 151, refused 1 | 99% of 148, refused 0 |
| beam | 67% of 192, refused 9 | 98% of 200, refused 2 |
| deepseek-v4-pro | 62% of 239, refused 3 | 86% of 238, refused 4 |
| fable | 86% of 108, refused 14 | 98% of 117, refused 1 |
| gemini-flash | 73% of 269, refused 3 | 99% of 268, refused 0 |
| gemma-31b | 67% of 245, refused 27 | 93% of 256, refused 12 |
| gpt-oss-20b | 13% of 151, refused 1 | 100% of 144, refused 4 |
| haiku | 63% of 161, refused 111 | 99% of 160, refused 108 |
| kimi | 85% of 226, refused 1 | 91% of 227, refused 0 |
| luna | 64% of 268, refused 4 | 87% of 244, refused 24 |
| opus | 73% of 211, refused 1 | 99% of 211, refused 1 |
| qwen3-32b | 60% of 85, refused 7 | 78% of 86, refused 2 |
| sol | 87% of 167, refused 0 | 96% of 163, refused 0 |
| sonnet | 38% of 164, refused 78 | 99% of 186, refused 56 |
| terra | 80% of 269, refused 3 | 98% of 263, refused 5 |

A model that is sure about fakes and unsure about the real text will look accurate on a set that is half `no`. That accuracy is not recognition.

## The negative item is an alphabet check for some traditions

A correct `no` is not the same question in every file. Sikhism, the Sanskrit Gita, the Pali Dhammapada, and the Greek New Testament are shown a passage in another script, because this corpus has no second work in Gurmukhi, Devanagari, Pali, or Greek. Islam is shown a hadith. The Talmud is shown the Bible. The Book of Mormon is shown a papal encyclical, and the encyclical is shown the Book of Mormon. Refusals are out of the percent.

| negative the model was shown | correct no | wrong yes | refused |
|---|---:|---:|---:|
| Different script | 99% (913/919) | 6 | 118 |
| NRSV shown the Book of Mormon | 100% (239/240) | 1 | 0 |
| Qur'an shown a hadith | 99% (627/634) | 7 | 11 |
| Encyclical shown the Book of Mormon | 97% (110/113) | 3 | 7 |
| Other same-script negative | 99% (450/455) | 5 | 20 |
| Talmud shown the Bible | 86% (579/675) | 96 | 45 |
| Book of Mormon shown an encyclical | 72% (83/116) | 33 | 19 |

Saying no to a different alphabet is nearly automatic. Saying no to the Bible when the question names the Talmud, and saying no to an encyclical when the question names the Book of Mormon, is where the errors are. The reverse pair is not the same: shown a Book of Mormon verse and asked if it is the encyclical, models almost always say no. A verify accuracy that averages these items ranks a tradition by how its negative was built.

## Quoting and citing are different skills

Each finished file, retrieve against cite. A wide gap means the model can do one and not the other. Refusals are out of the percent and shown beside it.

| model | file | retrieve | cite |
|---|---|---:|---:|
| sonnet | `islam/english/population` | 0% (0/24, refused 6) | 100% (30/30, refused 0) |
| sol | `islam/native/population/prompt-english` | 100% (30/30, refused 0) | 0% (0/30, refused 0) |
| sol | `christianity/native/masoretic/population/prompt-native` | 0% (0/21, refused 0) | 100% (21/21, refused 0) |
| opus | `christianity/native/masoretic/population/prompt-native` | 0% (0/21, refused 0) | 100% (21/21, refused 0) |
| kimi | `buddhism/native/population/prompt-english` | 0% (0/3, refused 0) | 100% (2/2, refused 0) |
| haiku | `hinduism/english/population` | 0% (0/1, refused 29) | 100% (27/27, refused 3) |
| haiku | `christianity/native/greek/population/prompt-english` | 0% (0/9, refused 0) | 100% (9/9, refused 0) |
| gemini-flash | `christianity/native/masoretic/population/prompt-native` | 0% (0/21, refused 0) | 100% (21/21, refused 0) |
| beam | `hinduism/native/population/prompt-english` | 0% (0/1, refused 29) | 100% (30/30, refused 0) |
| beam | `hinduism/english/population` | 0% (0/22, refused 8) | 100% (30/30, refused 0) |
| beam | `buddhism/native/population/prompt-english` | 0% (0/2, refused 1) | 100% (2/2, refused 0) |
| astra | `christianity/native/masoretic/population/prompt-native` | 0% (0/21, refused 0) | 100% (21/21, refused 0) |
| argon | `christianity/native/masoretic/population/prompt-native` | 0% (0/21, refused 0) | 100% (21/21, refused 0) |
| terra | `hinduism/english/population` | 3% (1/30, refused 0) | 100% (30/30, refused 0) |
| opus | `islam/native/population/prompt-english` | 97% (29/30, refused 0) | 0% (0/30, refused 0) |
| kimi | `hinduism/english/population` | 0% (0/7, refused 23) | 97% (29/30, refused 0) |
| luna | `hinduism/native/population/prompt-english` | 4% (1/26, refused 4) | 100% (30/30, refused 0) |
| terra | `christianity/native/masoretic/population/prompt-native` | 0% (0/21, refused 0) | 95% (20/21, refused 0) |
| kimi | `christianity/native/masoretic/population/prompt-native` | 0% (0/21, refused 0) | 95% (20/21, refused 0) |
| fable | `christianity/native/masoretic/population/prompt-native` | 0% (0/21, refused 0) | 95% (20/21, refused 0) |
| deepseek-v4-pro | `christianity/native/masoretic/population/prompt-native` | 0% (0/21, refused 0) | 95% (20/21, refused 0) |
| beam | `christianity/native/masoretic/population/prompt-native` | 0% (0/21, refused 0) | 95% (20/21, refused 0) |
| sonnet | `islam/native/population/prompt-english` | 97% (29/30, refused 0) | 3% (1/30, refused 0) |
| luna | `hinduism/english/population` | 0% (0/22, refused 8) | 93% (28/30, refused 0) |
| kimi | `hinduism/native/population/prompt-native` | 5% (1/20, refused 10) | 97% (29/30, refused 0) |
| sonnet | `christianity/native/masoretic/population/prompt-native` | 0% (0/21, refused 0) | 90% (19/21, refused 0) |
| luna | `christianity/native/masoretic/population/prompt-english` | 0% (0/21, refused 0) | 90% (19/21, refused 0) |
| sonnet | `hinduism/english/population` | 0% (0/30, refused 0) | 90% (27/30, refused 0) |
| gemini-flash | `islam/native/population/prompt-english` | 93% (28/30, refused 0) | 3% (1/30, refused 0) |
| opus | `christianity/native/greek/population/prompt-english` | 89% (8/9, refused 0) | 0% (0/9, refused 0) |
| haiku | `christianity/native/greek/population/prompt-native` | 11% (1/9, refused 0) | 100% (9/9, refused 0) |
| gemini-flash | `christianity/native/greek/population/prompt-english` | 89% (8/9, refused 0) | 0% (0/9, refused 0) |
| fable | `christianity/native/greek/population/prompt-english` | 89% (8/9, refused 0) | 0% (0/9, refused 0) |
| astra | `christianity/native/greek/population/prompt-english` | 89% (8/9, refused 0) | 0% (0/9, refused 0) |
| argon | `hinduism/english/population` | 11% (3/27, refused 3) | 100% (30/30, refused 0) |
| terra | `hinduism/native/population/prompt-native` | 10% (3/30, refused 0) | 97% (29/30, refused 0) |
| deepseek-v4-pro | `islam/english/population` | 13% (4/30, refused 0) | 100% (30/30, refused 0) |
| astra | `islam/native/population/prompt-english` | 97% (29/30, refused 0) | 10% (3/30, refused 0) |
| luna | `christianity/native/masoretic/population/prompt-native` | 0% (0/21, refused 0) | 86% (18/21, refused 0) |
| gemini-flash | `islam/english/population` | 14% (3/21, refused 9) | 100% (30/30, refused 0) |
| beam | `islam/english/population` | 17% (4/24, refused 6) | 100% (30/30, refused 0) |
| luna | `islam/english/population` | 18% (3/17, refused 13) | 100% (30/30, refused 0) |
| luna | `hinduism/native/population/prompt-native` | 12% (3/24, refused 6) | 93% (28/30, refused 0) |
| sol | `christianity/native/greek/population/prompt-english` | 78% (7/9, refused 0) | 0% (0/9, refused 0) |
| terra | `islam/english/population` | 23% (7/30, refused 0) | 100% (30/30, refused 0) |
| opus | `islam/english/population` | 23% (7/30, refused 0) | 100% (30/30, refused 0) |
| deepseek-v4-pro | `hinduism/native/population/prompt-english` | 10% (3/30, refused 0) | 87% (26/30, refused 0) |
| fable | `islam/english/population` | 24% (7/29, refused 1) | 100% (30/30, refused 0) |
| gemma-31b | `islam/native/population/prompt-native` | 0% (0/30, refused 0) | 73% (22/30, refused 0) |
| gemini-flash | `hinduism/english/population` | 27% (8/30, refused 0) | 100% (30/30, refused 0) |
| beam | `hinduism/native/population/prompt-native` | 20% (6/30, refused 0) | 93% (28/30, refused 0) |
| kimi | `islam/english/population` | 28% (8/29, refused 1) | 100% (30/30, refused 0) |
| argon | `islam/english/population` | 30% (9/30, refused 0) | 100% (30/30, refused 0) |
| haiku | `islam/native/population/prompt-english` | 85% (23/27, refused 3) | 17% (5/30, refused 0) |
| sonnet | `christianity/native/greek/population/prompt-english` | 67% (6/9, refused 0) | 0% (0/9, refused 0) |
| deepseek-v4-pro | `hinduism/english/population` | 0% (0/30, refused 0) | 67% (20/30, refused 0) |
| argon | `christianity/native/greek/population/prompt-english` | 67% (6/9, refused 0) | 0% (0/9, refused 0) |
| sonnet | `christianity/native/greek/population/prompt-native` | 33% (3/9, refused 0) | 100% (9/9, refused 0) |
| kimi | `christianity/native/greek/population/prompt-native` | 33% (3/9, refused 0) | 100% (9/9, refused 0) |
| kimi | `buddhism/native/population/prompt-native` | 33% (1/3, refused 0) | 100% (2/2, refused 0) |
| kimi | `islam/native/population/prompt-english` | 67% (20/30, refused 0) | 3% (1/30, refused 0) |
| luna | `christianity/english/population` | 30% (3/10, refused 20) | 93% (28/30, refused 0) |
| gemini-flash | `hinduism/native/population/prompt-native` | 40% (12/30, refused 0) | 100% (30/30, refused 0) |
| deepseek-v4-pro | `islam/native/population/prompt-native` | 3% (1/30, refused 0) | 63% (19/30, refused 0) |
| terra | `islam/native/population/prompt-english` | 100% (30/30, refused 0) | 43% (13/30, refused 0) |
| luna | `islam/native/population/prompt-native` | 43% (13/30, refused 0) | 100% (30/30, refused 0) |
| argon | `hinduism/native/population/prompt-native` | 44% (7/16, refused 14) | 100% (30/30, refused 0) |
| terra | `christianity/native/greek/population/prompt-native` | 44% (4/9, refused 0) | 100% (9/9, refused 0) |
| terra | `christianity/native/greek/population/prompt-english` | 67% (6/9, refused 0) | 11% (1/9, refused 0) |
| luna | `christianity/native/greek/population/prompt-native` | 44% (4/9, refused 0) | 100% (9/9, refused 0) |
| gemma-31b | `islam/native/population/prompt-english` | 0% (0/30, refused 0) | 53% (16/30, refused 0) |
| argon | `encyclicals/english/population` | 0% (0/8, refused 22) | 53% (16/30, refused 0) |
| terra | `buddhism/native/population/prompt-english` | 47% (14/30, refused 0) | 97% (29/30, refused 0) |
| opus | `hinduism/native/population/prompt-native` | 47% (14/30, refused 0) | 97% (29/30, refused 0) |
| sonnet | `buddhism/native/population/prompt-english` | 0% (0/3, refused 0) | 50% (1/2, refused 0) |
| qwen3-32b | `christianity/english/population` | 7% (2/30, refused 0) | 57% (17/30, refused 0) |
| haiku | `christianity/native/masoretic/population/prompt-native` | 0% (0/21, refused 0) | 50% (9/18, refused 3) |
| gemma-31b | `islam/english/population` | 0% (0/30, refused 0) | 50% (15/30, refused 0) |
| gemini-flash | `encyclicals/english/population` | 0% (0/6, refused 24) | 50% (15/30, refused 0) |
| deepseek-v4-pro | `buddhism/native/population/prompt-english` | 0% (0/3, refused 0) | 50% (1/2, refused 0) |
| haiku | `christianity/native/masoretic/population/prompt-english` | 0% (0/21, refused 0) | 48% (10/21, refused 0) |
| terra | `buddhism/native/population/prompt-native` | 50% (15/30, refused 0) | 97% (29/30, refused 0) |
| gemini-flash | `buddhism/native/population/prompt-native` | 43% (13/30, refused 0) | 90% (27/30, refused 0) |
| opus | `hinduism/english/population` | 55% (11/20, refused 10) | 100% (30/30, refused 0) |
| qwen3-32b | `christianity/native/greek/population/prompt-native` | 0% (0/9, refused 0) | 44% (4/9, refused 0) |
| kimi | `hinduism/native/population/prompt-english` | 0% (0/27, refused 3) | 43% (13/30, refused 0) |
| gemini-flash | `hinduism/native/population/prompt-english` | 50% (13/26, refused 4) | 7% (2/30, refused 0) |
| gemini-flash | `buddhism/native/population/prompt-english` | 47% (14/30, refused 0) | 90% (27/30, refused 0) |
| beam | `islam/native/population/prompt-native` | 57% (17/30, refused 0) | 100% (30/30, refused 0) |
| haiku | `christianity/english/population` | 40% (4/10, refused 20) | 83% (25/30, refused 0) |
| deepseek-v4-pro | `hinduism/native/population/prompt-native` | 44% (8/18, refused 12) | 87% (26/30, refused 0) |
| sonnet | `hinduism/native/population/prompt-native` | 57% (17/30, refused 0) | 97% (29/30, refused 0) |
| luna | `book-of-mormon/english/population` | 17% (5/29, refused 1) | 57% (17/30, refused 0) |
| luna | `buddhism/native/population/prompt-english` | 30% (9/30, refused 0) | 67% (20/30, refused 0) |
| gemini-flash | `book-of-mormon/english/population` | 50% (14/28, refused 2) | 87% (26/30, refused 0) |
| luna | `encyclicals/english/population` | 0% (0/25, refused 5) | 37% (11/30, refused 0) |
| beam | `islam/native/population/prompt-english` | 66% (19/29, refused 1) | 100% (30/30, refused 0) |
| haiku | `book-of-mormon/english/population` | 50% (1/2, refused 28) | 16% (4/25, refused 5) |
| terra | `encyclicals/english/population` | 0% (0/27, refused 3) | 33% (10/30, refused 0) |
| terra | `book-of-mormon/english/population` | 37% (11/30, refused 0) | 70% (21/30, refused 0) |
| sonnet | `buddhism/native/population/prompt-native` | 33% (1/3, refused 0) | 0% (0/2, refused 0) |
| kimi | `christianity/native/greek/population/prompt-english` | 22% (2/9, refused 0) | 56% (5/9, refused 0) |
| gemma-31b | `christianity/native/greek/population/prompt-english` | 0% (0/9, refused 0) | 33% (3/9, refused 0) |
| deepseek-v4-pro | `encyclicals/english/population` | 0% (0/30, refused 0) | 33% (10/30, refused 0) |
| opus | `buddhism/native/population/prompt-english` | 67% (2/3, refused 0) | 100% (2/2, refused 0) |
| kimi | `islam/native/population/prompt-native` | 67% (20/30, refused 0) | 100% (30/30, refused 0) |
| beam | `christianity/native/greek/population/prompt-native` | 56% (5/9, refused 0) | 89% (8/9, refused 0) |
| argon | `buddhism/native/population/prompt-native` | 67% (2/3, refused 0) | 100% (2/2, refused 0) |
| argon | `buddhism/native/population/prompt-english` | 67% (2/3, refused 0) | 100% (2/2, refused 0) |
| haiku | `hinduism/native/population/prompt-native` | 10% (3/30, refused 0) | 40% (12/30, refused 0) |
| gemma-31b | `christianity/english/population` | 0% (0/30, refused 0) | 30% (9/30, refused 0) |
| argon | `book-of-mormon/english/population` | 63% (19/30, refused 0) | 93% (28/30, refused 0) |
| opus | `hinduism/native/population/prompt-english` | 29% (2/7, refused 23) | 0% (0/30, refused 0) |
| deepseek-v4-pro | `christianity/native/masoretic/population/prompt-english` | 0% (0/21, refused 0) | 29% (6/21, refused 0) |
| beam | `christianity/english/population` | 73% (22/30, refused 0) | 100% (30/30, refused 0) |
| astra | `judaism/native/population/prompt-native` | 3% (1/30, refused 0) | 30% (9/30, refused 0) |
| terra | `christianity/english/population` | 67% (16/24, refused 6) | 93% (28/30, refused 0) |
| sonnet | `encyclicals/english/population` | 0% (0/1, refused 29) | 26% (7/27, refused 3) |
| qwen3-32b | `christianity/native/masoretic/population/prompt-native` | 0% (0/21, refused 0) | 24% (5/21, refused 0) |
| kimi | `christianity/english/population` | 73% (19/26, refused 4) | 97% (29/30, refused 0) |
| haiku | `islam/native/population/prompt-native` | 70% (21/30, refused 0) | 93% (28/30, refused 0) |
| argon | `christianity/english/population` | 77% (23/30, refused 0) | 100% (30/30, refused 0) |
| sol | `christianity/native/greek/population/prompt-native` | 78% (7/9, refused 0) | 100% (9/9, refused 0) |
| astra | `christianity/native/greek/population/prompt-native` | 78% (7/9, refused 0) | 100% (9/9, refused 0) |
| argon | `christianity/native/greek/population/prompt-native` | 78% (7/9, refused 0) | 100% (9/9, refused 0) |
| gemma-31b | `christianity/native/greek/population/prompt-native` | 0% (0/9, refused 0) | 22% (2/9, refused 0) |
| deepseek-v4-pro | `christianity/native/greek/population/prompt-english` | 22% (2/9, refused 0) | 0% (0/9, refused 0) |
| argon | `hinduism/native/population/prompt-english` | 29% (5/17, refused 13) | 50% (15/30, refused 0) |
| sonnet | `hinduism/native/population/prompt-english` | 47% (8/17, refused 13) | 27% (8/30, refused 0) |
| gemma-31b | `hinduism/native/population/prompt-native` | 0% (0/23, refused 7) | 20% (6/30, refused 0) |
| argon | `judaism/english/population` | 0% (0/3, refused 27) | 20% (6/30, refused 0) |
| terra | `hinduism/native/population/prompt-english` | 29% (8/28, refused 2) | 10% (3/30, refused 0) |
| opus | `buddhism/native/population/prompt-native` | 67% (2/3, refused 0) | 50% (1/2, refused 0) |
| luna | `islam/native/population/prompt-english` | 83% (25/30, refused 0) | 100% (30/30, refused 0) |
| gemini-flash | `christianity/english/population` | 83% (25/30, refused 0) | 100% (30/30, refused 0) |
| gemini-flash | `judaism/native/population/prompt-native` | 0% (0/30, refused 0) | 17% (5/30, refused 0) |
| gemini-flash | `judaism/native/population/prompt-english` | 5% (1/19, refused 11) | 20% (6/30, refused 0) |
| sonnet | `christianity/native/masoretic/population/prompt-english` | 0% (0/20, refused 1) | 14% (3/21, refused 0) |
| opus | `judaism/english/population` | 0% (0/1, refused 29) | 14% (4/29, refused 1) |
| gemma-31b | `hinduism/native/population/prompt-english` | 0% (0/15, refused 15) | 13% (4/30, refused 0) |
| sol | `judaism/native/population/prompt-native` | 7% (2/30, refused 0) | 20% (6/30, refused 0) |
| opus | `christianity/native/greek/population/prompt-native` | 89% (8/9, refused 0) | 100% (9/9, refused 0) |
| gemini-flash | `christianity/native/greek/population/prompt-native` | 89% (8/9, refused 0) | 100% (9/9, refused 0) |
| beam | `christianity/native/greek/population/prompt-english` | 56% (5/9, refused 0) | 67% (6/9, refused 0) |
| qwen3-32b | `christianity/native/greek/population/prompt-english` | 0% (0/9, refused 0) | 11% (1/9, refused 0) |
| deepseek-v4-pro | `christianity/native/greek/population/prompt-native` | 67% (6/9, refused 0) | 78% (7/9, refused 0) |
| sonnet | `christianity/english/population` | 79% (15/19, refused 11) | 90% (27/30, refused 0) |
| opus | `judaism/native/population/prompt-native` | 0% (0/30, refused 0) | 10% (3/29, refused 1) |
| terra | `judaism/native/population/prompt-native` | 3% (1/30, refused 0) | 13% (4/30, refused 0) |
| terra | `judaism/english/population` | 0% (0/29, refused 1) | 10% (3/30, refused 0) |
| haiku | `buddhism/native/population/prompt-native` | 10% (1/10, refused 20) | 0% (0/25, refused 5) |
| gemma-31b | `hinduism/english/population` | 0% (0/23, refused 7) | 10% (3/30, refused 0) |
| fable | `judaism/english/population` | 0% (0/2, refused 28) | 10% (3/30, refused 0) |
| beam | `judaism/native/population/prompt-native` | 0% (0/30, refused 0) | 10% (3/30, refused 0) |
| argon | `judaism/native/population/prompt-native` | 0% (0/30, refused 0) | 10% (3/30, refused 0) |
| argon | `judaism/native/population/prompt-english` | 0% (0/29, refused 1) | 10% (3/30, refused 0) |
| qwen3-32b | `christianity/native/masoretic/population/prompt-english` | 0% (0/21, refused 0) | 10% (2/21, refused 0) |
| kimi | `christianity/native/masoretic/population/prompt-english` | 0% (0/19, refused 2) | 10% (2/21, refused 0) |
| gemma-31b | `christianity/native/masoretic/population/prompt-native` | 0% (0/21, refused 0) | 10% (2/21, refused 0) |
| kimi | `judaism/english/population` | 0% (0/18, refused 12) | 7% (2/29, refused 1) |
| gpt-oss-20b | `islam/native/population/prompt-english` | 0% (0/29, refused 1) | 7% (2/29, refused 1) |
| gemini-flash | `islam/native/population/prompt-native` | 93% (28/30, refused 0) | 100% (30/30, refused 0) |
| deepseek-v4-pro | `islam/native/population/prompt-english` | 77% (23/30, refused 0) | 70% (21/30, refused 0) |
| argon | `islam/native/population/prompt-english` | 100% (30/30, refused 0) | 93% (28/30, refused 0) |
| terra | `judaism/native/population/prompt-english` | 0% (0/30, refused 0) | 7% (2/30, refused 0) |
| sonnet | `judaism/native/population/prompt-native` | 0% (0/30, refused 0) | 7% (2/30, refused 0) |
| luna | `judaism/english/population` | 0% (0/19, refused 11) | 7% (2/30, refused 0) |
| gemma-31b | `buddhism/native/population/prompt-english` | 0% (0/30, refused 0) | 7% (2/30, refused 0) |
| gemini-flash | `judaism/english/population` | 0% (0/1, refused 29) | 7% (2/30, refused 0) |
| sol | `judaism/native/population/prompt-english` | 4% (1/28, refused 2) | 10% (3/30, refused 0) |
| kimi | `book-of-mormon/english/population` | 54% (14/26, refused 4) | 60% (18/30, refused 0) |
| gemma-31b | `christianity/native/masoretic/population/prompt-english` | 0% (0/21, refused 0) | 5% (1/21, refused 0) |
| opus | `islam/native/population/prompt-native` | 93% (28/30, refused 0) | 97% (29/30, refused 0) |
| terra | `sikhism/native/population/prompt-english` | 0% (0/30, refused 0) | 3% (1/30, refused 0) |
| sol | `sikhism/native/population/prompt-native` | 0% (0/30, refused 0) | 3% (1/30, refused 0) |
| sol | `sikhism/native/population/prompt-english` | 0% (0/30, refused 0) | 3% (1/30, refused 0) |
| luna | `judaism/native/population/prompt-english` | 0% (0/30, refused 0) | 3% (1/30, refused 0) |
| kimi | `judaism/native/population/prompt-native` | 0% (0/30, refused 0) | 3% (1/30, refused 0) |
| gpt-oss-20b | `islam/native/population/prompt-native` | 0% (0/30, refused 0) | 3% (1/30, refused 0) |
| gpt-oss-20b | `christianity/english/population` | 0% (0/22, refused 8) | 3% (1/30, refused 0) |
| gemma-31b | `encyclicals/english/population` | 0% (0/30, refused 0) | 3% (1/30, refused 0) |
| gemma-31b | `book-of-mormon/english/population` | 0% (0/30, refused 0) | 3% (1/30, refused 0) |
| fable | `judaism/native/population/prompt-native` | 3% (1/30, refused 0) | 0% (0/30, refused 0) |
| fable | `judaism/native/population/prompt-english` | 3% (1/30, refused 0) | 0% (0/30, refused 0) |
| deepseek-v4-pro | `judaism/native/population/prompt-native` | 0% (0/30, refused 0) | 3% (1/30, refused 0) |
| deepseek-v4-pro | `judaism/english/population` | 0% (0/29, refused 1) | 3% (1/30, refused 0) |
| beam | `judaism/native/population/prompt-english` | 0% (0/6, refused 24) | 3% (1/30, refused 0) |
| beam | `judaism/english/population` | 0% (0/2, refused 28) | 3% (1/30, refused 0) |
| astra | `judaism/native/population/prompt-english` | 3% (1/30, refused 0) | 0% (0/30, refused 0) |
| luna | `buddhism/native/population/prompt-native` | 23% (7/30, refused 0) | 20% (6/30, refused 0) |
| sonnet | `islam/native/population/prompt-native` | 97% (29/30, refused 0) | 100% (30/30, refused 0) |
| opus | `christianity/english/population` | 97% (29/30, refused 0) | 100% (30/30, refused 0) |
| fable | `islam/native/population/prompt-native` | 97% (29/30, refused 0) | 100% (30/30, refused 0) |
| deepseek-v4-pro | `christianity/english/population` | 93% (28/30, refused 0) | 90% (27/30, refused 0) |
| argon | `islam/native/population/prompt-native` | 97% (29/30, refused 0) | 100% (30/30, refused 0) |
| sonnet | `book-of-mormon/english/population` | 43% (6/14, refused 16) | 40% (12/30, refused 0) |
| terra | `sikhism/native/population/prompt-native` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| terra | `islam/native/population/prompt-native` | 100% (30/30, refused 0) | 100% (30/30, refused 0) |
| terra | `christianity/native/masoretic/population/prompt-english` | 0% (0/21, refused 0) | 0% (0/21, refused 0) |
| sonnet | `sikhism/native/population/prompt-native` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| sonnet | `sikhism/native/population/prompt-english` | 0% (0/2, refused 28) | 0% (0/17, refused 13) |
| sol | `islam/native/population/prompt-native` | 100% (30/30, refused 0) | 100% (30/30, refused 0) |
| sol | `islam/english/population` | 100% (1/1, refused 29) | 100% (30/30, refused 0) |
| sol | `christianity/native/masoretic/population/prompt-english` | 0% (0/21, refused 0) | 0% (0/21, refused 0) |
| qwen3-32b | `judaism/native/population/prompt-native` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| qwen3-32b | `judaism/native/population/prompt-english` | 0% (0/29, refused 1) | 0% (0/30, refused 0) |
| qwen3-32b | `judaism/english/population` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| opus | `sikhism/native/population/prompt-native` | 0% (0/30, refused 0) | 0% (0/29, refused 1) |
| opus | `sikhism/native/population/prompt-english` | 0% (0/27, refused 3) | 0% (0/27, refused 3) |
| opus | `judaism/native/population/prompt-english` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| opus | `christianity/native/masoretic/population/prompt-english` | 0% (0/21, refused 0) | 0% (0/21, refused 0) |
| luna | `sikhism/native/population/prompt-native` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| luna | `judaism/native/population/prompt-native` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| luna | `christianity/native/greek/population/prompt-english` | 78% (7/9, refused 0) | 78% (7/9, refused 0) |
| kimi | `sikhism/native/population/prompt-native` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| kimi | `sikhism/native/population/prompt-english` | 0% (0/25, refused 5) | 0% (0/30, refused 0) |
| kimi | `judaism/native/population/prompt-english` | 0% (0/26, refused 4) | 0% (0/30, refused 0) |
| haiku | `sikhism/native/population/prompt-native` | 0% (0/30, refused 0) | 0% (0/13, refused 17) |
| haiku | `judaism/native/population/prompt-native` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| gpt-oss-20b | `sikhism/native/population/prompt-native` | 0% (0/16, refused 14) | 0% (0/30, refused 0) |
| gpt-oss-20b | `judaism/native/population/prompt-native` | 0% (0/21, refused 9) | 0% (0/30, refused 0) |
| gpt-oss-20b | `judaism/native/population/prompt-english` | 0% (0/3, refused 27) | 0% (0/30, refused 0) |
| gpt-oss-20b | `christianity/native/masoretic/population/prompt-native` | 0% (0/20, refused 1) | 0% (0/21, refused 0) |
| gpt-oss-20b | `christianity/native/masoretic/population/prompt-english` | 0% (0/20, refused 1) | 0% (0/21, refused 0) |
| gpt-oss-20b | `christianity/native/greek/population/prompt-native` | 0% (0/9, refused 0) | 0% (0/9, refused 0) |
| gpt-oss-20b | `christianity/native/greek/population/prompt-english` | 0% (0/8, refused 1) | 0% (0/9, refused 0) |
| gemma-31b | `sikhism/native/population/prompt-native` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| gemma-31b | `sikhism/native/population/prompt-english` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| gemma-31b | `judaism/native/population/prompt-native` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| gemma-31b | `judaism/native/population/prompt-english` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| gemma-31b | `judaism/english/population` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| gemma-31b | `buddhism/native/population/prompt-native` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| gemini-flash | `sikhism/native/population/prompt-native` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| gemini-flash | `sikhism/native/population/prompt-english` | 0% (0/28, refused 2) | 0% (0/30, refused 0) |
| gemini-flash | `christianity/native/masoretic/population/prompt-english` | 0% (0/21, refused 0) | 0% (0/21, refused 0) |
| fable | `christianity/native/masoretic/population/prompt-english` | 0% (0/21, refused 0) | 0% (0/21, refused 0) |
| fable | `christianity/native/greek/population/prompt-native` | 100% (9/9, refused 0) | 100% (9/9, refused 0) |
| fable | `christianity/english/population` | 100% (30/30, refused 0) | 100% (30/30, refused 0) |
| deepseek-v4-pro | `sikhism/native/population/prompt-native` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| deepseek-v4-pro | `sikhism/native/population/prompt-english` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| deepseek-v4-pro | `judaism/native/population/prompt-english` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| deepseek-v4-pro | `buddhism/native/population/prompt-native` | 0% (0/3, refused 0) | 0% (0/2, refused 0) |
| deepseek-v4-pro | `book-of-mormon/english/population` | 57% (17/30, refused 0) | 57% (17/30, refused 0) |
| beam | `sikhism/native/population/prompt-native` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| beam | `buddhism/native/population/prompt-native` | 0% (0/3, refused 0) | 0% (0/2, refused 0) |
| astra | `sikhism/native/population/prompt-english` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| astra | `islam/native/population/prompt-native` | 100% (30/30, refused 0) | 100% (30/30, refused 0) |
| astra | `christianity/native/masoretic/population/prompt-english` | 0% (0/21, refused 0) | 0% (0/21, refused 0) |
| argon | `sikhism/native/population/prompt-native` | 0% (0/30, refused 0) | 0% (0/30, refused 0) |
| argon | `sikhism/native/population/prompt-english` | 0% (0/16, refused 14) | 0% (0/30, refused 0) |
| argon | `christianity/native/masoretic/population/prompt-english` | 0% (0/21, refused 0) | 0% (0/21, refused 0) |

The flip is inside one model, on the same verses. Gemini Flash, Qur'an prompted in Arabic: quotation 28/30 and citation 30/30. The same file prompted in English: quotation 28/30 and citation 1/30. Hebrew Masoretic text prompted in Hebrew: citation 21/21, quotation 0/21. Prompted in English: citation 0/21 and quotation 0/21. Greek prompted in English: quotation 8/9, citation 0/9. Naming the verse and producing its words come apart, and the prompt language decides which one is available.

## Close wording that still scores incorrect

1299 incorrect answers still have token F1 of at least 0.70. The strict score is doing what it was built for: a near miss is not a hit. Most of them are Gemini Flash completions.

- terra, complete_unit: 99
- argon, complete_unit: 95
- gemini-flash, retrieve_quote: 80
- terra, retrieve_quote: 77
- luna, complete_unit: 72
- gemini-flash, complete_unit: 70
- kimi, complete_unit: 67
- opus, complete_unit: 64
- beam, retrieve_quote: 63
- argon, retrieve_quote: 62
- deepseek-v4-pro, complete_unit: 54
- beam, complete_unit: 53
- sol, complete_unit: 47
- opus, retrieve_quote: 40
- fable, complete_unit: 39
- kimi, retrieve_quote: 38
- luna, retrieve_quote: 36
- deepseek-v4-pro, retrieve_quote: 35
- sonnet, retrieve_quote: 34
- astra, complete_unit: 32
- fable, retrieve_quote: 29
- haiku, complete_unit: 28
- haiku, retrieve_quote: 20
- sonnet, complete_unit: 18
- sol, retrieve_quote: 10
- astra, retrieve_quote: 8
- gemma-31b, complete_unit: 7
- qwen3-32b, retrieve_quote: 7
- qwen3-32b, complete_unit: 6
- gemma-31b, retrieve_quote: 5
- gpt-oss-20b, complete_unit: 2
- gpt-oss-20b, retrieve_quote: 2

## A right citation in Arabic digits is scored wrong

327 incorrect citations are the right verse once Arabic-Indic digits are read as Western digits. 3314 wrong citations stay wrong after that fold.

- sonnet: 77
- gemini-flash: 41
- haiku: 37
- opus: 33
- sol: 30
- kimi: 29
- astra: 28
- terra: 19
- luna: 10
- deepseek-v4-pro: 8
- argon: 7
- gemma-31b: 5
- fable: 3

Examples:
- terra: expected `34:46`, answered `٣٤:٤٦`
- terra: expected `6:151`, answered `٦:١٥١`
- terra: expected `42:13`, answered `٤٢:١٣`

The cite score asks for the same characters as the Latin citation in the question file. A model that answers in the digits of the Qur'an is counted as naming a different book. That is the benchmark under-crediting a correct location, which is the failure the scorer was built to avoid.

## Another canon, accepted as this one

A verify `yes` on a `no` item means the model took a passage from somewhere else as the named edition. Across the finished files that happened twice.

**argon.** Asked whether this is the named edition, and said yes. The passage is 3 Nephi 22:13 (Book of Mormon, 2013 edition).

> And all thy children shall be taught of the Lord; and great shall be the peace of thy children.

Answer: Yes

**argon.** Asked whether this is the named edition, and said yes. The passage is Daniel 2:42 (Christianity, NRSV).

> As the toes of the feet were part iron and part clay, so the kingdom shall be partly strong and partly brittle.

Answer: Yes

**astra.** Asked whether this is the named edition, and said yes. The passage is Ezekiel 43:24 (Christianity, NRSV).

> You shall present them before the Lord , and the priests shall throw salt on them and offer them up as a burnt offering to the Lord .

Answer: Yes

**astra.** Asked whether this is the named edition, and said yes. The passage is 1 Samuel 31:6 (Christianity, NRSV).

> So Saul and his three sons and his armor-bearer and all his men died together on the same day.

Answer: Yes.

**beam.** Asked whether this is the named edition, and said yes. The passage is Ezekiel 23:16 (Christianity, NRSV).

> When she saw them she lusted after them, and sent messengers to them in Chaldea.

Answer: Yes

**beam.** Asked whether this is the named edition, and said yes. The passage is 2 Samuel 18:5 (Christianity, NRSV).

> The king ordered Joab and Abishai and Ittai, saying, “Deal gently for my sake with the young man Absalom.” And all the people heard when the king gave orders to all the commanders 

Answer: Yes

**beam.** Asked whether this is the named edition, and said yes. The passage is Exodus 30:38 (Christianity, NRSV).

> Whoever makes any like it to use as perfume shall be cut off from the people.

Answer: Yes

**beam.** Asked whether this is the named edition, and said yes. The passage is Isaiah 37:17 (Christianity, NRSV).

> Incline your ear, O Lord , and hear; open your eyes, O Lord , and see; hear all the words of Sennacherib, which he has sent to mock the living God.

Answer: Yes

**beam.** Asked whether this is the named edition, and said yes. The passage is 1 Samuel 31:6 (Christianity, NRSV).

> So Saul and his three sons and his armor-bearer and all his men died together on the same day.

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Christi Matri, para. 10 (Encyclicals, Vatican English text (Paul VI, 1966-09-15)).

> As the history of the Church makes clear, this very fruitful way of praying is not only efficacious in warding off evils and preventing calamities, but is also of great help in fos

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Quadragesimo Anno, para. 17 (Encyclicals, Vatican English text (Pius XI, 1931-05-15)).

> In the first place Leo himself clearly stated what ought to be expected from the Church:[15] 

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Quadragesimo Anno, para. 17 (Encyclicals, Vatican English text (Pius XI, 1931-05-15)).

> In the first place Leo himself clearly stated what ought to be expected from the Church:[15] 

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Aeterni Patris, para. 16 (Encyclicals, Vatican English text (Leo XIII, 1879-08-04)).

> Although these words seem to bear reference solely to Scholastic theology, nevertheless they may plainly be accepted as equally true of philosophy and its praises. For, the noble e

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Ut Unum Sint, para. 61 (Encyclicals, Vatican English text (John Paul II, 1995-05-25)).

> In view of all this, the Catholic Church desires nothing less than full communion between East and West. She finds inspiration for this in the experience of the first millennium. I

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Depuis le Jour, para. 22 (Encyclicals, Vatican English text (Leo XIII, 1899-09-08)).

> Is it necessary to add that the book par excellence in which students may with most profit study scholastic theology is the Summa Theologica of St. Thomas Aquinas? It is our wish, 

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

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Ezekiel 23:16 (Christianity, NRSV).

> When she saw them she lusted after them, and sent messengers to them in Chaldea.

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Jeremiah 50:23 (Christianity, NRSV).

> How the hammer of the whole earth is cut down and broken! How Babylon has become a horror among the nations!

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Daniel 2:42 (Christianity, NRSV).

> As the toes of the feet were part iron and part clay, so the kingdom shall be partly strong and partly brittle.

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is 2 Samuel 18:5 (Christianity, NRSV).

> The king ordered Joab and Abishai and Ittai, saying, “Deal gently for my sake with the young man Absalom.” And all the people heard when the king gave orders to all the commanders 

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Jeremiah 50:23 (Christianity, NRSV).

> How the hammer of the whole earth is cut down and broken! How Babylon has become a horror among the nations!

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is 2 Chronicles 26:15 (Christianity, NRSV).

> In Jerusalem he set up machines, invented by skilled workers, on the towers and the corners for shooting arrows and large stones. And his fame spread far, for he was marvelously he

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Isaiah 37:17 (Christianity, NRSV).

> Incline your ear, O Lord , and hear; open your eyes, O Lord , and see; hear all the words of Sennacherib, which he has sent to mock the living God.

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Leviticus 11:21 (Christianity, NRSV).

> But among the winged insects that walk on all fours you may eat those that have jointed legs above their feet, with which to leap on the ground.

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Judges 17:11 (Christianity, NRSV).

> The Levite agreed to stay with the man; and the young man became to him like one of his sons.

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Genesis 1:1 (Christianity, NRSV).

> In the beginning when God created the heavens and the earth,

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is 2 Samuel 18:5 (Christianity, NRSV).

> The king ordered Joab and Abishai and Ittai, saying, “Deal gently for my sake with the young man Absalom.” And all the people heard when the king gave orders to all the commanders 

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Ezekiel 43:24 (Christianity, NRSV).

> You shall present them before the Lord , and the priests shall throw salt on them and offer them up as a burnt offering to the Lord .

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Isaiah 37:17 (Christianity, NRSV).

> Incline your ear, O Lord , and hear; open your eyes, O Lord , and see; hear all the words of Sennacherib, which he has sent to mock the living God.

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Exodus 30:38 (Christianity, NRSV).

> Whoever makes any like it to use as perfume shall be cut off from the people.

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is 1 Samuel 31:6 (Christianity, NRSV).

> So Saul and his three sons and his armor-bearer and all his men died together on the same day.

Answer: Yes

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is 2 Chronicles 26:15 (Christianity, the Masoretic Text (Westminster Leningrad Codex)).

> וַ/יַּ֣עַשׂ ׀ בִּ/ירוּשָׁלִַ֨ם חִשְּׁבֹנ֜וֹת מַחֲשֶׁ֣בֶת חוֹשֵׁ֗ב לִ/הְי֤וֹת עַל־הַ/מִּגְדָּלִים֙ וְ/עַל־הַ/פִּנּ֔וֹת לִ/ירוֹא֙ בַּֽ/חִצִּ֔ים וּ/בָ/אֲבָנִ֖ים גְּדֹל֑וֹת וַ/יֵּצֵ֤א 

Answer: כן

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Exodus 28:43 (Christianity, the Masoretic Text (Westminster Leningrad Codex)).

> וְ/הָיוּ֩ עַל־אַהֲרֹ֨ן וְ/עַל־בָּנָ֜י/ו בְּ/בֹאָ֣/ם ׀ אֶל־אֹ֣הֶל מוֹעֵ֗ד א֣וֹ בְ/גִשְׁתָּ֤/ם אֶל־הַ/מִּזְבֵּ֨חַ֙ לְ/שָׁרֵ֣ת בַּ/קֹּ֔דֶשׁ וְ/לֹא־יִשְׂא֥וּ עָוֺ֖ן וָ/מֵ֑תוּ חֻקַּ֥ת ע

Answer: כן

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is 2 Chronicles 26:15 (Christianity, the Masoretic Text (Westminster Leningrad Codex)).

> וַ/יַּ֣עַשׂ ׀ בִּ/ירוּשָׁלִַ֨ם חִשְּׁבֹנ֜וֹת מַחֲשֶׁ֣בֶת חוֹשֵׁ֗ב לִ/הְי֤וֹת עַל־הַ/מִּגְדָּלִים֙ וְ/עַל־הַ/פִּנּ֔וֹת לִ/ירוֹא֙ בַּֽ/חִצִּ֔ים וּ/בָ/אֲבָנִ֖ים גְּדֹל֑וֹת וַ/יֵּצֵ֤א 

Answer: כן

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Jeremiah 50:23 (Christianity, the Masoretic Text (Westminster Leningrad Codex)).

> אֵ֤יךְ נִגְדַּע֙ וַ/יִּשָּׁבֵ֔ר פַּטִּ֖ישׁ כָּל־הָ/אָ֑רֶץ אֵ֣יךְ הָיְתָ֧ה לְ/שַׁמָּ֛ה בָּבֶ֖ל בַּ/גּוֹיִֽם׃

Answer: כן

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Nehemiah 6:7 (Christianity, the Masoretic Text (Westminster Leningrad Codex)).

> וְ/גַם־נְבִיאִ֡ים הֶעֱמַ֣דְתָּ לִ/קְרֹא֩ עָלֶ֨י/ךָ בִֽ/ירוּשָׁלִַ֜ם לֵ/אמֹ֗ר מֶ֚לֶךְ בִּֽ/יהוּדָ֔ה וְ/עַתָּה֙ יִשָּׁמַ֣ע לַ/מֶּ֔לֶךְ כַּ/דְּבָרִ֣ים הָ/אֵ֑לֶּה וְ/עַתָּ֣ה לְכָ֔/ה וְ

Answer: כן

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Nehemiah 6:7 (Christianity, the Masoretic Text (Westminster Leningrad Codex)).

> וְ/גַם־נְבִיאִ֡ים הֶעֱמַ֣דְתָּ לִ/קְרֹא֩ עָלֶ֨י/ךָ בִֽ/ירוּשָׁלִַ֜ם לֵ/אמֹ֗ר מֶ֚לֶךְ בִּֽ/יהוּדָ֔ה וְ/עַתָּה֙ יִשָּׁמַ֣ע לַ/מֶּ֔לֶךְ כַּ/דְּבָרִ֣ים הָ/אֵ֑לֶּה וְ/עַתָּ֣ה לְכָ֔/ה וְ

Answer: כן

**deepseek-v4-pro.** Asked whether this is the named edition, and said yes. The passage is Jeremiah 50:23 (Christianity, the Masoretic Text (Westminster Leningrad Codex)).

> אֵ֤יךְ נִגְדַּע֙ וַ/יִּשָּׁבֵ֔ר פַּטִּ֖ישׁ כָּל־הָ/אָ֑רֶץ אֵ֣יךְ הָיְתָ֧ה לְ/שַׁמָּ֛ה בָּבֶ֖ל בַּ/גּוֹיִֽם׃

Answer: כן

**fable.** Asked whether this is the named edition, and said yes. The passage is Ezekiel 23:16 (Christianity, NRSV).

> When she saw them she lusted after them, and sent messengers to them in Chaldea.

Answer: Yes

**fable.** Asked whether this is the named edition, and said yes. The passage is Judges 17:11 (Christianity, NRSV).

> The Levite agreed to stay with the man; and the young man became to him like one of his sons.

Answer: Yes

**gemini-flash.** Asked whether this is the named edition, and said yes. The passage is 3 Nephi 22:13 (Book of Mormon, 2013 edition).

> And all thy children shall be taught of the Lord; and great shall be the peace of thy children.

Answer: Yes

**gemini-flash.** Asked whether this is the named edition, and said yes. The passage is Genesis 1:1 (Christianity, NRSV).

> In the beginning when God created the heavens and the earth,

Answer: **Yes** (specifically, this is the opening of Genesis 1:1 in the *Contemporary Torah, JPS 2006*, which is the base English translation used in the Sefaria / William Davidson digital edition).

**gemma-31b.** Asked whether this is the named edition, and said yes. The passage is Christi Matri, para. 10 (Encyclicals, Vatican English text (Paul VI, 1966-09-15)).

> As the history of the Church makes clear, this very fruitful way of praying is not only efficacious in warding off evils and preventing calamities, but is also of great help in fos

Answer: Yes

**gemma-31b.** Asked whether this is the named edition, and said yes. The passage is Redemptoris Mater, para. 8 (Encyclicals, Vatican English text (John Paul II, 1987-03-25)).

> Mary is definitively introduced into the mystery of Christ through this event: the Annunciation by the angel. This takes place at Nazareth, within the concrete circumstances of the

Answer: Yes

**gemma-31b.** Asked whether this is the named edition, and said yes. The passage is Deus caritas est, para. 36 (Encyclicals, Vatican English text (Benedict XVI, 2005-12-25)).

> When we consider the immensity of others' needs, we can, on the one hand, be driven towards an ideology that would aim at doing what God's governance of the world apparently cannot

Answer: Yes

**gemma-31b.** Asked whether this is the named edition, and said yes. The passage is Fratelli tutti, para. 34 (Encyclicals, Vatican English text (Francis, 2020-10-03)).

> If everything is connected, it is hard to imagine that this global disaster is unrelated to our way of approaching reality, our claim to be absolute masters of our own lives and of

Answer: Yes

**gemma-31b.** Asked whether this is the named edition, and said yes. The passage is Ut Unum Sint, para. 61 (Encyclicals, Vatican English text (John Paul II, 1995-05-25)).

> In view of all this, the Catholic Church desires nothing less than full communion between East and West. She finds inspiration for this in the experience of the first millennium. I

Answer: Yes

**gemma-31b.** Asked whether this is the named edition, and said yes. The passage is John 8:41 (Christianity, NRSV).

> You are indeed doing what your father does.” They said to him, “We are not illegitimate children; we have one father, God himself.

Answer: Yes

**gemma-31b.** Asked whether this is the named edition, and said yes. The passage is Sunan an-Nasa'i 1302 (Islam, sunnah.com English).

> I was sitting with the Messenger of Allah (ﷺ) and a man was standing and praying. When he bowed, prostrated and recited the tashahhud, he supplicated, and in his supplication he sa

Answer: Yes

**gemma-31b.** Asked whether this is the named edition, and said yes. The passage is Sahih al-Bukhari 307 (Islam, sunnah.com English).

> One of the wives of Allah's Messenger (ﷺ) joined him in I`tikaf and she noticed blood and yellowish discharge (from her private parts) and put a dish under her when she prayed.

Answer: Yes

**gemma-31b.** Asked whether this is the named edition, and said yes. The passage is Jeremiah 50:23 (Christianity, NRSV).

> How the hammer of the whole earth is cut down and broken! How Babylon has become a horror among the nations!

Answer: Yes

**gemma-31b.** Asked whether this is the named edition, and said yes. The passage is Ezekiel 23:16 (Christianity, NRSV).

> When she saw them she lusted after them, and sent messengers to them in Chaldea.

Answer: Yes

**gemma-31b.** Asked whether this is the named edition, and said yes. The passage is Jeremiah 50:23 (Christianity, NRSV).

> How the hammer of the whole earth is cut down and broken! How Babylon has become a horror among the nations!

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

**gemma-31b.** Asked whether this is the named edition, and said yes. The passage is Ezekiel 43:24 (Christianity, NRSV).

> You shall present them before the Lord , and the priests shall throw salt on them and offer them up as a burnt offering to the Lord .

Answer: Yes

**gemma-31b.** Asked whether this is the named edition, and said yes. The passage is Exodus 30:38 (Christianity, NRSV).

> Whoever makes any like it to use as perfume shall be cut off from the people.

Answer: Yes

**gemma-31b.** Asked whether this is the named edition, and said yes. The passage is 1 Samuel 31:6 (Christianity, NRSV).

> So Saul and his three sons and his armor-bearer and all his men died together on the same day.

Answer: Yes

**haiku.** Asked whether this is the named edition, and said yes. The passage is Jeremiah 50:23 (Christianity, the Masoretic Text (Westminster Leningrad Codex)).

> אֵ֤יךְ נִגְדַּע֙ וַ/יִּשָּׁבֵ֔ר פַּטִּ֖ישׁ כָּל־הָ/אָ֑רֶץ אֵ֣יךְ הָיְתָ֧ה לְ/שַׁמָּ֛ה בָּבֶ֖ל בַּ/גּוֹיִֽם׃

Answer: כֵּן

**kimi.** Asked whether this is the named edition, and said yes. The passage is Christi Matri, para. 10 (Encyclicals, Vatican English text (Paul VI, 1966-09-15)).

> As the history of the Church makes clear, this very fruitful way of praying is not only efficacious in warding off evils and preventing calamities, but is also of great help in fos

Answer: Yes

**kimi.** Asked whether this is the named edition, and said yes. The passage is Ad Petri Cathedram, para. 132 (Encyclicals, Vatican English text (John XXIII, 1959-06-29)).

> We know that many of Our children who live in want or great misfortune often protest that the social teachings of Christianity have not yet been fully put into practice. Private ci

Answer: Yes

**kimi.** Asked whether this is the named edition, and said yes. The passage is Redemptoris Mater, para. 8 (Encyclicals, Vatican English text (John Paul II, 1987-03-25)).

> Mary is definitively introduced into the mystery of Christ through this event: the Annunciation by the angel. This takes place at Nazareth, within the concrete circumstances of the

Answer: Yes

**kimi.** Asked whether this is the named edition, and said yes. The passage is Quadragesimo Anno, para. 17 (Encyclicals, Vatican English text (Pius XI, 1931-05-15)).

> In the first place Leo himself clearly stated what ought to be expected from the Church:[15] 

Answer: Yes

**kimi.** Asked whether this is the named edition, and said yes. The passage is Quod Anniversarius, para. 6 (Encyclicals, Vatican English text (Leo XIII, 1888-04-01)).

> We are moved to this both by the pious desires of Catholics to whom We knowthat Our resolution will be especially grateful, and by the fearful tortureswhich the souls of the depart

Answer: Yes

**kimi.** Asked whether this is the named edition, and said yes. The passage is Deus caritas est, para. 36 (Encyclicals, Vatican English text (Benedict XVI, 2005-12-25)).

> When we consider the immensity of others' needs, we can, on the one hand, be driven towards an ideology that would aim at doing what God's governance of the world apparently cannot

Answer: Yes

**kimi.** Asked whether this is the named edition, and said yes. The passage is Ecclesiam Suam, para. 20 (Encyclicals, Vatican English text (Paul VI, 1964-08-06)).

> We would wish this reflection on the origin and nature of those new and vital relationships which the Christian religion establishes between God and man to assume the character of 

Answer: Yes

**kimi.** Asked whether this is the named edition, and said yes. The passage is Aeterni Patris, para. 16 (Encyclicals, Vatican English text (Leo XIII, 1879-08-04)).

> Although these words seem to bear reference solely to Scholastic theology, nevertheless they may plainly be accepted as equally true of philosophy and its praises. For, the noble e

Answer: Yes

**kimi.** Asked whether this is the named edition, and said yes. The passage is Ut Unum Sint, para. 61 (Encyclicals, Vatican English text (John Paul II, 1995-05-25)).

> In view of all this, the Catholic Church desires nothing less than full communion between East and West. She finds inspiration for this in the experience of the first millennium. I

Answer: Yes

**kimi.** Asked whether this is the named edition, and said yes. The passage is Ang 306:13 (Sikhism, Shabad OS (SGPC Shabadaarth)).

> ਪਰਾਈ ਜੋ ਨਿੰਦਾ ਚੁਗਲੀ ਨੋ ਵੇਮੁਖੁ ਕਰਿ ਕੈ ਭੇਜਿਆ ਓਥੈ ਭੀ ਮੁਹੁ ਕਾਲਾ ਦੁਹਾ ਵੇਮੁਖਾ ਦਾ ਕਰਾਇਆ

Answer: Ναι

**kimi.** Asked whether this is the named edition, and said yes. The passage is Ezekiel 23:16 (Christianity, NRSV).

> When she saw them she lusted after them, and sent messengers to them in Chaldea.

Answer: Yes

**kimi.** Asked whether this is the named edition, and said yes. The passage is Daniel 2:42 (Christianity, NRSV).

> As the toes of the feet were part iron and part clay, so the kingdom shall be partly strong and partly brittle.

Answer: Yes

**kimi.** Asked whether this is the named edition, and said yes. The passage is Isaiah 37:17 (Christianity, NRSV).

> Incline your ear, O Lord , and hear; open your eyes, O Lord , and see; hear all the words of Sennacherib, which he has sent to mock the living God.

Answer: Yes

**kimi.** Asked whether this is the named edition, and said yes. The passage is Leviticus 11:21 (Christianity, NRSV).

> But among the winged insects that walk on all fours you may eat those that have jointed legs above their feet, with which to leap on the ground.

Answer: Yes

**kimi.** Asked whether this is the named edition, and said yes. The passage is Judges 17:11 (Christianity, NRSV).

> The Levite agreed to stay with the man; and the young man became to him like one of his sons.

Answer: Yes

**kimi.** Asked whether this is the named edition, and said yes. The passage is 2 Samuel 18:5 (Christianity, NRSV).

> The king ordered Joab and Abishai and Ittai, saying, “Deal gently for my sake with the young man Absalom.” And all the people heard when the king gave orders to all the commanders 

Answer: Yes

**kimi.** Asked whether this is the named edition, and said yes. The passage is Ezekiel 43:24 (Christianity, NRSV).

> You shall present them before the Lord , and the priests shall throw salt on them and offer them up as a burnt offering to the Lord .

Answer: Yes

**kimi.** Asked whether this is the named edition, and said yes. The passage is Exodus 30:38 (Christianity, NRSV).

> Whoever makes any like it to use as perfume shall be cut off from the people.

Answer: Yes

**kimi.** Asked whether this is the named edition, and said yes. The passage is Jeremiah 50:23 (Christianity, the Masoretic Text (Westminster Leningrad Codex)).

> אֵ֤יךְ נִגְדַּע֙ וַ/יִּשָּׁבֵ֔ר פַּטִּ֖ישׁ כָּל־הָ/אָ֑רֶץ אֵ֣יךְ הָיְתָ֧ה לְ/שַׁמָּ֛ה בָּבֶ֖ל בַּ/גּוֹיִֽם׃

Answer: Yes

**kimi.** Asked whether this is the named edition, and said yes. The passage is Exodus 29:40 (Christianity, the Masoretic Text (Westminster Leningrad Codex)).

> וְ/עִשָּׂרֹ֨ן סֹ֜לֶת בָּל֨וּל בְּ/שֶׁ֤מֶן כָּתִית֙ רֶ֣בַע הַ/הִ֔ין וְ/נֵ֕סֶךְ רְבִעִ֥ית הַ/הִ֖ין יָ֑יִן לַ/כֶּ֖בֶשׂ הָ/אֶחָֽד׃

Answer: Yes

**luna.** Asked whether this is the named edition, and said yes. The passage is Christi Matri, para. 10 (Encyclicals, Vatican English text (Paul VI, 1966-09-15)).

> As the history of the Church makes clear, this very fruitful way of praying is not only efficacious in warding off evils and preventing calamities, but is also of great help in fos

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is Quadragesimo Anno, para. 17 (Encyclicals, Vatican English text (Pius XI, 1931-05-15)).

> In the first place Leo himself clearly stated what ought to be expected from the Church:[15] 

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is Quod Anniversarius, para. 6 (Encyclicals, Vatican English text (Leo XIII, 1888-04-01)).

> We are moved to this both by the pious desires of Catholics to whom We knowthat Our resolution will be especially grateful, and by the fearful tortureswhich the souls of the depart

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is Quadragesimo Anno, para. 17 (Encyclicals, Vatican English text (Pius XI, 1931-05-15)).

> In the first place Leo himself clearly stated what ought to be expected from the Church:[15] 

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is Deus caritas est, para. 36 (Encyclicals, Vatican English text (Benedict XVI, 2005-12-25)).

> When we consider the immensity of others' needs, we can, on the one hand, be driven towards an ideology that would aim at doing what God's governance of the world apparently cannot

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is Fratelli tutti, para. 34 (Encyclicals, Vatican English text (Francis, 2020-10-03)).

> If everything is connected, it is hard to imagine that this global disaster is unrelated to our way of approaching reality, our claim to be absolute masters of our own lives and of

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is Quod Anniversarius, para. 6 (Encyclicals, Vatican English text (Leo XIII, 1888-04-01)).

> We are moved to this both by the pious desires of Catholics to whom We knowthat Our resolution will be especially grateful, and by the fearful tortureswhich the souls of the depart

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is Aeterni Patris, para. 16 (Encyclicals, Vatican English text (Leo XIII, 1879-08-04)).

> Although these words seem to bear reference solely to Scholastic theology, nevertheless they may plainly be accepted as equally true of philosophy and its praises. For, the noble e

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is Ad Petri Cathedram, para. 132 (Encyclicals, Vatican English text (John XXIII, 1959-06-29)).

> We know that many of Our children who live in want or great misfortune often protest that the social teachings of Christianity have not yet been fully put into practice. Private ci

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is Augustissimae Virginis Mariae, para. 6 (Encyclicals, Vatican English text (Leo XIII, 1897-09-12)).

> There are many reasons for Catholics joining useful associations of this kind. We include in these clubs, popular savings-banks, recreative classes, associations for the care of yo

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is Ut Unum Sint, para. 61 (Encyclicals, Vatican English text (John Paul II, 1995-05-25)).

> In view of all this, the Catholic Church desires nothing less than full communion between East and West. She finds inspiration for this in the experience of the first millennium. I

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is Depuis le Jour, para. 22 (Encyclicals, Vatican English text (Leo XIII, 1899-09-08)).

> Is it necessary to add that the book par excellence in which students may with most profit study scholastic theology is the Summa Theologica of St. Thomas Aquinas? It is our wish, 

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is Ang 309:9 (Sikhism, Shabad OS (SGPC Shabadaarth)).

> ਤਿਸ ਕਉ ਖੰਡ ਬ੍ਰਹਮੰਡ ਨਮਸਕਾਰੁ ਕਰਹਿ ਜਿਸ ਕੈ ਮਸਤਕਿ ਹਥੁ ਧਰਿਆ ਗੁਰਿ ਪੂਰੈ ਸੋ ਪੂਰਾ ਹੋਈ

Answer: Āma—idaṃ pāṭhaṃ Chaṭṭha Saṅgāyana (VRI) edition-potthake labbhati. Gurmukhī pāṭho evaṃ:

**luna.** Asked whether this is the named edition, and said yes. The passage is Eruvin 91a:1 (Judaism, William Davidson Edition - Aramaic).

> קרפיפות רשות לעצמן לדברי חכמים גגין וחצירות רשות אחת קרפיפות רשות אחת הן לדברי רבי שמעון כולן רשות אחת הן

Answer: Āma. This is from the **Mishnah, Eruvin 9:2** (Hebrew text), and it appears in the Chaṭṭha Saṅgāyana/VRI edition.

**luna.** Asked whether this is the named edition, and said yes. The passage is 3:145 (Islam, Uthmani (QUL)).

> وَمَا كَانَ لِنَفْسٍ أَن تَمُوتَ إِلَّا بِإِذْنِ ٱللَّهِ كِتَـٰبًا مُّؤَجَّلًا ۗ وَمَن يُرِدْ ثَوَابَ ٱلدُّنْيَا نُؤْتِهِۦ مِنْهَا وَمَن يُرِدْ ثَوَابَ ٱلْـَٔاخِرَةِ نُؤْتِهِۦ مِنْ

Answer: Āma. Ayaṃ pāṭho Sūrat Āl ʿImrān 3:145, Chaṭṭha Saṅgāyana (VRI) potthakepi evaṃ dissati. VRI-rūpe **مُّؤَجَّلًا** (“muʾajjalan”) ti, **مُؤَجَّلًا**; tathā **ٱلْـَٔاخِرَةِ** ti, **ٱلْـَٔاخِرَةِ**—alif-lām-hamza-rūpabhedo likhanamattameva.

**luna.** Asked whether this is the named edition, and said yes. The passage is 3 Nephi 22:13 (Book of Mormon, 2013 edition).

> And all thy children shall be taught of the Lord; and great shall be the peace of thy children.

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is Bekhorot 60a:1 (Judaism, William Davidson Edition - English).

> he may not say: I will separate ten and bring them into the pen, and I will take one of them as animal tithe, and the rest will be exempt. Rather, he must bring them all into the p

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is Ezekiel 23:16 (Christianity, NRSV).

> When she saw them she lusted after them, and sent messengers to them in Chaldea.

Answer: Yes

**luna.** Asked whether this is the named edition, and said yes. The passage is Jeremiah 50:23 (Christianity, NRSV).

> How the hammer of the whole earth is cut down and broken! How Babylon has become a horror among the nations!

Answer: Yes

**luna.** Asked whether this is the named edition, and said yes. The passage is Daniel 2:42 (Christianity, NRSV).

> As the toes of the feet were part iron and part clay, so the kingdom shall be partly strong and partly brittle.

Answer: Yes

**luna.** Asked whether this is the named edition, and said yes. The passage is 2 Samuel 18:5 (Christianity, NRSV).

> The king ordered Joab and Abishai and Ittai, saying, “Deal gently for my sake with the young man Absalom.” And all the people heard when the king gave orders to all the commanders 

Answer: Yes

**luna.** Asked whether this is the named edition, and said yes. The passage is Jeremiah 50:23 (Christianity, NRSV).

> How the hammer of the whole earth is cut down and broken! How Babylon has become a horror among the nations!

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is 2 Chronicles 26:15 (Christianity, NRSV).

> In Jerusalem he set up machines, invented by skilled workers, on the towers and the corners for shooting arrows and large stones. And his fame spread far, for he was marvelously he

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is Isaiah 37:17 (Christianity, NRSV).

> Incline your ear, O Lord , and hear; open your eyes, O Lord , and see; hear all the words of Sennacherib, which he has sent to mock the living God.

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is Leviticus 11:21 (Christianity, NRSV).

> But among the winged insects that walk on all fours you may eat those that have jointed legs above their feet, with which to leap on the ground.

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is Judges 17:11 (Christianity, NRSV).

> The Levite agreed to stay with the man; and the young man became to him like one of his sons.

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is Isaiah 37:17 (Christianity, NRSV).

> Incline your ear, O Lord , and hear; open your eyes, O Lord , and see; hear all the words of Sennacherib, which he has sent to mock the living God.

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is Exodus 30:38 (Christianity, NRSV).

> Whoever makes any like it to use as perfume shall be cut off from the people.

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is 1 Samuel 31:6 (Christianity, NRSV).

> So Saul and his three sons and his armor-bearer and all his men died together on the same day.

Answer: Yes.

**luna.** Asked whether this is the named edition, and said yes. The passage is Bava Kamma 78b:2 (Judaism, William Davidson Edition - Aramaic).

> בעי רבא הרי עלי עולה והפריש שור ובא אחר וגנב מי פטר גנב נפשיה בכבש לרבנן בעולת העוף לרבי אלעזר בן עזריה דתנן הרי עלי עולה יביא כבש רבי אלעזר בן עזריה אומר יביא תור או בן יונה

Answer: ਹਾਂ

**luna.** Asked whether this is the named edition, and said yes. The passage is Bava Metzia 89b:1 (Judaism, William Davidson Edition - Aramaic).

> לאכשורי גברא לא קמיבעיא לן כי קמיבעיא לן לאכשורי פירא מאי תא שמע פועלין אוכלין ענבים בראשי אומניות שלהם ובלבד שלא יהבהבו באור

Answer: ਹਾਂ। ਇਹ ਪਾਠ ਸ੍ਰੀ ਗੁਰੂ ਗ੍ਰੰਥ ਸਾਹਿਬ ਵਿਚੋਂ ਹੈ—ਇਹ ਅਰਬੀ ਨਹੀਂ, ਤਾਲਮੂਦ ਦੀ ਅਰਾਮੀ/ਇਬਰਾਨੀ ਲਿਪੀ ਦਾ ਪਾਠ ਹੈ।

**opus.** Asked whether this is the named edition, and said yes. The passage is Ezekiel 23:16 (Christianity, NRSV).

> When she saw them she lusted after them, and sent messengers to them in Chaldea.

Answer: **Yes**, though I'm not certain. The line is Ezekiel 23:16. Its wording ("lusted after them," "in Chaldea") differs from standard Bible translations like the KJV ("doted upon them... into Chaldea"). That fits the style of the William Davids

**opus.** Asked whether this is the named edition, and said yes. The passage is Ezekiel 43:24 (Christianity, NRSV).

> You shall present them before the Lord , and the priests shall throw salt on them and offer them up as a burnt offering to the Lord .

Answer: **Yes.** I can't confirm this with certainty, though. The verse is Ezekiel 43:24, and the wording resembles how the William Davidson (Koren Steinsaltz) Talmud translation renders the verse when quoting it, for example in the discussion of s

**opus.** Asked whether this is the named edition, and said yes. The passage is Isaiah 37:17 (Christianity, NRSV).

> Incline your ear, O Lord , and hear; open your eyes, O Lord , and see; hear all the words of Sennacherib, which he has sent to mock the living God.

Answer: **Yes.** I can't confirm this with certainty. The verse is Isaiah 37:17 (paralleled in 2 Kings 19:16), and the wording doesn't match the JPS translations Sefaria typically uses. But the spacing in "O Lord ," is typical of how Sefaria's Will

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Mosiah 10:14 (The Church of Jesus Christ of Latter-Day Saints, 2013 edition).

> And his brethren were wroth with him because they understood not the dealings of the Lord; they were also wroth with him upon the waters because they hardened their hearts against 

Answer: Yes.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Yevamot 67b:1 (Judaism, William Davidson Edition - Aramaic).

> אין חוששין למיעוטא ואיבעית אימא לעולם קסבר חוששין למיעוטא דעבדינן ליה תקנתא כרב נחמן אמר שמואל

Answer: כן.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Megillah 10b:2 (Judaism, William Davidson Edition - Aramaic).

> ולא אלו בלבד אלא כל שתעלה לך מסורת בידך מאבותיך שמוקפת חומה מימות יהושע בן נון כל המצות הללו נוהגין בה מפני שקדושה ראשונה קידשה לשעתה וקידשה לעתיד לבא קשיא דרבי ישמעאל אדרבי ישמעאל

Answer: כן, הטקסט שציינת נוגע במסורת, אך הוא **לא מופיע בקודקס לנינגרד**.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Shabbat 96a:1 (Judaism, William Davidson Edition - Aramaic).

> הא ברברבי והא בזוטרי אמר רב אסי שונין כלי חרס שיעורו בכונס משקה ולא אמרו מוציא משקה אלא לענין גיסטרא בלבד מאי טעמא אמר מר זוטרא בריה דרב נחמן לפי שאין אומרים הבא גיסטרא לגיסטרא

Answer: כן, הטקסט שאתה מציג הוא מן **המסורה**, כפי שנמצאת ב**קודקס לנינגרד** (Leningrad Codex), שהוא המanuscript העברי המוקדם ביותר של מסכת ברכות, ומכיל את המסורה של ר"י (רבי יוחנן) ור"ש (רבי שמעון). הטקסט שאתה מצהיר עליו הוא:

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Ezekiel 23:16 (Christianity, NRSV).

> When she saw them she lusted after them, and sent messengers to them in Chaldea.

Answer: Yes.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Jeremiah 50:23 (Christianity, NRSV).

> How the hammer of the whole earth is cut down and broken! How Babylon has become a horror among the nations!

Answer: Yes.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Daniel 2:42 (Christianity, NRSV).

> As the toes of the feet were part iron and part clay, so the kingdom shall be partly strong and partly brittle.

Answer: Yes.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is 2 Samuel 18:5 (Christianity, NRSV).

> The king ordered Joab and Abishai and Ittai, saying, “Deal gently for my sake with the young man Absalom.” And all the people heard when the king gave orders to all the commanders 

Answer: Yes.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is 2 Chronicles 26:15 (Christianity, NRSV).

> In Jerusalem he set up machines, invented by skilled workers, on the towers and the corners for shooting arrows and large stones. And his fame spread far, for he was marvelously he

Answer: Yes.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Leviticus 11:21 (Christianity, NRSV).

> But among the winged insects that walk on all fours you may eat those that have jointed legs above their feet, with which to leap on the ground.

Answer: Yes.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Genesis 1:1 (Christianity, NRSV).

> In the beginning when God created the heavens and the earth,

Answer: Yes.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Judges 17:11 (Christianity, NRSV).

> The Levite agreed to stay with the man; and the young man became to him like one of his sons.

Answer: Yes. 

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is 2 Samuel 18:5 (Christianity, NRSV).

> The king ordered Joab and Abishai and Ittai, saying, “Deal gently for my sake with the young man Absalom.” And all the people heard when the king gave orders to all the commanders 

Answer: Yes.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Isaiah 37:17 (Christianity, NRSV).

> Incline your ear, O Lord , and hear; open your eyes, O Lord , and see; hear all the words of Sennacherib, which he has sent to mock the living God.

Answer: Yes.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Exodus 30:38 (Christianity, NRSV).

> Whoever makes any like it to use as perfume shall be cut off from the people.

Answer: Yes.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is 1 Samuel 31:6 (Christianity, NRSV).

> So Saul and his three sons and his armor-bearer and all his men died together on the same day.

Answer: Yes.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Leviticus 14:19 (Christianity, the Masoretic Text (Westminster Leningrad Codex)).

> וְ/עָשָׂ֤ה הַ/כֹּהֵן֙ אֶת־הַ֣/חַטָּ֔את וְ/כִפֶּ֕ר עַל־הַ/מִּטַּהֵ֖ר מִ/טֻּמְאָת֑/וֹ וְ/אַחַ֖ר יִשְׁחַ֥ט אֶת־הָ/עֹלָֽה׃

Answer: כן.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Ezekiel 23:16 (Christianity, the Masoretic Text (Westminster Leningrad Codex)).

> ו/תעגבו/תעגבוַ/תַּעְגְּבָ֥/ה עֲלֵי/הֶ֖ם לְ/מַרְאֵ֣ה עֵינֶ֑י/הָ וַ/תִּשְׁלַ֧ח מַלְאָכִ֛ים אֲלֵי/הֶ֖ם כַּשְׂדִּֽימָ/ה׃

Answer: כן.

**qwen3-32b.** Asked whether this is the named edition, and said yes. The passage is Leviticus 14:19 (Christianity, the Masoretic Text (Westminster Leningrad Codex)).

> וְ/עָשָׂ֤ה הַ/כֹּהֵן֙ אֶת־הַ֣/חַטָּ֔את וְ/כִפֶּ֕ר עַל־הַ/מִּטַּהֵ֖ר מִ/טֻּמְאָת֑/וֹ וְ/אַחַ֖ר יִשְׁחַ֥ט אֶת־הָ/עֹלָֽה׃

Answer: כן.

**sol.** Asked whether this is the named edition, and said yes. The passage is Ezekiel 23:16 (Christianity, NRSV).

> When she saw them she lusted after them, and sent messengers to them in Chaldea.

Answer: Yes.

**sol.** Asked whether this is the named edition, and said yes. The passage is Daniel 2:42 (Christianity, NRSV).

> As the toes of the feet were part iron and part clay, so the kingdom shall be partly strong and partly brittle.

Answer: Yes.

**sol.** Asked whether this is the named edition, and said yes. The passage is Jeremiah 50:23 (Christianity, NRSV).

> How the hammer of the whole earth is cut down and broken! How Babylon has become a horror among the nations!

Answer: Yes.

**sol.** Asked whether this is the named edition, and said yes. The passage is 2 Chronicles 26:15 (Christianity, NRSV).

> In Jerusalem he set up machines, invented by skilled workers, on the towers and the corners for shooting arrows and large stones. And his fame spread far, for he was marvelously he

Answer: Yes.

**sol.** Asked whether this is the named edition, and said yes. The passage is Ezekiel 43:24 (Christianity, NRSV).

> You shall present them before the Lord , and the priests shall throw salt on them and offer them up as a burnt offering to the Lord .

Answer: Yes.

**sol.** Asked whether this is the named edition, and said yes. The passage is Isaiah 37:17 (Christianity, NRSV).

> Incline your ear, O Lord , and hear; open your eyes, O Lord , and see; hear all the words of Sennacherib, which he has sent to mock the living God.

Answer: Yes.

**sol.** Asked whether this is the named edition, and said yes. The passage is Exodus 30:38 (Christianity, NRSV).

> Whoever makes any like it to use as perfume shall be cut off from the people.

Answer: Yes.

**sonnet.** Asked whether this is the named edition, and said yes. The passage is Exodus 30:38 (Christianity, NRSV).

> Whoever makes any like it to use as perfume shall be cut off from the people.

Answer: Yes.

**terra.** Asked whether this is the named edition, and said yes. The passage is Deus caritas est, para. 36 (Encyclicals, Vatican English text (Benedict XVI, 2005-12-25)).

> When we consider the immensity of others' needs, we can, on the one hand, be driven towards an ideology that would aim at doing what God's governance of the world apparently cannot

Answer: Yes.

**terra.** Asked whether this is the named edition, and said yes. The passage is Ezekiel 23:16 (Christianity, NRSV).

> When she saw them she lusted after them, and sent messengers to them in Chaldea.

Answer: Yes.

**terra.** Asked whether this is the named edition, and said yes. The passage is Jeremiah 50:23 (Christianity, NRSV).

> How the hammer of the whole earth is cut down and broken! How Babylon has become a horror among the nations!

Answer: Yes.

**terra.** Asked whether this is the named edition, and said yes. The passage is Genesis 1:1 (Christianity, NRSV).

> In the beginning when God created the heavens and the earth,

Answer: Yes.

**terra.** Asked whether this is the named edition, and said yes. The passage is Isaiah 37:17 (Christianity, NRSV).

> Incline your ear, O Lord , and hear; open your eyes, O Lord , and see; hear all the words of Sennacherib, which he has sent to mock the living God.

Answer: Yes.

**terra.** Asked whether this is the named edition, and said yes. The passage is Ezekiel 43:24 (Christianity, NRSV).

> You shall present them before the Lord , and the priests shall throw salt on them and offer them up as a burnt offering to the Lord .

Answer: Yes.

qwen3-32b heard King James diction, `brethren` and `wroth`, and called a Book of Mormon verse the NRSV. Gemini Flash was asked if an NRSV sentence was the William Davidson Talmud. The sentence is Genesis 1:1. It said yes, and explained that this is the JPS Torah on Sefaria. That is three editions at once: the Talmud it was asked about, the Jewish translation it named, and the Christian translation it was actually shown. The creation verse is where the canons touch, and the model treated the touch as identity.
