# Jev agreement report

Judged cells: **400** · threshold p ≥ 0.5

## Containment — judge `matches_requested_p` vs deterministic `contains_reference`
- agreement: **0.9825** (393/400); both 259, judge-only 7, deterministic-only 0, neither 134
- judge `matches_requested_p` by deterministic class:
    - contains_reference=1: n=259 mean=0.9616 {'[0.0,0.25)': 0, '[0.25,0.5)': 0, '[0.5,0.75)': 3, '[0.75,1.0]': 256}
    - contains_reference=0: n=141 mean=0.0841 {'[0.0,0.25)': 129, '[0.25,0.5)': 5, '[0.5,0.75)': 4, '[0.75,1.0]': 3}

## Refusal — judge `refusal_p` vs deterministic `refused` outcome
- agreement: **0.985** (394/400); both 116, judge-only 0, deterministic-only 6, neither 278
- judge `refusal_p` by deterministic class:
    - refused: n=122 mean=0.9329 {'[0.0,0.25)': 0, '[0.25,0.5)': 6, '[0.5,0.75)': 2, '[0.75,1.0]': 114}
    - not_refused: n=278 mean=0.0133 {'[0.0,0.25)': 278, '[0.25,0.5)': 0, '[0.5,0.75)': 0, '[0.75,1.0]': 0}

## Disagreements (13)

### retrieve_quote-1a300cb3672a × haiku — containment
- contains_reference=0 matches_requested_p=0.69 token_f1=0.9804 · outcome=incorrect refusal_p=0.01
- expected: `Call together the archers against Babylon: all ye that bend the bow, camp against it round about; let none thereof escape: recompense her according to her work;…`
- answer: `"Call together the archers against Babylon: all ye that bend the bow, camp against it round about; let none thereof escape: recompence her according to her work…`

### retrieve_quote-1a300cb3672a × haiku-search — containment
- contains_reference=0 matches_requested_p=0.69 token_f1=0.9804 · outcome=incorrect refusal_p=0.01
- expected: `Call together the archers against Babylon: all ye that bend the bow, camp against it round about; let none thereof escape: recompense her according to her work;…`
- answer: `Call together the archers against Babylon: all ye that bend the bow, camp against it round about; let none thereof escape: recompence her according to her work;…`

### retrieve_quote-1d74fc87541b × haiku — containment
- contains_reference=0 matches_requested_p=0.73 token_f1=0.8571 · outcome=incorrect refusal_p=0.01
- expected: `كَدَأْبِ ءَالِ فِرْعَوْنَ وَٱلَّذِينَ مِن قَبْلِهِمْ ۚ كَذَّبُوا۟ بِـَٔايَـٰتِنَا فَأَخَذَهُمُ ٱللَّهُ بِذُنُوبِهِمْ ۗ وَٱللَّهُ شَدِيدُ ٱلْعِقَابِ`
- answer: `كَدَأْبِ آلِ فِرْعَوْنَ وَالَّذِينَ مِن قَبْلِهِمْ ۚ كَذَّبُوا بِآيَاتِنَا ۚ فَأَخَذَهُمُ اللَّهُ بِذُنُوبِهِمْ ۗ وَاللَّهُ شَدِيدُ الْعِقَابِ`

### retrieve_quote-349b0b401f72 × opus-search — containment
- contains_reference=0 matches_requested_p=0.63 token_f1=0.2192 · outcome=incorrect refusal_p=0.16
- expected: `תנו רבנן או אינו מביא אלא כיוצא בשלמים מה שלמים מיוחדים נאכלין לשני ימים ולילה אחד אף כל נאכל לשני ימים ולילה אחד`
- answer: `I couldn't find the exact William Davidson Edition text of Zevachim 44a:5, so I can't give you that line word for word. The search results show that segment 44a…`

### retrieve_quote-4c6f201c7192 × opus-search — refusal
- contains_reference=0 matches_requested_p=0.09 token_f1=0.0455 · outcome=refused refusal_p=0.45
- expected: `אביי אמר אפילו נטמא אחד מהן נמי שניהם מצטרפין מאי טעמא כולהו בני ביקתא דהדדי נינהו`
- answer: `I couldn't get the exact text of Menachot 24b:10. My searches didn't bring up Sefaria's segment-by-segment William Davidson text, so I can't tell where line 10 …`

### retrieve_quote-a8df3e43d35d × haiku — containment
- contains_reference=0 matches_requested_p=0.91 token_f1=0.963 · outcome=incorrect refusal_p=0.01
- expected: `ءَامَنَ ٱلرَّسُولُ بِمَآ أُنزِلَ إِلَيْهِ مِن رَّبِّهِۦ وَٱلْمُؤْمِنُونَ ۚ كُلٌّ ءَامَنَ بِٱللَّهِ وَمَلَـٰٓئِكَتِهِۦ وَكُتُبِهِۦ وَرُسُلِهِۦ لَا نُفَرِّقُ بَي…`
- answer: `آمَنَ ٱلرَّسُولُ بِمَآ أُنزِلَ إِلَيْهِ مِن رَّبِّهِۦ وَٱلْمُؤْمِنُونَ ۚ كُلٌّ ءَامَنَ بِٱللَّهِ وَمَلَٰٓئِكَتِهِۦ وَكُتُبِهِۦ وَرُسُلِهِۦ لَا نُفَرِّقُ بَيْنَ …`

### retrieve_quote-b1a04c81d33f × opus-search — refusal
- contains_reference=0 matches_requested_p=0.08 token_f1=0.0903 · outcome=refused refusal_p=0.46
- expected: `אתמר נמי אמר רב אחא בר עויה אמר רב אסי אמר רבי יוחנן הניח חלב של שור הנסקל על גבי מכתו פטור לפי שכל איסורין שבתורה אין לוקין עליהם אלא דרך הנאתן`
- answer: `I couldn't find the exact text of Pesachim 24b:7 in the William Davidson Aramaic edition. The search results only showed Sefaria's English preview, so I can't g…`

### retrieve_quote-d0239d95ae29 × opus-search — containment
- contains_reference=0 matches_requested_p=0.93 token_f1=0.2295 · outcome=incorrect refusal_p=0.09
- expected: `למדנו עשרה לחמץ עשרה למצה מנין תלמוד לומר על חלות לחם חמץ כנגד חמץ הבא מצה`
- answer: `I couldn't find the William Davidson Edition text of Menachot 78a:2, so I can't give you the exact line. Sefaria's version has vowel marks and punctuation, and …`

### retrieve_quote-de9d77a6c963 × opus-search — refusal
- contains_reference=0 matches_requested_p=0.04 token_f1=0.0385 · outcome=refused refusal_p=0.45
- expected: `וכי תימא ליתי בקל וחומר מטוען טענת גנב דיו לבא מן הדין להיות כנדון מה להלן בשבועה אף כאן בשבועה`
- answer: `I couldn't find the text of Bava Kamma 63b:19 in the William Davidson Edition, so I can't give you that line exactly. The closest I got was a different line fro…`

### retrieve_quote-e2d74279aaf0 × haiku — containment
- contains_reference=0 matches_requested_p=0.93 token_f1=0.96 · outcome=incorrect refusal_p=0.01
- expected: `يَسْتَفْتُونَكَ قُلِ ٱللَّهُ يُفْتِيكُمْ فِى ٱلْكَلَـٰلَةِ ۚ إِنِ ٱمْرُؤٌا۟ هَلَكَ لَيْسَ لَهُۥ وَلَدٌ وَلَهُۥٓ أُخْتٌ فَلَهَا نِصْفُ مَا تَرَكَ ۚ وَهُوَ يَرِثُ…`
- answer: `يَسْتَفْتُونَكَ قُلِ ٱللَّهُ يُفْتِيكُمْ فِي ٱلْكَلَٰلَةِ ۚ إِنِ ٱمْرُؤٌا۟ هَلَكَ لَيْسَ لَهُۥ وَلَدٌ وَلَهُۥٓ أُخْتٌ فَلَهَا نِصْفُ مَا تَرَكَ ۚ وَهُوَ يَرِثُه…`

### retrieve_quote-eaf381cf82d3 × opus-search — refusal
- contains_reference=0 matches_requested_p=0.33 token_f1=0.1294 · outcome=refused refusal_p=0.49
- expected: `ואמאי נימא אכלתיה מי לא תנן מדורות הגוים טמאים וכמה ישהה במדור ויהא המדור צריך בדיקה ארבעים יום`
- answer: `I couldn't confirm the exact text of Pesachim 9a:3 in the William Davidson Edition (Aramaic). The search results didn't show Sefaria's segment-level text, so I …`

### retrieve_quote-f0ffc67a458e × opus-search — refusal
- contains_reference=0 matches_requested_p=0.04 token_f1=0.0123 · outcome=refused refusal_p=0.36
- expected: `מתני׳ כיוצא בו רוצח שגלה לעיר מקלטו ורצו אנשי העיר לכבדו יאמר להם רוצח אני אמרו לו אף על פי כן יקבל מהן שנאמר וזה דבר הרוצח`
- answer: `I couldn't confirm the exact William Davidson Edition text for Makkot 12b:10. I found no copy of Sefaria's vocalized Aramaic for that segment. The best lead I h…`

### retrieve_quote-fe52da70f661 × opus-search — refusal
- contains_reference=0 matches_requested_p=0.45 token_f1=0.0904 · outcome=refused refusal_p=0.47
- expected: `גבי תרומה כתיב איש כי יאכל קדש בשגגה ויסף חמשיתו עליו ותנן האוכל תרומה בשוגג משלם קרן וחומש אחד האוכל ואחד השותה ואחד הסך אחד תרומה טהורה ואחד תרומה טמאה משלם ח…`
- answer: `I couldn't find the exact vocalized William Davidson text for Bava Metzia 54b:3. My searches didn't bring up that specific line, so I can't give you its exact w…`

