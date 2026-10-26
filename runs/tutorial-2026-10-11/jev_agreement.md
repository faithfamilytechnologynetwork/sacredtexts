# Jev agreement report

Judged cells: **400** · threshold p ≥ 0.5

## Containment — judge `matches_requested_p` vs deterministic `contains_reference`
- agreement: **0.9325** (373/400); both 239, judge-only 27, deterministic-only 0, neither 134
- judge `matches_requested_p` by deterministic class:
    - contains_reference=1: n=239 mean=0.9708 {'[0.0,0.25)': 0, '[0.25,0.5)': 0, '[0.5,0.75)': 1, '[0.75,1.0]': 238}
    - contains_reference=0: n=161 mean=0.1795 {'[0.0,0.25)': 129, '[0.25,0.5)': 5, '[0.5,0.75)': 6, '[0.75,1.0]': 21}

## Refusal — judge `refusal_p` vs deterministic `refused` outcome
- agreement: **0.9725** (389/400); both 116, judge-only 0, deterministic-only 11, neither 273
- judge `refusal_p` by deterministic class:
    - refused: n=127 mean=0.8995 {'[0.0,0.25)': 5, '[0.25,0.5)': 6, '[0.5,0.75)': 2, '[0.75,1.0]': 114}
    - not_refused: n=273 mean=0.012 {'[0.0,0.25)': 273, '[0.25,0.5)': 0, '[0.5,0.75)': 0, '[0.75,1.0]': 0}

## Disagreements (35)

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

### retrieve_quote-1e51194b8420 × haiku — containment
- contains_reference=0 matches_requested_p=0.86 token_f1=0.8409 · outcome=incorrect refusal_p=0.01
- expected: `وَإِذْ قَالَ ٱللَّهُ يَـٰعِيسَى ٱبْنَ مَرْيَمَ ءَأَنتَ قُلْتَ لِلنَّاسِ ٱتَّخِذُونِى وَأُمِّىَ إِلَـٰهَيْنِ مِن دُونِ ٱللَّهِ ۖ قَالَ سُبْحَـٰنَكَ مَا يَكُونُ ل…`
- answer: `وَإِذْ قَالَ ٱللَّهُ يَٰعِيسَى ٱبْنَ مَرْيَمَ ءَأَنتَ قُلْتَ لِلنَّاسِ ٱتَّخِذُونِي وَأُمِّيَ إِلَٰهَيْنِ مِن دُونِ ٱللَّهِ ۖ قَالَ سُبْحَٰنَكَ مَا يَكُونُ لِيٓ…`

### retrieve_quote-349b0b401f72 × opus-search — containment, refusal
- contains_reference=0 matches_requested_p=0.63 token_f1=0.2192 · outcome=refused refusal_p=0.16
- expected: `תנו רבנן או אינו מביא אלא כיוצא בשלמים מה שלמים מיוחדים נאכלין לשני ימים ולילה אחד אף כל נאכל לשני ימים ולילה אחד`
- answer: `I couldn't find the exact William Davidson Edition text of Zevachim 44a:5, so I can't give you that line word for word. The search results show that segment 44a…`

### retrieve_quote-4c6f201c7192 × opus-search — refusal
- contains_reference=0 matches_requested_p=0.09 token_f1=0.0455 · outcome=refused refusal_p=0.45
- expected: `אביי אמר אפילו נטמא אחד מהן נמי שניהם מצטרפין מאי טעמא כולהו בני ביקתא דהדדי נינהו`
- answer: `I couldn't get the exact text of Menachot 24b:10. My searches didn't bring up Sefaria's segment-by-segment William Davidson text, so I can't tell where line 10 …`

### retrieve_quote-528c5b83569e × haiku — containment
- contains_reference=0 matches_requested_p=0.94 token_f1=0.9333 · outcome=incorrect refusal_p=0.01
- expected: `وَأَنْ أَتْلُوَا۟ ٱلْقُرْءَانَ ۖ فَمَنِ ٱهْتَدَىٰ فَإِنَّمَا يَهْتَدِى لِنَفْسِهِۦ ۖ وَمَن ضَلَّ فَقُلْ إِنَّمَآ أَنَا۠ مِنَ ٱلْمُنذِرِينَ`
- answer: `وَأَنْ أَتْلُوَا۟ ٱلْقُرْءَانَ ۖ فَمَنِ ٱهْتَدَىٰ فَإِنَّمَا يَهْتَدِي لِنَفْسِهِ ۖ وَمَن ضَلَّ فَقُلْ إِنَّمَآ أَنَا۠ مِنَ ٱلْمُنذِرِينَ`

### retrieve_quote-528c5b83569e × haiku-search — containment
- contains_reference=0 matches_requested_p=0.86 token_f1=0.9333 · outcome=incorrect refusal_p=0.01
- expected: `وَأَنْ أَتْلُوَا۟ ٱلْقُرْءَانَ ۖ فَمَنِ ٱهْتَدَىٰ فَإِنَّمَا يَهْتَدِى لِنَفْسِهِۦ ۖ وَمَن ضَلَّ فَقُلْ إِنَّمَآ أَنَا۠ مِنَ ٱلْمُنذِرِينَ`
- answer: `وَأَنۡ أَتۡلُوَاْ ٱلۡقُرۡءَانَۖ فَمَنِ ٱهۡتَدَىٰ فَإِنَّمَا يَهۡتَدِي لِنَفۡسِهِۦۖ وَمَن ضَلَّ فَقُلۡ إِنَّمَآ أَنَا۠ مِنَ ٱلۡمُنذِرِينَ`

### retrieve_quote-571bf774a203 × haiku — containment
- contains_reference=0 matches_requested_p=0.86 token_f1=0.9348 · outcome=incorrect refusal_p=0.01
- expected: `هُوَ ٱلَّذِىٓ أَنزَلَ عَلَيْكَ ٱلْكِتَـٰبَ مِنْهُ ءَايَـٰتٌ مُّحْكَمَـٰتٌ هُنَّ أُمُّ ٱلْكِتَـٰبِ وَأُخَرُ مُتَشَـٰبِهَـٰتٌ ۖ فَأَمَّا ٱلَّذِينَ فِى قُلُوبِهِمْ…`
- answer: `هُوَ ٱلَّذِيٓ أَنزَلَ عَلَيۡكَ ٱلۡكِتَٰبَ مِنۡهُ ءَايَٰتٞ مُّحۡكَمَٰتٌ هُنَّ أُمُّ ٱلۡكِتَٰبِ وَأُخَرُ مُتَشَٰبِهَٰتٞۖ فَأَمَّا ٱلَّذِينَ فِي قُلُوبِهِمۡ زَيۡغٞ…`

### retrieve_quote-60993d0becf0 × haiku — containment
- contains_reference=0 matches_requested_p=0.74 token_f1=0.8333 · outcome=incorrect refusal_p=0.01
- expected: `وَقَالَ لِلَّذِى ظَنَّ أَنَّهُۥ نَاجٍ مِّنْهُمَا ٱذْكُرْنِى عِندَ رَبِّكَ فَأَنسَىٰهُ ٱلشَّيْطَـٰنُ ذِكْرَ رَبِّهِۦ فَلَبِثَ فِى ٱلسِّجْنِ بِضْعَ سِنِينَ`
- answer: `وَقَالَ لِلَّذِي ظَنَّ أَنَّهُۥ نَاجٖ مِّنْهُمَا ٱذْكُرْنِي عِندَ رَبِّكَ فَأَنسَىٰهُ ٱلشَّيْطَٰنُ ذِكْرَ رَبِّهِۦ فَلَبِثَ فِي ٱلسِّجْنِ بِضْعَ سِنِينَ`

### retrieve_quote-60993d0becf0 × haiku-search — containment
- contains_reference=0 matches_requested_p=0.77 token_f1=0.8333 · outcome=incorrect refusal_p=0.01
- expected: `وَقَالَ لِلَّذِى ظَنَّ أَنَّهُۥ نَاجٍ مِّنْهُمَا ٱذْكُرْنِى عِندَ رَبِّكَ فَأَنسَىٰهُ ٱلشَّيْطَـٰنُ ذِكْرَ رَبِّهِۦ فَلَبِثَ فِى ٱلسِّجْنِ بِضْعَ سِنِينَ`
- answer: `وَقَالَ لِلَّذِي ظَنَّ أَنَّهُۥ نَاجٖ مِّنۡهُمَا ٱذۡكُرۡنِي عِندَ رَبِّكَ فَأَنسَىٰهُ ٱلشَّيۡطَٰنُ ذِكۡرَ رَبِّهِۦ فَلَبِثَ فِي ٱلسِّجۡنِ بِضۡعَ سِنِينَ`

### retrieve_quote-66d7a26e7e93 × haiku-search — containment
- contains_reference=0 matches_requested_p=0.84 token_f1=0.3607 · outcome=incorrect refusal_p=0.01
- expected: `وَقَالَ مُوسَىٰٓ إِنِّى عُذْتُ بِرَبِّى وَرَبِّكُم مِّن كُلِّ مُتَكَبِّرٍ لَّا يُؤْمِنُ بِيَوْمِ ٱلْحِسَابِ`
- answer: `وَقَالَ مُوسَىٰٓ إِنِّي عُذۡتُ بِرَبِّي وَرَبِّكُم مِّن كُلِّ مُتَكَبِّرٖ لَّا يُؤۡمِنُ بِيَوۡمِ ٱلۡحِسَابِ (I couldn't open the QUL page for 40:27 directly. Th…`

### retrieve_quote-66d7a26e7e93 × haiku — containment
- contains_reference=0 matches_requested_p=0.84 token_f1=0.8462 · outcome=incorrect refusal_p=0.01
- expected: `وَقَالَ مُوسَىٰٓ إِنِّى عُذْتُ بِرَبِّى وَرَبِّكُم مِّن كُلِّ مُتَكَبِّرٍ لَّا يُؤْمِنُ بِيَوْمِ ٱلْحِسَابِ`
- answer: `وَقَالَ مُوسَىٰٓ إِنِّي عُذۡتُ بِرَبِّي وَرَبِّكُم مِّن كُلِّ مُتَكَبِّرٖ لَّا يُؤۡمِنُ بِيَوۡمِ ٱلۡحِسَابِ`

### retrieve_quote-91c4ddd54da1 × haiku — containment
- contains_reference=0 matches_requested_p=0.92 token_f1=0.8824 · outcome=incorrect refusal_p=0.01
- expected: `قَالُوا۟ ٱدْعُ لَنَا رَبَّكَ يُبَيِّن لَّنَا مَا هِىَ إِنَّ ٱلْبَقَرَ تَشَـٰبَهَ عَلَيْنَا وَإِنَّآ إِن شَآءَ ٱللَّهُ لَمُهْتَدُونَ`
- answer: `قَالُوا ادْعُ لَنَا رَبَّكَ يُبَيِّن لَّنَا مَا هِيَ ۚ إِنَّ الْبَقَرَ تَشَابَهَ عَلَيْنَا ۚ وَإِنَّا إِن شَاءَ اللَّهُ لَمُهْتَدُونَ`

### retrieve_quote-a8df3e43d35d × haiku — containment
- contains_reference=0 matches_requested_p=0.91 token_f1=0.963 · outcome=incorrect refusal_p=0.01
- expected: `ءَامَنَ ٱلرَّسُولُ بِمَآ أُنزِلَ إِلَيْهِ مِن رَّبِّهِۦ وَٱلْمُؤْمِنُونَ ۚ كُلٌّ ءَامَنَ بِٱللَّهِ وَمَلَـٰٓئِكَتِهِۦ وَكُتُبِهِۦ وَرُسُلِهِۦ لَا نُفَرِّقُ بَي…`
- answer: `آمَنَ ٱلرَّسُولُ بِمَآ أُنزِلَ إِلَيْهِ مِن رَّبِّهِۦ وَٱلْمُؤْمِنُونَ ۚ كُلٌّ ءَامَنَ بِٱللَّهِ وَمَلَٰٓئِكَتِهِۦ وَكُتُبِهِۦ وَرُسُلِهِۦ لَا نُفَرِّقُ بَيْنَ …`

### retrieve_quote-b1a04c81d33f × opus-search — refusal
- contains_reference=0 matches_requested_p=0.08 token_f1=0.0903 · outcome=refused refusal_p=0.46
- expected: `אתמר נמי אמר רב אחא בר עויה אמר רב אסי אמר רבי יוחנן הניח חלב של שור הנסקל על גבי מכתו פטור לפי שכל איסורין שבתורה אין לוקין עליהם אלא דרך הנאתן`
- answer: `I couldn't find the exact text of Pesachim 24b:7 in the William Davidson Aramaic edition. The search results only showed Sefaria's English preview, so I can't g…`

### retrieve_quote-b70583402f8f × haiku-search — containment
- contains_reference=0 matches_requested_p=0.8 token_f1=0.6923 · outcome=incorrect refusal_p=0.01
- expected: `قَالَ هِىَ عَصَاىَ أَتَوَكَّؤُا۟ عَلَيْهَا وَأَهُشُّ بِهَا عَلَىٰ غَنَمِى وَلِىَ فِيهَا مَـَٔارِبُ أُخْرَىٰ`
- answer: `قَالَ هِيَ عَصَايَ أَتَوَكَّؤُا۟ عَلَيۡهَا وَأَهُشُّ بِهَا عَلَىٰ غَنَمِي وَلِيَ فِيهَا مَـَٔارِبُ أُخۡرَىٰ`

### retrieve_quote-b70583402f8f × haiku — containment
- contains_reference=0 matches_requested_p=0.9 token_f1=0.7692 · outcome=incorrect refusal_p=0.01
- expected: `قَالَ هِىَ عَصَاىَ أَتَوَكَّؤُا۟ عَلَيْهَا وَأَهُشُّ بِهَا عَلَىٰ غَنَمِى وَلِىَ فِيهَا مَـَٔارِبُ أُخْرَىٰ`
- answer: `قَالَ هِيَ عَصَاىَ أَتَوَكَّؤُا۟ عَلَيْهَا وَأَهُشُّ بِهَا عَلَىٰ غَنَمِي وَلِيَ فِيهَا مَـَٔارِبُ أُخْرَىٰ`

### retrieve_quote-b33e7e040058 × opus-search — refusal
- contains_reference=0 matches_requested_p=0.28 token_f1=0.2458 · outcome=refused refusal_p=0.11
- expected: `ומה חשחן ובני תורין ודכרין ואמרין לעלון לאלה שמיא חנטין מלח חמר ומשח כמאמר כהניא די בירושלם להוא מתיהב להם יום ביום די לא שלו אמר לו רבי יצחק רבי מטונך די להון …`
- answer: `I couldn't confirm the full line word for word. Two sources show how it starts: Hadran's page for Rosh Hashanah 4 opens with ״וּמָה חַשְׁחָן וּבְנֵי תוֹרִין וְד…`

### retrieve_quote-c211a13b8670 × haiku — containment
- contains_reference=0 matches_requested_p=0.89 token_f1=0.9231 · outcome=incorrect refusal_p=0.01
- expected: `وَٱتْلُ عَلَيْهِمْ نَبَأَ ٱلَّذِىٓ ءَاتَيْنَـٰهُ ءَايَـٰتِنَا فَٱنسَلَخَ مِنْهَا فَأَتْبَعَهُ ٱلشَّيْطَـٰنُ فَكَانَ مِنَ ٱلْغَاوِينَ`
- answer: `وَٱتْلُ عَلَيْهِمْ نَبَإَ ٱلَّذِيٓ ءَاتَيْنَٰهُ ءَايَٰتِنَا فَٱنسَلَخَ مِنْهَا فَأَتْبَعَهُ ٱلشَّيْطَٰنُ فَكَانَ مِنَ ٱلْغَاوِينَ`

### retrieve_quote-d0239d95ae29 × opus-search — containment, refusal
- contains_reference=0 matches_requested_p=0.93 token_f1=0.2295 · outcome=refused refusal_p=0.09
- expected: `למדנו עשרה לחמץ עשרה למצה מנין תלמוד לומר על חלות לחם חמץ כנגד חמץ הבא מצה`
- answer: `I couldn't find the William Davidson Edition text of Menachot 78a:2, so I can't give you the exact line. Sefaria's version has vowel marks and punctuation, and …`

### retrieve_quote-d4c3bda0b400 × opus-search — refusal
- contains_reference=0 matches_requested_p=0.27 token_f1=0.2255 · outcome=refused refusal_p=0.04
- expected: `תא שמע המשמשת וראתה נדה צריכה טבילה ורבי יהודה פוטר והא משמשת וראתה נדה כבעל קרי שראה זיבה דמיא וקא פטר רבי יהודה שמע מינה תני רבי חייא בהדיא בעל קרי שראה זיבה …`
- answer: `I couldn't confirm the exact Sefaria text, and I'm not sure which passage is segment 9. What follows is my best reconstruction of the standard Vilna wording, wh…`

### retrieve_quote-de9d77a6c963 × opus-search — refusal
- contains_reference=0 matches_requested_p=0.04 token_f1=0.0385 · outcome=refused refusal_p=0.45
- expected: `וכי תימא ליתי בקל וחומר מטוען טענת גנב דיו לבא מן הדין להיות כנדון מה להלן בשבועה אף כאן בשבועה`
- answer: `I couldn't find the text of Bava Kamma 63b:19 in the William Davidson Edition, so I can't give you that line exactly. The closest I got was a different line fro…`

### retrieve_quote-e2d74279aaf0 × haiku — containment
- contains_reference=0 matches_requested_p=0.93 token_f1=0.96 · outcome=incorrect refusal_p=0.01
- expected: `يَسْتَفْتُونَكَ قُلِ ٱللَّهُ يُفْتِيكُمْ فِى ٱلْكَلَـٰلَةِ ۚ إِنِ ٱمْرُؤٌا۟ هَلَكَ لَيْسَ لَهُۥ وَلَدٌ وَلَهُۥٓ أُخْتٌ فَلَهَا نِصْفُ مَا تَرَكَ ۚ وَهُوَ يَرِثُ…`
- answer: `يَسْتَفْتُونَكَ قُلِ ٱللَّهُ يُفْتِيكُمْ فِي ٱلْكَلَٰلَةِ ۚ إِنِ ٱمْرُؤٌا۟ هَلَكَ لَيْسَ لَهُۥ وَلَدٌ وَلَهُۥٓ أُخْتٌ فَلَهَا نِصْفُ مَا تَرَكَ ۚ وَهُوَ يَرِثُه…`

### retrieve_quote-e2d74279aaf0 × haiku-search — containment, refusal
- contains_reference=0 matches_requested_p=0.87 token_f1=0.6806 · outcome=refused refusal_p=0.03
- expected: `يَسْتَفْتُونَكَ قُلِ ٱللَّهُ يُفْتِيكُمْ فِى ٱلْكَلَـٰلَةِ ۚ إِنِ ٱمْرُؤٌا۟ هَلَكَ لَيْسَ لَهُۥ وَلَدٌ وَلَهُۥٓ أُخْتٌ فَلَهَا نِصْفُ مَا تَرَكَ ۚ وَهُوَ يَرِثُ…`
- answer: `I couldn't retrieve the full QUL text to verify against. The only Uthmani-style source I found was truncated. From memory, the Uthmani text of 4:176 is: يَسْتَف…`

### retrieve_quote-ed21c10a072e × haiku-search — containment
- contains_reference=0 matches_requested_p=0.91 token_f1=0.4478 · outcome=incorrect refusal_p=0.01
- expected: `۞ إِنَّ ٱللَّهَ فَالِقُ ٱلْحَبِّ وَٱلنَّوَىٰ ۖ يُخْرِجُ ٱلْحَىَّ مِنَ ٱلْمَيِّتِ وَمُخْرِجُ ٱلْمَيِّتِ مِنَ ٱلْحَىِّ ۚ ذَٰلِكُمُ ٱللَّهُ ۖ فَأَنَّىٰ تُؤْفَكُونَ`
- answer: `إِنَّ ٱللَّهَ فَالِقُ ٱلۡحَبِّ وَٱلنَّوَىٰۖ يُخۡرِجُ ٱلۡحَيَّ مِنَ ٱلۡمَيِّتِ وَمُخۡرِجُ ٱلۡمَيِّتِ مِنَ ٱلۡحَيِّۚ ذَٰلِكُمُ ٱللَّهُۖ فَأَنَّىٰ تُؤۡفَكُونَ (I c…`

### retrieve_quote-eaf381cf82d3 × opus-search — refusal
- contains_reference=0 matches_requested_p=0.33 token_f1=0.1294 · outcome=refused refusal_p=0.49
- expected: `ואמאי נימא אכלתיה מי לא תנן מדורות הגוים טמאים וכמה ישהה במדור ויהא המדור צריך בדיקה ארבעים יום`
- answer: `I couldn't confirm the exact text of Pesachim 9a:3 in the William Davidson Edition (Aramaic). The search results didn't show Sefaria's segment-level text, so I …`

### retrieve_quote-f4e378e5065d × haiku-search — containment
- contains_reference=0 matches_requested_p=0.93 token_f1=0.9167 · outcome=incorrect refusal_p=0.01
- expected: `فِى قُلُوبِهِم مَّرَضٌ فَزَادَهُمُ ٱللَّهُ مَرَضًا ۖ وَلَهُمْ عَذَابٌ أَلِيمٌۢ بِمَا كَانُوا۟ يَكْذِبُونَ`
- answer: `فِي قُلُوبِهِم مَّرَضٌ فَزَادَهُمُ ٱللَّهُ مَرَضًاۖ وَلَهُمْ عَذَابٌ أَلِيمُۢ بِمَا كَانُوا۟ يَكْذِبُونَ`

### retrieve_quote-f4e378e5065d × haiku — containment
- contains_reference=0 matches_requested_p=0.88 token_f1=0.9167 · outcome=incorrect refusal_p=0.01
- expected: `فِى قُلُوبِهِم مَّرَضٌ فَزَادَهُمُ ٱللَّهُ مَرَضًا ۖ وَلَهُمْ عَذَابٌ أَلِيمٌۢ بِمَا كَانُوا۟ يَكْذِبُونَ`
- answer: `فِي قُلُوبِهِم مَّرَضٞ فَزَادَهُمُ ٱللَّهُ مَرَضٗاۖ وَلَهُمۡ عَذَابٌ أَلِيمُۢ بِمَا كَانُواْ يَكۡذِبُونَ`

### retrieve_quote-f0ffc67a458e × opus-search — refusal
- contains_reference=0 matches_requested_p=0.04 token_f1=0.0123 · outcome=refused refusal_p=0.36
- expected: `מתני׳ כיוצא בו רוצח שגלה לעיר מקלטו ורצו אנשי העיר לכבדו יאמר להם רוצח אני אמרו לו אף על פי כן יקבל מהן שנאמר וזה דבר הרוצח`
- answer: `I couldn't confirm the exact William Davidson Edition text for Makkot 12b:10. I found no copy of Sefaria's vocalized Aramaic for that segment. The best lead I h…`

### retrieve_quote-fb0ce4da6218 × haiku — containment
- contains_reference=0 matches_requested_p=0.74 token_f1=0.9286 · outcome=incorrect refusal_p=0.01
- expected: `وَقَالُوا۟ ٱتَّخَذَ ٱللَّهُ وَلَدًا ۗ سُبْحَـٰنَهُۥ ۖ بَل لَّهُۥ مَا فِى ٱلسَّمَـٰوَٰتِ وَٱلْأَرْضِ ۖ كُلٌّ لَّهُۥ قَـٰنِتُونَ`
- answer: `وَقَالُوا۟ ٱتَّخَذَ ٱللَّهُ وَلَدًا ۗ سُبْحَٰنَهُۥ ۖ بَل لَّهُۥ مَا فِي ٱلسَّمَٰوَٰتِ وَٱلْأَرْضِ ۖ كُلٌّ لَّهُۥ قَٰنِتُونَ`

### retrieve_quote-fb0ce4da6218 × haiku-search — containment
- contains_reference=0 matches_requested_p=0.8 token_f1=0.4643 · outcome=incorrect refusal_p=0.01
- expected: `وَقَالُوا۟ ٱتَّخَذَ ٱللَّهُ وَلَدًا ۗ سُبْحَـٰنَهُۥ ۖ بَل لَّهُۥ مَا فِى ٱلسَّمَـٰوَٰتِ وَٱلْأَرْضِ ۖ كُلٌّ لَّهُۥ قَـٰنِتُونَ`
- answer: `وَقَالُوا۟ ٱتَّخَذَ ٱللَّهُ وَلَدࣰاۘ سُبۡحَٰنَهُۥۚ بَل لَّهُۥ مَا فِي ٱلسَّمَٰوَٰتِ وَٱلۡأَرۡضِۖ كُلّٞ لَّهُۥ قَٰنِتُونَ *Note: I couldn't retrieve the QUL file…`

### retrieve_quote-fd566a54bc82 × haiku — containment
- contains_reference=0 matches_requested_p=0.87 token_f1=0.95 · outcome=incorrect refusal_p=0.01
- expected: `وَأَلَّفَ بَيْنَ قُلُوبِهِمْ ۚ لَوْ أَنفَقْتَ مَا فِى ٱلْأَرْضِ جَمِيعًا مَّآ أَلَّفْتَ بَيْنَ قُلُوبِهِمْ وَلَـٰكِنَّ ٱللَّهَ أَلَّفَ بَيْنَهُمْ ۚ إِنَّهُۥ عَ…`
- answer: `وَأَلَّفَ بَيْنَ قُلُوبِهِمْ ۚ لَوْ أَنفَقْتَ مَا فِي ٱلْأَرْضِ جَمِيعًا مَّآ أَلَّفْتَ بَيْنَ قُلُوبِهِمْ وَلَٰكِنَّ ٱللَّهَ أَلَّفَ بَيْنَهُمْ ۚ إِنَّهُۥ عَزِ…`

### retrieve_quote-fd566a54bc82 × haiku-search — containment
- contains_reference=0 matches_requested_p=0.82 token_f1=0.95 · outcome=incorrect refusal_p=0.01
- expected: `وَأَلَّفَ بَيْنَ قُلُوبِهِمْ ۚ لَوْ أَنفَقْتَ مَا فِى ٱلْأَرْضِ جَمِيعًا مَّآ أَلَّفْتَ بَيْنَ قُلُوبِهِمْ وَلَـٰكِنَّ ٱللَّهَ أَلَّفَ بَيْنَهُمْ ۚ إِنَّهُۥ عَ…`
- answer: `وَأَلَّفَ بَيۡنَ قُلُوبِهِمۡۚ لَوۡ أَنفَقۡتَ مَا فِي ٱلۡأَرۡضِ جَمِيعٗا مَّآ أَلَّفۡتَ بَيۡنَ قُلُوبِهِمۡ وَلَٰكِنَّ ٱللَّهَ أَلَّفَ بَيۡنَهُمۡۚ إِنَّهُۥ عَزِيز…`

### retrieve_quote-fe52da70f661 × opus-search — refusal
- contains_reference=0 matches_requested_p=0.45 token_f1=0.0904 · outcome=refused refusal_p=0.47
- expected: `גבי תרומה כתיב איש כי יאכל קדש בשגגה ויסף חמשיתו עליו ותנן האוכל תרומה בשוגג משלם קרן וחומש אחד האוכל ואחד השותה ואחד הסך אחד תרומה טהורה ואחד תרומה טמאה משלם ח…`
- answer: `I couldn't find the exact vocalized William Davidson text for Bava Metzia 54b:3. My searches didn't bring up that specific line, so I can't give you its exact w…`

