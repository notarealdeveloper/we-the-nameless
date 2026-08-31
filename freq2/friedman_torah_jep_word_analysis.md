# Bottom-up lexical source analysis of the Friedman Torah translation

## Executive result

This analysis uses **all 4,302 word types** in the supplied J/E/P count file and normalizes them against the very unequal corpus sizes:

| Source    |      Tokens | Corpus share |
| --------- | ----------: | -----------: |
| J         |      24,404 |      21.239% |
| E         |      24,158 |      21.025% |
| P         |      66,342 |      57.737% |
| **Total** | **114,904** |     **100%** |

The central result is not subtle: **P is lexically much easier to distinguish from J/E than J and E are from one another.** Pairwise Jensen–Shannon divergence of the complete word distributions is:

| Pair | JS divergence (bits) | JS distance |
|---|---:|---:|
| J vs E | 0.1095 | 0.3309 |
| E vs P | 0.2039 | 0.4515 |
| J vs P | 0.2294 | 0.4790 |

So on this English translation, **J and E are the nearest lexical pair; P is the outlier**, especially relative to J.

The whole word identity carries about **0.243 bits/token of mutual information about source**. Before seeing a word, source entropy is 1.405 bits; after learning only the word identity it falls to 1.162 bits. A trivial “always guess P” classifier is 57.7% accurate; an in-sample word-identity oracle rises to 63.8%. The latter is deliberately descriptive rather than a held-out classifier—it overfits rare words—but shows that source affiliation is visibly written into the vocabulary.

### In plain English

**J:** interpersonal, familial, embodied narrative. Its strongest ordinary-language contrasts include father, she, her, brother, servant, city, woman, down, ground, pregnant, and a great deal of story motion and conversation (went, came, said). Relative to E specifically, the family/women/household signal gets even clearer.

**E:** God, people, Egypt, Pharaoh, Moses, dream, hand, elders, serve, plus a more deictic/dialogic set (here, now, this, you'll, would, go, set). Proper names such as Balaam and Balak are spectacular classifiers, but those are obviously topic/location-of-story evidence rather than prose style.

**P:** a qualitatively different register. Ritual/legal/technical vocabulary dominates (offering, priest, holy, impure, congregation, atonement, tabernacle, oil, pure, blood), alongside genealogy/administration/counting (tribe, family, families, counts, hundred, thousand). Even the high-frequency grammatical texture differs: shall, of, the, its, their, any, for, and by are strongly P-heavy. The combination strongly suggests **prescriptive + classificatory + nominal + enumerative prose**, not merely different subject matter.

That last point is the most interesting bottom-up result in the English: **P is distinguishable not only by what it talks about, but by the machinery of the sentences used to talk about it.**

---

## Method: “surprise bits”

Raw counts cannot be compared directly because P contains 2.72× as many tokens as J and 2.75× as many as E.

For a word with counts c_J, c_E, c_P, let n be the word's total count. The null expectation is simply the corpus source prior

q = (N_J/N, N_E/N, N_P/N).

The observed source distribution for that word is

p = (c_J/n, c_E/n, c_P/n).

The main score is:

**global surprise bits = n × D_KL(p || q)**

or explicitly:

I(word) = Σ_s c_s log2[(c_s/n)/(N_s/N)].

This has an unusually useful interpretation: it is the **total number of bits by which the observed source allocation of the word surprises us**, compared with randomly drawing its occurrences in proportion to corpus size.

This automatically solves the one-off problem. An exclusive word occurring once is perfectly “pure” but supplies only a few bits. A word repeated dozens or hundreds of times in the wrong proportions can supply enormous evidence.

### Source-specific evidence

For each source I also compute a signed binary KL score, source-vs-rest:

source_info_bits = ± n × D_KL(observed source share || corpus source share).

Positive means enriched; negative means depleted. characteristic_source is whichever source has the largest positive source-information score.

### Cryptanalytic weight of evidence

For each source I also report a Jeffreys-corrected **log2 odds ratio** (WoE bits) comparing occurrence in that source against occurrence in the other two sources. This acts like a cryptanalytic/naive-Bayes “how many bits should this token shift my odds?” statistic.

- **WoE** = discriminatory strength per occurrence.
- **source info bits** = amount of source-specific evidence accumulated across occurrences.
- **global surprise bits** = total three-way discrepancy.

Use all three together. Rare exclusive words often have impressive WoE but little accumulated evidence.

### Significance reference

G² = 2 ln(2) × global surprise bits, with a χ²(2) reference distribution. I compute nominal p-values and Benjamini–Hochberg q-values across all 4,302 word types.

**Important caveat:** token independence is false in continuous texts. Words cluster by story, law, genealogy, and passage. Therefore these p/q values are anti-conservative and should not be treated as formal authorship probabilities. The information scores are the primary ranking measures. A truly inferential version should permute or bootstrap at verse/pericope/block level.

---

## Strongest discrepancies in the entire corpus

Hebrew cells give the leading vocalized surface-form correspondence(s) learned from the source-aligned Torah text. They are translation-specific statistical alignments, not necessarily lexicon headwords; / marks strong alternatives.

| word           |                  Hebrew                  |    J |    E |    P | characteristic | global surprise bits |         q |
| -------------- | :--------------------------------------: | ---: | ---: | ---: | :------------: | -------------------: | --------: |
| shall        |                   —                    |   56 |  199 | 1736 |       P        |               655.59 | 1.91e-194 |
| said         |               וַיֹּאמֶר                |  380 |  329 |  115 |       J        |               493.90 | 4.50e-146 |
| of           |                   —                    |  611 |  669 | 3336 |       P        |               304.71 |  2.69e-89 |
| offering     |     קרְבָּנוֹ / קרְבַּן / לַיהֹוָה     |    3 |   19 |  412 |       P        |               237.73 |  2.94e-69 |
| my           |                  ־ִי                   |  224 |  190 |  105 |       J        |               222.32 |  1.02e-64 |
| the          |                  הַ־                   | 1324 | 1335 | 5388 |       P        |               207.71 |  2.13e-60 |
| me           |              לִי / אֵלַי               |  198 |  188 |  109 |       J        |               189.65 |  5.00e-55 |
| priest       |                הַכֹּהֵן                |    1 |    4 |  244 |       P        |               165.65 |  6.52e-48 |
| and          |                  וְ־                   | 2612 | 2311 | 5074 |       J        |               153.61 |  2.48e-44 |
| people       |                 הָעָם                  |   97 |  174 |   87 |       E        |               135.83 |  5.06e-39 |
| its          |               ־וֹ / ־ָהּ               |   35 |   46 |  457 |       P        |               135.11 |  7.65e-39 |
| holy         |           קֹדֶשׁ / הַקֹּדֶשׁ           |    1 |    2 |  191 |       P        |               133.00 |  3.05e-38 |
| impure       |       יִטְמָא / טָמֵא / וְטָמֵא        |    0 |    0 |  167 |       P        |               132.34 |  4.47e-38 |
| was          |                וַיְהִי                 |  297 |  190 |  278 |       J        |               118.45 |  5.92e-34 |
| father       |             אָבִיו / אָבִי             |  107 |   31 |   29 |       J        |               114.62 |  7.95e-33 |
| children     |                 בְּנֵי                 |   28 |   65 |  427 |       P        |               112.79 |  2.66e-32 |
| here         |           וְהִנֵּה / הִנֵּה            |  100 |  114 |   60 |       E        |               106.44 |  2.06e-30 |
| us           |            לָנוּ / אִתָּנוּ            |   74 |   64 |   18 |       J        |               105.70 |  3.27e-30 |
| to           |                  אֶל                   |  878 |  865 | 1563 |       J        |               105.38 |  3.87e-30 |
| i'll         |                  אֶ־                   |   87 |   75 |   31 |       J        |               103.70 |  1.18e-29 |
| pharaoh      |                פַּרְעֹה                |   24 |   92 |   23 |       E        |               103.57 |  1.24e-29 |
| went         |               וַיֵּלֶךְ                |   99 |   73 |   38 |       J        |               103.23 |  1.50e-29 |
| balaam       |                בִּלְעָם                |    0 |   45 |    1 |       E        |                95.09 |  4.09e-27 |
| god          |                אֱלֹהִים                |   54 |  183 |  150 |       E        |                95.03 |  4.10e-27 |
| joseph       |                 יוֹסֵף                 |   52 |   70 |   17 |       E        |                92.62 |  2.09e-26 |
| you'll       |                  תִּ־                  |   56 |   72 |   20 |       E        |                91.90 |  3.33e-26 |
| their        |               ־ָם / ־ֶן                |   94 |   56 |  512 |       P        |                87.78 |  5.59e-25 |
| forward      | וְהִקְרִיב / וַיַּקְרֵב / וַיִּקְרְבוּ |    0 |    0 |  108 |       P        |                85.58 |  2.47e-24 |
| egypt        |               מִצְרַיִם                |   63 |  123 |   71 |       E        |                83.50 |  1.01e-23 |
| now          |           וְעַתָּה / עַתָּה            |   31 |   43 |    2 |       E        |                81.69 |  3.45e-23 |
| make         |         וְעָשִׂיתָ / תַּעֲשֶׂה         |   27 |   29 |  289 |       P        |                77.92 |  4.42e-22 |
| him          |          אֵלָיו / לוֹ / אֹתוֹ          |  263 |  190 |  310 |       J        |                72.97 |  1.33e-20 |
| congregation |            הָעֵדָה / עֲדַת             |    0 |    0 |   92 |       P        |                72.90 |  1.35e-20 |
| lord         |                אֲדֹנִי                 |   50 |   15 |    5 |       J        |                72.83 |  1.39e-20 |
| servant      |      עַבְדְּךָ / עֶבֶד / הָעֶבֶד       |   41 |    8 |    1 |       J        |                71.90 |  2.50e-20 |
| we           |              וַיֹּאמְרוּ               |   69 |   33 |   21 |       J        |                71.38 |  3.50e-20 |
| she          |               וַתֹּאמֶר                |  112 |   33 |   71 |       J        |                71.32 |  3.56e-20 |
| up           |     וַיַּעַל / מִבֶּן / וָמַעְלָה      |   95 |  138 |  112 |       E        |                70.61 |  5.68e-20 |
| tribe        |           לְמַטֵּה / מַטֵּה            |    0 |    0 |   88 |       P        |                69.73 |  9.96e-20 |
| atonement    |          וְכִפֶּר / לְכַפֵּר           |    0 |    1 |   93 |       P        |                67.96 |  3.34e-19 |

A few examples show why normalization matters:

- shall is the single strongest lexical discrepancy in the corpus: J=56, E=199, P=1,736.
- said runs in the opposite register: J=380, E=329, P=115. It is fundamentally a **J/E narrative vs P** discriminator; its J-over-E difference is much smaller.
- offering is J=3, E=19, P=412.
- father is J=107, E=31, P=29.
- God is J=54, E=183, P=150; after normalization E's rate is far higher than either J or P.
- people is J=97, E=174, P=87; again E is much denser despite P's much larger corpus.

The top 10 clean tokens account for 10.3% of all non-artifact lexical source information; the top 50 account for 23.2%. So source signal is concentrated, but not confined to a tiny keyword list.

---

## What defines J?

### Headline J-characteristic words

| word | Hebrew | J | E | P | rate/10k in source | log2 enrich. | source-info bits | global surprise bits | WoE bits | q |
| ---------- | :---: | ---: | ---: | ---: | -----------------: | -----------: | ---------------: | -------------------: | -------: | --------: |
| said     | וַיֹּאמֶר |  380 |  329 |  115 |             155.71 |         1.12 |           181.91 |               493.90 |     1.68 | 4.50e-146 |
| father   | אָבִיו / אָבִי |  107 |   31 |   29 |              43.85 |         1.59 |           102.51 |               114.62 |     2.73 |  7.95e-33 |
| and      | וְ־ | 2612 | 2311 | 5074 |            1070.32 |         0.30 |            97.92 |               153.61 |     0.43 |  2.48e-44 |
| my       | ־ִי |  224 |  190 |  105 |              91.79 |         1.02 |            90.33 |               222.32 |     1.50 |  1.02e-64 |
| was      | וַיְהִי |  297 |  190 |  278 |             121.70 |         0.87 |            87.87 |               118.45 |     1.25 |  5.92e-34 |
| she      | וַתֹּאמֶר |  112 |   33 |   71 |              45.89 |         1.28 |            70.38 |                71.32 |     2.00 |  3.56e-20 |
| me       | לִי / אֵלַי |  198 |  188 |  109 |              81.13 |         0.91 |            64.26 |               189.65 |     1.31 |  5.00e-55 |
| servant  | עַבְדְּךָ / עֶבֶד / הָעֶבֶד |   41 |    8 |    1 |              16.80 |         1.92 |            60.74 |                71.90 |     4.02 |  2.50e-20 |
| lord     | אֲדֹנִי |   50 |   15 |    5 |              20.49 |         1.73 |            58.23 |                72.83 |     3.19 |  1.39e-20 |
| her      | לָהּ / אֵלֶיהָ / אֹתָהּ |  140 |   57 |  136 |              57.37 |         0.98 |            52.52 |                53.08 |     1.43 |  6.54e-15 |
| we       | וַיֹּאמְרוּ |   69 |   33 |   21 |              28.27 |         1.39 |            51.15 |                71.38 |     2.24 |  3.50e-20 |
| him      | אֵלָיו / לוֹ / אֹתוֹ |  263 |  190 |  310 |             107.77 |         0.70 |            51.08 |                72.97 |     0.97 |  1.33e-20 |
| went     | וַיֵּלֶךְ |   99 |   73 |   38 |              40.57 |         1.15 |            50.02 |               103.23 |     1.73 |  1.50e-29 |
| down     | וַיֵּרֶד |   52 |   18 |   11 |              21.31 |         1.58 |            50.00 |                61.45 |     2.72 |  2.52e-17 |
| brother  | אֶחָיו / אָחִיךָ |   63 |   16 |   31 |              25.82 |         1.42 |            48.69 |                49.58 |     2.31 |  6.54e-14 |
| camels   | הַגְּמַלִּים |   22 |    2 |    0 |               9.01 |         2.05 |            39.93 |                43.74 |     5.06 |  3.11e-12 |
| i'll     | אֶ־ |   87 |   75 |   31 |              35.65 |         1.08 |            39.33 |               103.70 |     1.61 |  1.18e-29 |
| well     | גַּם |   45 |   22 |    7 |              18.44 |         1.50 |            39.09 |                61.02 |     2.52 |  3.34e-17 |
| to       | אֶל |  878 |  865 | 1563 |             359.78 |         0.32 |            38.17 |               105.38 |     0.44 |  3.87e-30 |
| us       | לָנוּ / אִתָּנוּ |   74 |   64 |   18 |              30.32 |         1.16 |            37.95 |               105.70 |     1.75 |  3.27e-30 |
| won't    | לֹא |   53 |   31 |   13 |              21.72 |         1.35 |            37.23 |                63.59 |     2.16 |  6.20e-18 |
| name     | שָׁם / שְׁמוֹ |   68 |   33 |   41 |              27.86 |         1.17 |            35.67 |                43.54 |     1.77 |  3.47e-12 |
| rebekah  | רִבְקָה |   22 |    0 |    4 |               9.01 |         1.95 |            34.45 |                36.24 |     4.21 |  4.31e-10 |
| ground   | הָאֲדָמָה / אַרְצָה |   34 |   10 |    8 |              13.93 |         1.60 |            33.81 |                38.61 |     2.79 |  8.71e-11 |
| came     | וַיָּבֹא / וַיָּבֹאוּ |   89 |   63 |   59 |              36.47 |         0.99 |            33.70 |                58.26 |     1.44 |  2.01e-16 |
| cain     | קַיִן |   15 |    0 |    0 |               6.15 |         2.15 |            33.53 |                33.53 |     6.85 |  2.59e-09 |
| brothers | אֶחָיו |   50 |   24 |   20 |              20.49 |         1.32 |            33.19 |                44.15 |     2.08 |  2.43e-12 |
| jacob    | יַעֲקֹב |   68 |   51 |   29 |              27.86 |         1.11 |            32.25 |                66.84 |     1.66 |  6.77e-19 |
| pregnant | וַתַּהַר / הָרָה |   18 |    2 |    0 |               7.38 |         2.02 |            31.54 |                35.35 |     4.78 |  7.71e-10 |
| city     | הָעִיר / עִיר |   33 |    5 |   15 |              13.52 |         1.53 |            29.98 |                30.00 |     2.60 |  2.69e-08 |
| youngest | הַקָּטֹן |   13 |    0 |    0 |               5.33 |         2.13 |            29.06 |                29.06 |     6.65 |  4.87e-08 |
| garden   | הַגָּן |   13 |    0 |    0 |               5.33 |         2.13 |            29.06 |                29.06 |     6.65 |  4.87e-08 |
| esau     | עֵשָׂו |   35 |    9 |   17 |              14.34 |         1.42 |            27.15 |                27.72 |     2.31 |  1.17e-07 |
| sodom    | סְדֹם |   12 |    0 |    0 |               4.92 |         2.12 |            26.82 |                26.82 |     6.54 |  2.02e-07 |
| birth    | וַתֵּלֶד / יָלְדָה |   44 |   17 |   26 |              18.03 |         1.24 |            26.17 |                28.58 |     1.93 |  6.71e-08 |
| his      | אֶת |  393 |  296 |  717 |             161.04 |         0.40 |            25.53 |                27.87 |     0.53 |  1.07e-07 |
| abram    | אַבְרָם |   27 |    0 |   16 |              11.06 |         1.54 |            24.92 |                32.08 |     2.63 |  6.66e-09 |
| there    | שָׁם |   91 |   67 |   83 |              37.29 |         0.83 |            24.60 |                40.68 |     1.18 |  2.28e-11 |
| you're   | אֹתָהּ / אֹתָם |   26 |   11 |    4 |              10.65 |         1.55 |            24.44 |                34.64 |     2.67 |  1.22e-09 |
| he       | אֶת |  450 |  412 |  798 |             184.40 |         0.35 |            23.22 |                46.15 |     0.47 |  6.40e-13 |
| gave     | וַיִּתֵּן / נָתַן |   45 |   16 |   34 |              18.44 |         1.15 |            23.00 |                23.50 |     1.74 |  1.76e-06 |
| ruled    | וַיִּמְלֹךְ / תַּחְתָּיו |   10 |    0 |    0 |               4.10 |         2.10 |            22.35 |                22.35 |     6.28 |  3.64e-06 |
| joseph's | יוֹסֵף |   18 |    6 |    1 |               7.38 |         1.72 |            21.26 |                29.00 |     3.19 |  5.05e-08 |
| lord's   | אֲדֹנִי / אֲדֹנָיו |   17 |    6 |    0 |               6.97 |         1.75 |            21.02 |                32.45 |     3.32 |  5.23e-09 |
| told     | וַיַּגֵּד / וַיְסַפֵּר |   25 |   16 |    1 |              10.24 |         1.46 |            20.84 |                46.29 |     2.44 |  5.88e-13 |
| called   | וַיִּקְרָא |   53 |   44 |   27 |              21.72 |         1.01 |            20.81 |                48.71 |     1.47 |  1.18e-13 |
| again    | עוֹד |   15 |    0 |    4 |               6.15 |         1.83 |            20.80 |                22.59 |     3.68 |  3.11e-06 |
| sent     | וַיִּשְׁלַח |   31 |   20 |    7 |              12.70 |         1.32 |            20.79 |                39.74 |     2.09 |  4.17e-11 |
| your     | לְךָ / וַיֹּאמֶר / אֶת |  270 |  258 |  418 |             110.64 |         0.43 |            20.22 |                50.66 |     0.57 |  3.27e-14 |
| i've     | נָתַתִּי / הִנֵּה / וַיֹּאמֶר |   45 |   30 |   26 |              18.44 |         1.06 |            19.74 |                32.76 |     1.58 |  4.30e-09 |

### J as language, not merely topic

The most persuasive J signals are not the proper names. They are the **human-scale narrative words**. J is strongly enriched for personal and kinship vocabulary (father, she, her, brother, daughter, woman), first-person interaction (my, me, we, us), and ordinary physical/narrative motion (went, came, down). ground, earth, city, and concrete household/pastoral nouns reinforce the same texture.

said is enormously informative globally, but it should be interpreted carefully: it chiefly says “this is narrative rather than P.” J and E both use it heavily. The J-vs-E table below is better for isolating what separates those two.

### Selected ordinary-language J markers

| word | Hebrew | J | E | P | source rate/10k | source info bits | global bits |
| --- | :---: | ---: | ---: | ---: | ---: | ---: | ---: |
| said | וַיֹּאמֶר | 380 | 329 | 115 | 155.71 | 181.91 | 493.90 |
| father | אָבִיו / אָבִי | 107 | 31 | 29 | 43.85 | 102.51 | 114.62 |
| she | וַתֹּאמֶר | 112 | 33 | 71 | 45.89 | 70.38 | 71.32 |
| her | לָהּ / אֵלֶיהָ / אֹתָהּ | 140 | 57 | 136 | 57.37 | 52.52 | 53.08 |
| brother | אֶחָיו / אָחִיךָ | 63 | 16 | 31 | 25.82 | 48.69 | 49.58 |
| servant | עַבְדְּךָ / עֶבֶד / הָעֶבֶד | 41 | 8 | 1 | 16.80 | 60.74 | 71.90 |
| city | הָעִיר / עִיר | 33 | 5 | 15 | 13.52 | 29.98 | 30.00 |
| was | וַיְהִי | 297 | 190 | 278 | 121.70 | 87.87 | 118.45 |
| earth | הָאָרֶץ | 54 | 16 | 65 | 22.13 | 17.52 | 19.06 |
| camels | הַגְּמַלִּים | 22 | 2 | 0 | 9.01 | 39.93 | 43.74 |
| daughter | בַּת | 30 | 6 | 41 | 12.29 | 8.98 | 12.88 |
| woman | הָאִשָּׁה / אִשָּׁה | 32 | 7 | 51 | 13.11 | 7.00 | 12.37 |
| down | וַיֵּרֶד | 52 | 18 | 11 | 21.31 | 50.00 | 61.45 |
| ground | הָאֲדָמָה / אַרְצָה | 34 | 10 | 8 | 13.93 | 33.81 | 38.61 |
| pregnant | וַתַּהַר / הָרָה | 18 | 2 | 0 | 7.38 | 31.54 | 35.35 |
| name | שָׁם / שְׁמוֹ | 68 | 33 | 41 | 27.86 | 35.67 | 43.54 |
| went | וַיֵּלֶךְ | 99 | 73 | 38 | 40.57 | 50.02 | 103.23 |
| came | וַיָּבֹא / וַיָּבֹאוּ | 89 | 63 | 59 | 36.47 | 33.70 | 58.26 |
| we | וַיֹּאמְרוּ | 69 | 33 | 21 | 28.27 | 51.15 | 71.38 |
| won't | לֹא | 53 | 31 | 13 | 21.72 | 37.23 | 63.59 |

---

## What defines E?

### Headline E-characteristic words

| word | Hebrew | J | E | P | rate/10k in source | log2 enrich. | source-info bits | global surprise bits | WoE bits | q |
| --------------- | :---: | --: | --: | --: | -----------------: | -----------: | ---------------: | -------------------: | -------: | -------: |
| people        | הָעָם |  97 | 174 |  87 |              72.03 |         1.21 |            96.33 |               135.83 |     1.84 | 5.06e-39 |
| god           | אֱלֹהִים |  54 | 183 | 150 |              75.75 |         1.17 |            95.01 |                95.03 |     1.76 | 4.10e-27 |
| pharaoh       | פַּרְעֹה |  24 |  92 |  23 |              38.08 |         1.65 |            94.69 |               103.57 |     2.88 | 1.24e-29 |
| balaam        | בִּלְעָם |   0 |  45 |   1 |              18.63 |         2.19 |            94.63 |                95.09 |     6.83 | 4.09e-27 |
| balak         | בָּלָק |   1 |  32 |   0 |              13.25 |         2.16 |            65.87 |                67.77 |     6.35 | 3.73e-19 |
| egypt         | מִצְרַיִם |  63 | 123 |  71 |              50.91 |         1.18 |            65.70 |                83.50 |     1.79 | 1.01e-23 |
| up            | וַיַּעַל / מִבֶּן / וָמַעְלָה |  95 | 138 | 112 |              57.12 |         0.93 |            45.99 |                70.61 |     1.33 | 5.68e-20 |
| here          | וְהִנֵּה / הִנֵּה | 100 | 114 |  60 |              47.19 |         0.98 |            42.56 |               106.44 |     1.43 | 2.06e-30 |
| joseph        | יוֹסֵף |  52 |  70 |  17 |              28.98 |         1.25 |            41.99 |                92.62 |     1.93 | 2.09e-26 |
| you'll        | תִּ־ |  56 |  72 |  20 |              29.80 |         1.21 |            39.95 |                91.90 |     1.83 | 3.33e-26 |
| hail          | הַבָּרָד / בָּרָד |   0 |  17 |   0 |               7.04 |         2.17 |            38.25 |                38.25 |     7.04 | 1.11e-10 |
| ass           | חֲמוֹר / הָאָתוֹן |   5 |  25 |   1 |              10.35 |         1.90 |            36.32 |                42.34 |     3.88 | 7.65e-12 |
| i             | אֲנִי / אָנֹכִי | 139 | 203 | 272 |              84.03 |         0.65 |            34.52 |                41.42 |     0.90 | 1.41e-11 |
| dream         | חֲלוֹם / בַּחֲלוֹם |   5 |  23 |   0 |               9.52 |         1.92 |            34.49 |                43.97 |     4.01 | 2.69e-12 |
| now           | וְעַתָּה / עַתָּה |  31 |  43 |   2 |              17.80 |         1.42 |            32.93 |                81.69 |     2.29 | 3.45e-23 |
| this          | הַזֶּה / זֶה | 118 | 145 | 145 |              60.02 |         0.76 |            32.76 |                60.87 |     1.06 | 3.65e-17 |
| nile          | הַיְאֹר |   4 |  21 |   0 |               8.69 |         1.95 |            32.75 |                40.33 |     4.17 | 2.88e-11 |
| because       | כִּי | 124 | 148 | 150 |              61.26 |         0.74 |            31.84 |                62.35 |     1.03 | 1.41e-17 |
| meaning       | פָּתַר / חֲלֹמוֹ / פִּתְרֹנוֹ |   0 |  13 |   0 |               5.38 |         2.15 |            29.25 |                29.25 |     6.66 | 4.35e-08 |
| heavy         | כָּבֵד |   9 |  23 |   0 |               9.52 |         1.74 |            27.38 |                44.44 |     3.22 | 2.01e-12 |
| hand          | יָדוֹ / בְּיַד |  55 |  95 | 100 |              39.32 |         0.85 |            27.01 |                30.97 |     1.21 | 1.42e-08 |
| owner         | בְּעָלָיו / לִבְעָלָיו |   0 |  12 |   0 |               4.97 |         2.14 |            27.00 |                27.00 |     6.55 | 1.82e-07 |
| cows          | פָּרוֹת / וּשְׁבַע |   0 |  12 |   0 |               4.97 |         2.14 |            27.00 |                27.00 |     6.55 | 1.82e-07 |
| ears          | בְּאזְנֵי |   2 |  20 |   4 |               8.28 |         1.83 |            26.78 |                26.86 |     3.57 | 1.98e-07 |
| serve         | וְיַעַבְדֻנִי׃ / שָׁלַח / עַמִּי |   3 |  19 |   2 |               7.86 |         1.86 |            26.73 |                28.46 |     3.74 | 7.22e-08 |
| out           | וַיֵּצֵא / יֹצֵא |  69 | 119 | 154 |              49.26 |         0.73 |            24.85 |                26.15 |     1.01 | 3.07e-07 |
| elders        | זִקְנֵי / מִזִּקְנֵי |   3 |  18 |   2 |               7.45 |         1.84 |            24.83 |                26.56 |     3.66 | 2.38e-07 |
| pit           | הַבּוֹר |   0 |  11 |   0 |               4.55 |         2.13 |            24.75 |                24.75 |     6.43 | 7.83e-07 |
| drive         | מִפָּנֶיךָ / אֲגָרְשֶׁנּוּ |   0 |  11 |   0 |               4.55 |         2.13 |            24.75 |                24.75 |     6.43 | 7.83e-07 |
| go            | אֶל / לְךָ | 109 | 134 | 157 |              55.47 |         0.67 |            24.08 |                41.84 |     0.93 | 1.06e-11 |
| set           | וַיָּשֶׂם / וְשַׂמְתָּ |  14 |  56 |  61 |              23.18 |         1.02 |            22.53 |                24.54 |     1.49 | 8.80e-07 |
| yesterday     | שִׁלְשֹׁם / כִּתְמוֹל |   0 |  10 |   0 |               4.14 |         2.12 |            22.50 |                22.50 |     6.30 | 3.30e-06 |
| moses         | מֹשֶׁה |  48 | 178 | 351 |              73.68 |         0.55 |            21.99 |                60.00 |     0.75 | 6.44e-17 |
| would         | מִמֶּנָּה / כּל / לַעֲבֹדָה |  26 |  49 |  36 |              20.28 |         1.07 |            21.46 |                26.16 |     1.57 | 3.07e-07 |
| servants      | עֲבָדָיו / עֲבָדֶיךָ / עַבְדֵי |  30 |  38 |  10 |              15.73 |         1.20 |            21.15 |                50.06 |     1.84 | 4.75e-14 |
| father-in-law | חֹתֵן / חֹתְנוֹ |   3 |  14 |   0 |               5.80 |         1.90 |            21.09 |                26.77 |     3.96 | 2.08e-07 |
| bad           | רַע / רָעָה |  19 |  33 |  12 |              13.66 |         1.28 |            20.85 |                32.42 |     2.00 | 5.31e-09 |
| jethro        | יִתְרוֹ |   0 |   9 |   0 |               3.73 |         2.11 |            20.25 |                20.25 |     6.16 | 1.34e-05 |
| boys          | נְעָרָיו |   1 |  11 |   0 |               4.55 |         2.02 |            20.12 |                22.02 |     4.85 | 4.37e-06 |
| angel         | מַלְאַךְ |   8 |  18 |   0 |               7.45 |         1.68 |            20.07 |                35.23 |     3.03 | 8.36e-10 |
| let           | נָא / וַיֹּאמֶר / אֶל |  70 |  74 |  54 |              30.63 |         0.83 |            19.92 |                54.45 |     1.17 | 2.66e-15 |
| abraham       | אַבְרָהָם |  31 |  51 |  39 |              21.11 |         1.00 |            19.74 |                26.76 |     1.46 | 2.09e-07 |
| they'll       | וְאָמְרוּ / לָהֶם / מֵעִם |  12 |  24 |   5 |               9.93 |         1.46 |            19.65 |                29.79 |     2.40 | 3.09e-08 |
| ox            | שׁוֹר / הַשּׁוֹר |   2 |  22 |  12 |               9.11 |         1.51 |            19.56 |                20.49 |     2.54 | 1.17e-05 |
| gods          | אֱלֹהֵי |   8 |  19 |   2 |               7.86 |         1.60 |            19.20 |                28.04 |     2.80 | 9.60e-08 |
| pharaoh's     | פַּרְעֹה |  15 |  27 |   8 |              11.18 |         1.34 |            18.81 |                29.41 |     2.14 | 3.98e-08 |
| eyes          | בְּעֵינֵי |  48 |  53 |  30 |              21.94 |         0.94 |            18.27 |                47.79 |     1.36 | 2.18e-13 |
| pile          | הַגַּל / הַמַּצֵּבָה |   0 |   8 |   0 |               3.31 |         2.09 |            18.00 |                18.00 |     6.00 | 5.61e-05 |
| pray          | הַעְתִּירוּ / וַאֲשַׁלְּחָה / לַיהֹוָה |   0 |   8 |   0 |               3.31 |         2.09 |            18.00 |                18.00 |     6.00 | 5.61e-05 |
| pay           | יְשַׁלֵּם |   8 |  24 |  11 |               9.93 |         1.39 |            17.89 |                19.36 |     2.24 | 2.38e-05 |

### E as language, not merely topic

E has two layers of signal.

First is **story inventory**: Balaam, Balak, Pharaoh, Egypt, Joseph, Moses. These are powerful source classifiers in this partition, but weak evidence for a general authorial dialect because a different story necessarily names different people and places.

Second is a more reusable lexical texture: God, people, dream, hand, elders, serve, here, now, this, because, go, set, would, plus strong first/second-person dialogue. dream is especially clean: it appears 5× in J, 23× in E, and 0× in P.

The divine-name signal is also impossible to miss bottom-up. But it is **not independent confirmation** of the source partition: divine naming was historically part of the evidence used to construct source divisions, and the English translation can sharpen that distinction.

### Selected ordinary-language E markers

| word | Hebrew | J | E | P | source rate/10k | source info bits | global bits |
| --- | :---: | ---: | ---: | ---: | ---: | ---: | ---: |
| god | אֱלֹהִים | 54 | 183 | 150 | 75.75 | 95.01 | 95.03 |
| people | הָעָם | 97 | 174 | 87 | 72.03 | 96.33 | 135.83 |
| up | וַיַּעַל / מִבֶּן / וָמַעְלָה | 95 | 138 | 112 | 57.12 | 45.99 | 70.61 |
| here | וְהִנֵּה / הִנֵּה | 100 | 114 | 60 | 47.19 | 42.56 | 106.44 |
| you'll | תִּ־ | 56 | 72 | 20 | 29.80 | 39.95 | 91.90 |
| i | אֲנִי / אָנֹכִי | 139 | 203 | 272 | 84.03 | 34.52 | 41.42 |
| dream | חֲלוֹם / בַּחֲלוֹם | 5 | 23 | 0 | 9.52 | 34.49 | 43.97 |
| now | וְעַתָּה / עַתָּה | 31 | 43 | 2 | 17.80 | 32.93 | 81.69 |
| this | הַזֶּה / זֶה | 118 | 145 | 145 | 60.02 | 32.76 | 60.87 |
| because | כִּי | 124 | 148 | 150 | 61.26 | 31.84 | 62.35 |
| heavy | כָּבֵד | 9 | 23 | 0 | 9.52 | 27.38 | 44.44 |
| hand | יָדוֹ / בְּיַד | 55 | 95 | 100 | 39.32 | 27.01 | 30.97 |
| serve | וְיַעַבְדֻנִי׃ / שָׁלַח / עַמִּי | 3 | 19 | 2 | 7.86 | 26.73 | 28.46 |
| elders | זִקְנֵי / מִזִּקְנֵי | 3 | 18 | 2 | 7.45 | 24.83 | 26.56 |
| go | אֶל / לְךָ | 109 | 134 | 157 | 55.47 | 24.08 | 41.84 |
| set | וַיָּשֶׂם / וְשַׂמְתָּ | 14 | 56 | 61 | 23.18 | 22.53 | 24.54 |
| would | מִמֶּנָּה / כּל / לַעֲבֹדָה | 26 | 49 | 36 | 20.28 | 21.46 | 26.16 |
| angel | מַלְאַךְ | 8 | 18 | 0 | 7.45 | 20.07 | 35.23 |
| if | וְאִם / אִם | 51 | 94 | 155 | 38.91 | 12.54 | 12.89 |

---

## What defines P?

### Headline P-characteristic words

| word | Hebrew | J | E | P | rate/10k in source | log2 enrich. | source-info bits | global surprise bits | WoE bits | q |
| --- | :---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| shall | — | 56 | 199 | 1736 | 261.67 | 0.59 | 593.20 | 655.59 | 2.35 | 1.91e-194 |
| of | — | 611 | 669 | 3336 | 502.85 | 0.32 | 302.36 | 304.71 | 0.97 | 2.69e-89 |
| offering | קרְבָּנוֹ / קרְבַּן / לַיהֹוָה | 3 | 19 | 412 | 62.10 | 0.71 | 228.25 | 237.73 | 3.75 | 2.94e-69 |
| the | הַ־ | 1324 | 1335 | 5388 | 812.16 | 0.21 | 207.55 | 207.71 | 0.61 | 2.13e-60 |
| priest | הַכֹּהֵן | 1 | 4 | 244 | 36.78 | 0.76 | 164.24 | 165.65 | 5.03 | 6.52e-48 |
| its | ־וֹ / ־ָהּ | 35 | 46 | 457 | 68.89 | 0.55 | 133.94 | 135.11 | 2.05 | 7.65e-39 |
| holy | קֹדֶשׁ / הַקֹּדֶשׁ | 1 | 2 | 191 | 28.79 | 0.76 | 132.74 | 133.00 | 5.33 | 3.05e-38 |
| impure | יִטְמָא / טָמֵא / וְטָמֵא | 0 | 0 | 167 | 25.17 | 0.78 | 132.34 | 132.34 | 7.94 | 4.47e-38 |
| children | בְּנֵי | 28 | 65 | 427 | 64.36 | 0.51 | 101.60 | 112.79 | 1.75 | 2.66e-32 |
| forward | וְהִקְרִיב / וַיַּקְרֵב / וַיִּקְרְבוּ | 0 | 0 | 108 | 16.28 | 0.78 | 85.58 | 85.58 | 7.31 | 2.47e-24 |
| their | ־ָם / ־ֶן | 94 | 56 | 512 | 77.18 | 0.42 | 81.03 | 87.78 | 1.32 | 5.59e-25 |
| make | וְעָשִׂיתָ / תַּעֲשֶׂה | 27 | 29 | 289 | 43.56 | 0.53 | 77.85 | 77.92 | 1.91 | 4.42e-22 |
| congregation | הָעֵדָה / עֲדַת | 0 | 0 | 92 | 13.87 | 0.78 | 72.90 | 72.90 | 7.08 | 1.35e-20 |
| tribe | לְמַטֵּה / מַטֵּה | 0 | 0 | 88 | 13.26 | 0.78 | 69.73 | 69.73 | 7.02 | 9.96e-20 |
| atonement | וְכִפֶּר / לְכַפֵּר | 0 | 1 | 93 | 14.02 | 0.76 | 66.95 | 67.96 | 5.51 | 3.34e-19 |
| tabernacle | הַמִּשְׁכָּן | 0 | 0 | 80 | 12.06 | 0.77 | 63.39 | 63.39 | 6.88 | 6.96e-18 |
| any | כּל / וְכל / מִכּל | 3 | 7 | 129 | 19.44 | 0.67 | 62.78 | 64.00 | 3.18 | 4.76e-18 |
| oil | שֶׁמֶן | 0 | 2 | 88 | 13.26 | 0.74 | 58.38 | 60.40 | 4.70 | 4.97e-17 |
| counts | פְּקֻדֵיהֶם / אֶלֶף / וּפְקֻדֵיהֶם | 0 | 0 | 71 | 10.70 | 0.77 | 56.26 | 56.26 | 6.71 | 7.90e-16 |
| meeting | מוֹעֵד / אֹהֶל | 0 | 6 | 103 | 15.53 | 0.70 | 55.56 | 61.61 | 3.55 | 2.31e-17 |
| pure | טָהוֹר | 4 | 0 | 93 | 14.02 | 0.72 | 54.62 | 58.59 | 3.93 | 1.63e-16 |
| hundred | מֵאוֹת | 6 | 7 | 127 | 19.14 | 0.64 | 54.36 | 54.42 | 2.79 | 2.66e-15 |
| for | אֶת / לוֹ / לָכֶם | 187 | 172 | 825 | 124.36 | 0.27 | 51.77 | 52.12 | 0.76 | 1.23e-14 |
| family | מִשְׁפַּחַת | 3 | 0 | 84 | 12.66 | 0.73 | 51.47 | 54.44 | 4.15 | 2.66e-15 |
| levites | הַלְוִיִּם | 0 | 0 | 64 | 9.65 | 0.77 | 50.72 | 50.72 | 6.56 | 3.19e-14 |
| thousand | אֶלֶף | 0 | 4 | 85 | 12.81 | 0.71 | 48.79 | 52.81 | 3.80 | 7.76e-15 |
| families | לְמִשְׁפְּחֹתָם / מִשְׁפַּחַת | 4 | 2 | 91 | 13.72 | 0.69 | 47.09 | 47.57 | 3.37 | 2.51e-13 |
| work | עֲבֹדַת / מְלָאכָה / לַעֲבֹד | 12 | 6 | 131 | 19.75 | 0.60 | 46.96 | 48.38 | 2.38 | 1.47e-13 |
| affliction | הַנֶּגַע / נֶגַע | 0 | 0 | 59 | 8.89 | 0.77 | 46.75 | 46.75 | 6.45 | 4.37e-13 |
| bases | וְאַדְנֵיהֶם / אֲדֹנִי | 0 | 0 | 55 | 8.29 | 0.77 | 43.58 | 43.58 | 6.35 | 3.40e-12 |
| by | עַל | 76 | 63 | 393 | 59.24 | 0.35 | 43.29 | 44.07 | 1.05 | 2.53e-12 |
| front | לִפְנֵי | 16 | 39 | 218 | 32.86 | 0.46 | 43.21 | 50.53 | 1.53 | 3.53e-14 |
| army | צָבָא׃ / לַצָּבָא | 1 | 2 | 72 | 10.85 | 0.71 | 42.61 | 42.86 | 3.92 | 5.49e-12 |
| aaron | אַהֲרֹן | 2 | 35 | 172 | 25.93 | 0.51 | 41.50 | 67.52 | 1.75 | 4.33e-19 |
| sin | לְחַטָּאת׃ / הַחַטָּאת / חַטָּאת | 5 | 17 | 131 | 19.75 | 0.56 | 40.25 | 45.33 | 2.10 | 1.11e-12 |
| altar | הַמִּזְבֵּחַ / מִזְבַּח | 7 | 20 | 144 | 21.71 | 0.54 | 40.06 | 44.86 | 1.95 | 1.51e-12 |
| sons | בְּנֵי / בָּנָיו | 36 | 21 | 214 | 32.26 | 0.45 | 39.29 | 42.06 | 1.45 | 9.17e-12 |
| five | וַחֲמֵשׁ / חֲמִשָּׁה / חָמֵשׁ | 7 | 2 | 88 | 13.26 | 0.64 | 37.68 | 39.77 | 2.77 | 4.13e-11 |
| a | אֶת / לַיהֹוָה / כִּי | 289 | 331 | 1203 | 181.33 | 0.19 | 37.55 | 39.92 | 0.51 | 3.75e-11 |
| it | אֹתוֹ / אֹתָהּ | 198 | 275 | 958 | 144.40 | 0.21 | 36.82 | 46.48 | 0.57 | 5.23e-13 |
| shekels | שֶׁקֶל | 0 | 1 | 54 | 8.14 | 0.74 | 36.82 | 37.83 | 4.73 | 1.47e-10 |
| wash | וְרָחַץ / יְכַבֵּס / וְכִבֶּס | 4 | 0 | 66 | 9.95 | 0.69 | 35.15 | 39.12 | 3.44 | 6.20e-11 |
| equipment | כֵּלָיו / כְּלִי | 0 | 0 | 44 | 6.63 | 0.76 | 34.87 | 34.87 | 6.03 | 1.05e-09 |
| eternal | עוֹלָם | 0 | 0 | 44 | 6.63 | 0.76 | 34.87 | 34.87 | 6.03 | 1.05e-09 |
| blood | הַדָּם / דַּם | 7 | 15 | 119 | 17.94 | 0.54 | 33.55 | 35.76 | 1.96 | 5.93e-10 |
| eleazar | אֶלְעָזָר | 0 | 0 | 41 | 6.18 | 0.76 | 32.49 | 32.49 | 5.93 | 5.13e-09 |
| one | אֶחָד | 81 | 66 | 376 | 56.68 | 0.31 | 32.45 | 33.44 | 0.91 | 2.73e-09 |
| an | לַיהֹוָה | 31 | 64 | 271 | 40.85 | 0.36 | 30.44 | 39.13 | 1.06 | 6.20e-11 |
| burn | וְהִקְטִיר | 1 | 2 | 53 | 7.99 | 0.69 | 28.85 | 29.10 | 3.49 | 4.79e-08 |
| commanded | צִוָּה | 12 | 11 | 111 | 16.73 | 0.51 | 27.90 | 27.93 | 1.80 | 1.03e-07 |
| cubits | אַמָּה / בָּאַמָּה | 1 | 1 | 47 | 7.08 | 0.70 | 27.67 | 27.67 | 3.80 | 1.20e-07 |
| fire | אֵשׁ / בָּאֵשׁ / אִשָּׁה | 9 | 10 | 100 | 15.07 | 0.53 | 27.46 | 27.51 | 1.92 | 1.33e-07 |
| four | וְאַרְבַּע / אַרְבַּע | 2 | 3 | 58 | 8.74 | 0.65 | 26.98 | 27.13 | 2.96 | 1.69e-07 |
| columns | וְאַדְנֵיהֶם / עַמֻּדֵיהֶם | 0 | 0 | 34 | 5.12 | 0.75 | 26.94 | 26.94 | 5.66 | 1.88e-07 |
| skin | בָּעוֹר / עוֹר | 1 | 1 | 45 | 6.78 | 0.70 | 26.21 | 26.21 | 3.74 | 3.01e-07 |
| peace-offering | הַשְּׁלָמִים | 0 | 1 | 40 | 6.03 | 0.72 | 26.16 | 27.16 | 4.31 | 1.66e-07 |
| donation | תְּרוּמַת / תְּרוּמָה / הַתְּרוּמָה | 0 | 0 | 33 | 4.97 | 0.75 | 26.15 | 26.15 | 5.62 | 3.07e-07 |
| frames | הַקְּרָשִׁים / קְרָשִׁים | 0 | 0 | 33 | 4.97 | 0.75 | 26.15 | 26.15 | 5.62 | 3.07e-07 |
| person | נֶפֶשׁ / הַנֶּפֶשׁ | 1 | 4 | 56 | 8.44 | 0.65 | 25.64 | 27.05 | 2.91 | 1.78e-07 |
| impurity | נִדָּה / טְמֵאָה / עָלָיו | 0 | 0 | 32 | 4.82 | 0.75 | 25.36 | 25.36 | 5.57 | 5.24e-07 |

### P as language, not merely topic

P is the clearest lexical system by far. Three mutually reinforcing layers appear.

1. **Cult / purity / ritual:** offering, priest, holy, impure, atonement, tabernacle, oil, pure, altar, sin, blood, wash.
2. **Classification / genealogy / administration:** congregation, tribe, family, families, Levites, counts, hundred, thousand, repeated numerals and measurements.
3. **Grammatical and structural texture:** shall, of, the, its, their, any, for, by, plus spatial/technical words such as front and forward.

The third layer matters most if the goal is authorship/style rather than subject matter. A priestly law will of course say priest; a genealogy will of course say family. But there is no topical necessity for **the enormous density of of, possessive its/their, determiners, numerals, and prescriptive shall**. Those features are compatible with long noun phrases, object specifications, classifications, and formulaic instructions—the syntactic feel readers traditionally notice in P.

### Selected ordinary/structural P markers

| word | Hebrew | J | E | P | source rate/10k | source info bits | global bits |
| --- | :---: | ---: | ---: | ---: | ---: | ---: | ---: |
| shall | — | 56 | 199 | 1736 | 261.67 | 593.20 | 655.59 |
| of | — | 611 | 669 | 3336 | 502.85 | 302.36 | 304.71 |
| the | הַ־ | 1324 | 1335 | 5388 | 812.16 | 207.55 | 207.71 |
| its | ־וֹ / ־ָהּ | 35 | 46 | 457 | 68.89 | 133.94 | 135.11 |
| their | ־ָם / ־ֶן | 94 | 56 | 512 | 77.18 | 81.03 | 87.78 |
| any | כּל / וְכל / מִכּל | 3 | 7 | 129 | 19.44 | 62.78 | 64.00 |
| for | אֶת / לוֹ / לָכֶם | 187 | 172 | 825 | 124.36 | 51.77 | 52.12 |
| by | עַל | 76 | 63 | 393 | 59.24 | 43.29 | 44.07 |
| make | וְעָשִׂיתָ / תַּעֲשֶׂה | 27 | 29 | 289 | 43.56 | 77.85 | 77.92 |
| children | בְּנֵי | 28 | 65 | 427 | 64.36 | 101.60 | 112.79 |
| offering | קרְבָּנוֹ / קרְבַּן / לַיהֹוָה | 3 | 19 | 412 | 62.10 | 228.25 | 237.73 |
| priest | הַכֹּהֵן | 1 | 4 | 244 | 36.78 | 164.24 | 165.65 |
| holy | קֹדֶשׁ / הַקֹּדֶשׁ | 1 | 2 | 191 | 28.79 | 132.74 | 133.00 |
| impure | יִטְמָא / טָמֵא / וְטָמֵא | 0 | 0 | 167 | 25.17 | 132.34 | 132.34 |
| congregation | הָעֵדָה / עֲדַת | 0 | 0 | 92 | 13.87 | 72.90 | 72.90 |
| atonement | וְכִפֶּר / לְכַפֵּר | 0 | 1 | 93 | 14.02 | 66.95 | 67.96 |
| tabernacle | הַמִּשְׁכָּן | 0 | 0 | 80 | 12.06 | 63.39 | 63.39 |
| oil | שֶׁמֶן | 0 | 2 | 88 | 13.26 | 58.38 | 60.40 |
| counts | פְּקֻדֵיהֶם / אֶלֶף / וּפְקֻדֵיהֶם | 0 | 0 | 71 | 10.70 | 56.26 | 56.26 |
| meeting | מוֹעֵד / אֹהֶל | 0 | 6 | 103 | 15.53 | 55.56 | 61.61 |
| pure | טָהוֹר | 4 | 0 | 93 | 14.02 | 54.62 | 58.59 |
| hundred | מֵאוֹת | 6 | 7 | 127 | 19.14 | 54.36 | 54.42 |
| family | מִשְׁפַּחַת | 3 | 0 | 84 | 12.66 | 51.47 | 54.44 |
| families | לְמִשְׁפְּחֹתָם / מִשְׁפַּחַת | 4 | 2 | 91 | 13.72 | 47.09 | 47.57 |
| thousand | אֶלֶף | 0 | 4 | 85 | 12.81 | 48.79 | 52.81 |
| blood | הַדָּם / דַּם | 7 | 15 | 119 | 17.94 | 33.55 | 35.76 |

---

## J versus E directly

Because J and E are almost exactly the same corpus size (24,404 vs 24,158 tokens), their direct contrast is particularly clean. The table below ignores P when calculating the signed J-vs-E information score. Positive values favor J; negative values favor E.

### Strongest J-over-E contrasts (minimum 10 J+E occurrences)

| word | Hebrew | J | E | P | J-vs-E signed info bits | J-vs-E WoE bits |
| --- | :---: | ---: | ---: | ---: | ---: | ---: |
| she | וַתֹּאמֶר | 112 | 33 | 71 | 32.23 | 1.74 |
| father | אָבִיו / אָבִי | 107 | 31 | 29 | 31.39 | 1.76 |
| abram | אַבְרָם | 27 | 0 | 16 | 26.80 | 5.77 |
| her | לָהּ / אֵלֶיהָ / אֹתָהּ | 140 | 57 | 136 | 25.43 | 1.28 |
| rebekah | רִבְקָה | 22 | 0 | 4 | 21.84 | 5.48 |
| brother | אֶחָיו / אָחִיךָ | 63 | 16 | 31 | 21.23 | 1.93 |
| judah | יְהוּדָה | 21 | 0 | 13 | 20.85 | 5.41 |
| lot | לוֹט | 20 | 0 | 17 | 19.85 | 5.34 |
| servant | עַבְדְּךָ / עֶבֶד / הָעֶבֶד | 41 | 8 | 1 | 17.30 | 2.27 |
| city | הָעִיר / עִיר | 33 | 5 | 15 | 16.45 | 2.59 |
| was | וַיְהִי | 297 | 190 | 278 | 16.32 | 0.63 |
| ark | הַתֵּבָה / הָאָרֹן | 16 | 0 | 41 | 15.88 | 5.03 |
| earth | הָאָרֶץ | 54 | 16 | 65 | 15.44 | 1.71 |
| cain | קַיִן | 15 | 0 | 0 | 14.89 | 4.94 |
| again | עוֹד | 15 | 0 | 4 | 14.89 | 4.94 |
| lord | אֲדֹנִי | 50 | 15 | 5 | 14.09 | 1.69 |
| camels | הַגְּמַלִּים | 22 | 2 | 0 | 13.92 | 3.16 |
| brother's | אָחִיךָ / אֶחָיו | 13 | 0 | 7 | 12.91 | 4.74 |
| garden | הַגָּן | 13 | 0 | 0 | 12.91 | 4.74 |
| youngest | הַקָּטֹן | 13 | 0 | 0 | 12.91 | 4.74 |
| daughter | בַּת | 30 | 6 | 41 | 12.42 | 2.22 |
| woman | הָאִשָּׁה / אִשָּׁה | 32 | 7 | 51 | 12.34 | 2.10 |
| down | וַיֵּרֶד | 52 | 18 | 11 | 12.18 | 1.49 |
| sodom | סְדֹם | 12 | 0 | 0 | 11.91 | 4.63 |
| esau | עֵשָׂו | 35 | 9 | 17 | 11.65 | 1.89 |
| and | וְ־ | 2612 | 2311 | 5074 | 11.18 | 0.18 |
| human | הָאָדָם / אָדָם | 32 | 8 | 33 | 10.95 | 1.92 |
| noah | נֹחַ | 11 | 0 | 16 | 10.92 | 4.51 |
| pregnant | וַתַּהַר / הָרָה | 18 | 2 | 0 | 10.50 | 2.87 |
| gave | וַיִּתֵּן / נָתַן | 45 | 16 | 34 | 10.15 | 1.45 |
| edom | אֱדוֹם | 10 | 0 | 8 | 9.93 | 4.38 |
| ruled | וַיִּמְלֹךְ / תַּחְתָּיו | 10 | 0 | 0 | 9.93 | 4.38 |
| ground | הָאֲדָמָה / אַרְצָה | 34 | 10 | 8 | 9.80 | 1.70 |
| son | בֶּן | 83 | 42 | 177 | 9.59 | 0.96 |
| his | אֶת | 393 | 296 | 717 | 9.19 | 0.40 |

### Strongest E-over-J contrasts (minimum 10 J+E occurrences)

| word | Hebrew | J | E | P | J-vs-E signed info bits | J-vs-E WoE bits |
| --- | :---: | ---: | ---: | ---: | ---: | ---: |
| shall | — | 56 | 199 | 1736 | -62.39 | -1.84 |
| moses | מֹשֶׁה | 48 | 178 | 351 | -58.35 | -1.90 |
| god | אֱלֹהִים | 54 | 183 | 150 | -54.45 | -1.77 |
| balaam | בִּלְעָם | 0 | 45 | 1 | -45.33 | -6.53 |
| will | כִּי / אֲשֶׁר / יִהְיֶה | 123 | 261 | 708 | -37.60 | -1.11 |
| pharaoh | פַּרְעֹה | 24 | 92 | 23 | -31.18 | -1.94 |
| balak | בָּלָק | 1 | 32 | 0 | -26.76 | -4.45 |
| aaron | אַהֲרֹן | 2 | 35 | 172 | -26.02 | -3.84 |
| set | וַיָּשֶׂם / וְשַׂמְתָּ | 14 | 56 | 61 | -19.77 | -1.98 |
| you | לָכֶם / לְךָ | 358 | 502 | 1138 | -18.54 | -0.51 |
| burnt | הָעֹלָה / לְעֹלָה׃ / עֹלָה | 0 | 18 | 92 | -18.13 | -5.23 |
| hail | הַבָּרָד / בָּרָד | 0 | 17 | 0 | -17.12 | -5.14 |
| people | הָעָם | 97 | 174 | 87 | -16.57 | -0.86 |
| seven | שֶׁבַע / שִׁבְעַת | 14 | 49 | 71 | -15.11 | -1.79 |
| egypt | מִצְרַיִם | 63 | 123 | 71 | -14.66 | -0.98 |
| ox | שׁוֹר / הַשּׁוֹר | 2 | 22 | 12 | -14.22 | -3.19 |
| meaning | פָּתַר / חֲלֹמוֹ / פִּתְרֹנוֹ | 0 | 13 | 0 | -13.10 | -4.77 |
| ears | בְּאזְנֵי | 2 | 20 | 4 | -12.46 | -3.05 |
| not | לֹא | 108 | 176 | 465 | -12.36 | -0.72 |
| swarm | עַמִּי / וּבְכל / הָעָרֶב׃ | 0 | 12 | 6 | -12.09 | -4.66 |
| cows | פָּרוֹת / וּשְׁבַע | 0 | 12 | 0 | -12.09 | -4.66 |
| owner | בְּעָלָיו / לִבְעָלָיו | 0 | 12 | 0 | -12.09 | -4.66 |
| children | בְּנֵי | 28 | 65 | 427 | -11.19 | -1.22 |
| drive | מִפָּנֶיךָ / אֲגָרְשֶׁנּוּ | 0 | 11 | 0 | -11.08 | -4.54 |
| pit | הַבּוֹר | 0 | 11 | 0 | -11.08 | -4.54 |
| chiefs | שָׂרֵי | 2 | 18 | 17 | -10.74 | -2.90 |
| ass | חֲמוֹר / הָאָתוֹן | 5 | 25 | 1 | -10.65 | -2.23 |
| out | וַיֵּצֵא / יֹצֵא | 69 | 119 | 154 | -10.08 | -0.80 |
| yesterday | שִׁלְשֹׁם / כִּתְמוֹל | 0 | 10 | 0 | -10.07 | -4.41 |
| wood | עֲצֵי | 0 | 10 | 38 | -10.07 | -4.41 |
| joshua | יְהוֹשֻׁעַ / וִיהוֹשֻׁעַ | 0 | 10 | 10 | -10.07 | -4.41 |
| if | וְאִם / אִם | 51 | 94 | 155 | -9.66 | -0.89 |
| it | אֹתוֹ / אֹתָהּ | 198 | 275 | 958 | -9.65 | -0.49 |
| serve | וְיַעַבְדֻנִי׃ / שָׁלַח / עַמִּי | 3 | 19 | 2 | -9.48 | -2.49 |
| offering | קרְבָּנוֹ / קרְבַּן / לַיהֹוָה | 3 | 19 | 412 | -9.48 | -2.49 |

This direct comparison sharpens the qualitative distinction:

- **J > E:** female/kinship/household and ancestral-story language (she, father, her, Rebekah, brother, Judah, Lot, daughter, woman), plus servant, city, earth, ground, camels, down.
- **E > J:** Moses, God, Pharaoh, Aaron, people, Egypt, along with will/shall, set, you, not, if, serve, elders, ox, and the dream/plague vocabulary.

Again, some of this is story distribution. The pronouns, auxiliaries, prepositions, deictics, and common verbs are more interesting for style.

---

## How much of this is “style” versus “what the source happens to narrate”?

This is the main interpretive limitation of a unigram study.

### Strong but topic-bound evidence

Names (Balaam, Sodom, Rebekah, etc.), cult objects, plague terms, genealogical labels, and specialized legal nouns may classify passages brilliantly without revealing a stable authorial dialect. They answer: **“What kinds of material are assigned to this source?”**

### More stylistically interesting evidence

High-frequency function words, pronouns, auxiliaries, discourse markers, and ordinary verbs are harder to explain away by subject matter:

- P: shall, of, the, its, their, any, for, by.
- J: unusually personal pronouns and kinship framing; was, went, came, down, there; much direct narrative.
- E: here, now, this, because, would, if, go, set, with strong dialogue and directive language.

These are exactly the kinds of features worth testing next in Hebrew with lemmas, particles, morphology, clause templates, and n-grams.

### Translation dependence

This is an analysis of **Friedman's English**, not directly of Hebrew authors. It can capture:
- real differences in the source texts that survive translation;
- Friedman's translation choices for recurring Hebrew words/constructions;
- genre/topic differences;
- extraction/tokenization artifacts.

Therefore this is best understood as a **bottom-up map of the lexical fingerprints present in Friedman's source-separated English text**, not a proof of source authorship.

---

## Corpus-level diagnostics

- Unique word types: **4,302**
- Types assigned by largest source-information score: **J 1,198; E 1,124; P 1,980**
- Nominal FDR<.05 types: **866** total (J 287; E 237; P 342)
- Suspected extraction fragments flagged: **44 types**, representing 1,606 tokens.
- Pairwise lexical divergence: **J/E closest; J/P farthest**.

The fragment flag is deliberately conservative and **does not delete anything**. Odd tokens such as isolated letters/fragments can receive huge scores simply because they occur only in one extraction stream. They remain in the full tables and machine-readable data, but headline rankings omit flagged candidates.

---

## Bottom-up source fingerprints: concise formulation

If forced to identify each source from nothing but Friedman's English vocabulary:

> **J sounds like people in families doing things to one another.**  
> Fathers, women, brothers, servants, births, cities, ground, movement, speech, embodied domestic narrative.

> **E sounds like people encountering God in northern/Exodus-style crisis narrative.**  
> God, people, Egypt/Pharaoh/Moses, dreams, hands, elders, commands, here/now/this, movement and dialogue.

> **P sounds like a specification, census, ritual manual, and legal taxonomy.**  
> Shall; of; its; offering; priest; holy/impure; congregation; atonement; tabernacle; oil; blood; families; tribes; counts; hundreds/thousands; measured spatial and object vocabulary.

The most robust structural conclusion is therefore **not merely “P likes priestly words.” It is that P occupies a distinct lexical register, while J and E are much more nearly neighboring narrative dialects in English.**

---

# Complete source-ranked lexicon

Every one of the 4,302 word types is listed below. The assigned source is descriptive, not categorical authorship. For rare words, especially n=1–2, the assignment is weak even when exclusivity is perfect.

### All words assigned to J (1,198 types)

The assignment is the source with the largest positive source-vs-rest information score. **Do not treat a one-off as strong evidence**: use source info bits, global bits, total count, and q-value together.

| word | Hebrew | J | E | P | n | source info bits | global bits | source WoE bits | q | FDR<.05 | artifact? |
| --- | :---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: | :---: |
| said | וַיֹּאמֶר | 380 | 329 | 115 | 824 | 181.911 | 493.903 | 1.682 | 4.50e-146 | yes |  |
| father | אָבִיו / אָבִי | 107 | 31 | 29 | 167 | 102.509 | 114.617 | 2.725 | 7.95e-33 | yes |  |
| and | וְ־ | 2612 | 2311 | 5074 | 9997 | 97.922 | 153.605 | 0.432 | 2.48e-44 | yes |  |
| my | ־ִי | 224 | 190 | 105 | 519 | 90.332 | 222.320 | 1.503 | 1.02e-64 | yes |  |
| was | וַיְהִי | 297 | 190 | 278 | 765 | 87.871 | 118.450 | 1.246 | 5.92e-34 | yes |  |
| she | וַתֹּאמֶר | 112 | 33 | 71 | 216 | 70.382 | 71.320 | 2.002 | 3.56e-20 | yes |  |
| me | לִי / אֵלַי | 198 | 188 | 109 | 495 | 64.255 | 189.647 | 1.314 | 5.00e-55 | yes |  |
| servant | עַבְדְּךָ / עֶבֶד / הָעֶבֶד | 41 | 8 | 1 | 50 | 60.741 | 71.903 | 4.020 | 2.50e-20 | yes |  |
| lord | אֲדֹנִי | 50 | 15 | 5 | 70 | 58.232 | 72.828 | 3.194 | 1.39e-20 | yes |  |
| her | לָהּ / אֵלֶיהָ / אֹתָהּ | 140 | 57 | 136 | 333 | 52.521 | 53.083 | 1.434 | 6.54e-15 | yes |  |
| we | וַיֹּאמְרוּ | 69 | 33 | 21 | 123 | 51.154 | 71.380 | 2.245 | 3.50e-20 | yes |  |
| him | אֵלָיו / לוֹ / אֹתוֹ | 263 | 190 | 310 | 763 | 51.079 | 72.966 | 0.973 | 1.33e-20 | yes |  |
| went | וַיֵּלֶךְ | 99 | 73 | 38 | 210 | 50.016 | 103.234 | 1.731 | 1.50e-29 | yes |  |
| down | וַיֵּרֶד | 52 | 18 | 11 | 81 | 49.998 | 61.454 | 2.725 | 2.52e-17 | yes |  |
| brother | אֶחָיו / אָחִיךָ | 63 | 16 | 31 | 110 | 48.693 | 49.582 | 2.313 | 6.54e-14 | yes |  |
| camels | הַגְּמַלִּים | 22 | 2 | 0 | 24 | 39.933 | 43.743 | 5.062 | 3.11e-12 | yes |  |
| i'll | אֶ־ | 87 | 75 | 31 | 193 | 39.328 | 103.704 | 1.611 | 1.18e-29 | yes |  |
| well | גַּם | 45 | 22 | 7 | 74 | 39.090 | 61.022 | 2.518 | 3.34e-17 | yes |  |
| to | אֶל | 878 | 865 | 1563 | 3306 | 38.173 | 105.384 | 0.437 | 3.87e-30 | yes |  |
| us | לָנוּ / אִתָּנוּ | 74 | 64 | 18 | 156 | 37.948 | 105.698 | 1.747 | 3.27e-30 | yes |  |
| won't | לֹא | 53 | 31 | 13 | 97 | 37.226 | 63.589 | 2.159 | 6.20e-18 | yes |  |
| name | שָׁם / שְׁמוֹ | 68 | 33 | 41 | 142 | 35.668 | 43.539 | 1.772 | 3.47e-12 | yes |  |
| rebekah | רִבְקָה | 22 | 0 | 4 | 26 | 34.449 | 36.241 | 4.214 | 4.31e-10 | yes |  |
| ground | הָאֲדָמָה / אַרְצָה | 34 | 10 | 8 | 52 | 33.808 | 38.606 | 2.792 | 8.71e-11 | yes |  |
| came | וַיָּבֹא / וַיָּבֹאוּ | 89 | 63 | 59 | 211 | 33.696 | 58.264 | 1.441 | 2.01e-16 | yes |  |
| cain | קַיִן | 15 | 0 | 0 | 15 | 33.529 | 33.529 | 6.846 | 2.59e-09 | yes |  |
| brothers | אֶחָיו | 50 | 24 | 20 | 94 | 33.194 | 44.146 | 2.076 | 2.43e-12 | yes |  |
| jacob | יַעֲקֹב | 68 | 51 | 29 | 148 | 32.254 | 66.843 | 1.661 | 6.77e-19 | yes |  |
| pregnant | וַתַּהַר / הָרָה | 18 | 2 | 0 | 20 | 31.543 | 35.354 | 4.779 | 7.71e-10 | yes |  |
| city | הָעִיר / עִיר | 33 | 5 | 15 | 53 | 29.975 | 29.997 | 2.601 | 2.69e-08 | yes |  |
| garden | הַגָּן | 13 | 0 | 0 | 13 | 29.058 | 29.058 | 6.646 | 4.87e-08 | yes |  |
| youngest | הַקָּטֹן | 13 | 0 | 0 | 13 | 29.058 | 29.058 | 6.646 | 4.87e-08 | yes |  |
| esau | עֵשָׂו | 35 | 9 | 17 | 61 | 27.150 | 27.720 | 2.314 | 1.17e-07 | yes |  |
| sodom | סְדֹם | 12 | 0 | 0 | 12 | 26.823 | 26.823 | 6.535 | 2.02e-07 | yes |  |
| birth | וַתֵּלֶד / יָלְדָה | 44 | 17 | 26 | 87 | 26.170 | 28.579 | 1.925 | 6.71e-08 | yes |  |
| his | אֶת | 393 | 296 | 717 | 1406 | 25.530 | 27.868 | 0.533 | 1.07e-07 | yes |  |
| abram | אַבְרָם | 27 | 0 | 16 | 43 | 24.915 | 32.083 | 2.629 | 6.66e-09 | yes |  |
| there | שָׁם | 91 | 67 | 83 | 241 | 24.598 | 40.678 | 1.176 | 2.28e-11 | yes |  |
| you're | אֹתָהּ / אֹתָם | 26 | 11 | 4 | 41 | 24.438 | 34.640 | 2.666 | 1.22e-09 | yes |  |
| he | אֶת | 450 | 412 | 798 | 1660 | 23.222 | 46.150 | 0.472 | 6.40e-13 | yes |  |
| gave | וַיִּתֵּן / נָתַן | 45 | 16 | 34 | 95 | 22.998 | 23.497 | 1.742 | 1.76e-06 | yes |  |
| ruled | וַיִּמְלֹךְ / תַּחְתָּיו | 10 | 0 | 0 | 10 | 22.352 | 22.352 | 6.284 | 3.64e-06 | yes |  |
| joseph's | יוֹסֵף | 18 | 6 | 1 | 25 | 21.259 | 28.998 | 3.194 | 5.05e-08 | yes |  |
| lord's | אֲדֹנִי / אֲדֹנָיו | 17 | 6 | 0 | 23 | 21.020 | 32.453 | 3.321 | 5.23e-09 | yes |  |
| told | וַיַּגֵּד / וַיְסַפֵּר | 25 | 16 | 1 | 42 | 20.842 | 46.290 | 2.435 | 5.88e-13 | yes |  |
| called | וַיִּקְרָא | 53 | 44 | 27 | 124 | 20.814 | 48.713 | 1.474 | 1.18e-13 | yes |  |
| again | עוֹד | 15 | 0 | 4 | 19 | 20.799 | 22.591 | 3.676 | 3.11e-06 | yes |  |
| sent | וַיִּשְׁלַח | 31 | 20 | 7 | 58 | 20.791 | 39.744 | 2.088 | 4.17e-11 | yes |  |
| your | לְךָ / וַיֹּאמֶר / אֶת | 270 | 258 | 418 | 946 | 20.222 | 50.659 | 0.574 | 3.27e-14 | yes |  |
| i've | נָתַתִּי / הִנֵּה / וַיֹּאמֶר | 45 | 30 | 26 | 101 | 19.740 | 32.757 | 1.580 | 4.30e-09 | yes |  |
| another | אַחַר | 16 | 4 | 2 | 22 | 19.233 | 22.241 | 3.236 | 3.88e-06 | yes |  |
| judah | יְהוּדָה | 21 | 0 | 13 | 34 | 18.788 | 24.612 | 2.563 | 8.47e-07 | yes |  |
| abel | הֶבֶל | 8 | 0 | 0 | 8 | 17.882 | 17.882 | 5.979 | 6.00e-05 | yes |  |
| bag | אַמְתַּחְתּוֹ׃ / אַמְתְּחֹת | 8 | 0 | 0 | 8 | 17.882 | 17.882 | 5.979 | 6.00e-05 | yes |  |
| older | הַגָּדֹל | 8 | 0 | 0 | 8 | 17.882 | 17.882 | 5.979 | 6.00e-05 | yes |  |
| younger | הַצְּעִירָה / הַבְּכִירָה / וַתֹּאמֶר | 10 | 1 | 0 | 11 | 17.862 | 19.768 | 4.699 | 1.85e-05 | yes |  |
| tree | הָעֵץ / עֵץ | 19 | 5 | 6 | 30 | 17.816 | 19.097 | 2.654 | 2.81e-05 | yes |  |
| wife | אִשְׁתּוֹ / אֵשֶׁת / אִשָּׁה | 49 | 21 | 48 | 118 | 17.750 | 18.096 | 1.403 | 5.31e-05 | yes |  |
| earth | הָאָרֶץ | 54 | 16 | 65 | 135 | 17.524 | 19.057 | 1.312 | 2.87e-05 | yes |  |
| canaanite | הַכְּנַעֲנִי | 16 | 6 | 2 | 24 | 16.480 | 22.319 | 2.849 | 3.70e-06 | yes |  |
| had | אֲשֶׁר / אֶת / כַּאֲשֶׁר | 118 | 88 | 164 | 370 | 16.372 | 22.314 | 0.802 | 3.70e-06 | yes |  |
| saw | וַיַּרְא | 44 | 40 | 21 | 105 | 16.356 | 45.321 | 1.426 | 1.11e-12 | yes |  |
| lived | וַיֵּשֶׁב | 21 | 4 | 12 | 37 | 15.940 | 15.957 | 2.274 | 2.01e-04 | yes |  |
| jar | כַּדָּהּ / וַתֵּרֶד / מִכַּדֵּךְ׃ | 9 | 0 | 1 | 10 | 15.772 | 16.220 | 4.554 | 1.69e-04 | yes |  |
| spring | הָעָיִן׃ / וָאֹמַר / עֵין | 9 | 0 | 1 | 10 | 15.772 | 16.220 | 4.554 | 1.69e-04 | yes |  |
| girl | הַנַּעַר | 9 | 1 | 0 | 10 | 15.772 | 17.677 | 4.554 | 6.82e-05 | yes |  |
| isaac | יִצְחָק | 36 | 22 | 23 | 81 | 15.691 | 22.930 | 1.574 | 2.49e-06 | yes |  |
| drink | שְׁתֵה / נִשְׁתֶּה / מַיִם | 22 | 9 | 9 | 40 | 15.664 | 18.845 | 2.174 | 3.25e-05 | yes |  |
| watered | הָרֹעִים / וַיִּשַּׁק / וְ | 7 | 0 | 0 | 7 | 15.647 | 15.647 | 5.798 | 2.39e-04 | yes |  |
| draw | לִשְׁאֹב / לִגְמַלֶּיךָ / אֶשְׁאָב | 7 | 0 | 0 | 7 | 15.647 | 15.647 | 5.798 | 2.39e-04 | yes |  |
| bags | אַמְתְּחֹתֵינוּ / הַכֶּסֶף / בְּאַמְתְּחֹתֵינוּ | 7 | 0 | 0 | 7 | 15.647 | 15.647 | 5.798 | 2.39e-04 | yes |  |
| successful | מַצְלִיחַ | 7 | 0 | 0 | 7 | 15.647 | 15.647 | 5.798 | 2.39e-04 | yes |  |
| our | אָבִינוּ / אָחִינוּ / אֱלֹהֵינוּ | 45 | 38 | 27 | 110 | 15.612 | 36.463 | 1.367 | 3.72e-10 | yes |  |
| flock | הַצֹּאן | 24 | 13 | 9 | 46 | 15.286 | 22.616 | 2.015 | 3.07e-06 | yes |  |
| live | לָשֶׁבֶת / וָחַי / בָּהּ | 36 | 12 | 34 | 82 | 15.195 | 15.201 | 1.543 | 3.15e-04 | yes |  |
| kindness | חֶסֶד / עִמָּדִי | 11 | 3 | 0 | 14 | 15.127 | 20.843 | 3.608 | 9.37e-06 | yes |  |
| you've | עָשִׂיתָ | 27 | 26 | 2 | 55 | 15.009 | 55.051 | 1.840 | 1.80e-15 | yes |  |
| we'll | וַיֹּאמְרוּ / עִמָּנוּ / נָמוּת | 27 | 25 | 3 | 55 | 15.009 | 50.234 | 1.840 | 4.28e-14 | yes |  |
| else | פֶּן | 15 | 5 | 3 | 23 | 14.846 | 18.081 | 2.758 | 5.35e-05 | yes |  |
| also | וְגַם / גַּם | 27 | 23 | 6 | 56 | 14.392 | 39.575 | 1.791 | 4.65e-11 | yes |  |
| ate | וַיֹּאכְלוּ / וַיֹּאכַל | 16 | 8 | 2 | 26 | 14.216 | 23.136 | 2.544 | 2.21e-06 | yes |  |
| blessed | וַיְבָרֶךְ / בָּרוּךְ | 24 | 10 | 14 | 48 | 13.912 | 15.722 | 1.892 | 2.30e-04 | yes |  |
| man | אִישׁ | 82 | 45 | 119 | 246 | 13.877 | 13.910 | 0.897 | 7.09e-04 | yes |  |
| don't | אֶל / לֹא / נָא | 29 | 24 | 10 | 63 | 13.819 | 34.314 | 1.666 | 1.51e-09 | yes |  |
| lot | לוֹט | 20 | 0 | 17 | 37 | 13.736 | 21.352 | 2.120 | 6.70e-06 | yes |  |
| hamor | חֲמוֹר / שְׁכֶם | 8 | 1 | 0 | 9 | 13.697 | 15.602 | 4.394 | 2.45e-04 | yes |  |
| game | צַיִד | 8 | 0 | 1 | 9 | 13.697 | 14.145 | 4.394 | 6.10e-04 | yes |  |
| hurried | וַיְמַהֵר | 8 | 1 | 0 | 9 | 13.697 | 15.602 | 4.394 | 2.45e-04 | yes |  |
| presence | פְּנֵי / מִפְּנֵי / עֹמֵד | 8 | 0 | 1 | 9 | 13.697 | 14.145 | 4.394 | 6.10e-04 | yes |  |
| human | הָאָדָם / אָדָם | 32 | 8 | 33 | 73 | 13.452 | 14.285 | 1.539 | 5.69e-04 | yes |  |
| wept | וַיֵּבְךְּ | 11 | 4 | 0 | 15 | 13.416 | 21.037 | 3.245 | 8.23e-06 | yes |  |
| we're | אֲנַחְנוּ | 11 | 3 | 1 | 15 | 13.416 | 16.335 | 3.245 | 1.58e-04 | yes |  |
| birthright | כַּיּוֹם / לִי / וַיִּמְכֹּר | 6 | 0 | 0 | 6 | 13.411 | 13.411 | 5.592 | 9.40e-04 | yes |  |
| eden | עֵדֶן | 6 | 0 | 0 | 6 | 13.411 | 13.411 | 5.592 | 9.40e-04 | yes |  |
| shepherds | רֹעֵי / צֹאן / אֲבוֹתֵינוּ׃ | 6 | 0 | 0 | 6 | 13.411 | 13.411 | 5.592 | 9.40e-04 | yes |  |
| can't | נוּכַל / לֹא / וַנֹּאמֶר | 6 | 0 | 0 | 6 | 13.411 | 13.411 | 5.592 | 9.40e-04 | yes |  |
| dove | הַיּוֹנָה / וַיִּשְׁלַח | 6 | 0 | 0 | 6 | 13.411 | 13.411 | 5.592 | 9.40e-04 | yes |  |
| sheol | שְׁאֹלָה | 6 | 0 | 0 | 6 | 13.411 | 13.411 | 5.592 | 9.40e-04 | yes |  |
| delicacies | מַטְעַמִּים / כַּאֲשֶׁר | 6 | 0 | 0 | 6 | 13.411 | 13.411 | 5.592 | 9.40e-04 | yes |  |
| drew | וַתִּשְׁאַב / וַתְּבִאֵהוּ / מְשִׁיתִהוּ׃ | 6 | 0 | 0 | 6 | 13.411 | 13.411 | 5.592 | 9.40e-04 | yes |  |
| humankind | הָאָדָם | 6 | 0 | 0 | 6 | 13.411 | 13.411 | 5.592 | 9.40e-04 | yes |  |
| dug | חָפְרוּ / בְּאֵר / וַיַּחְפְּרוּ | 9 | 2 | 0 | 11 | 13.282 | 17.092 | 3.817 | 9.80e-05 | yes |  |
| nahor | נָחוֹר | 9 | 0 | 2 | 11 | 13.282 | 14.178 | 3.817 | 6.01e-04 | yes |  |
| became | וַתַּהַר / וַיְהִי / וַתְּהִי | 20 | 7 | 11 | 38 | 12.981 | 13.893 | 2.040 | 7.16e-04 | yes |  |
| took | וַיִּקַּח | 55 | 48 | 49 | 152 | 12.830 | 29.249 | 1.080 | 4.35e-08 | yes |  |
| brother's | אָחִיךָ / אֶחָיו | 13 | 0 | 7 | 20 | 12.788 | 15.924 | 2.739 | 2.05e-04 | yes |  |
| know | יָדַעְתִּי / כִּי / יָדַע | 33 | 29 | 16 | 78 | 12.600 | 32.773 | 1.450 | 4.28e-09 | yes |  |
| he's | הוּא | 12 | 6 | 0 | 18 | 12.360 | 23.793 | 2.835 | 1.45e-06 | yes |  |
| still | עוֹד / עוֹדֶנּוּ | 14 | 7 | 2 | 23 | 12.184 | 19.540 | 2.502 | 2.12e-05 | yes |  |
| river | הַנָּהָר | 11 | 5 | 0 | 16 | 11.973 | 21.500 | 2.955 | 6.17e-06 | yes |  |
| maybe | אוּלַי | 11 | 5 | 0 | 16 | 11.973 | 21.500 | 2.955 | 6.17e-06 | yes |  |
| negeb | הַנֶּגֶב / הַנֶּגְבָּה׃ / בַּנֶּגֶב | 7 | 0 | 1 | 8 | 11.643 | 12.091 | 4.213 | 0.0022 | yes |  |
| looked | וַיַּרְא | 7 | 1 | 0 | 8 | 11.643 | 13.548 | 4.213 | 8.93e-04 | yes |  |
| found | יִמָּצֵא / מָצָאתִי / נָא | 25 | 18 | 12 | 55 | 11.543 | 22.087 | 1.633 | 4.20e-06 | yes |  |
| prostitute | וְזָנוּ / זֹנָה / וַחֲלָלָה | 9 | 0 | 3 | 12 | 11.415 | 12.759 | 3.332 | 0.0014 | yes |  |
| daughters | בְּנוֹת / בְּנֹתָיו / מִבְּנוֹת | 29 | 14 | 25 | 68 | 11.320 | 12.464 | 1.471 | 0.0017 | yes |  |
| rachel | רָחֵל | 17 | 12 | 3 | 32 | 11.256 | 24.636 | 2.067 | 8.42e-07 | yes |  |
| far | עַד / הַרְחֵק | 12 | 6 | 1 | 19 | 11.194 | 18.933 | 2.628 | 3.08e-05 | yes |  |
| lamech | לֶמֶךְ | 5 | 0 | 0 | 5 | 11.176 | 11.176 | 5.351 | 0.0038 | yes |  |
| tamar | תָּמָר / לְתָמָר | 5 | 0 | 0 | 5 | 11.176 | 11.176 | 5.351 | 0.0038 | yes |  |
| honest | כֵּנִים / רַעֲבוֹן | 5 | 0 | 0 | 5 | 11.176 | 11.176 | 5.351 | 0.0038 | yes |  |
| escape | הִמָּלֵט / הָהָרָה / אוּכַל | 5 | 0 | 0 | 5 | 11.176 | 11.176 | 5.351 | 0.0038 | yes |  |
| faithfulness | וֶאֱמֶת | 5 | 0 | 0 | 5 | 11.176 | 11.176 | 5.351 | 0.0038 | yes |  |
| began | הֵחֵל / וַיָּחֶל | 5 | 0 | 0 | 5 | 11.176 | 11.176 | 5.351 | 0.0038 | yes |  |
| gomorrah | וַעֲמֹרָה / עֲמֹרָה / וְעַל | 5 | 0 | 0 | 5 | 11.176 | 11.176 | 5.351 | 0.0038 | yes |  |
| lowered | הָרָתָה / בְּעֵינֶיהָ׃ | 5 | 0 | 0 | 5 | 11.176 | 11.176 | 5.351 | 0.0038 | yes |  |
| zoar | מִצּוֹעַר / בְּצוֹעַר / וּשְׁתֵּי | 5 | 0 | 0 | 5 | 11.176 | 11.176 | 5.351 | 0.0038 | yes |  |
| fathered | יָלַד / אֶת / וְאֶת | 11 | 1 | 5 | 17 | 10.731 | 10.976 | 2.714 | 0.0042 | yes |  |
| abraham's | אַבְרָהָם | 13 | 6 | 3 | 22 | 10.686 | 15.197 | 2.398 | 3.15e-04 | yes |  |
| let's | הָבָה / לְכָה / מֵאָבִינוּ | 13 | 9 | 0 | 22 | 10.686 | 27.834 | 2.398 | 1.09e-07 | yes |  |
| words | דִּבְרֵי / הַדְּבָרִים | 17 | 16 | 0 | 33 | 10.532 | 41.019 | 1.976 | 1.82e-11 | yes |  |
| house | בֵּית / הַבַּיִת / בֵּיתוֹ | 63 | 30 | 97 | 190 | 10.423 | 10.876 | 0.887 | 0.0045 | yes |  |
| laban | לָבָן | 21 | 19 | 5 | 45 | 10.351 | 31.075 | 1.703 | 1.33e-08 | yes |  |
| opened | וַיִּפְתַּח | 10 | 4 | 1 | 15 | 10.300 | 14.760 | 2.824 | 4.22e-04 | yes |  |
| good | טוֹב | 27 | 20 | 17 | 64 | 10.227 | 19.127 | 1.444 | 2.77e-05 | yes |  |
| boy | הַנַּעַר / הַיֶּלֶד | 15 | 13 | 0 | 28 | 10.109 | 34.880 | 2.091 | 1.05e-09 | yes |  |
| alive | חַי | 15 | 7 | 6 | 28 | 10.109 | 13.191 | 2.091 | 0.0011 | yes |  |
| blessing | בְּרָכָה׃ / בִּרְכָתִי | 9 | 2 | 2 | 13 | 9.919 | 10.625 | 2.969 | 0.0052 | yes |  |
| bethuel | בְּתוּאֵל / אָחִי / וּבְתוּאֵל | 8 | 0 | 3 | 11 | 9.616 | 10.960 | 3.171 | 0.0043 | yes |  |
| goshen | גֹּשֶׁן | 8 | 2 | 1 | 11 | 9.616 | 11.120 | 3.171 | 0.0039 | yes |  |
| birthplace | וּלְמוֹלַדְתֶּךָ / אַרְצִי / מוֹלַדְתִּי | 6 | 0 | 1 | 7 | 9.614 | 10.062 | 4.007 | 0.0073 | yes |  |
| gerar | גְּרָר / גְרָרָה | 6 | 1 | 0 | 7 | 9.614 | 11.520 | 4.007 | 0.0031 | yes |  |
| mourning | אֵבֶל | 6 | 0 | 1 | 7 | 9.614 | 10.062 | 4.007 | 0.0073 | yes |  |
| raised | וַיִּשָּׂא / עֵינָיו | 14 | 8 | 4 | 26 | 9.538 | 15.553 | 2.106 | 2.52e-04 | yes |  |
| garment | בִּגְדוֹ / הַחוּצָה׃ | 7 | 0 | 2 | 9 | 9.458 | 10.354 | 3.476 | 0.0062 | yes |  |
| drank | וַיִּשְׁתּוּ / וַיָּשֶׁת | 7 | 1 | 1 | 9 | 9.458 | 9.811 | 3.476 | 0.0086 | yes |  |
| loved | וַיֶּאֱהַב / אָהַב | 7 | 2 | 0 | 9 | 9.458 | 13.269 | 3.476 | 0.0010 | yes |  |
| how | אִם / וְאֵיךְ / כֹּה | 17 | 11 | 7 | 35 | 9.220 | 15.962 | 1.811 | 2.01e-04 | yes |  |
| daughter | בַּת | 30 | 6 | 41 | 77 | 8.976 | 12.880 | 1.253 | 0.0013 | yes |  |
| abiram | וַאֲבִירָם / וְדָתָן | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| nights | לַיְלָה / יוֹם / וְאַרְבָּעִים | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| anguish | וְהַגְּמַלִּים / וַיִּצֶר / בְּיָגוֹן | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| ishmaelites | לַיִּשְׁמְעֵאלִים / מִצְרַיְמָה / וְנִמְכְּרֶנּוּ | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| articles | כְּלִי / וּכְלֵי | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| spies | מְרַגְּלִים | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| fodder | מִסְפּוֹא | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| sake | בַּעֲבוּר / יִמָּצְאוּן / לְדַבֵּר | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| brown | חוּם / בַּכְּשָׂבִים | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| grown | הַגְּבֹהִים / מַשְׁחִתִים / וַיְשַׁלְּחֵנוּ | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| doesn't | לֹא / תֹסִפוּן / בְּיָדִי | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| invoked | בְּשֵׁם / וַיִּקְרָא | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| timnah | תִּמְנָתָה׃ | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| dathan | וַאֲבִירָם / וְדָתָן | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| gazed | וַיַּשְׁקֵף | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| column | עַמּוּד / בְּעַמּוּד | 9 | 5 | 0 | 14 | 8.675 | 18.202 | 2.680 | 4.95e-05 | yes |  |
| too | גַּם / וְגַם | 19 | 15 | 8 | 42 | 8.667 | 19.394 | 1.622 | 2.33e-05 | yes |  |
| get | קוּם | 17 | 14 | 5 | 36 | 8.624 | 21.741 | 1.735 | 5.27e-06 | yes |  |
| heard | וַיִּשְׁמַע / שָׁמַעְתִּי | 23 | 15 | 17 | 55 | 8.500 | 12.787 | 1.424 | 0.0014 | yes |  |
| before | לִפְנֵי | 33 | 31 | 25 | 89 | 8.388 | 23.121 | 1.138 | 2.23e-06 | yes |  |
| ran | וַיָּרץ | 8 | 2 | 2 | 12 | 8.240 | 8.947 | 2.809 | 0.0140 | yes |  |
| virtuous | צַדִּיק / תַּהֲרֹג׃ | 8 | 4 | 0 | 12 | 8.240 | 15.862 | 2.809 | 2.12e-04 | yes |  |
| asked | וַיִּשְׁאֲלוּ / וַיִּשְׁאַל / הֲיֵשׁ | 8 | 4 | 0 | 12 | 8.240 | 15.862 | 2.809 | 2.12e-04 | yes |  |
| many | רַבִּים | 10 | 6 | 1 | 17 | 8.147 | 15.886 | 2.377 | 2.10e-04 | yes |  |
| we've | חָטָאנוּ׃ / עָשִׂינוּ / וַיַּשְׁכִּמוּ | 7 | 1 | 2 | 10 | 7.867 | 7.914 | 2.991 | 0.0251 | yes |  |
| she's | אֲחֹתִי / הוּא / אָמַרְתָּ | 7 | 3 | 0 | 10 | 7.867 | 13.583 | 2.991 | 8.74e-04 | yes |  |
| sihon | סִיחֹן / עִמּוֹ | 5 | 0 | 1 | 6 | 7.621 | 8.068 | 3.766 | 0.0234 | yes |  |
| sight | פְּנֵי / וַיַּשְׁקִפוּ / לְשַׁלְּחָם׃ | 5 | 0 | 1 | 6 | 7.621 | 8.068 | 3.766 | 0.0234 | yes |  |
| dinah | דִּינָה | 5 | 0 | 1 | 6 | 7.621 | 8.068 | 3.766 | 0.0234 | yes |  |
| messengers | מַלְאָכִים | 5 | 1 | 0 | 6 | 7.621 | 9.526 | 3.766 | 0.0101 | yes |  |
| language | אַחַת / וּדְבָרִים / אֲחָדִים | 5 | 0 | 1 | 6 | 7.621 | 8.068 | 3.766 | 0.0234 | yes |  |
| shelah | שֵׁלָה / לְשֵׁלָה / וַתֵּשֶׁב | 6 | 0 | 2 | 8 | 7.610 | 8.506 | 3.270 | 0.0177 | yes |  |
| whole | כּל | 6 | 1 | 1 | 8 | 7.610 | 7.964 | 3.270 | 0.0249 | yes |  |
| egyptians | הַמִּצְרִים | 6 | 2 | 0 | 8 | 7.610 | 11.421 | 3.270 | 0.0033 | yes |  |
| mother | אִמּוֹ | 14 | 4 | 11 | 29 | 7.485 | 7.485 | 1.795 | 0.0325 | yes |  |
| bless | שְׁמִי / בַּעֲבוּר / יְבָרֵךְ | 15 | 11 | 6 | 32 | 7.474 | 15.198 | 1.716 | 3.15e-04 | yes |  |
| edom | אֱדוֹם | 10 | 0 | 8 | 18 | 7.269 | 10.853 | 2.196 | 0.0045 | yes |  |
| place | הַמָּקוֹם / בְּמָקוֹם / מָקוֹם | 52 | 26 | 85 | 163 | 7.226 | 7.675 | 0.805 | 0.0293 | yes |  |
| fled | וַיָּנס / בְּרַח | 8 | 4 | 1 | 13 | 7.108 | 11.568 | 2.519 | 0.0030 | yes |  |
| could | לִמְנוֹת / יִמָּנֶה׃ / יוּכַל | 8 | 2 | 3 | 13 | 7.108 | 7.408 | 2.519 | 0.0340 | yes |  |
| little | מְעַט | 8 | 4 | 1 | 13 | 7.108 | 11.568 | 2.519 | 0.0030 | yes |  |
| woman | הָאִשָּׁה / אִשָּׁה | 32 | 7 | 51 | 90 | 7.001 | 12.369 | 1.044 | 0.0018 | yes |  |
| bowed | וַיִּשְׁתַּחוּ / וַיִּשְׁתַּחֲווּ | 12 | 10 | 2 | 24 | 6.956 | 19.106 | 1.891 | 2.80e-05 | yes |  |
| wine | יַיִן | 9 | 0 | 7 | 16 | 6.709 | 9.845 | 2.232 | 0.0084 | yes |  |
| shechem | שְׁכֶם | 9 | 6 | 1 | 16 | 6.709 | 14.448 | 2.232 | 5.13e-04 | yes |  |
| ammon | עַמּוֹן / עַד | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| lot's | לוֹט | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| nostrils | בְּאַפָּיו / נִשְׁמַת | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| attractive | תֹּאַר / מַרְאֶה | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| marah | מָרָתָה / מִמָּרָה / מָרָה׃ | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| eve | חַוָּה / אִשְׁתּוֹ / הָיְתָה | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| king's | הַמֶּלֶךְ | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| colors | הַפַּסִּים / פַּסִּים׃ / וַיַּפְשִׁיטוּ | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| mistress | וַתֵּקַל / גְּבִרְתָּהּ / בָאת | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| nakedness | עֶרְוַת / בַּחוּץ / לִשְׁנֵי | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| three-year-old | קְחָה / מְשֻׁלֶּשֶׁת / מְשֻׁלָּשׁ | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| lodging | בַּמָּלוֹן / הַמָּלוֹן / וַנִּפְתְּחָה | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| warden | שַׂר / בֵּית / הַסֹּהַר | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| gray | שֵׂיבָתִי / וְהוֹרַדְתֶּם / בְּיָגוֹן | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| shechem's | שְׁכֶם / חֲמוֹר / לְדַבֵּר | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| defiled | טָמֵא / בֹּאָם׃ / וְיַעֲקֹב | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| enoch | כְּשֵׁם / חֲנוֹךְ / וְ | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| rain | הַגֶּשֶׁם | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| zillah | וְצִלָּה | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| delayed | תֹאמְרוּן / גַּרְתִּי / וְאַחַר | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| jobab | יוֹבָב | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| hairy | שַׁעַר / הִכִּירוֹ / כִּידֵי | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| sacred | קְדֵשָׁה׃ / בָזֶה / הָיְתָה | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| pt | — | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| completed | וְאָבוֹאָה / מִלְאוּ / הָבָה | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| aroma | כְּרֵיחַ / בֵּרְכוֹ / וַיְבָרְכֵהוּ | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| pledge | הָעֵרָבוֹן / עֵרָבוֹן / שׁלְחֶךָ׃ | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| adullamite | הָעֲדֻלָּמִי / רֵעֵהוּ / עֲדֻלָּמִי | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| amalekite | הָעֲמָלֵקִי / וְהַכְּנַעֲנִי | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| burial | וְשָׁכַבְתִּי / וּנְשָׂאתַנִי / וּקְבַרְתַּנִי | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| bracelets | יָדֶיהָ׃ / הַנֶּזֶם | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| roll | וְגָלְלוּ / מֵעַל / וְהִשְׁקוּ | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| spying | מְרַגְּלִים / לֹא / נָחְנוּ | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| consent | אַךְ / בְּזֹאת | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| circles | אֶרֶץ | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| nephilim | הַנְּפִלִים | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| egyptian | מִצְרִי / הַמִּצְרִי / הַמִּצְרִית | 7 | 2 | 2 | 11 | 6.622 | 7.329 | 2.628 | 0.0358 | yes |  |
| neck | צַוָּארָיו׃ / בְשֶׂה / וַעֲרַפְתּוֹ | 7 | 3 | 1 | 11 | 6.622 | 9.541 | 2.628 | 0.0101 | yes |  |
| time | הַפַּעַם / שֵׁנִית | 20 | 14 | 16 | 50 | 6.490 | 10.430 | 1.318 | 0.0059 | yes |  |
| much | מְאֹד / רַב | 11 | 4 | 7 | 22 | 6.376 | 6.732 | 1.891 | 0.0480 | yes |  |
| face | פְּנֵי | 27 | 26 | 22 | 75 | 6.183 | 17.821 | 1.073 | 6.21e-05 | yes |  |
| grew | וַיִּגְדַּל / וַיִּגְבְּרוּ | 6 | 2 | 1 | 9 | 6.180 | 7.684 | 2.784 | 0.0292 | yes |  |
| flocks | הָעֲדָרִים / הַבְּאֵר / צֹאן | 6 | 1 | 2 | 9 | 6.180 | 6.227 | 2.784 | 0.0630 |  |  |
| spotted | בַּכְּשָׂבִים / הָעַתֻּדִים / וּבְרֻדִּים׃ | 6 | 2 | 1 | 9 | 6.180 | 7.684 | 2.784 | 0.0292 | yes |  |
| amorite | הָאֱמֹרִי | 8 | 5 | 1 | 14 | 6.155 | 12.230 | 2.278 | 0.0020 | yes |  |
| may | נָא / עַמִּי / מִכּל | 26 | 23 | 23 | 72 | 6.021 | 14.150 | 1.080 | 6.10e-04 | yes |  |
| soul | נַפְשִׁי | 9 | 5 | 3 | 17 | 5.915 | 9.151 | 2.052 | 0.0127 | yes |  |
| road | בַּדֶּרֶךְ | 9 | 8 | 0 | 17 | 5.915 | 21.158 | 2.052 | 7.63e-06 | yes |  |
| days | יָמִים | 50 | 32 | 80 | 162 | 5.900 | 6.043 | 0.736 | 0.0707 |  |  |
| shem | שָׁם | 5 | 0 | 2 | 7 | 5.823 | 6.719 | 3.029 | 0.0480 | yes |  |
| plain | הַכִּכָּר | 5 | 0 | 2 | 7 | 5.823 | 6.719 | 3.029 | 0.0480 | yes |  |
| rods | הַמַּקְלוֹת / וַחֲשֻׁקֵיהֶם / וָוֵי | 5 | 0 | 2 | 7 | 5.823 | 6.719 | 3.029 | 0.0480 | yes |  |
| waters | הַמַּיִם | 12 | 4 | 10 | 26 | 5.756 | 5.774 | 1.677 | 0.0835 |  |  |
| suffering | אָמַר / וְיֹלַדְתְּ / ענְיֵךְ׃ | 4 | 1 | 0 | 5 | 5.676 | 7.581 | 3.476 | 0.0306 | yes |  |
| bearing | אֲכַלְתֶּם / לָשֵׂאת / וְאַתָּה | 4 | 0 | 1 | 5 | 5.676 | 6.124 | 3.476 | 0.0671 |  |  |
| recognize | הַכֶּר | 4 | 1 | 0 | 5 | 5.676 | 7.581 | 3.476 | 0.0306 | yes |  |
| few | יִמְעַט / מִהְיוֹת / וּשְׁכֵנוֹ | 4 | 0 | 1 | 5 | 5.676 | 6.124 | 3.476 | 0.0671 |  |  |
| kid | גְּדִי | 4 | 1 | 0 | 5 | 5.676 | 7.581 | 3.476 | 0.0306 | yes |  |
| rose | וַיָּקם | 4 | 1 | 0 | 5 | 5.676 | 7.581 | 3.476 | 0.0306 | yes |  |
| bush | הַסְּנֶה | 4 | 1 | 0 | 5 | 5.676 | 7.581 | 3.476 | 0.0306 | yes |  |
| spend | הַגִּידִי / לָלִין׃ / הֲיֵשׁ | 4 | 1 | 0 | 5 | 5.676 | 7.581 | 3.476 | 0.0306 | yes |  |
| sarai | שָׂרֵי | 8 | 0 | 7 | 15 | 5.341 | 8.477 | 2.072 | 0.0180 | yes |  |
| today | הַיּוֹם | 13 | 11 | 6 | 30 | 5.299 | 13.024 | 1.517 | 0.0012 | yes |  |
| find | אֶמְצָא / תִּמְצָא / לִמְצֹא | 13 | 12 | 5 | 30 | 5.299 | 15.547 | 1.517 | 2.52e-04 | yes |  |
| forty | אַרְבָּעִים | 13 | 1 | 16 | 30 | 5.299 | 8.886 | 1.517 | 0.0144 | yes |  |
| king | מֶלֶךְ | 13 | 12 | 5 | 30 | 5.299 | 15.547 | 1.517 | 2.52e-04 | yes |  |
| very | מְאֹד | 25 | 21 | 25 | 71 | 5.273 | 10.738 | 1.025 | 0.0049 | yes |  |
| isn't | אֵין / הֲלֹא / אֵינֶנּוּ | 9 | 8 | 1 | 18 | 5.217 | 16.379 | 1.891 | 1.53e-04 | yes |  |
| they | וַיֹּאמְרוּ / אֶת | 200 | 161 | 432 | 793 | 5.198 | 5.243 | 0.328 | 0.1129 |  |  |
| son's | בִּנְךָ / מִצֵּיד / וַיִּגַּשׁ | 6 | 1 | 3 | 10 | 5.080 | 5.084 | 2.422 | 0.1245 |  |  |
| knew | וַיֵּדַע / יָדַע | 6 | 2 | 2 | 10 | 5.080 | 5.787 | 2.422 | 0.0829 |  |  |
| philistines | פְּלִשְׁתִּים | 6 | 4 | 0 | 10 | 5.080 | 12.701 | 2.422 | 0.0015 | yes |  |
| sister | אֲחֹתִי / אֲחוֹת / הוּא | 14 | 5 | 15 | 34 | 4.950 | 4.971 | 1.392 | 0.1316 |  |  |
| where | אֲשֶׁר / שָׁם | 19 | 17 | 15 | 51 | 4.909 | 12.111 | 1.154 | 0.0022 | yes |  |
| pass | תַעֲבֹר / וְהַעֲבַרְתָּ / עֵבֶר | 13 | 6 | 12 | 31 | 4.842 | 5.121 | 1.437 | 0.1218 |  |  |
| upon | בּוֹ / הָשֵׁב | 7 | 3 | 3 | 13 | 4.769 | 5.829 | 2.098 | 0.0808 |  |  |
| son | בֶּן | 83 | 42 | 177 | 302 | 4.765 | 9.653 | 0.498 | 0.0095 | yes |  |
| those | הָהֵם / בַּיַּמִּים | 18 | 3 | 27 | 48 | 4.755 | 8.497 | 1.170 | 0.0178 | yes |  |
| come | אֶל / יָבֹא / בָּא | 64 | 53 | 108 | 225 | 4.687 | 6.888 | 0.568 | 0.0465 | yes |  |
| maid | שִׁפְחָה / שִׁפְחַת / שִׁפְחָתוֹ | 11 | 7 | 7 | 25 | 4.670 | 7.144 | 1.557 | 0.0397 | yes |  |
| dust | עֲפַר | 8 | 0 | 8 | 16 | 4.637 | 8.221 | 1.891 | 0.0213 | yes |  |
| coat | כְּתֹנֶת / הַכֻּתֹּנֶת | 8 | 0 | 8 | 16 | 4.637 | 8.221 | 1.891 | 0.0213 | yes |  |
| asses | וַחֲמֹרִים / הַבָּקָר | 8 | 2 | 6 | 16 | 4.637 | 4.646 | 1.891 | 0.1414 |  |  |
| call | לִקְרֹא | 9 | 5 | 5 | 19 | 4.600 | 6.367 | 1.747 | 0.0586 |  |  |
| yet | טֶרֶם | 5 | 3 | 0 | 8 | 4.574 | 10.290 | 2.543 | 0.0063 | yes |  |
| gift | הַמִּנְחָה / מַתָּנָה / בְּיָדָם | 5 | 0 | 3 | 8 | 4.574 | 5.918 | 2.543 | 0.0764 |  |  |
| household | בֵּיתוֹ | 5 | 0 | 3 | 8 | 4.574 | 5.918 | 2.543 | 0.0764 |  |  |
| stopped | חָדַל | 5 | 3 | 0 | 8 | 4.574 | 10.290 | 2.543 | 0.0063 | yes |  |
| lahai-roi | רֹאִי׃ / לַחַי / עִם | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| care | וְעֵינְכֶם / תָּחֹס / כְּלֵיכֶם | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| chesed | כֶּשֶׂד / חֲזוֹ / פִּלְדָּשׁ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| territory | שְׂדֵה / אַרְצָה / לְפָנָיו | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| undertaken | הוֹאַלְתִּי / לְדַבֵּר / וָאֵפֶר׃ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| smooth | חֵלֶק / וְאָנֹכִי / הִלְבִּישָׁה | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| peeled | הַמַּקְלוֹת | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| substance | הַיְקוּם / הָאֲדָמָה | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| bridegroom | דָּמִים / חֹתֵן | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| waited | אֲחֵרִים / וַיָּחֶל | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| sheaves | מְאַלְּמִים / אֲלֻמִּים / קָמָה | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| twins | בְּבִטְנָהּ׃ / לִדְתָּהּ / תְאוֹמִים | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| later | לְשִׁבְעַת / וּמֵי / הַיָּמִים | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| abounding | וְרַב / אַפַּיִם / אֹרֶךְ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| oaks | בְּאֵלֹנֵי / בְּחֶבְרוֹן / וַיֶּאֱהַל | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| hirah | עֲדֻלָּמִי / חִירָה׃ / וְשָׂמוּ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| hazo | כֶּשֶׂד / חֲזוֹ / פִּלְדָּשׁ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| nimrod | גִּבֹּר | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| tending | רָעָה / דִּבָּתָם / בְּצֹאן | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| weren't | מְרַגְּלִים / לֹא / נָחְנוּ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| remnant | שָׂרִיד / וַיִּירְשׁוּ / וַיֻּכּוּ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| says | אֹתָהּ / מְצָאָתְנוּ׃ / מִקְדַּשׁ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| sidon | צִידֹן / וּכְנָעַן׃ / בְּכֹרוֹ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| leaves | יַעֲזב / וְדָבַק / בְּאִשְׁתּוֹ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| tahash | וּפִילַגְשׁוֹ / רְאוּמָה / גַּחַם | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| sarai's | וַתֹּאמֶר / בָאת / תֵלֵכִי | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| husham | חֻשָׁם | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| annihilate | תִּסְפֶּה / הַאַף / וַיִּגַּשׁ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| friend | הָעֲדֻלָּמִי / רֵעֵהוּ / הָעִזִּים | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| pildash | כֶּשֶׂד / חֲזוֹ / פִּלְדָּשׁ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| euphrates | פְרָת / מִנְּהַר / נְהַר | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| plowing | בֶּחָרִישׁ / וּבַקָּצִיר / תַעֲבֹד | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| wretchedness | אֵיךְ / בְּרָע / יִמָּצֵא | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| present | נָכוֹן / וְנִצַּבְתָּ / לַבֹּקֶר | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| ai | אהֳלֹה | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| rode | וַיַּרְכִּבֵם / הַחֲמֹר / אַרְצָה | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| extended | חִנּוֹ / וַיֵּט / הַחַלּוֹן | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| hamor's | וַיִּיטְבוּ / דִּבְרֵיהֶם / וּבְעֵינֵי | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| herded | אָז / רֹעֵי / יֹשֵׁב | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| environs | בְּנֹתֶיהָ / וּבְכל | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| joktan | יקְטָן׃ / וּלְעֵבֶר / פֶּלֶג | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| expelled | גֵּרַשְׁתָּ / וּמִפָּנֶיךָ / אֶסָּתֵר | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| kids | גְּדָיֵי / טֹבִים / לְאָבִיךָ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| troughs | וּלְכֹהֵן / וַתִּדְלֶנָה / וַתְּמַלֶּאנָה | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| copulate | הַמְקֻשָּׁרוֹת / לְיַחְמֵנָּה / בַּמַּקְלוֹת׃ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| buz | בּוּז / בְּכֹרוֹ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| wiped | וַיִּמַח / וַיִּמָּחוּ / וַיִּשָּׁאֶר | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| israelites | וַיְדַבֵּר / יִשְׂרָאֵל / בְּנֵי | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| heel | וְאֵיבָה / אָשִׁית / בֵּינְךָ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| shinar | שִׁנְעָר׃ / בִקְעָה / בְּנסְעָם | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| compassion | עָלָיו / וַתִּרְאֵהוּ / וַתַּחְמֹל | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| rained | הִמְטִיר | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| atad | בַּעֲבֻר / הָאָטָד / הָאֵבֶל | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| tender | רָץ / רַךְ / וְטוֹב | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| maacah | וּפִילַגְשׁוֹ / רְאוּמָה / גַּחַם | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| slow | וְרַב / אַפַּיִם / אֹרֶךְ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| irad | לַחֲנוֹךְ / עִירָד / וְעִירָד | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| mentioned | אֲמַרְתֶּם / הַעוֹדֶנּוּ / הַזָּקֵן | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| finds | גֵּרַשְׁתָּ / וּמִפָּנֶיךָ / אֶסָּתֵר | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| achbor | עַכְבּוֹר׃ / חָנָן / בַּעַל | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| hitched | וַיֶּאְסֹר / רִכְבּוֹ / לָקַח | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| countable | יִסָּפֵר / מֵרֹב׃ / לָהּ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| tower | הַמִּגְדָּל / לִרְאֹת / בְּנוֹ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| grow | וַיַּצְמַח / נֶחְמָד / לְמַרְאֶה | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| drinking | כִּלּוּ / נֶזֶם / מִשְׁקָלוֹ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| thread | יֹצֵא / הַשֵּׁנִי / יָדוֹ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| pishon | פִּישׁוֹן / הַסֹּבֵב / הַחֲוִילָה | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| nursed | מִלֵּל / הֵינִיקָה / לִזְקֻנָיו׃ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| widowhood | וַתָּסַר / אַלְמְנוּתָהּ / מֵעָלֶיהָ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| slumber | וְתַרְדֵּמָה / נָפְלָה / אֵימָה | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| roamer | נָע / וָנָד / בְּאֶרֶץ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| dawn | הַשַּׁחַר / עֹלָה | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| quick | מִהַרְתֶּן / וַתָּבֹאנָה / אֲבִיהֶן | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| disgrace | לָבוּז / מְצָאתָהּ׃ / הַגְּדִי | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| pasture | מִרְעֶה / לַצֹּאן / יֵשְׁבוּ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| resting | מָנוֹחַ / לְכַף / רַגְלָהּ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| superior | גְבִיר / יַעַבְדוּךָ / הֱוֵה | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| canaanites | הַכְּנַעֲנִי / וְאֶת | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| mehuya-el | לַחֲנוֹךְ / עִירָד / וְעִירָד | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| pairs | שִׁבְעָה / וְאִשְׁתּוֹ / מֵעוֹף | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| loaded | שִׁבְרָם / וַיִּשְׂאוּ / חֲמֹרֵיהֶם | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| desire | עִצְּבוֹנֵךְ / וְהֵרֹנֵךְ / בְּעֶצֶב | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| stew | וַיָּזֶד / נָזִיד / וְהוּא | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| nineveh | נִינְוֵה / כָּלַח׃ / וְאֶת | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| hunting | מִצֵּידוֹ׃ / לְבָרֵךְ / וְעָשׂוּ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| baal-hanan | עַכְבּוֹר׃ / חָנָן / בַּעַל | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| ripped | וַיִּקְרְעוּ / וַיַּעֲמֹס / הָעִירָה׃ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| led | בַּדֶּרֶךְ / אֱלֹהֵי / אָחִי | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| hunter | כְּנִמְרֹד / גִּבּוֹר / יֹאמַר | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| swallow | נָסוּ / לְקֹלָם / תִּבְלָעֵנוּ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| calah | נִינְוֵה / כָּלַח׃ / וְאֶת | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| hadad | הֲדַד | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| proportion | יֵיטִיב / וְהֵטַבְנוּ / הַטּוֹב | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| loves | קָטָן / אֲהֵבוֹ׃ / וְיֶלֶד | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| stuff | הַלְעִיטֵנִי / הָאָדָם / נָא | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| pain | עִצְּבוֹנֵךְ / וְהֵרֹנֵךְ / בְּעֶצֶב | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| week | שֶׁבַע / זֹאת / בַּעֲבֹדָה | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| backwards | הַשִּׂמְלָה / אֲחֹרַנִּית / וּפְנֵיהֶם | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| sustain | צַדִּיקִם / בִסְדֹם / וְנָשָׂאתִי | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| eased | מֵעַל / הֲקַלּוּ / מֵאִתּוֹ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| samlah | שַׂמְלָה / תַּחְתָּיו | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| follow | אַחֲרֵי / תֵלֵךְ / וָאֹמַר | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| wells | בִּימֵי / בְּאֵרֹת / וַיְסַתְּמוּם | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| noon | בַּצּהֳרָיִם׃ / יֹאכְלוּ / וּטְבֹחַ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| tebah | וּפִילַגְשׁוֹ / רְאוּמָה / גַּחַם | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| virtue | צִדְקָתִי / וְחוּם / גָּנוּב | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| rover | נָע / וָנָד / בְּאֶרֶץ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| seal | מוּצֵאת / חָמִיהָ / הַחֹתֶמֶת | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| resident | לְיוֹשֵׁב / פֶּן / תִּכְרֹת | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| struggled | שָׂרִיתָ / וַתּוּכָל׃ / יֹאמַר | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| limit | וְהִגְבַּלְתָּ / הִשָּׁמְרוּ / בְּקָצֵהוּ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| herders | רֹעֶיךָ / רֹעֵי / מְרִיבָה | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| portions | מַשְׂאֹת / וַתֵּרֶב / מִמַּשְׂאֹת | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| eber | יָלַד / עֵבֶר / וְשִׁלַּח | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| metusha-el | לַחֲנוֹךְ / עִירָד / וְעִירָד | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| restrained | וַיִּתְאַפַּק / שִׂימוּ / וַיִּכָּלֵא | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| shua | שׁוּעַ / כְּנַעֲנִי / וַיִּקָּחֶהָ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| mightier | מֵעִמָּנוּ / עָצַמְתָּ / גיים | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| reumah | וּפִילַגְשׁוֹ / רְאוּמָה / גַּחַם | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| traveling | לְחֹבָב / הַמִּדְיָנִי / נֹסְעִים | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| hormah | וַיַּחֲרֵם / חרְמָה׃ / אֶתְהֶם | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| sevenfold | שִׁבְעָתַיִם | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| channels | בָּרְהָטִים | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| fighting | אָנוּסָה / מִפְּנֵי / נִלְחָם | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| physicians | הָרֹפְאִים / לַחֲנֹט / וַיְצַו | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| loud | בִּבְכִי / וַיִּשְׁמְעוּ / וַיִּתֵּן | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| good-looking | מַרְאֶה / לְאִשְׁתּוֹ / טוֹבַת | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| exhausted | עָיֵף׃ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| trusted | בַּיהֹוָה / וַיַּאֲמִינוּ / הַיָּד | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| walking | לִקְרָאתֵנוּ / הַצָּעִיף / וַתִּתְכָּס׃ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| reaches | וּמִגְדָּל / וְנַעֲשֶׂה / נָפוּץ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| deception | בְּמִרְמָה / בִּרְכָתֶךָ׃ / בָּא | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| sought | הַמְבַקְשִׁים / שָׁב / מֵתוּ׃ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| flame | בְּלַבַּת / וְהַסְּנֶה / בֹּעֵר | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| bitumen | נִלְבְּנָה / וְנִשְׂרְפָה / לִשְׂרֵפָה | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| bore | וָאֶשְׁאַל / וְהַצְּמִידִים / אָפָה | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| inclination | יֵצֶר / לִבּוֹ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| reckoning | וָפֶשַׁע / יְנַקֶּה / רִבֵּעִים׃ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| associated | לְבַעַל / וַיִּצָּמֶד / שֹׁפְטֵי | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| jidlaph | כֶּשֶׂד / חֲזוֹ / פִּלְדָּשׁ | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| greatly | מְאֹד | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| cluster | הָאֶשְׁכּוֹל / כָּרְתוּ / אֹדוֹת | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| gaham | וּפִילַגְשׁוֹ / רְאוּמָה / גַּחַם | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| rising | מְאַלְּמִים / אֲלֻמִּים / קָמָה | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| father's | אָבִיךָ / אָבִיו / אָבִי | 26 | 20 | 32 | 78 | 4.400 | 6.860 | 0.905 | 0.0472 | yes |  |
| great | רַב | 11 | 6 | 9 | 26 | 4.200 | 5.100 | 1.461 | 0.1235 |  |  |
| milcah | מִלְכָּה | 6 | 0 | 5 | 11 | 4.199 | 6.439 | 2.132 | 0.0570 |  |  |
| youth | בַּעֲבוּר / וְעַד / אָבִיהָ | 4 | 0 | 2 | 6 | 4.120 | 5.016 | 2.739 | 0.1292 |  |  |
| she'll | וּבֵרַכְתִּי / וּבֵרַכְתִּיהָ / מִמֶּנָּה | 4 | 1 | 1 | 6 | 4.120 | 4.473 | 2.739 | 0.1414 |  |  |
| yaphet | יֶפֶת / וָיֶפֶת | 4 | 0 | 2 | 6 | 4.120 | 5.016 | 2.739 | 0.1292 |  |  |
| laban's | לָבָן | 4 | 2 | 0 | 6 | 4.120 | 7.931 | 2.739 | 0.0250 | yes |  |
| lying | מִשְׁכְּבֵי / שָׁכַב / עָלֶיהָ | 4 | 0 | 2 | 6 | 4.120 | 5.016 | 2.739 | 0.1292 |  |  |
| tents | לְלוֹט / וְאֹהָלִים׃ / הַהֹלֵךְ | 4 | 0 | 2 | 6 | 4.120 | 5.016 | 2.739 | 0.1292 |  |  |
| age | זָקֵן / זְקֻנִים / בְּשֵׂיבָה | 4 | 2 | 0 | 6 | 4.120 | 7.931 | 2.739 | 0.0250 | yes |  |
| spent | וַיָּלִינוּ / לְאֶחָיו / וַיִּזְבַּח | 4 | 2 | 0 | 6 | 4.120 | 7.931 | 2.739 | 0.0250 | yes |  |
| happen | הַקְרֵה / בְּנוֹ | 4 | 2 | 0 | 6 | 4.120 | 7.931 | 2.739 | 0.0250 | yes |  |
| indeed | אַךְ / חַי / וְאוּלָם | 4 | 1 | 1 | 6 | 4.120 | 4.473 | 2.739 | 0.1414 |  |  |
| bilhah | בִּלְהָה | 4 | 0 | 2 | 6 | 4.120 | 5.016 | 2.739 | 0.1292 |  |  |
| bury | לִקְבֹּר / וְאֶקְבְּרָה / קָבְרוּ | 7 | 0 | 7 | 14 | 4.058 | 7.194 | 1.891 | 0.0391 | yes |  |
| listened | וַיִּשְׁמַע | 9 | 6 | 5 | 20 | 4.050 | 6.789 | 1.616 | 0.0480 | yes |  |
| east | קֵדְמָה / מִזְרָחָה / מִקֶּדֶם | 13 | 5 | 15 | 33 | 4.026 | 4.048 | 1.289 | 0.1796 |  |  |
| feet | וְרָחֲצוּ / רַגְלָיו / רַגְלֵיהֶם׃ | 8 | 2 | 7 | 17 | 4.024 | 4.093 | 1.731 | 0.1796 |  |  |
| done | עָשָׂה / יַעֲשֶׂה / עֵשָׂו | 25 | 21 | 30 | 76 | 3.995 | 7.600 | 0.877 | 0.0305 | yes |  |
| than | מִמֶּנּוּ / מִן | 14 | 9 | 14 | 37 | 3.811 | 5.022 | 1.195 | 0.1292 |  |  |
| naked | עִירָם / הַמָּן / אֹכֶלֶת | 3 | 0 | 1 | 4 | 3.805 | 4.253 | 3.113 | 0.1621 |  |  |
| prepared | בּוֹא / פִּנִּיתִי / וּמָקוֹם | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| dreams | חֲלֹמֹתָיו | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| unless | תִרְאוּ / בִּלְתִּי / אִם | 3 | 0 | 1 | 4 | 3.805 | 4.253 | 3.113 | 0.1621 |  |  |
| expanded | וַיִּפְרֹץ / וּשְׁפָחוֹת / רַבּוֹת | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| wrong | הֲרֵעֹתֶם / הַעוֹד / אָח | 3 | 0 | 1 | 4 | 3.805 | 4.253 | 3.113 | 0.1621 |  |  |
| though | לוּז / לָרִאשֹׁנָה׃ / וָפֶשַׁע | 3 | 0 | 1 | 4 | 3.805 | 4.253 | 3.113 | 0.1621 |  |  |
| harm | אָסוֹן / וְהוּא | 3 | 0 | 1 | 4 | 3.805 | 4.253 | 3.113 | 0.1621 |  |  |
| planted | וַיִּטַּע | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| pitched | וַיֵּט / אהֳלוֹ | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| destroying | כְּגַן / כְּאֶרֶץ / צֹעַר׃ | 3 | 0 | 1 | 4 | 3.805 | 4.253 | 3.113 | 0.1621 |  |  |
| ourselves | מָצָא | 3 | 0 | 1 | 4 | 3.805 | 4.253 | 3.113 | 0.1621 |  |  |
| valley | וְהָעֲמָלֵקִי / בָּעֵמֶק / פְּנוּ | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| trembled | וַיֶּחֱרַד | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| divided | וַיַּחַץ | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| hurry | מַהֲרוּ / וַעֲלוּ / שָׂמַנִי | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| hid | יָרֵא / קֹלְךָ / וָאִ | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| ready | נְכֹנִים / לִשְׁלֹשֶׁת / תִּגְּשׁוּ | 3 | 0 | 1 | 4 | 3.805 | 4.253 | 3.113 | 0.1621 |  |  |
| hated | שְׂנוּאָה / שְׂנֵאתֶם / וַתְּשַׁלְּחוּנִי | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| concubine | פִּילֶגֶשׁ / בִּשְׁכֹּן / פ | 3 | 0 | 1 | 4 | 3.805 | 4.253 | 3.113 | 0.1621 |  |  |
| beautiful | יֶפֶת / מִצְרַיְמָה / מַרְאֶה | 3 | 0 | 1 | 4 | 3.805 | 4.253 | 3.113 | 0.1621 |  |  |
| consoled | וַיִּנָּחֶם | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| recognized | וַיַּכֵּר / וַיַּכִּירָהּ / הִכִּרֻהוּ׃ | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| door | הַדֶּלֶת | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| noah | נֹחַ | 11 | 0 | 16 | 27 | 3.770 | 10.938 | 1.370 | 0.0043 | yes |  |
| himself | לְבַדּוֹ / לוֹ | 10 | 9 | 5 | 24 | 3.658 | 9.882 | 1.425 | 0.0082 | yes |  |
| jacob's | יַעֲקֹב | 10 | 5 | 9 | 24 | 3.658 | 4.053 | 1.425 | 0.1796 |  |  |
| sun | הַשֶּׁמֶשׁ | 5 | 2 | 2 | 9 | 3.634 | 4.341 | 2.181 | 0.1546 |  |  |
| speckled | עֲקֻדִּים / נְקֻדִּים | 5 | 4 | 0 | 9 | 3.634 | 11.256 | 2.181 | 0.0037 | yes |  |
| themselves | לָהֶם / לְבָד | 9 | 8 | 4 | 21 | 3.561 | 9.576 | 1.495 | 0.0099 | yes |  |
| yourself | לְךָ / הִשָּׁמֶר / לְבַדֶּךָ׃ | 9 | 8 | 4 | 21 | 3.561 | 9.576 | 1.495 | 0.0099 | yes |  |
| wives | וּנְשֵׁי / לְנָשִׁים / נְשֵׁי | 12 | 4 | 15 | 31 | 3.517 | 3.752 | 1.250 | 0.2067 |  |  |
| sarah | שָׂרָה | 12 | 8 | 11 | 31 | 3.517 | 5.032 | 1.250 | 0.1287 |  |  |
| buy | לִשְׁבֹּר | 8 | 6 | 4 | 18 | 3.487 | 7.002 | 1.586 | 0.0433 | yes |  |
| milk | זָבַת / וּדְבָשׁ / חֵלֶב | 6 | 4 | 2 | 12 | 3.478 | 6.486 | 1.891 | 0.0553 |  |  |
| speaking | לְדַבֵּר / מִדְבַּר | 7 | 2 | 6 | 15 | 3.450 | 3.459 | 1.710 | 0.2494 |  |  |
| trip | דֶּרֶךְ / אֱלֹהֵינוּ | 4 | 3 | 0 | 7 | 3.078 | 8.794 | 2.254 | 0.0152 | yes |  |
| wadi | בְּנַחַל / מִשָּׁם / וַיִּקָּחֵם | 4 | 1 | 2 | 7 | 3.078 | 3.124 | 2.254 | 0.2897 |  |  |
| closed | סָגַר / וַיִּסְגֹּר / בַּעֲדוֹ | 4 | 2 | 1 | 7 | 3.078 | 4.582 | 2.254 | 0.1414 |  |  |
| perizzite | וְהַפְּרִזִּי | 4 | 3 | 0 | 7 | 3.078 | 8.794 | 2.254 | 0.0152 | yes |  |
| knelt | וַיִּקֹּד / וַיִּקְּדוּ | 4 | 3 | 0 | 7 | 3.078 | 8.794 | 2.254 | 0.0152 | yes |  |
| eating | לֶאֱכֹל / וְכִי / הַשֶּׁבֶר | 4 | 1 | 2 | 7 | 3.078 | 3.124 | 2.254 | 0.2897 |  |  |
| worked | עֲבַדְתִּיךָ / יָדַעְתָּ / הָעֶבֶד | 4 | 1 | 2 | 7 | 3.078 | 3.124 | 2.254 | 0.2897 |  |  |
| prison | הַסֹּהַר / בְּבֵית / אֲסוּרִים | 4 | 3 | 0 | 7 | 3.078 | 8.794 | 2.254 | 0.0152 | yes |  |
| fact | וְאוּלָם | 4 | 3 | 0 | 7 | 3.078 | 8.794 | 2.254 | 0.0152 | yes |  |
| hate | וַיּוֹסִפוּ / שְׂנֹא / וַיַּחֲלֹם | 4 | 1 | 2 | 7 | 3.078 | 3.124 | 2.254 | 0.2897 |  |  |
| skies | הַשָּׁמַיִם | 16 | 12 | 19 | 47 | 2.956 | 4.483 | 0.958 | 0.1414 |  |  |
| killed | וַיַּהַרְגוּ / הָרַגְתִּי / אֹתָם | 7 | 4 | 5 | 16 | 2.927 | 3.869 | 1.550 | 0.1913 |  |  |
| isaac's | יִצְחָק | 5 | 3 | 2 | 10 | 2.898 | 4.656 | 1.891 | 0.1414 |  |  |
| toward | פְּנֵי / אֶל / לִקְרָאתָם | 12 | 7 | 14 | 33 | 2.849 | 3.175 | 1.109 | 0.2834 |  |  |
| seed | זֶרַע / זַרְעֲךָ / וּלְזַרְעֲךָ | 30 | 17 | 55 | 102 | 2.711 | 2.970 | 0.642 | 0.3182 |  |  |
| finished | וַיְכַל / כִּלָּה | 8 | 3 | 9 | 20 | 2.596 | 2.609 | 1.335 | 0.3223 |  |  |
| nurse | וַתֹּאמֶר / מֵנִקְתָּהּ / אֲנָשָׁיו׃ | 3 | 2 | 0 | 5 | 2.540 | 6.351 | 2.376 | 0.0586 |  |  |
| scattered | וַיָּפֶץ / וַיִּשְׂרֹף / וַיִּטְחַן | 3 | 2 | 0 | 5 | 2.540 | 6.351 | 2.376 | 0.0586 |  |  |
| benjamin's | בִנְיָמִן | 3 | 0 | 2 | 5 | 2.540 | 3.436 | 2.376 | 0.2510 |  |  |
| havilah | וַיִּשְׁכְּנוּ / מֵחֲוִילָה / אַשּׁוּרָה | 3 | 0 | 2 | 5 | 2.540 | 3.436 | 2.376 | 0.2510 |  |  |
| multiplied | וַיִּרְבּוּ | 3 | 0 | 2 | 5 | 2.540 | 3.436 | 2.376 | 0.2510 |  |  |
| allow | לַהֲלֹךְ / יִתֵּן / בִּגְבֻלוֹ | 3 | 2 | 0 | 5 | 2.540 | 6.351 | 2.376 | 0.0586 |  |  |
| prepare | וְהָכֵן | 3 | 2 | 0 | 5 | 2.540 | 6.351 | 2.376 | 0.0586 |  |  |
| daughter-in-law | כַּלָּתוֹ | 3 | 0 | 2 | 5 | 2.540 | 3.436 | 2.376 | 0.2510 |  |  |
| ham | חָם / וְחָם | 3 | 0 | 2 | 5 | 2.540 | 3.436 | 2.376 | 0.2510 |  |  |
| feast | מִשְׁתֶּה | 3 | 2 | 0 | 5 | 2.540 | 6.351 | 2.376 | 0.0586 |  |  |
| heshbon | בְּחֶשְׁבּוֹן / אַרְצוֹ | 3 | 0 | 2 | 5 | 2.540 | 3.436 | 2.376 | 0.2510 |  |  |
| sending | מְשַׁלֵּחַ / שָׁלַח / וְנִשְׁבְּרָה | 3 | 2 | 0 | 5 | 2.540 | 6.351 | 2.376 | 0.0586 |  |  |
| fought | וַיִּלָּחֶם / וְהוּא / בְּיִשְׂרָאֵל | 3 | 1 | 1 | 5 | 2.540 | 2.893 | 2.376 | 0.3223 |  |  |
| left | וְהַנּוֹתָר / נִשְׁאַר | 21 | 16 | 31 | 68 | 2.486 | 3.374 | 0.748 | 0.2612 |  |  |
| leah | לֵאָה | 7 | 6 | 4 | 17 | 2.475 | 5.990 | 1.406 | 0.0729 |  |  |
| powerful | וְעָצוּם | 4 | 3 | 1 | 8 | 2.319 | 5.238 | 1.891 | 0.1131 |  |  |
| h | מֵעוֹלָם / הָ / הַשֵּׁם | 4 | 0 | 4 | 8 | 2.319 | 4.111 | 1.891 | 0.1783 |  | ⚠ |
| wagons | הָעֲגָלוֹת / הָעֲגָלֹת / עֲגָלוֹת | 4 | 0 | 4 | 8 | 2.319 | 4.111 | 1.891 | 0.1783 |  |  |
| stay | שְׁבוּ / יַעַל / יֹשֵׁב | 5 | 3 | 3 | 11 | 2.309 | 3.369 | 1.650 | 0.2619 |  |  |
| whatever | וַאֲשֶׁר / תֹּאמְרוּ / הַנֹּגַעַת | 5 | 3 | 3 | 11 | 2.309 | 3.369 | 1.650 | 0.2619 |  |  |
| cursed | אָרוּר / הַמְקַלֵּל | 5 | 2 | 4 | 11 | 2.309 | 2.402 | 1.650 | 0.3223 |  |  |
| ad | — | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| childed | עֲצָרַנִי / אִבָּנֶה / מִמֶּנָּה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| bered | לַבְּאֵר / בָּרָד / לַחַי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| grows | שְׁבִי / יִגְדַּל / כְּאֶחָיו | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| note | שָׁמַר / וַיְקַנְאוּ / וְאָבִיו | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| worker | וְקַיִן / וַתֹּסֶף / אֲדָמָה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| gihon | גִּיחוֹן / הַסּוֹבֵב / כּוּשׁ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| based | כָּרַתִּי / פִּי / אִתְּךָ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| bowing | וְהַיָּרֵחַ / כּוֹכָבִים / מִשְׁתַּחֲוִים | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| forgets | וְשָׁכַח / וּלְקַחְתִּיךָ / שְׁנֵיכֶם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| loving | כְּיָמִים / בְּאַהֲבָתוֹ / אֲחָדִים | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| crouches | תֵּיטִיב / וְאֵלֶיךָ / תְּשׁוּקָתוֹ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| peleth | וְאוֹן / פֶּלֶת / וְדָתָן | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| droves | וְהַכְּשָׂבִים / הִפְרִיד / עָקֹד | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| gum | מִזִּמְרַת / בִּכְלֵיכֶם / צֳרִי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| sad | תֵּעָצְבוּ / לְמִחְיָה / בְּעֵינֵיכֶם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| exert | הַשְּׁמֵנָה / רָזָה / וְהִתְחַזַּקְתֶּם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| bozrah | מִבּצְרָה׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| jerah | וְיקְטָן / אַלְמוֹדָד / שָׁלֶף | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| revolving | לְגַן / לַהַט / הַחֶרֶב | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| sinite | הַעַרְקִי / הַסִּינִי׃ / וְאֶת | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| rehovoth-ir | אַשּׁוּר / רְחֹבֹת / עִיר | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| desired | בְּבַת / נִכְבָּד / חָפֵץ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| uzal | הֲדוֹרָם / אוּזָל / דִּקְלָה׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| shadow | אוֹצִיאָה / כַּטּוֹב / לָאֲנָשִׁים | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| overturn | הפְכִּי / נָשָׂאתִי / לְבִלְתִּי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| besides | הֲבִיאֹתָנוּ / וָכָרֶם / הַעֵינֵי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| former | בְּמֶלֶךְ / מִיָּדָו / הָרִאשׁוֹן | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| magnitude | סְלַח / לַעֲוֺן / כְּגֹדֶל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| diklah | הֲדוֹרָם / אוּזָל / דִּקְלָה׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| rules | מֹשֵׁל / וַיָּפג / הֶאֱמִין | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| satisfy | וְאֶקְחָה / פַת / וְסַעֲדוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| precious | וּבְגָדִים / וּמִגְדָּנֹת / לְאָחִיהָ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| lahai | לַבְּאֵר / בָּרָד / לַחַי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| shield | בַּמַּחֲזֶה / מִגַּן / שְׂכָרְךָ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| attraction | וְנֶחְמָד / לְהַשְׂכִּיל / מִפִּרְיוֹ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| farthest | יִשְׁכָּבוּ / נָסַבּוּ / מִנַּעַר | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| cause | מִבְּנֹתָיו / לְבָנֶיךָ / וְהִזְנוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| plane | מַקַּל / לַח / וְלוּז | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| reward | בַּמַּחֲזֶה / מִגַּן / שְׂכָרְךָ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| deeds | נִפְלָאֹת / נִבְרְאוּ / נֶגֶד | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| roi | לַבְּאֵר / בָּרָד / לַחַי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| el-roi | הֲגַם / רֹאִי׃ / הֲלֹם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| exercising | יֶשְׁכֶם / הַגִּידוּ / וְאֶפְנֶה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| naharaim | מִגְּמַלֵּי / נַהֲרַיִם / גְמַלִּים | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| quiver | כֵלֶיךָ / תֶּלְיְךָ / וְקַשְׁתֶּךָ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| emptied | וַתְּעַר / הַשֹּׁקֶת / גְּמַלָּיו׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| exist | וַיִּתְרֹצְצוּ / הַבָּנִים / בְּקִרְבָּהּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| widespread | וָאָרְדְּ׃ / לְהַצִּילוֹ / וּלְהַעֲלֹתוֹ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| peni-el | פְּנִיאֵל / וַתִּנָּצֵל / נַפְשִׁי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| accad | מַמְלַכְתּוֹ / וְאֶרֶךְ / וְאַכַּד | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| brother-in-law | לְאוֹנָן / וְיַבֵּם / וְהָקֵם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| salvation | הִתְיַצְּבוּ / יְשׁוּעַת / לִרְאֹתָם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| almodad | וְיקְטָן / אַלְמוֹדָד / שָׁלֶף | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| heedlessly | וַיַּעְפִּלוּ / מָשׁוּ / לַעֲלוֹת | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| precluded | וְשָׂפָה / הַחִלָּם / יִבָּצֵר | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| daily | אֲנַסֶּנּוּ / הֲיֵלֵךְ / בְּתוֹרָתִי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| hamathite | הָאַרְוָדִי / הַצְּמָרִי / הַחֲמָתִי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| blindness | הִכּוּ / בַּסַּנְוֵרִים / מִקָּטֹן | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| cold | וְקֹר / וְקַיִץ / וָחֹרֶף | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| he'd | לַעֲזֹב / וְעָזַב / יוּכַל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| sons-in-law's | חֲתָנָיו / לֹקְחֵי / מַשְׁחִית | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| unloaded | וּמִסְפּוֹא / וְרַגְלֵי / לִרְחֹץ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| sheleph | וְיקְטָן / אַלְמוֹדָד / שָׁלֶף | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| rib | הַצֵּלָע / וַיְבִאֶהָ / לְאִשָּׁה׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| ten-thousands | הֲיִי / שֹׂנְאָיו׃ / וְיִירַשׁ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| feebler | וּבְהַעֲטִיף / הָעֲטֻפִים / וְהַקְּשֻׁרִים | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| followed | וַתִּרְכַּבְנָה / וַתֵּלַכְנָה / וְנַעֲרֹתֶיהָ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| forger | תּוּבַל / לֹטֵשׁ / וּבַרְזֶל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| embalming | יִמְלְאוּ / הַחֲנֻטִים / וַיִּמְלְאוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| pains | עֳנִי / נֹגְשָׂיו / מַכְאֹבָיו׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| idea | מִתְנַחֵם / לְהרְגֶךָ׃ / וַתִּשְׁלַח | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| soon | וַיִּשְׂטֹם / וְאַהַרְגָה / יִקְרְבוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| ben-ammi | וְהַצְּעִירָה / עַמִּי / וַתִּקְרָא | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| clings | יַעֲזב / וְדָבַק / בְּאִשְׁתּוֹ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| fittest | הַמְקֻשָּׁרוֹת / לְיַחְמֵנָּה / בַּמַּקְלוֹת׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| breadth | וְיִסְחֲרוּ / יָדַיִם / בְּנֹתָם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| sphinxes | לְגַן / לַהַט / הַחֶרֶב | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| mesha | מוֹשָׁבָם / מִמֵּשָׁא / סְפָרָה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| eber's | וּלְשֵׁם / הַגָּדוֹל / עֵבֶר | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| feeble | וּבְהַעֲטִיף / הָעֲטֻפִים / וְהַקְּשֻׁרִים | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| girl's | וַתִּדְבַּק / בְּדִינָה / נַפְשׁוֹ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| cattleman | יָבָל / וּמִקְנֶה / יֹשֵׁב | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| console | לְנַחֲמוֹ / לְהִתְנַחֵם / אֵרֵד | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| poplar | מַקַּל / לַח / וְלוּז | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| girgashites | הַגִּרְגָּשִׁי׃ / הַיְבוּסִי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| stiff-necked | וְסָלַחְתָּ / לַעֲוֺנֵנוּ / וּלְחַטָּאתֵנוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| matred | הֲדַר / פָּעוּ / מְהֵיטַבְאֵל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| ruler | שְׁלַחְתֶּם / וַיְשִׂימֵנִי / וּלְאָדוֹן | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| whenever | הַמְקֻשָּׁרוֹת / לְיַחְמֵנָּה / בַּמַּקְלוֹת׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| blowing | יָרֹה / יִיָּרֶה / בִּמְשֹׁךְ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| numb | מֹשֵׁל / וַיָּפג / הֶאֱמִין | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| regular | וְהֵכִינוּ / יִלְקְטוּ / יָבִיאוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| moon | וְהַיָּרֵחַ / כּוֹכָבִים / מִשְׁתַּחֲוִים | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| worse | גֶּשׁ / שָׁפוֹט / נָרַע | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| in-sides | יִירָשְׁךָ / מִמֵּעֶיךָ / הוּא | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| tubal-cain's | תּוּבַל / לֹטֵשׁ / וּבַרְזֶל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| iram | מַגְדִּיאֵל / לְמֹשְׁבֹתָם / עִירָם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| pipe | תֹּפֵשׂ / כִּנּוֹר / וְעוּגָב | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| dislocated | וַיִּגַּע / וַתֵּקַע / בְּהֵאָבְקוֹ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| she'd | הַמַּטְעַמִּים / עָשָׂתָה / וַתִּתֵּן | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| naphtuhim | לוּדִים / עֲנָמִים / לְהָבִים | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| preserve | תֵּעָצְבוּ / לְמִחְיָה / בְּעֵינֵיכֶם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| longs | חָשְׁקָה / בְּבִתְּכֶם / תְּנוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| consoles | מִתְנַחֵם / לְהרְגֶךָ׃ / וַתִּשְׁלַח | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| event | כְּמוֹת / יְמֻתוּן / וּפְקֻדַּת | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| merciful | רַחוּם / וְחַנּוּן / וַיַּעֲבֹר | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| country | וְהָעַי / הָהָרָה / מַיִם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| survive | וְהִכָּהוּ / הַנִּשְׁאָר / לִפְלֵיטָה׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| boiling | נִכְמְרוּ / רַחֲמָיו / לִבְכּוֹת | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| tent-dweller | יָבָל / וּמִקְנֶה / יֹשֵׁב | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| sweat | בְּזֵעַת / אַפֶּיךָ / שׁוּבְךָ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| pinon | פִּינֹן׃ / אֵלֶּה / אַלּוּף | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| hobab | לְחֹבָב / הַמִּדְיָנִי / נֹסְעִים | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| visibly | מְקֹמָהּ / הַקְּדֵשָׁה / בָעֵינַיִם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| circumcisions | וַיִּרֶף / לַמּוּלֹת׃ / אָמְרָה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| bulrushes | הַצְּפִינוֹ / גֹּמֶא / וַתַּחְמְרָה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| tossed | לְאֵיתָנוֹ / נָסִים / וַיְנַעֵר | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| joker | חֲתָנָיו / לֹקְחֵי / מַשְׁחִית | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| masrekah | מִמַּשְׂרֵקָה׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| succeed | תִצְלָח׃ / עֹבְרִים / וְהוּא | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| granted | הפְכִּי / נָשָׂאתִי / לְבִלְתִּי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| chezib | בִכְזִיב / וַתֹּסֶף / בְּלִדְתָּהּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| promised | יְדַעְתִּיו / צְדָקָה׃ / הֵבִיא | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| wondrous | צָחֲקָה / אֻמְנָם / אֵלֵד | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| building | לִבְנֹת / וַיַּחְדְּלוּ / מִשָּׁם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| sitnah | שִׂטְנָה׃ / אַחֶרֶת / וַיָּרִיבוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| ashamed | עֲרוּמִּים / יִתְבֹּשָׁשׁוּ / וְאִשְׁתּוֹ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| threshold | תֵּיטִיב / וְאֵלֶיךָ / תְּשׁוּקָתוֹ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| perizzites | הַפְּרִזִּי / הָרֹפְאִים / הַחִתִּי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| proceeded | בִכְזִיב / וַתֹּסֶף / בְּלִדְתָּהּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| jubal | תֹּפֵשׂ / כִּנּוֹר / וְעוּגָב | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| kad-monites | הַקֵּינִי / הַקְּנִזִּי / הַקַּדְמֹנִי׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| tend | אֶרְעֶה / אָשׁוּבָה / צֹאנְךָ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| lit | וְהַחֹשֶׁךְ / וַיָּאֶר / קָרַב | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| considered | וְהֶאֱמִן / וַיַּחְשְׁבֶהָ / צְדָקָה׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| shepherdess | עַמָּם׃ / רָעָה / בָּאָה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| figs | זְמוֹרָה / וְאֶשְׁכּוֹל / וַיִּשָּׂאֻהוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| rehovot | רְחֹבוֹת / הִרְחִיב / וּפָרִינוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| warned | הַעֵדֹתָה / וְקִדַּשְׁתּוֹ׃ / לַעֲלֹת | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| rule | תִּמְלֹךְ / מָשׁוֹל / דְּבָרָיו׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| eye-to-eye | בְּעַיִן / וַעֲנָנְךָ / וּבְעַמֻּד | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| erech | מַמְלַכְתּוֹ / וְאֶרֶךְ / וְאַכַּד | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| watchman | אֵי / הִשָּׁמֶר / אָנֹכִי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| meditate | לָשׂוּחַ / בָּאִים / לִפְנוֹת | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| calneh | מַמְלַכְתּוֹ / וְאֶרֶךְ / וְאַכַּד | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| milcah's | לְנָחוֹר / מִלְכָּה / יָלְדָה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| tricked | הִשִּׁיאַנִי / לְאִשָּׁה׃ / וַתֹּאמֶר | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| fter | — | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| sinful | וְחַטָּאִים / רָעִים / וְאַנְשֵׁי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| migdal-eder | מֵהָלְאָה / לְמִגְדַּל / עֵדֶר | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| alvah | לִמְקֹמֹתָם / עַלְוָה / יְתֵת׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| knead | מַהֲרִי / סְאִים / לוּשִׁי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| removing | הָסֵר / וְנָקֹד / אֶעֱבֹר | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| damascus | עֲרִירִי / מֶשֶׁק / דַּמֶּשֶׂק | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| abimael | עוֹבָל / אֲבִימָאֵל / וְאֶת | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| he-goat | וַיִּשְׁחֲטוּ / וַיִּטְבְּלוּ / עִזִּים | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| pistachios | מִזִּמְרַת / בִּכְלֵיכֶם / צֳרִי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| arms | — | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| desirable | וְנֶחְמָד / לְהַשְׂכִּיל / מִפִּרְיוֹ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| sheepshearers | גֹּזְזֵי / וְחִירָה / וַיִּרְבּוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| everywhere | וּשְׁמַרְתִּיךָ / וַהֲשִׁבֹתִיךָ / אֶעֱזבְךָ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| sackcloth | בְּמתְנָיו / וַיִּתְאַבֵּל / שִׂמְלֹתָיו | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| mehetabel | הֲדַר / פָּעוּ / מְהֵיטַבְאֵל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| kush | גִּיחוֹן / הַסּוֹבֵב / כּוּשׁ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| load | טַעֲנוּ / בְּעִירְכֶם / עֵשָׂו | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| envied | וַעֲבֻדָּה / וַיְקַנְאוּ / רַבָּה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| removed | הַתְּיָשִׁים / הָעֲקֻדִּים / וְהַטְּלֻאִים | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| summer | וְקֹר / וְקַיִץ / וָחֹרֶף | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| erom | וַתִּפָּקַחְנָה / עֵירֻמִּם / וַיִּתְפְּרוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| jetheth | לִמְקֹמֹתָם / עַלְוָה / יְתֵת׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| dirt | הַבְּאֵרֹת / סִתְּמוּם / וַיְמַלְאוּם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| expand | וּפָרַצְתָּ / וְצָפֹנָה / וּבְזַרְעֶךָ׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| dinhabah | בֶּאֱדוֹם / דִּנְהָבָה׃ / עִירוֹ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| nd | מֵעוֹלָם / הָ / הַשֵּׁם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| everyone's | פֶּרֶא / יִשְׁכֹּן׃ / וְיַד | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| breathing | בֶּחָרָבָה / מֵתוּ׃ / מִכּל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| egyptian's | הִפְקִיד / בְּבֵיתוֹ / בִּגְלַל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| bathe | הַסּוּף / אֲמָתָהּ / וַתִּקָּחֶהָ׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| approach | יִתְקַדָּשׁוּ / הַנֹּגְשִׂים / בָּהֶם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| rehoboth | מֵרְחֹבוֹת | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| room | נִכְמְרוּ / רַחֲמָיו / לִבְכּוֹת | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| hurting | כֹּאֲבִים / בֶּטַח / דִּינָה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| potency | תֵּת / כֹּחָהּ / תַעֲבֹד | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| elder | הַמֹּשֵׁל / זָקֵן / עַבְדּוֹ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| drinks | יִשְׁתֶּה / הֲרֵעֹתֶם / נַחֵשׁ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| hat | מֵעוֹלָם / הָ / הַשֵּׁם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| harvested | וַיִּזְרַע / וַיִּמְצָא / שְׂעֹרִים | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| thorn | וְקוֹץ / וְדַרְדַּר / תַּצְמִיחַ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| magnified | וַתַּגְדֵּל / לְהִמָּלֵט / תִּדְבָּקַנִי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| beth | וַיִּקְבֹּר / בַגַּי / קְבֻרָתוֹ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| confirmed | וְיֵאָמְנוּ / תָּבִיאוּ / דִּבְרֵיכֶם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| praised | וַיְהַלְלוּ / וַתִּקַּח / שָׂרֵי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| penuel | וַיִּזְרַח / פְּנוּאֵל / צֶלַע | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| enlarge | לְיֶפֶת / בְּאהֳלֵי / וַיִּשְׁכֹּן | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| divines | יִשְׁתֶּה / הֲרֵעֹתֶם / נַחֵשׁ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| whored | כְּמִשְׁלֹשׁ / זָנְתָה / לִזְנוּנִים | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| handsome | וִיפֵה / יָפָה / אוּכַל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| praise | אוֹדֶה / קָרְאָה / וַתַּעֲמֹד | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| trough | וַתְּעַר / הַשֹּׁקֶת / גְּמַלָּיו׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| pits | וְנַהַרְגֵהוּ / וְנַשְׁלִכֵהוּ / הַבֹּרוֹת | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| run | כִּרְאוֹתָהּ / עָזַב / בְּיָדָהּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| pained | כְּשׁמְעָם / וַיִּתְעַצְּבוּ / נְבֵלָה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| nearly | כִּמְעַט / וְהֵבֵאתָ / עָלֵינוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| additional | הוֹרַדְנוּ / אַחַר / שָׁם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| clever | — | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| winter | וְקֹר / וְקַיִץ / וָחֹרֶף | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| garden's | מִתְהַלֵּךְ / לְרוּחַ / וַיִּתְחַבֵּא | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| couple | לְאוֹנָן / וְיַבֵּם / וְהָקֵם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| lasha | מִצִּידֹן / וְאַדְמָה / וּצְבֹיִם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| furious | כְּשׁמְעָם / וַיִּתְעַצְּבוּ / נְבֵלָה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| hadoram | הֲדוֹרָם / אוּזָל / דִּקְלָה׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| tangled | הִתְעַשְּׂקוּ / עֵשֶׂק / וַיָּרִיבוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| biggest | הִכּוּ / בַּסַּנְוֵרִים / מִקָּטֹן | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| adm | — | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| finishing | וַתִּבָּקַע / תַּחְתֵּיהֶם׃ / כְּכַלֹּתוֹ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| jabal | יָבָל / וּמִקְנֶה / יֹשֵׁב | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| babble | וְנָבְלָה / שְׂפָתָם / יִשְׁמְעוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| wearied | הִכּוּ / בַּסַּנְוֵרִים / מִקָּטֹן | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| implement | תּוּבַל / לֹטֵשׁ / וּבַרְזֶל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| flint | וַתִּכְרֹת / ערְלַת / וַתַּגַּע | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| divine | הַמַּעֲשֶׂה / יְנַחֵשׁ / עֲשִׂיתִם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| gaza | מִצִּידֹן / וְאַדְמָה / וּצְבֹיִם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| admh | — | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| resen | רֶסֶן / הַגְּדֹלָה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| hittites | הַפְּרִזִּי / הָרֹפְאִים / הַחִתִּי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| follows | כְּזֹאת / נֹשְׂאֹת / וּמָזוֹן | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| mibzar | מִבְצָר׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| balm | מִזִּמְרַת / בִּכְלֵיכֶם / צֳרִי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| knowing | אֲכלְכֶם / וְנִפְקְחוּ / כֵּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| affront | וַאֲבָרְכָה / מְבָרְכֶיךָ / וּמְקַלֶּלְךָ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| gh | — | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  | ⚠ |
| past | מֵהָלְאָה / לְמִגְדַּל / עֵדֶר | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| avith | עֲוִית׃ / בְּדַד / עִירוֹ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| embalm | הָרֹפְאִים / לַחֲנֹט / וַיְצַו | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| hostility | פֶּרֶא / יִשְׁכֹּן׃ / וְיַד | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| peaceable | וְיִסְחֲרוּ / יָדַיִם / בְּנֹתָם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| phicol | מִגְּרָר / וַאֲחֻזַּת / מֵרֵעֵהוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| kills | הַכּוֹת / מֹצְאוֹ / הֹרֵג | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| esek | הִתְעַשְּׂקוּ / עֵשֶׂק / וַיָּרִיבוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| certified | הָעֵד / בְּנוֹ / בִּלְתִּי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| cainites | הַקֵּינִי / הַקְּנִזִּי / הַקַּדְמֹנִי׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| warn | הָעֵד / בָּעָם / מִמֶּנּוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| disdained | וּנְזִיד / עֲדָשִׁים / וַיִּבֶז | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| vitality | בְּמֹתוֹ / כָהֲתָה / לֵחֹה׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| member | יוֹרֵשׁ / נָתַתָּה / בֵּיתִי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| feelings | נִכְמְרוּ / רַחֲמָיו / לִבְכּוֹת | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| obal | עוֹבָל / אֲבִימָאֵל / וְאֶת | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| trickster | יְמֻשֵּׁנִי / כִּמְתַעְתֵּעַ / קְלָלָה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| overturned | וְצֶמַח / וַיַּהֲפֹךְ / הָאֵל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| men's | שְׂאֵת / יוּכְלוּן / וְשִׂים | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| caravan | אֹרְחַת / יִשְׁמְעֵאלִים / מִגִּלְעָד | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| taking | יוֹרֵשׁ / נָתַתָּה / בֵּיתִי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| she-goat | קְחָה / מְשֻׁלֶּשֶׁת / מְשֻׁלָּשׁ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| joktan's | אוֹפִר / חֲוִילָה / יקְטָן׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| married | חֲתָנָיו / לֹקְחֵי / מַשְׁחִית | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| kindnesses | קָטֹנְתִּי / הַחֲסָדִים / בְמַקְלִי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| arvadite | הָאַרְוָדִי / הַצְּמָרִי / הַחֲמָתִי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| rephaim | הַפְּרִזִּי / הָרֹפְאִים / הַחִתִּי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| carve | פְּסל / לְךָ / אֲבָנִים | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| finest | הַחֲמֻדֹת / וַתַּלְבֵּשׁ / וַתִּקַּח | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| violating | תִצְלָח׃ / עֹבְרִים / וְהוּא | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| arad | עֲרָד / הָאֲתָרִים / שְׁבִי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| leaders | וְהוֹקַע / רָאשֵׁי / מִיִּשְׂרָאֵל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| servant's | וְלִינוּ / וְהִשְׁכַּמְתֶּם / לְדַרְכְּכֶם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| sodom's | אַפַּיִם / בְּשַׁעַר / לִקְרָאתָם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| nonetheless | בְּצֻרוֹת / גְּדֹלֹת / יְלָדַי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| stripes | מַקַּל / לַח / וְלוּז | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| magdiel | מַגְדִּיאֵל / לְמֹשְׁבֹתָם / עִירָם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| builder | כְּשֵׁם / חֲנוֹךְ / וְ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| quieted | וַיַּהַס / וְיָרַשְׁנוּ / יָכוֹל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| attracted | וַתִּקְרֶאןָ / לְזִבְחֵי / לֵאלֹהֵיהֶן׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| curds | חֶמְאָה / וְחֵלֶב / וּבֶן | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| pau | הֲדַר / פָּעוּ / מְהֵיטַבְאֵל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| covet | אוֹרִישׁ / וְהִרְחַבְתִּי / יַחְמֹד | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| shot | יָרֹה / יִיָּרֶה / בִּמְשֹׁךְ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| advance | לְהוֹרֹת / גֹּשְׁנָה / אַרְצָה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| asherahs | מִזְבְּחֹתָם / תִּתֹּצוּן / מַצֵּבֹתָם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| chariotry | בָּחוּר / וְשָׁלִשִׁם / רֶכֶב | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| dream-master | הַלָּזֶה / הַחֲלֹמוֹת / בַּעַל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| understand | וְנָבְלָה / שְׂפָתָם / יִשְׁמְעוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| retrieved | הָעַיִט / הַפְּגָרִים / וַיֵּשֶׁב | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| casluhim | פַּתְרֻסִים / כַּסְלֻחִים / כַּפְתֹּרִים׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| girls | הַסּוּף / אֲמָתָהּ / וַתִּקָּחֶהָ׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| deceived | רִמִּיתָנִי׃ / עָבַדְתִּי / בְּרָחֵל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| prevailed | לְנֹכַח / לַיהֹוָה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| pathrusim | פַּתְרֻסִים / כַּסְלֻחִים / כַּפְתֹּרִים׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| heroes | מֵעוֹלָם / הָ / הַשֵּׁם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| simple | וַיִּגְדְּלוּ / אֹהָלִים׃ / תֹּם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| respected | בְּבַת / נִכְבָּד / חָפֵץ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| actually | מִשְּׁנָתוֹ / אָכֵן / יֶשׁ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| trembling | חֲרָדָה / הַצָּד / וָאֲבָרְכֵהוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| brimstone | גּפְרִית / וַיהֹוָה / וְאֵשׁ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| noses | הַשַּׁלִּיט / הַמַּשְׁבִּיר / אַפַּיִם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| elah | פִּינֹן׃ / אֵלֶּה / אַלּוּף | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| almonds | מִזִּמְרַת / בִּכְלֵיכֶם / צֳרִי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| righteousness | יְדַעְתִּיו / צְדָקָה׃ / הֵבִיא | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| lords | וְלִינוּ / וְהִשְׁכַּמְתֶּם / לְדַרְכְּכֶם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| you'd | וְשֹׁפֵט / הַלְהרְגֵנִי / הָרַגְתָּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| continually | וָשׁוֹב / הָלוֹךְ / מֵעַל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| babbled | בָּלַל / הֱפִיצָם / בָּבֶל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| babel | מַמְלַכְתּוֹ / וְאֶרֶךְ / וְאַכַּד | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| endowed | שַׂמְתִּיו / סְמַכְתִּיו / וּלְכָה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| pleasure | וַתִּצְחַק / עֶדְנָה / וַאדֹנִי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| proverbially | הַמֹּשְׁלִים / יֹאמְרוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| faced | הַשִּׂמְלָה / אֲחֹרַנִּית / וּפְנֵיהֶם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| impoverished | וְכִלְכַּלְתִּי / תִּוָּרֵשׁ / וּבֵיתְךָ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| afterward | וְאֶקְחָה / פַת / וְסַעֲדוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| annoyed | וַיִּגְעַר / חָלָמְתָּ / הֲבוֹא | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| dominion | תָּרִיד / וּפָרַקְתָּ / צַוָּארֶךָ׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| earth's | וְקֹר / וְקַיִץ / וָחֹרֶף | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| amazed | כִּבְכֹרָתוֹ / וְהַצָּעִיר / כִּצְעִרָתוֹ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| anamim | לוּדִים / עֲנָמִים / לְהָבִים | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| driving | מְצַוְּךָ / שָׁמַר / גָּרֵשׁ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| babylon | בָּלַל / הֱפִיצָם / בָּבֶל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| edrei | אֶדְרֶעִי׃ / לִקְרָאתָם / עִמּוֹ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| different | וְעַבְדִּי / וַהֲבִיאֹתִיו / יוֹרִשֶׁנָּה׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| grasshoppers | הַנְּפִילִים / עֲנָק / וַנְּהִי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| despoil | וְשָׁאֲלָה / מִשְּׁכֶנְתָּהּ / וּמִגָּרַת | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| regret | בָּרָאתִי / נִחַמְתִּי / עֲשִׂיתִם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| thistle | וְקוֹץ / וְדַרְדַּר / תַּצְמִיחַ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| city-take | חֹתֵן / בָּעִיר / פֶּה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| faltering | וַיִּזְרַח / פְּנוּאֵל / צֶלַע | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| tubal-cain | תּוּבַל / לֹטֵשׁ / וּבַרְזֶל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| divined | נִחַשְׁתִּי / וַיְבָרְכֵנִי / בִּגְלָלֵךְ׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| sephar | מוֹשָׁבָם / מִמֵּשָׁא / סְפָרָה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| hundredfold | וַיִּזְרַע / וַיִּמְצָא / שְׂעֹרִים | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| caphtorim | פַּתְרֻסִים / כַּסְלֻחִים / כַּפְתֹּרִים׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| tigris | חִדֶּקֶל / וְהַנָּהָר / אַשּׁוּר | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| direct | לְהוֹרֹת / גֹּשְׁנָה / אַרְצָה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| hunted | חֲרָדָה / הַצָּד / וָאֲבָרְכֵהוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| raining | אֲנַסֶּנּוּ / הֲיֵלֵךְ / בְּתוֹרָתִי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| suffer | שׁוּבִי / גְּבִרְתֵּךְ / וְהִתְעַנִּי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| hazarmaveth | וְיקְטָן / אַלְמוֹדָד / שָׁלֶף | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| lentil | וּנְזִיד / עֲדָשִׁים / וַיִּבֶז | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| news | וַיְבִיאֵהוּ / כִשְׁמֹעַ / לְלָבָן | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| supply | כְּזֹאת / נֹשְׂאֹת / וּמָזוֹן | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| ahuzat | מִגְּרָר / וַאֲחֻזַּת / מֵרֵעֵהוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| grieved | וַיִּתְעַצֵּב / וַיִּנָּחֶם / בְּאֶרֶץ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| finding | הִכּוּ / בַּסַּנְוֵרִים / מִקָּטֹן | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| occupation | מַּעֲשֵׂיכֶם׃ / וָאֹמַר / יִקָּרֵא | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| spy | וַיִּלְכְּדוּ / לְרֶגֶל / וְיִירַשׁ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| almond | מַקַּל / לַח / וְלוּז | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| lehabim | לוּדִים / עֲנָמִים / לְהָבִים | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| beasts | טַעֲנוּ / בְּעִירְכֶם / עֵשָׂו | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| mated | וַיֶּחֱמוּ / וַתֵּלַדְןָ / וּטְלֻאִים׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| exposing | מַקַּל / לַח / וְלוּז | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| surviving | וַיִּשְׁלָחֵנִי / שְׁאֵרִית / וּלְהַחֲיוֹת | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| content | וַיּוֹאֶל / לְמֹשֶׁה / בִתּוֹ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| copulated | וַיַּצֵּג / פִּצֵּל / בְּשִׁקְתוֹת | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| player | תֹּפֵשׂ / כִּנּוֹר / וְעוּגָב | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| watering | וַיַּצֵּג / פִּצֵּל / בְּשִׁקְתוֹת | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| naamah | תּוּבַל / לֹטֵשׁ / וּבַרְזֶל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| ration | אֲנַסֶּנּוּ / הֲיֵלֵךְ / בְּתוֹרָתִי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| regretted | וַיִּתְעַצֵּב / וַיִּנָּחֶם / בְּאֶרֶץ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| heifer | קְחָה / מְשֻׁלֶּשֶׁת / מְשֻׁלָּשׁ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| uphold | גּוּר / וַהֲקִמֹתִי / וְאֶהְיֶה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| really | וַיַּעְקְבֵנִי / בְּכֹרָתִי / אָצַלְתָּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| shittim | בַּשִּׁטִּים / לִזְנוֹת / וַיָּחֶל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| widened | רְחֹבוֹת / הִרְחִיב / וּפָרִינוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| pomegranates | הָרִמֹּנִים / וַיַּעֲשׂוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| dawn's | וַיֵּאָבֵק / הַשַּׁחַר / עֹלוֹת | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| arise | קוּמָה / וְיָפֻצוּ / מְשַׂנְאֶיךָ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| jahaz | יָהְצָה / לִקְרַאת / הַמִּדְבָּרָה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| admah | מִצִּידֹן / וְאַדְמָה / וּצְבֹיִם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| wrestled | וַיֵּאָבֵק / הַשַּׁחַר / עֹלוֹת | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| clung | וַתִּדְבַּק / בְּדִינָה / נַפְשׁוֹ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| fitter | וּבְהַעֲטִיף / הָעֲטֻפִים / וְהַקְּשֻׁרִים | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| wrestling | וַיִּגַּע / וַתֵּקַע / בְּהֵאָבְקוֹ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| bedad | עֲוִית׃ / בְּדַד / עִירוֹ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| zeboim | מִצִּידֹן / וְאַדְמָה / וּצְבֹיִם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| quarreling | רֹעֶיךָ / רֹעֵי / מְרִיבָה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| sweetened | וַיּוֹרֵהוּ / וַיִּמְתְּקוּ / וַיַּשְׁלֵךְ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| loincloths | וַתִּפָּקַחְנָה / עֵירֻמִּם / וַיִּתְפְּרוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| create | בְּרִיאָה / יִבְרָא / וּפָצְתָה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| silver's | הוּשַׁב / כַּסְפִּי / בְאַמְתַּחְתִּי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| ou | — | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| kenizzites | הַקֵּינִי / הַקְּנִזִּי / הַקַּדְמֹנִי׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| cord | חֹתָמְךָ / וּפְתִילֶךָ / וּמַטְּךָ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| measures | מַהֲרִי / סְאִים / לוּשִׁי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| dinah's | כֹּאֲבִים / בֶּטַח / דִּינָה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| there'll | וְעוֹד / חָרִישׁ / שְׁנָתַיִם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| temani | הַתֵּימָנִי׃ / מֵאֶרֶץ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| accused | כִּמְרַגְּלִים / וַיִּתֵּן / דַּבֵּר | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| practicing | יְדַעְתִּיו / צְדָקָה׃ / הֵבִיא | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| renown | מֵעוֹלָם / הָ / הַשֵּׁם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| ludim | לוּדִים / עֲנָמִים / לְהָבִים | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| gir-gashite | הַיְבוּסִי / הַגִּרְגָּשִׁי׃ / וְאֶת | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| moreh | מוֹרֶה / אָז / וַיַּעֲבֹר | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| stealthily | כֹּאֲבִים / בֶּטַח / דִּינָה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| seventy-seven | וְלֶמֶךְ / וְשִׁבְעָה / שִׁבְעִים | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| dwell | לְיֶפֶת / בְּאהֳלֵי / וַיִּשְׁכֹּן | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| mezahab | הֲדַר / פָּעוּ / מְהֵיטַבְאֵל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| usurped | וַיַּעְקְבֵנִי / בְּכֹרָתִי / אָצַלְתָּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| thoughts | רָעַת / מַחֲשָׁבֹת / רַבָּה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| marry | וְהִתְחַתְּנוּ / תִּקְחוּ / בְּנֹתֵינוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| profit | נַהֲרֹג / וְכִסִּינוּ / בֶּצַע | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| slier | וְהַנָּחָשׁ / עָרוּם / אַף | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| urged | וּכְמוֹ / וַיָּאִיצוּ / הַנִּמְצָאֹת | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| hill | וְהָעַי / הָהָרָה / מַיִם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| fire's | בְּלַבַּת / וְהַסְּנֶה / בֹּעֵר | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| arkite | הַעַרְקִי / הַסִּינִי׃ / וְאֶת | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| ruddy | אַדְמוֹנִי / כְּאַדֶּרֶת / כִּלּוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| several | וּמִקְצֵה / וַיַּצִּגֵם / לָקַח | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| ophir | אוֹפִר / חֲוִילָה / יקְטָן׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| smeared | הַצְּפִינוֹ / גֹּמֶא / וַתַּחְמְרָה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| k | — | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  | ⚠ |
| funeral | וַיִּסְפְּדוּ / מִסְפֵּד / וְכָבֵד | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| meager | הַשְּׁמֵנָה / רָזָה / וְהִתְחַזַּקְתֶּם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| atharim | עֲרָד / הָאֲתָרִים / שְׁבִי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| tip | הַטִּי / כַדֵּךְ / וְאֶשְׁתֶּה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| highway | בַּמְסִלָּה / וּמִקְנַי / מִכְרָם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| balsam | אֹרְחַת / יִשְׁמְעֵאלִים / מִגִּלְעָד | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| grasped | וַתִּתְפְּשֵׂהוּ / בְּבִגְדוֹ / בְּיָדָהּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| foolhardy | כְּשׁמְעָם / וַיִּתְעַצְּבוּ / נְבֵלָה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| kin | וְכִי / לְאָבִיהָ׃ / אָחִי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| plagued | וַיְנַגַּע / נְגָעִים / גְּדֹלִים׃ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| justify | נֹּאמַר / נְּדַבֵּר / נִּצְטַדָּק | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| song | יָשִׁיר / הַשִּׁירָה / וּבְנֵי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| son-in-law | — | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| tied | וַתִּקְשֹׁר / רִאשֹׁנָה / וַתִּקַּח | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| assyria | חִדֶּקֶל / וְהַנָּהָר / אַשּׁוּר | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| flow | לְאֵיתָנוֹ / נָסִים / וַיְנַעֵר | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| handle | וַיַּהַס / וְיָרַשְׁנוּ / יָכוֹל | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| smallest | הִכּוּ / בַּסַּנְוֵרִים / מִקָּטֹן | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| visible | בַּצָּעִיף / וַתִּתְעַלָּף / בְּפֶתַח | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| nod | נוֹד / קִדְמַת / מִלִּפְנֵי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| despised | וַיִּשְׂטֹם / וְאַהַרְגָה / יִקְרְבוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| turns | וְשָׁכַח / וּלְקַחְתִּיךָ / שְׁנֵיכֶם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| plenty | לָלוּן׃ / רַב / עִמָּנוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| peleg | וּלְעֵבֶר / פֶּלֶג / בְיָמָיו | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| surely | מֵאִתִּי / רְאִיתִיו / אַךְ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| zemarite | הָאַרְוָדִי / הַצְּמָרִי / הַחֲמָתִי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| relax | וְהִשָּׁעֲנוּ / יִקַּח / רַגְלֵיכֶם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| never | הִתְיַצְּבוּ / יְשׁוּעַת / לִרְאֹתָם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| jebu-sites | הַגִּרְגָּשִׁי׃ / הַיְבוּסִי | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| widen | אוֹרִישׁ / וְהִרְחַבְתִּי / יַחְמֹד | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| child's | לֵכִי / הָעַלְמָה / הַיֶּלֶד | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| another's | וְנָבְלָה / שְׂפָתָם / יִשְׁמְעוּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| acted | וַיַּעְפִּלוּ / מָשׁוּ / לַעֲלוֹת | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| ribs | תַּרְדֵּמָה / מִצַּלְעֹתָיו / תַּחְתֶּנָּה | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| sons-in-law | חֲתָנָיו / לֹקְחֵי / מַשְׁחִית | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| sure | וְשֹׁפֵט / הַלְהרְגֵנִי / הָרַגְתָּ | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| catch | הִרְחִיקוּ / וְהִשַּׂגְתָּם / שִׁלַּמְתֶּם | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| brought | מֵאֶרֶץ / וַיָּבֹא | 43 | 37 | 79 | 159 | 2.177 | 3.292 | 0.470 | 0.2759 |  |  |
| men | הָאֲנָשִׁים / אִישׁ | 15 | 14 | 18 | 47 | 2.088 | 5.190 | 0.823 | 0.1164 |  |  |
| swear | הִשָּׁבְעָה / וַיִּשָּׁבַע / אִשָּׁבֵעַ׃ | 7 | 6 | 5 | 18 | 2.082 | 4.820 | 1.274 | 0.1414 |  |  |
| eshcol | נַחַל / אֶשְׁכּוֹל / עַד | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| laugh | וַתְּכַחֵשׁ / צָחַקְתִּי / צָחָקְתְּ׃ | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| empty-handed | רֵיקָם׃ | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| listening | שָׁמַעְתָּ / אָשׁוּב / כָּעֵת | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| willing | תֹאבֶה / לָלֶכֶת | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| freed | תִּנָּקֶה / מֵאָלָתִי / נָקִי | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| conceal | מֵאַבְרָהָם / הַמְכַסֶּה / וַיהֹוָה | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| myrrh | נְכֹאת / וָלֹט | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| children's | וְצֹאנְךָ / וּבְקָרְךָ / קָרוֹב | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| attention | וְאֶל / מִנְחָתוֹ / תִּכְבַּד | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| ours | לָנוּ / וְקִנְיָנָם / נֵאוֹתָה | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| zipporah | צִפֹּרָה | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| caused | דִבָּה / לְהוֹצִיא / וַיִּלּוֹנוּ | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| window | חַלּוֹן | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| chosen | מִבְּחֻרָיו / כְּלָאֵם׃ / מִשְׁרַת | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| chose | וַיִּבְחַר / מִכּל | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| laughed | לֵאמֹר / הַלְּבֶן / וְיִצְחָק | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| double | מִשְׁנֶה / וּמִשְׁנֶה / לָקְחוּ | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| upset | זֹעֲפִים׃ / וְהִנָּם / אֲלֵיהֶם | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| hunt | יָצוּד / וְשָׁפַךְ / וְכִסָּהוּ | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| rebekah's | רִבְקָה | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| here's | הִנֵּה / הֲשָׁלוֹם / שָׁלוֹם | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| feel | וַאֲמֻשְׁךָ / הַאַתָּה / גְּשָׁה | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| giants | רָאִינוּ / הָעֲנָק / וְשֵׁם | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| happens | תִּקְצָר / הֲיִקְרְךָ / הַיָּד | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| shepherd | רָעָה | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| fool | לְצַחֶק | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| baal | לְבַעַל / וַיִּצָּמֶד / שֹׁפְטֵי | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| arnon | אַרְנֹן׃ / אַרְצוֹ / לִקְרָאתוֹ | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| justice | חָלִלָה / כַצַּדִּיק / כָּרָשָׁע | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| companion | וְשָׁפַטְתִּי / וְהוֹדַעְתִּי / חֻקֵּי | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| she-asses | אֲתֹנֹת | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| smelled | וַיָּרַח / רֵיחַ | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| twice | פְּעָמִים / וַתֵּשְׁתְּ / וּבְעִירָם׃ | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| stronger | לַעֲלוֹת / חָזָק / אָמְרוּ | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| ever | לְדַבֵּר / אֶשְׁמֹר׃ / יָשִׂים | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| kemuel | קְמוּאֵל | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| annihilated | תִּסְפֶּה / וְאֶל | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| amorites | הָאֱמֹרִי | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| changes | חֲלִפוֹת / שְׂמָלֹת / וּלְבִנְיָמִן | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| bashan | הַבָּשָׁן / עוֹג | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| fashioned | גַּן / בְּעֵדֶן / יֵצֶר | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| drunk | וַיִּשְׁכָּר / וַיִּתְגַּל / הַיַּיִן | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| knows | יָדַע | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| judges | גֶּשׁ / שָׁפוֹט / נָרַע | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| destroy | אַשְׁחִית / לְשַׁחֵת | 6 | 1 | 8 | 15 | 1.947 | 2.907 | 1.344 | 0.3223 |  |  |
| best | חֶלְבּוֹ / טוֹב / חֵלֶב | 5 | 2 | 5 | 12 | 1.829 | 1.838 | 1.444 | 0.4138 |  |  |
| honey | זָבַת / וּדְבָשׁ / חֵלֶב | 5 | 3 | 4 | 12 | 1.829 | 2.440 | 1.444 | 0.3223 |  |  |
| things | הַדְּבָרִים / הָאֵלֶּה | 18 | 10 | 32 | 60 | 1.823 | 1.955 | 0.691 | 0.3827 |  |  |
| long | עַד / אָנָה | 4 | 2 | 3 | 9 | 1.743 | 2.044 | 1.601 | 0.3625 |  |  |
| saved | וַיַּצִּלֵהוּ / נַכֶּנּוּ / מִיָּדָם | 3 | 2 | 1 | 6 | 1.739 | 3.243 | 1.891 | 0.2834 |  |  |
| delivered | וַיִּתֵּן / וַיַּצֵּל / אֲבִיכֶם | 3 | 2 | 1 | 6 | 1.739 | 3.243 | 1.891 | 0.2834 |  |  |
| kadesh | מִדְבַּר / בַּקֹּדֶשׁ | 3 | 0 | 3 | 6 | 1.739 | 3.083 | 1.891 | 0.2967 |  |  |
| power | כֹּחַ / יִגְדַּל / דִּבַּרְתָּ | 3 | 2 | 1 | 6 | 1.739 | 3.243 | 1.891 | 0.2834 |  |  |
| touched | נֶגַע / נְגַעֲנוּךָ / וַנְּשַׁלֵּחֲךָ | 3 | 1 | 2 | 6 | 1.739 | 1.786 | 1.891 | 0.4260 |  |  |
| keeping | לְמִשְׁמֶרֶת / שֹׁמְרֵי | 3 | 0 | 3 | 6 | 1.739 | 3.083 | 1.891 | 0.2967 |  |  |
| mourned | וַיִּבְכּוּ / יוֹם / וַיִּתְאַבָּלוּ | 3 | 1 | 2 | 6 | 1.739 | 1.786 | 1.891 | 0.4260 |  |  |
| abram's | אַבְרָם / אֵשֶׁת | 3 | 0 | 3 | 6 | 1.739 | 3.083 | 1.891 | 0.2967 |  |  |
| veil | הַמַּסְוֶה / לְדַבֵּר / יְצַוֶּה | 3 | 0 | 3 | 6 | 1.739 | 3.083 | 1.891 | 0.2967 |  |  |
| trees | עֵץ | 3 | 0 | 3 | 6 | 1.739 | 3.083 | 1.891 | 0.2967 |  |  |
| no | אֵין / לֹא | 21 | 20 | 32 | 73 | 1.655 | 4.115 | 0.603 | 0.1780 |  |  |
| appeared | וַיַּרְא / נִרְאָה | 8 | 5 | 10 | 23 | 1.610 | 1.843 | 1.024 | 0.4126 |  |  |
| crime | עֲוֺן / עֲוֺנוֹ׃ | 9 | 0 | 18 | 27 | 1.523 | 9.587 | 0.929 | 0.0099 | yes |  |
| canaan | כְּנָעַן | 17 | 5 | 36 | 58 | 1.505 | 5.227 | 0.645 | 0.1138 |  |  |
| oath | עִמָּךְ / אֵלֶּה / שִׁבְעַת | 5 | 1 | 7 | 13 | 1.436 | 2.129 | 1.263 | 0.3447 |  |  |
| vineyard | וּבְכֶרֶם / בְּאַרְצֶךָ / נְטֵה | 4 | 3 | 3 | 10 | 1.298 | 2.358 | 1.360 | 0.3223 |  |  |
| life | נֶפֶשׁ / חַיֵּי | 14 | 4 | 30 | 48 | 1.203 | 4.497 | 0.641 | 0.1414 |  |  |
| onan | אוֹנָן׃ / בָּא / וְשִׁחֵת | 3 | 0 | 4 | 7 | 1.187 | 2.979 | 1.528 | 0.3163 |  |  |
| prisoners | הַשְּׁבִי / מַלְקוֹחַ / וְרָאשֵׁי | 3 | 1 | 3 | 7 | 1.187 | 1.191 | 1.528 | 0.5711 |  |  |
| er | עֵר | 3 | 0 | 4 | 7 | 1.187 | 2.979 | 1.528 | 0.3163 |  |  |
| ring | הַנֶּזֶם / וְיַחְדָּו / לִשְׁנֵיהֶם | 3 | 1 | 3 | 7 | 1.187 | 1.191 | 1.528 | 0.5711 |  |  |
| completely | מִלְאוּ / בִּלְתִּי / עָרֵיהֶם | 3 | 2 | 2 | 7 | 1.187 | 1.894 | 1.528 | 0.3989 |  |  |
| peor | פְּעוֹר | 3 | 1 | 3 | 7 | 1.187 | 1.191 | 1.528 | 0.5711 |  |  |
| covered | וַיְכַס / וַתְּכַס / וַיְכֻסּוּ | 7 | 3 | 11 | 21 | 1.185 | 1.334 | 0.940 | 0.5193 |  |  |
| fruit | פִּרְיוֹ / הָאָרֶץ / מִפְּרִי | 7 | 1 | 13 | 21 | 1.185 | 3.717 | 0.940 | 0.2110 |  |  |
| surrounded | מֻסַבֹּת | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| fallen | נָפְלוּ / חָרָה / שָׁעָה | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| sees | וְרָאָה / פָּשְׂתָה / כִּרְאוֹתוֹ | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| zilpah | זִלְפָּה / עֲשָׂרָה | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| despoiled | וַיָּבֹזּוּ / חֵילָם / טַפָּם | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| weights | וַיִּמְכְּרוּ / בְּעֶשְׂרִים / מֹאזְנֵי | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| dispossess | מִפְּנֵיכֶם / אַכֶּנּוּ / וְאוֹרִשֶׁנּוּ | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| bigger | גָּדוֹל | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| uz | עוּץ | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| rod | תַּחַת / הַשָּׁבֶט / וָצֹאן | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| rather | אִם / אֵלֵךְ׃ | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| wasn't | מִבִּלְתִּי / יְכֹלֶת / וַיִּשְׁחָטֵם | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| happened | הַקֹּרֹת / עֹלָתָם / וַתִּקְרֶאנָה | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| months | חֳדָשִׁים | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| lain | שָׁכַב / וְעַד | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| borne | יָלְדָה | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| infertile | עֲקָרָה | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| dispersed | נִפְרְדוּ / בְּגוֹיֵהֶם׃ / לְתוֹלְדֹתָם | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| gathering | הֵאָסֵף / וְחַג / הַשָּׁנָה | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| furnace | הַכִּבְשָׁן | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| possessions | וְנֹאחֲזוּ / בְּתֹכְכֶם / נַפְשׁוֹת | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| degraded | תְּעַנֶּה / שִׁפְחָתֵךְ / וַתְּעַנֶּהָ | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| wonders | בְּקִרְבּוֹ׃ / הַמֹּפְתִים / לָשׁוּב | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| knowledge | הַדַּעַת / וָרָע / וּמֵעֵץ | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| chariot | וַיֶּאְסֹר / רִכְבּוֹ / לָקַח | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| begun | הֵחֵל / הַנָּגֶף׃ / תּוֹךְ | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| beginning | בָּרִאשֹׁנָה / רִאשׁוֹן / לְחדְשֵׁי | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| rejected | מְאַסְתֶּם / לַאֲבֹתָם / מְנַאֲצַי | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| curse | תֹּאַר / עָלַי / עִמָּהֶם | 5 | 4 | 5 | 14 | 1.112 | 2.054 | 1.102 | 0.3599 |  |  |
| passed | וְהוּא / בַּמַּחֲנֶה׃ / עֵבֶר | 5 | 4 | 5 | 14 | 1.112 | 2.054 | 1.102 | 0.3599 |  |  |
| give | לָתֵת / אֶתֵּן / תִּתֵּן | 45 | 41 | 94 | 180 | 1.055 | 1.710 | 0.317 | 0.4455 |  |  |
| benjamin | בִנְיָמִן / בִּנְיָמִין | 7 | 3 | 12 | 22 | 0.961 | 1.224 | 0.844 | 0.5598 |  |  |
| harvest | קְצִיר | 4 | 1 | 6 | 11 | 0.950 | 1.401 | 1.154 | 0.4999 |  |  |
| died | וַיָּמת | 14 | 10 | 26 | 50 | 0.921 | 0.936 | 0.559 | 0.5969 |  |  |
| giving | נָתַן | 5 | 1 | 9 | 15 | 0.846 | 2.094 | 0.958 | 0.3531 |  |  |
| flood | הַמַּבּוּל׃ | 3 | 0 | 5 | 8 | 0.792 | 3.032 | 1.239 | 0.3059 |  |  |
| quiet | וְהֶחֱרִשׁ / וְקָמוּ / וְשָׁמַע | 3 | 0 | 5 | 8 | 0.792 | 3.032 | 1.239 | 0.3059 |  |  |
| adah | עָדָה | 3 | 0 | 5 | 8 | 0.792 | 3.032 | 1.239 | 0.3059 |  |  |
| created | בָּרָא / וַיִּבְרָא / וַיְקַדֵּשׁ | 3 | 0 | 5 | 8 | 0.792 | 3.032 | 1.239 | 0.3059 |  |  |
| wife's | אֵשֶׁת / אִשְׁתּוֹ | 3 | 0 | 5 | 8 | 0.792 | 3.032 | 1.239 | 0.3059 |  |  |
| possess | לָרֶשֶׁת / וְיִרַשׁ / וְהוֹרַשְׁתֶּם | 4 | 3 | 5 | 12 | 0.677 | 0.998 | 0.973 | 0.5969 |  |  |
| reside | יָגוּר / לָגוּר | 4 | 0 | 8 | 12 | 0.677 | 4.261 | 0.973 | 0.1621 |  |  |
| die | יָמוּת / וְלֹא / לָמוּת | 18 | 17 | 34 | 69 | 0.665 | 1.456 | 0.414 | 0.4823 |  |  |
| city's | הָעִיר / בָּאֵי / עִירוֹ | 2 | 1 | 2 | 5 | 0.649 | 0.696 | 1.405 | 0.6341 |  |  |
| saul | שָׁאוּל | 2 | 0 | 3 | 5 | 0.649 | 1.993 | 1.405 | 0.3732 |  |  |
| destroyed | תְשׁוּבֻן / לְהַנִּיחוֹ / וְשִׁחַתֶּם | 2 | 1 | 2 | 5 | 0.649 | 0.696 | 1.405 | 0.6341 |  |  |
| dew | מִטַּל / וּמִשְׁמַנֵּי / דָּגָן | 2 | 1 | 2 | 5 | 0.649 | 0.696 | 1.405 | 0.6341 |  |  |
| floor | בְּקַרְקַע / הֶעָפָר / בִּכְלִי | 2 | 0 | 3 | 5 | 0.649 | 1.993 | 1.405 | 0.3732 |  |  |
| fortified | וַיֵּשֶׁב / וַיִּתְחַזֵּק / בִּנְךָ | 2 | 1 | 2 | 5 | 0.649 | 0.696 | 1.405 | 0.6341 |  |  |
| forgive | יִסְלַח / וַיהֹוָה | 2 | 0 | 3 | 5 | 0.649 | 1.993 | 1.405 | 0.3732 |  |  |
| even | עַד | 2 | 1 | 2 | 5 | 0.649 | 0.696 | 1.405 | 0.6341 |  |  |
| captured | שְׁבוּ / נְשֵׁיהֶם / וַיִּלְכֹּד | 2 | 0 | 3 | 5 | 0.649 | 1.993 | 1.405 | 0.3732 |  |  |
| bela | בֶּלַע | 2 | 0 | 3 | 5 | 0.649 | 1.993 | 1.405 | 0.3732 |  |  |
| threshing | גֹּרֶן / וְנֶחְשַׁב | 2 | 0 | 3 | 5 | 0.649 | 1.993 | 1.405 | 0.3732 |  |  |
| infants | טַפָּם / טַפֵּנוּ / טַפְּכֶם | 6 | 5 | 9 | 20 | 0.608 | 1.003 | 0.733 | 0.5969 |  |  |
| lie | יִשְׁכַּב | 8 | 3 | 17 | 28 | 0.603 | 1.739 | 0.621 | 0.4398 |  |  |
| break | תִשְׁבְּרוּ / יֶהֶרְסוּ / רֵד | 7 | 3 | 14 | 24 | 0.601 | 1.161 | 0.669 | 0.5832 |  |  |
| paid | וְהֶבֶל / מִבְּכֹרת / וּמֵחֶלְבֵהֶן | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| hadar | הֲדַר / פָּעוּ / מְהֵיטַבְאֵל | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| onyx | שֹׁהַם / הַשֹּׁהַם / וְלַחֹשֶׁן׃ | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| og | הַבָּשָׁן / עוֹג | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| pigeon | וּבִמְלֹאת / תֹר / יוֹנָה | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| complete | וּסְפַרְתֶּם / שַׁבָּתוֹת / תְּמִימֹת | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| arrival | וַיָּכִינוּ / עַד / הַנּוֹלָדִים | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| wail | עֳנִי / נֹגְשָׂיו / מַכְאֹבָיו׃ | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| shoulders | זִכָּרֹן / כְתֵפָיו / שְׁמוֹתָם | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| leaf | עֹלָה | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| oldest | נוֹשָׁן / וְיָשָׁן / תּוֹצִיאוּ׃ | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| reject | יְנַאֲצֻנִי / וְעַד / יַאֲמִינוּ | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| shoes | שַׁל / נְעָלֶיךָ / רַגְלֶיךָ | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| astonished | מִשְׁתָּאֵה / מַחֲרִישׁ / הַהִצְלִיחַ | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| wore | לָבַשׁ / וְהִנִּיחָם / בְּבֹאוֹ | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| re-bekah | הֲתֵלְכִי / לְרִבְקָה / אֵלֵךְ׃ | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| fig | וּתְאֵנָה / וְגֶפֶן / לְהָבִיא | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| area | וְהֵאִיר / פָּנֶיהָ׃ / עֵבֶר | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| sheep's | יוּסַר / הַכֶּשֶׂב / חֶלְבָּהּ | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| beyond | יָזוּב / זוֹב / תָזוּב | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| camel | הַגָּמָל / וַתִּפֹּל / עֵינֶיהָ | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| scatter | אֱזָרֶה / וַהֲרִיקֹתִי / וְעָרֵיכֶם | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| trust | בִּי / הֶאֱמַנְתֶּם / יַעַן | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| dispossessed | וַיּוֹרֶשׁ / גִּלְעָדָה / וַיִּלְכְּדֻהָ | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| concealed | וַתִּצְפְּנֵהוּ / יְרָחִים׃ / וְנִסְתְּרָה | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| lied | וְנִשְׁבַּע / לַחֲטֹא / בָהֵנָּה׃ | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| weeks | כְּנִדָּתָהּ / וְשֵׁשֶׁת / וְשִׁשִּׁים | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| cush | וְכוּשׁ / נִמְרֹד / לִהְיוֹת | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| growth | סְפִיחַ / תִקְצוֹר / עִנְּבֵי | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| use | בְּכֹרָה׃ / וְלָמָּה / הוֹלֵךְ | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| shur | שׁוֹר / וַיִּמְצָאָהּ | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| seventeen | עֲשָׂרָה / שֶׁבַע / חַיָּיו | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| arpachshad | וְאַרְפַּכְשַׁד | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| commanding | מְצַוָּה / לַאֲשֶׁר / לְצַוֺּת | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| insides | בְּמֵעַיִךְ / לַצְבּוֹת / בֶּטֶן | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| beqa | לְשֵׁשׁ / בֶּקַע / הָעֹבֵר | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| touching | יֹשֶׁבֶת / בְּנגְעוֹ / וְהִגְבַּלְתָּ | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| stands | מִגֹּאֵל / לַמִּשְׁפָּט׃ / עִמְדוּ | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| showed | וַיָּשִׁיבוּ / וַיַּרְאוּם / קְדֵשָׁה׃ | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| belly | גְּחֹנְךָ / וּמִכֹּל / עָשִׂיתָ | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| dipped | בַּדָּם / וַיִּטְבֹּל | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| corpses | הַחֲלָלִים / טִמְּאוּ / אֲחוֹתָם׃ | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| jealous | קַנָּא / וַתְּקַנֵּא / בַּאֲחֹתָהּ | 3 | 2 | 4 | 9 | 0.508 | 0.601 | 0.998 | 0.6761 |  |  |
| exposed | עֶרְוַת / גִּלָּה / וְאִישׁ | 3 | 1 | 5 | 9 | 0.508 | 0.753 | 0.998 | 0.6126 |  |  |
| regarding | וַיִּזְרֹק / כָּרַת / עִמָּכֶם | 3 | 2 | 4 | 9 | 0.508 | 0.601 | 0.998 | 0.6761 |  |  |
| along | בַּיַּמִּים / וְאַבְרָהָם / וְעַל | 3 | 1 | 5 | 9 | 0.508 | 0.753 | 0.998 | 0.6126 |  |  |
| third | הַשְּׁלִישִׁי | 8 | 6 | 15 | 29 | 0.472 | 0.499 | 0.552 | 0.7217 |  |  |
| both | גַּם / שְׁנֵיהֶם | 7 | 3 | 15 | 25 | 0.460 | 1.196 | 0.588 | 0.5698 |  |  |
| nations | הַגּוֹיִם / גּוֹיִם / גּוֹיֵי | 7 | 3 | 15 | 25 | 0.460 | 1.196 | 0.588 | 0.5698 |  |  |
| fell | וַיִּפֹּל / וַיִּפְּלוּ | 5 | 3 | 9 | 17 | 0.452 | 0.465 | 0.706 | 0.7384 |  |  |
| ten | עֲשָׂרָה | 12 | 8 | 26 | 46 | 0.443 | 0.572 | 0.426 | 0.6891 |  |  |
| sister's | אֲחֹתוֹ / אֲחוֹת | 2 | 0 | 4 | 6 | 0.338 | 2.130 | 1.043 | 0.3444 |  |  |
| noah's | נֹחַ / וּמֵאֵלֶּה | 2 | 0 | 4 | 6 | 0.338 | 2.130 | 1.043 | 0.3444 |  |  |
| fresh | חַיִּים / וַיִּמְצְאוּ / אָבִיב | 2 | 1 | 3 | 6 | 0.338 | 0.343 | 1.043 | 0.7999 |  |  |
| security | לָבֶטַח / וִישַׁבְתֶּם / הַיָּמִים | 2 | 1 | 3 | 6 | 0.338 | 0.343 | 1.043 | 0.7999 |  |  |
| corresponding | עֵזֶר / כְּנֶגְדּוֹ / וּלְעוֹף | 2 | 1 | 3 | 6 | 0.338 | 0.343 | 1.043 | 0.7999 |  |  |
| report | דִּבַּת / נִשְׁמַע / וְהַקֹּל | 2 | 1 | 3 | 6 | 0.338 | 0.343 | 1.043 | 0.7999 |  |  |
| home | בֵּית / מוֹשָׁבוֹ׃ / בְּדַד | 2 | 1 | 3 | 6 | 0.338 | 0.343 | 1.043 | 0.7999 |  |  |
| sheaf | הָעֹמֶר / מִמּחֳרָת / עֹמֶר | 2 | 0 | 4 | 6 | 0.338 | 2.130 | 1.043 | 0.3444 |  |  |
| bone | וְעֶצֶם / תוֹצִיא / חוּצָה | 2 | 0 | 4 | 6 | 0.338 | 2.130 | 1.043 | 0.3444 |  |  |
| stayed | וַיֵּשֶׁב / עֹמֵד / בְּעֵינָיו | 3 | 1 | 6 | 10 | 0.304 | 0.756 | 0.791 | 0.6118 |  |  |
| dominate | בּוֹ / תִרְדֶּה / וּרְדוּ | 3 | 1 | 6 | 10 | 0.304 | 0.756 | 0.791 | 0.6118 |  |  |
| something | וְעָשׂוּ / אֱלֹהֵי / בְּעַבְדֶּךָ | 3 | 2 | 5 | 10 | 0.304 | 0.313 | 0.791 | 0.8162 |  |  |
| thousands | אַלְפֵי / לְאַלְפֵי / הָאֲלָפִים | 4 | 2 | 8 | 14 | 0.302 | 0.477 | 0.668 | 0.7322 |  |  |
| given | נָתַתִּי / נָתַן | 15 | 9 | 37 | 61 | 0.285 | 1.205 | 0.306 | 0.5667 |  |  |
| childless | עֲרִירִים / יִהְיוּ | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| who's | לִקְרָאתֵנוּ / הַצָּעִיף / וַתִּתְכָּס׃ | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| chaldees | כַּשְׂדִּים / מֵאוּר | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| stricken | אָב / תִּנָּגְפוּ / תַעֲלוּ | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| seek | וּבִקַּשְׁתֶּם / אֶעֶרְבֶנּוּ / תְּבַקְשֶׁנּוּ | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| demolish | וְנָתַץ / אֲבָנָיו / עֵצָיו | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| asshur | וַיִּשְׁכְּנוּ / מֵחֲוִילָה / אַשּׁוּרָה | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| teman | תֵּימָן / קְנַז׃ | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| roof | גַּגּוֹ / קִירֹתָיו | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| during | בְּנִדַּת / טֻמְאָתָהּ / תִּקְרַב | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| breath | חַיִּים / רוּחַ / בּוֹ | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| ur | כַּשְׂדִּים / מֵאוּר | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| fury | חֲמַת / אֲחָדִים / תָּשׁוּב | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| rescue | מִיַּד | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| kenaz | תֵּימָן / קְנַז׃ | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| whoring | כְּמִשְׁלֹשׁ / זָנְתָה / לִזְנוּנִים | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| weep | וּלְאֶלְעָזָר / וּלְאִיתָמָר / רָאשֵׁיכֶם | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| gotten | תַּחַת / קַמְתֶּם / תַּרְבּוּת | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| tented | עַד / וַיֶּאֱהַל / וַיִּסְעוּ | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| enmity | בְאֵיבָה / בְּיָדוֹ / הוּא | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| yoke | פְּרֵה / אֲדָמָה / וַיִּקְחוּ | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| binding | כְּפִי / בְּתוֹכוֹ / לְפִיו | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| cling | תִסֹּב / יִדְבְּקוּ / מִמַּטֶּה | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| arm | וַתַּשְׁקֵהוּ׃ / יָדָהּ / וַתֵּרֶד | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| sarah's | שָׂרָה / וַיִּהְיוּ / וְעֶשְׂרִים | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| crushed | וַיַּכּוּם / וַיַּכְּתוּם / הַחרְמָה׃ | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| remaining | וּמִיֶּתֶר / הַנּוֹתָרֹת׃ / בֵּינוֹ | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| taken | לָקַח / לָקַחְתִּי | 7 | 6 | 15 | 28 | 0.164 | 0.191 | 0.371 | 0.8836 |  |  |
| cease | תִּשְׁבֹּת | 3 | 2 | 6 | 11 | 0.162 | 0.171 | 0.611 | 0.8951 |  |  |
| appear | פְּנֵי | 3 | 2 | 6 | 11 | 0.162 | 0.171 | 0.611 | 0.8951 |  |  |
| places | וְנָתַתִּי / הַבְּמַחֲנִים / בְּמִבְצָרִים׃ | 2 | 1 | 4 | 7 | 0.151 | 0.239 | 0.753 | 0.8555 |  |  |
| remain | יָלִין / זִבְחִי / תֵּשֵׁב | 2 | 1 | 4 | 7 | 0.151 | 0.239 | 0.753 | 0.8555 |  |  |
| residents | יֹשְׁבֵי | 2 | 1 | 4 | 7 | 0.151 | 0.239 | 0.753 | 0.8555 |  |  |
| mother's | אִמְּךָ / אִמּוֹ | 4 | 3 | 9 | 16 | 0.094 | 0.107 | 0.417 | 0.9333 |  |  |
| have | יִהְיֶה / לָכֶם / כִּי | 54 | 52 | 146 | 252 | 0.004 | 0.018 | 0.026 | 0.9893 |  |  |

### All words assigned to E (1,124 types)

The assignment is the source with the largest positive source-vs-rest information score. **Do not treat a one-off as strong evidence**: use source info bits, global bits, total count, and q-value together.

| word | Hebrew | J | E | P | n | source info bits | global bits | source WoE bits | q | FDR<.05 | artifact? |
| --- | :---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: | :---: |
| people | הָעָם | 97 | 174 | 87 | 358 | 96.333 | 135.829 | 1.836 | 5.06e-39 | yes |  |
| god | אֱלֹהִים | 54 | 183 | 150 | 387 | 95.013 | 95.026 | 1.761 | 4.10e-27 | yes |  |
| pharaoh | פַּרְעֹה | 24 | 92 | 23 | 139 | 94.692 | 103.574 | 2.876 | 1.24e-29 | yes |  |
| balaam | בִּלְעָם | 0 | 45 | 1 | 46 | 94.634 | 95.085 | 6.835 | 4.09e-27 | yes |  |
| balak | בָּלָק | 1 | 32 | 0 | 33 | 65.871 | 67.766 | 6.349 | 3.73e-19 | yes |  |
| egypt | מִצְרַיִם | 63 | 123 | 71 | 257 | 65.702 | 83.500 | 1.791 | 1.01e-23 | yes |  |
| up | וַיַּעַל / מִבֶּן / וָמַעְלָה | 95 | 138 | 112 | 345 | 45.990 | 70.611 | 1.331 | 5.68e-20 | yes |  |
| here | וְהִנֵּה / הִנֵּה | 100 | 114 | 60 | 274 | 42.564 | 106.441 | 1.426 | 2.06e-30 | yes |  |
| joseph | יוֹסֵף | 52 | 70 | 17 | 139 | 41.991 | 92.621 | 1.933 | 2.09e-26 | yes |  |
| you'll | תִּ־ | 56 | 72 | 20 | 148 | 39.947 | 91.898 | 1.835 | 3.33e-26 | yes |  |
| hail | הַבָּרָד / בָּרָד | 0 | 17 | 0 | 17 | 38.248 | 38.248 | 7.040 | 1.11e-10 | yes |  |
| ass | חֲמוֹר / הָאָתוֹן | 5 | 25 | 1 | 31 | 36.316 | 42.341 | 3.883 | 7.65e-12 | yes |  |
| i | אֲנִי / אָנֹכִי | 139 | 203 | 272 | 614 | 34.523 | 41.421 | 0.899 | 1.41e-11 | yes |  |
| dream | חֲלוֹם / בַּחֲלוֹם | 5 | 23 | 0 | 28 | 34.495 | 43.969 | 4.006 | 2.69e-12 | yes |  |
| now | וְעַתָּה / עַתָּה | 31 | 43 | 2 | 76 | 32.933 | 81.688 | 2.288 | 3.45e-23 | yes |  |
| this | הַזֶּה / זֶה | 118 | 145 | 145 | 408 | 32.760 | 60.866 | 1.057 | 3.65e-17 | yes |  |
| nile | הַיְאֹר | 4 | 21 | 0 | 25 | 32.751 | 40.330 | 4.167 | 2.88e-11 | yes |  |
| because | כִּי | 124 | 148 | 150 | 422 | 31.838 | 62.352 | 1.027 | 1.41e-17 | yes |  |
| meaning | פָּתַר / חֲלֹמוֹ / פִּתְרֹנוֹ | 0 | 13 | 0 | 13 | 29.248 | 29.248 | 6.665 | 4.35e-08 | yes |  |
| heavy | כָּבֵד | 9 | 23 | 0 | 32 | 27.383 | 44.435 | 3.217 | 2.01e-12 | yes |  |
| hand | יָדוֹ / בְּיַד | 55 | 95 | 100 | 250 | 27.007 | 30.969 | 1.209 | 1.42e-08 | yes |  |
| cows | פָּרוֹת / וּשְׁבַע | 0 | 12 | 0 | 12 | 26.998 | 26.998 | 6.554 | 1.82e-07 | yes |  |
| owner | בְּעָלָיו / לִבְעָלָיו | 0 | 12 | 0 | 12 | 26.998 | 26.998 | 6.554 | 1.82e-07 | yes |  |
| ears | בְּאזְנֵי | 2 | 20 | 4 | 26 | 26.777 | 26.864 | 3.568 | 1.98e-07 | yes |  |
| serve | וְיַעַבְדֻנִי׃ / שָׁלַח / עַמִּי | 3 | 19 | 2 | 24 | 26.731 | 28.464 | 3.736 | 7.22e-08 | yes |  |
| out | וַיֵּצֵא / יֹצֵא | 69 | 119 | 154 | 342 | 24.848 | 26.150 | 1.010 | 3.07e-07 | yes |  |
| elders | זִקְנֵי / מִזִּקְנֵי | 3 | 18 | 2 | 23 | 24.826 | 26.560 | 3.660 | 2.38e-07 | yes |  |
| drive | מִפָּנֶיךָ / אֲגָרְשֶׁנּוּ | 0 | 11 | 0 | 11 | 24.748 | 24.748 | 6.434 | 7.83e-07 | yes |  |
| pit | הַבּוֹר | 0 | 11 | 0 | 11 | 24.748 | 24.748 | 6.434 | 7.83e-07 | yes |  |
| go | אֶל / לְךָ | 109 | 134 | 157 | 400 | 24.078 | 41.835 | 0.927 | 1.06e-11 | yes |  |
| set | וַיָּשֶׂם / וְשַׂמְתָּ | 14 | 56 | 61 | 131 | 22.526 | 24.535 | 1.493 | 8.80e-07 | yes |  |
| yesterday | שִׁלְשֹׁם / כִּתְמוֹל | 0 | 10 | 0 | 10 | 22.499 | 22.499 | 6.302 | 3.30e-06 | yes |  |
| moses | מֹשֶׁה | 48 | 178 | 351 | 577 | 21.991 | 59.998 | 0.751 | 6.44e-17 | yes |  |
| would | מִמֶּנָּה / כּל / לַעֲבֹדָה | 26 | 49 | 36 | 111 | 21.456 | 26.156 | 1.575 | 3.07e-07 | yes |  |
| servants | עֲבָדָיו / עֲבָדֶיךָ / עַבְדֵי | 30 | 38 | 10 | 78 | 21.152 | 50.062 | 1.838 | 4.75e-14 | yes |  |
| father-in-law | חֹתֵן / חֹתְנוֹ | 3 | 14 | 0 | 17 | 21.091 | 26.775 | 3.961 | 2.08e-07 | yes |  |
| bad | רַע / רָעָה | 19 | 33 | 12 | 64 | 20.847 | 32.419 | 2.000 | 5.31e-09 | yes |  |
| jethro | יִתְרוֹ | 0 | 9 | 0 | 9 | 20.249 | 20.249 | 6.158 | 1.34e-05 | yes |  |
| boys | נְעָרָיו | 1 | 11 | 0 | 12 | 20.123 | 22.018 | 4.849 | 4.37e-06 | yes |  |
| angel | מַלְאַךְ | 8 | 18 | 0 | 26 | 20.069 | 35.227 | 3.032 | 8.36e-10 | yes |  |
| let | נָא / וַיֹּאמֶר / אֶל | 70 | 74 | 54 | 198 | 19.921 | 54.448 | 1.171 | 2.66e-15 | yes |  |
| abraham | אַבְרָהָם | 31 | 51 | 39 | 121 | 19.740 | 26.762 | 1.458 | 2.09e-07 | yes |  |
| they'll | וְאָמְרוּ / לָהֶם / מֵעִם | 12 | 24 | 5 | 41 | 19.652 | 29.790 | 2.396 | 3.09e-08 | yes |  |
| ox | שׁוֹר / הַשּׁוֹר | 2 | 22 | 12 | 36 | 19.557 | 20.486 | 2.544 | 1.17e-05 | yes |  |
| gods | אֱלֹהֵי | 8 | 19 | 2 | 29 | 19.201 | 28.043 | 2.803 | 9.60e-08 | yes |  |
| pharaoh's | פַּרְעֹה | 15 | 27 | 8 | 50 | 18.809 | 29.407 | 2.137 | 3.98e-08 | yes |  |
| eyes | בְּעֵינֵי | 48 | 53 | 30 | 131 | 18.266 | 47.793 | 1.358 | 2.18e-13 | yes |  |
| pray | הַעְתִּירוּ / וַאֲשַׁלְּחָה / לַיהֹוָה | 0 | 8 | 0 | 8 | 17.999 | 17.999 | 5.997 | 5.61e-05 | yes |  |
| pile | הַגַּל / הַמַּצֵּבָה | 0 | 8 | 0 | 8 | 17.999 | 17.999 | 5.997 | 5.61e-05 | yes |  |
| pay | יְשַׁלֵּם | 8 | 24 | 11 | 43 | 17.887 | 19.359 | 2.240 | 2.38e-05 | yes |  |
| back | וַיֵּשֶׁב | 52 | 61 | 48 | 161 | 17.177 | 37.509 | 1.203 | 1.82e-10 | yes |  |
| got | וַיָּקם | 17 | 24 | 4 | 45 | 16.292 | 35.558 | 2.099 | 6.75e-10 | yes |  |
| abimelek | אֲבִימֶלֶךְ | 7 | 15 | 0 | 22 | 16.279 | 29.542 | 2.957 | 3.65e-08 | yes |  |
| insect | הָעָרֶב׃ / עֶרֶב / מִפַּרְעֹה | 0 | 7 | 0 | 7 | 15.749 | 15.749 | 5.817 | 2.26e-04 | yes |  |
| purpose | בַּעֲבוּר / וּלְמַעַן / בָּא | 0 | 7 | 0 | 7 | 15.749 | 15.749 | 5.817 | 2.26e-04 | yes |  |
| execrate | לְכָה / קָבָה / בָרֵךְ | 0 | 7 | 0 | 7 | 15.749 | 15.749 | 5.817 | 2.26e-04 | yes |  |
| that | אֲשֶׁר | 262 | 294 | 546 | 1102 | 14.428 | 23.154 | 0.457 | 2.20e-06 | yes |  |
| livestock | מִקְנֵה | 8 | 19 | 7 | 34 | 14.195 | 17.565 | 2.241 | 7.32e-05 | yes |  |
| you | לָכֶם / לְךָ | 358 | 502 | 1138 | 1998 | 13.966 | 18.902 | 0.341 | 3.14e-05 | yes |  |
| whoever | מִי / וַאֲשֶׁר / מִקְנֵהוּ | 0 | 8 | 1 | 9 | 13.810 | 14.262 | 4.412 | 5.69e-04 | yes |  |
| way | בַּדֶּרֶךְ / דֶּרֶךְ | 18 | 21 | 1 | 40 | 13.789 | 42.694 | 2.051 | 6.11e-12 | yes |  |
| did | וַיַּעַשׂ / וְלֹא / וַיַּעֲשׂוּ | 44 | 61 | 67 | 172 | 13.677 | 19.785 | 1.053 | 1.83e-05 | yes |  |
| midwives | הַמְיַלֶּדֶת / לַמְיַלְּדֹת / וַתְּחַיֶּיןָ | 0 | 6 | 0 | 6 | 13.499 | 13.499 | 5.610 | 9.13e-04 | yes |  |
| bountifulness | הַשָּׂבָע / שְׁנֵי | 0 | 6 | 0 | 6 | 13.499 | 13.499 | 5.610 | 9.13e-04 | yes |  |
| thunders | קֹלֹת / הַקֹּלוֹת / וּבָרָד | 0 | 6 | 0 | 6 | 13.499 | 13.499 | 5.610 | 9.13e-04 | yes |  |
| drink-stewards | הַמַּשְׁקִים | 0 | 6 | 0 | 6 | 13.499 | 13.499 | 5.610 | 9.13e-04 | yes |  |
| dies | וָמֵת | 0 | 6 | 0 | 6 | 13.499 | 13.499 | 5.610 | 9.13e-04 | yes |  |
| miriam | מִרְיָם | 0 | 9 | 2 | 11 | 13.405 | 14.309 | 3.836 | 5.64e-04 | yes |  |
| beer-sheba | שֶׁבַע / בְּאֵר | 3 | 10 | 0 | 13 | 13.389 | 19.073 | 3.495 | 2.85e-05 | yes |  |
| if | וְאִם / אִם | 51 | 94 | 155 | 300 | 12.539 | 12.890 | 0.784 | 0.0013 | yes |  |
| swarm | עַמִּי / וּבְכל / הָעָרֶב׃ | 0 | 12 | 6 | 18 | 12.512 | 15.224 | 2.853 | 3.12e-04 | yes |  |
| answered | וַיַּעַן | 5 | 14 | 4 | 23 | 12.353 | 14.715 | 2.520 | 4.34e-04 | yes |  |
| seven | שֶׁבַע / שִׁבְעַת | 14 | 49 | 71 | 134 | 12.250 | 15.999 | 1.122 | 1.97e-04 | yes |  |
| didn't | לֹא / הֲלֹא | 9 | 17 | 5 | 31 | 12.225 | 18.373 | 2.181 | 4.45e-05 | yes |  |
| people's | הָעָם | 3 | 15 | 8 | 26 | 11.939 | 11.940 | 2.341 | 0.0024 | yes |  |
| anger | אַף | 8 | 15 | 3 | 26 | 11.939 | 19.154 | 2.341 | 2.73e-05 | yes |  |
| what | מַה | 45 | 54 | 54 | 153 | 11.894 | 23.150 | 1.043 | 2.20e-06 | yes |  |
| stolen | גֻנֹּב / גְּנֻבְתִי / מֵעִמּוֹ | 1 | 7 | 0 | 8 | 11.741 | 13.636 | 4.232 | 8.47e-04 | yes |  |
| entire | כּל / עָלַי | 0 | 7 | 1 | 8 | 11.741 | 12.193 | 4.232 | 0.0021 | yes |  |
| only | רַק | 9 | 16 | 4 | 29 | 11.649 | 18.932 | 2.200 | 3.08e-05 | yes |  |
| early | וַיַּשְׁכֵּם / בַּבֹּקֶר | 3 | 9 | 0 | 12 | 11.535 | 17.219 | 3.350 | 9.04e-05 | yes |  |
| straw | תֶּבֶן | 2 | 8 | 0 | 10 | 11.461 | 15.250 | 3.675 | 3.08e-04 | yes |  |
| famine | הָרָעָב | 10 | 14 | 0 | 24 | 11.386 | 30.334 | 2.376 | 2.15e-08 | yes |  |
| ewes | כְּבָשֹׂת | 0 | 5 | 0 | 5 | 11.249 | 11.249 | 5.369 | 0.0037 | yes |  |
| balak's | בָּלָק | 0 | 5 | 0 | 5 | 11.249 | 11.249 | 5.369 | 0.0037 | yes |  |
| master | אֲדֹנָיו / חפְשִׁי׃ / אֵצֵא | 0 | 5 | 0 | 5 | 11.249 | 11.249 | 5.369 | 0.0037 | yes |  |
| communicated | וַיִּקָּר / וְנִזְבְּחָה / נֵלְכָה | 0 | 5 | 0 | 5 | 11.249 | 11.249 | 5.369 | 0.0037 | yes |  |
| bakers | הָאֹפִים | 0 | 5 | 0 | 5 | 11.249 | 11.249 | 5.369 | 0.0037 | yes |  |
| voice | בְּקֹלִי | 18 | 19 | 1 | 38 | 11.217 | 40.122 | 1.910 | 3.30e-11 | yes |  |
| i'm | אָנֹכִי / הִנְנִי / אֲנִי | 28 | 30 | 15 | 73 | 10.817 | 30.528 | 1.398 | 1.89e-08 | yes |  |
| able | יָכְלוּ / אוּכַל / וְלֹא | 12 | 18 | 6 | 36 | 10.627 | 19.546 | 1.910 | 2.12e-05 | yes |  |
| mouth | בְּפִי / פִּי / בְּפִיו | 18 | 19 | 2 | 39 | 10.576 | 36.205 | 1.838 | 4.38e-10 | yes |  |
| it's | הוּא | 14 | 19 | 6 | 39 | 10.576 | 22.188 | 1.838 | 3.93e-06 | yes |  |
| tomorrow | מָחָר | 2 | 10 | 3 | 15 | 10.427 | 10.717 | 2.843 | 0.0049 | yes |  |
| tell | לִי / הַגִּידָה / הִגַּדְתָּ | 10 | 15 | 3 | 28 | 10.278 | 20.449 | 2.109 | 1.19e-05 | yes |  |
| neighbor | רֵעֵהוּ | 1 | 9 | 3 | 13 | 10.034 | 10.040 | 2.988 | 0.0074 | yes |  |
| there's | אֵין / אָפֵס / נָמוּת | 3 | 9 | 1 | 13 | 10.034 | 12.925 | 2.988 | 0.0013 | yes |  |
| flared | וַיִּחַר | 2 | 9 | 2 | 13 | 10.034 | 10.728 | 2.988 | 0.0049 | yes |  |
| pillar | מַצֵּבָה | 1 | 9 | 3 | 13 | 10.034 | 10.040 | 2.988 | 0.0074 | yes |  |
| chiefs | שָׂרֵי | 2 | 18 | 17 | 37 | 9.987 | 12.235 | 1.834 | 0.0020 | yes |  |
| say | וְאָמַרְתָּ / אָמַר | 27 | 39 | 40 | 106 | 9.959 | 14.023 | 1.138 | 6.59e-04 | yes |  |
| witness | עַד / וּבֵינֶךָ | 0 | 8 | 3 | 11 | 9.722 | 11.077 | 3.190 | 0.0040 | yes |  |
| hebrews | הָעִבְרִים / אֱלֹהֵי | 3 | 8 | 0 | 11 | 9.722 | 15.406 | 3.190 | 2.78e-04 | yes |  |
| why | לָמָּה | 22 | 24 | 10 | 56 | 9.721 | 27.250 | 1.503 | 1.58e-07 | yes |  |
| bosom | בְּחֵיקֶךָ / וַיּוֹצִאָהּ / יָדְךָ | 1 | 6 | 0 | 7 | 9.698 | 11.593 | 4.025 | 0.0030 | yes |  |
| rescued | מִיַּד | 1 | 6 | 0 | 7 | 9.698 | 11.593 | 4.025 | 0.0030 | yes |  |
| continue | תֹסֵף / רְאוֹת | 1 | 6 | 0 | 7 | 9.698 | 11.593 | 4.025 | 0.0030 | yes |  |
| believe | יַאֲמִינוּ / אֵלֶיךָ | 1 | 6 | 0 | 7 | 9.698 | 11.593 | 4.025 | 0.0030 | yes |  |
| distance | מֵרָחֹק | 2 | 7 | 0 | 9 | 9.552 | 13.342 | 3.495 | 9.82e-04 | yes |  |
| maids | הַשְּׁפָחוֹת / וַעֲבָדִים / וּשְׁפָחֹת | 2 | 7 | 0 | 9 | 9.552 | 13.342 | 3.495 | 9.82e-04 | yes |  |
| locust | הָאַרְבֶּה / אַרְבֶּה | 0 | 7 | 2 | 9 | 9.552 | 10.456 | 3.495 | 0.0058 | yes |  |
| stood | וַיַּעֲמֹד / וַיַּעַמְדוּ | 6 | 15 | 8 | 29 | 9.540 | 10.730 | 2.006 | 0.0049 | yes |  |
| account | כֵּן | 21 | 21 | 5 | 47 | 9.485 | 33.170 | 1.608 | 3.27e-09 | yes |  |
| they're | הֵם | 3 | 12 | 6 | 21 | 9.373 | 9.504 | 2.306 | 0.0101 | yes |  |
| against | כִּי / עָלַי / עַל | 16 | 35 | 43 | 94 | 9.305 | 9.306 | 1.165 | 0.0114 | yes |  |
| mountain | הָהָר / בְּהַר | 21 | 22 | 8 | 51 | 9.067 | 27.829 | 1.519 | 1.09e-07 | yes |  |
| throne | כִּסְאוֹ / הַיֹּשֵׁב / עַד | 0 | 4 | 0 | 4 | 8.999 | 8.999 | 5.079 | 0.0138 | yes |  |
| honor | אֲכַבֶּדְךָ / כָּבֵד / וּלְכָה | 0 | 4 | 0 | 4 | 8.999 | 8.999 | 5.079 | 0.0138 | yes |  |
| knife | הַמַּאֲכֶלֶת / בְּנוֹ / לִשְׁחֹט | 0 | 4 | 0 | 4 | 8.999 | 8.999 | 5.079 | 0.0138 | yes |  |
| boy's | הַיֶּלֶד / אָנָה | 0 | 4 | 0 | 4 | 8.999 | 8.999 | 5.079 | 0.0138 | yes |  |
| zippor | צִפּוֹר | 0 | 4 | 0 | 4 | 8.999 | 8.999 | 5.079 | 0.0138 | yes |  |
| liberated | לַחפְשִׁי | 0 | 4 | 0 | 4 | 8.999 | 8.999 | 5.079 | 0.0138 | yes |  |
| maid's | הָאָמָה / אֲשִׂימֶנּוּ / יְשַׁלְּחֶנּוּ | 0 | 4 | 0 | 4 | 8.999 | 8.999 | 5.079 | 0.0138 | yes |  |
| gore | יִגַּח | 0 | 4 | 0 | 4 | 8.999 | 8.999 | 5.079 | 0.0138 | yes |  |
| going | יֹצֵא | 15 | 24 | 19 | 58 | 8.824 | 12.172 | 1.416 | 0.0021 | yes |  |
| land | הָאָרֶץ / אֶרֶץ / בְּאֶרֶץ | 122 | 131 | 218 | 471 | 8.797 | 18.290 | 0.539 | 4.69e-05 | yes |  |
| cried | וַיִּצְעַק | 3 | 9 | 2 | 14 | 8.787 | 10.521 | 2.698 | 0.0056 | yes |  |
| officers | שֹׁטְרֵי / וְשֹׁטְרָיו / לֵאמֹר | 2 | 8 | 2 | 12 | 8.341 | 9.035 | 2.827 | 0.0137 | yes |  |
| he'll | יִשְׁלַח / וְאָכַל | 15 | 18 | 7 | 40 | 8.278 | 20.009 | 1.628 | 1.58e-05 | yes |  |
| favor | חֵן | 12 | 14 | 2 | 28 | 8.265 | 23.622 | 1.910 | 1.62e-06 | yes |  |
| amalek | עֲמָלֵק | 1 | 7 | 2 | 10 | 7.958 | 8.001 | 3.009 | 0.0243 | yes |  |
| wind | קָדִים / רוּחַ / הַקָּדִים | 2 | 7 | 1 | 10 | 7.958 | 9.444 | 3.009 | 0.0105 | yes |  |
| coming | בָּא / וְהִנֵּה | 14 | 19 | 11 | 44 | 7.852 | 14.610 | 1.523 | 4.64e-04 | yes |  |
| eye | עֵין | 3 | 9 | 3 | 15 | 7.728 | 8.767 | 2.457 | 0.0154 | yes |  |
| turned | וַיִּפֶן / וַיִּפְנוּ / סָר | 10 | 17 | 11 | 38 | 7.703 | 10.655 | 1.613 | 0.0051 | yes |  |
| frogs | הַצְפַרְדְּעִים | 0 | 6 | 2 | 8 | 7.690 | 8.594 | 3.288 | 0.0167 | yes |  |
| changed | בַּמַּטֶּה / מַשְׂכֻּרְתִּי / מֹנִים | 1 | 6 | 1 | 8 | 7.690 | 8.037 | 3.288 | 0.0238 | yes |  |
| none | אֵין / תֵּדַע / יִרְאוּ | 1 | 6 | 1 | 8 | 7.690 | 8.037 | 3.288 | 0.0238 | yes |  |
| guards | הַטַּבָּחִים | 1 | 5 | 0 | 6 | 7.690 | 9.584 | 3.784 | 0.0099 | yes |  |
| written | כְּתֻבִים / בְּאֶצְבַּע / כְּכַלֹּתוֹ | 0 | 5 | 1 | 6 | 7.690 | 8.142 | 3.784 | 0.0224 | yes |  |
| refuse | מֵאֵן / לְשַׁלַּח | 0 | 5 | 1 | 6 | 7.690 | 8.142 | 3.784 | 0.0224 | yes |  |
| prayed | וַיֶּעְתַּר / וַיִּתְפַּלֵּל / מֵעִם | 1 | 5 | 0 | 6 | 7.690 | 9.584 | 3.784 | 0.0099 | yes |  |
| standing | נִצָּב / עֹמֵד | 11 | 14 | 4 | 29 | 7.631 | 17.731 | 1.814 | 6.59e-05 | yes |  |
| israel's | יִשְׂרָאֵל | 4 | 15 | 13 | 32 | 7.627 | 7.700 | 1.735 | 0.0290 | yes |  |
| see | וְרָאָה / לִרְאוֹת / רְאֵה | 30 | 40 | 49 | 119 | 7.288 | 10.602 | 0.937 | 0.0053 | yes |  |
| judge | וְשָׁפְטוּ / הַדָּבָר | 3 | 8 | 2 | 13 | 7.205 | 8.939 | 2.538 | 0.0140 | yes |  |
| sat | וַיֵּשֶׁב / וַיָּשֻׁבוּ | 3 | 8 | 2 | 13 | 7.205 | 8.939 | 2.538 | 0.0140 | yes |  |
| struck | וַיַּךְ / הִכָּה | 6 | 16 | 14 | 36 | 7.129 | 7.199 | 1.597 | 0.0390 | yes |  |
| watch | בְּמִשְׁמַר / הִשָּׁמֶר | 11 | 15 | 7 | 33 | 7.074 | 13.726 | 1.655 | 7.98e-04 | yes |  |
| hard-necked | עֹרֶף / קְשֵׁה / עִם | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| impose | עָלָיו / מַתְכֹּנֶת / לֵאלֹהֵינוּ׃ | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| scorched | שְׁדֻפוֹת / אַחֲרֵיהֶן | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| bottle | וַתֵּלֶךְ / הַחֵמֶת / וַיִּפְקַח | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| drink-steward | וְהָאֹפֶה / לַמֹּלֶךְ / לַאֲדֹנֵיהֶם | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| harnessed | וַיַּחֲבֹשׁ / וַיְבַקַּע / אִתָּנוּ | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| dispute | בְּרִיבוֹ׃ / וְדָל | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| trouble | וְנַעֲלֶה / הָעֹנֶה / צָרָתִי | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| hazeroth | וַתִּסָּגֵר / הֵאָסֵף / וְהָעָם | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| continued | וַיֹּסֶף | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| looking | וַיַּסְתֵּר / מֵהַבִּיט / אֵיפֹה | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| lazy | נִרְפִּים / נִזְבְּחָה / נֵלְכָה | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| thief | הַגַּנָּב / יִמָּצֵא | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| mercy | רַחֲמִים / שָׁכֹלְתִּי / וְשִׁלַּח | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| burden | וְיָרַדְתִּי / וְאָצַלְתִּי / בְּמַשָּׂא | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| teraphim | הַתְּרָפִים / מָצָא | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| arranged | הַמִּזְבְּחֹת / עָרַכְתִּי / וָאַעַל | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| scrawny | הָרַקּוֹת / הַפָּרוֹת / וְהָרָעוֹת | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| horeb | וְהִכִּיתָ / בַצּוּר / וְשָׁתָה | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| stole | וַתִּגְנֹב | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| lightning | קֹלֹת / וּבְרָקִים / וְקֹל | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| singing | עֲנוֹת / גְּבוּרָה / חֲלוּשָׁה | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| subtract | תִגְרְעוּ / מִלִּבְנֵיכֶם / בְּרָע | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| bend | תַטֶּה / אֶבְיֹנְךָ / לְרָעֹת | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| wouldn't | לַעֲבֹר / וְזָהָב / מְלֹא | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| dreamed | וַיַּחֲלֹם / וַנַּחַלְמָה | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| attendant | מְשָׁרְתוֹ / הַר | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| sacrificing | נִזְבַּח / יִסְקְלֻנוּ׃ / נָכוֹן | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| jewelry | שָׁתוּ / עֶדְיוֹ / הָרָע | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| ahead | לְפָנֶיךָ | 4 | 7 | 0 | 11 | 6.709 | 14.288 | 2.647 | 5.69e-04 | yes |  |
| held | בְּבֵית / בָּא / וַיְהִי | 4 | 10 | 5 | 19 | 6.601 | 7.520 | 2.054 | 0.0318 | yes |  |
| speak | דַּבֵּר | 12 | 35 | 57 | 104 | 6.408 | 8.910 | 0.941 | 0.0142 | yes |  |
| night | הַלַּיְלָה / בַּלַּיְלָה / לַיְלָה | 19 | 20 | 12 | 51 | 6.278 | 17.851 | 1.290 | 6.11e-05 | yes |  |
| like | לֹא / כֵּן | 36 | 43 | 56 | 135 | 6.199 | 10.877 | 0.822 | 0.0045 | yes |  |
| joshua | יְהוֹשֻׁעַ / וִיהוֹשֻׁעַ | 0 | 10 | 10 | 20 | 5.904 | 10.423 | 1.910 | 0.0059 | yes |  |
| place's | הַמָּקוֹם / הַהוּא | 2 | 5 | 0 | 7 | 5.888 | 9.678 | 3.047 | 0.0093 | yes |  |
| remember | בְּכל / זָכָר / וְזָכַרְתִּי | 0 | 5 | 2 | 7 | 5.888 | 6.792 | 3.047 | 0.0480 | yes |  |
| bricks | הַלְּבֵנִים / עַבְדּוֹ / לְבֵנִים | 1 | 5 | 1 | 7 | 5.888 | 6.235 | 3.047 | 0.0627 |  |  |
| tooth | שֵׁן / תַּחַת | 0 | 5 | 2 | 7 | 5.888 | 6.792 | 3.047 | 0.0480 | yes |  |
| offense | פֶּשַׁע | 2 | 5 | 0 | 7 | 5.888 | 9.678 | 3.047 | 0.0093 | yes |  |
| send | שָׁלַח | 11 | 12 | 3 | 26 | 5.877 | 17.580 | 1.696 | 7.27e-05 | yes |  |
| houses | בָּתֵּי / הַבָּתִּים / מִיּוֹם | 2 | 12 | 12 | 26 | 5.877 | 6.806 | 1.696 | 0.0480 | yes |  |
| afraid | וַיִּירְאוּ / תִּירָאוּ | 10 | 11 | 2 | 23 | 5.866 | 17.917 | 1.789 | 5.91e-05 | yes |  |
| sheep | הַצֹּאן / צֹאן | 21 | 25 | 24 | 70 | 5.750 | 11.529 | 1.075 | 0.0031 | yes |  |
| day's | בְּיוֹמוֹ / יוֹם / דַּבֵּר | 0 | 4 | 1 | 5 | 5.730 | 6.182 | 3.494 | 0.0647 |  |  |
| balaam's | בִּלְעָם | 0 | 4 | 1 | 5 | 5.730 | 6.182 | 3.494 | 0.0647 |  |  |
| foreign | הַנֵּכָר / הָיִיתִי / גֵּרְשֹׁם | 1 | 4 | 0 | 5 | 5.730 | 7.625 | 3.494 | 0.0300 | yes |  |
| taskmasters | נֹגְשֵׂי / שֹׁטְרָיו / הַנֹּגְשִׂים | 1 | 4 | 0 | 5 | 5.730 | 7.625 | 3.494 | 0.0300 | yes |  |
| scroll | מִי / אֶמְחֶנּוּ / מִסִּפְרִי׃ | 0 | 4 | 1 | 5 | 5.730 | 6.182 | 3.494 | 0.0647 |  |  |
| flare | יִחַר / אַפְּךָ / אַפִּי | 1 | 4 | 0 | 5 | 5.730 | 7.625 | 3.494 | 0.0300 | yes |  |
| dying | מֵת | 1 | 4 | 0 | 5 | 5.730 | 7.625 | 3.494 | 0.0300 | yes |  |
| fight | לְהִלָּחֵם / אֲנָשִׁים / וְגֵרַשְׁתִּיו׃ | 1 | 4 | 0 | 5 | 5.730 | 7.625 | 3.494 | 0.0300 | yes |  |
| bereaved | שִׁכַּלְתֶּם / כֻלָּנָה׃ / וְשִׁמְעוֹן | 1 | 4 | 0 | 5 | 5.730 | 7.625 | 3.494 | 0.0300 | yes |  |
| felt | וַיְמֻשֵּׁהוּ / הַקֹּל / וְהַיָּדַיִם | 1 | 4 | 0 | 5 | 5.730 | 7.625 | 3.494 | 0.0300 | yes |  |
| following | יַלְדֵיהֶן / אַחֲרֹנִים / רִאשֹׁנָה | 1 | 4 | 0 | 5 | 5.730 | 7.625 | 3.494 | 0.0300 | yes |  |
| nation | לְגוֹי / הַגּוֹי | 3 | 8 | 4 | 15 | 5.431 | 6.026 | 2.090 | 0.0714 |  |  |
| haven't | לֹא | 8 | 9 | 1 | 18 | 5.313 | 16.394 | 1.910 | 1.52e-04 | yes |  |
| moab | מוֹאָב | 7 | 11 | 6 | 24 | 5.296 | 8.326 | 1.678 | 0.0199 | yes |  |
| hear | שָׁמַעְתִּי / שָׁמַע / אָנֹכִי | 2 | 6 | 2 | 10 | 5.152 | 5.845 | 2.440 | 0.0800 |  |  |
| look | הַחוּצָה׃ / יָרֵא / יָקוּמוּ | 3 | 6 | 1 | 10 | 5.152 | 8.043 | 2.440 | 0.0238 | yes |  |
| known | יָדַע / וְאֵדָעֲךָ / יָדַעְתָּ | 6 | 12 | 10 | 28 | 4.860 | 5.477 | 1.509 | 0.0969 |  |  |
| staff | בְּיָדֶךָ / מַטֵּה / הַמַּטֶּה | 2 | 12 | 14 | 28 | 4.860 | 6.279 | 1.509 | 0.0610 |  |  |
| together | יַחְדָּו | 0 | 7 | 6 | 13 | 4.848 | 7.559 | 2.116 | 0.0310 | yes |  |
| cry | צְעָקָה / אֵלַי | 4 | 7 | 2 | 13 | 4.848 | 7.821 | 2.116 | 0.0267 | yes |  |
| bow | וְהִשְׁתַּחֲווּ / תִשְׁתַּחֲוֶה / וַאֲנִי | 5 | 7 | 1 | 13 | 4.848 | 10.873 | 2.116 | 0.0045 | yes |  |
| seen | רָאִיתִי / רְאִיתֶם | 11 | 11 | 3 | 25 | 4.776 | 16.479 | 1.575 | 1.44e-04 | yes |  |
| offered | בַּמִּזְבֵּחַ׃ / וַיַּעַל | 2 | 5 | 1 | 8 | 4.635 | 6.122 | 2.562 | 0.0671 |  |  |
| generation | הַדּוֹר / דֹּר׃ / וְכל | 2 | 5 | 1 | 8 | 4.635 | 6.122 | 2.562 | 0.0671 |  |  |
| about | עַל | 16 | 18 | 15 | 49 | 4.572 | 10.689 | 1.142 | 0.0050 | yes |  |
| increased | וַיָּרֶב / וַיַּעַצְמוּ / וַיִּיטַב | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| abused | לָאָתוֹן / הִתְעַלַּלְתְּ / הֲרַגְתִּיךְ׃ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| nor | מִשִּׁלְשֹׁם / דַּבֶּרְךָ / לָשׁוֹן | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| beaten | וּלְבֵנִים / מֻכִּים / אֹמְרִים | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| beneath | הָאַלּוֹן / בָּכוּת׃ / דְּבֹרָה | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| produced | לִקְמָצִים׃ / וַתַּעַשׂ / בְּשֶׁבַע | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| fat-fleshed | וַתִּרְעֶינָה / בָּאָחוּ׃ / עֹלֹת | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| sukkot | סֻכֹּתָה / וּלְמִקְנֵהוּ / סֻכֹּת | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| snow | מְצֹרַעַת / כַּשָּׁלֶג׃ / וְהֶעָנָן | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| drum | — | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| feeding | רָעִים | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| medad | אֶלְדָּד / בַּמַּחֲנֶה׃ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| ear | וְהַיָּשָׁר / וְהַאֲזַנְתָּ / לְמִצְוֺתָיו | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| ephrat | אֶפְרָתָה | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| quota | וְתֶבֶן / וְתֹכֶן / יִנָּתֵן | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| apparel | כְּסוּתָהּ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| eldad | אֶלְדָּד / בַּמַּחֲנֶה׃ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| innocence | בְּתם / גַּם / זֹאת | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| heaps | חֳמָרִם / וַתִּבְאַשׁ / וְיִצְבְּרוּ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| mo-riah | הַמֹּרִיָּה / וְהַעֲלֵהוּ / אָהַבְתָּ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| belongings | מִשַּׁשְׁתָּ / וְיוֹכִיחוּ / שְׁנֵינוּ׃ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| piled | וַיִּצְבֹּר / לִסְפֹּר / הַרְבֵּה | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| station | כַּנִּי / וְאֹתוֹ / הֵשִׁיב | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| oppress | וְגֵר / הֱיִיתֶם / גֵרִים | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| theft | הִמָּצֵא / הַגְּנֵבָה / תִּמְצָא | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| disgust | מִפְּנֵי | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| bad-looking | רָעוֹת / הַפָּרוֹת / וְדַקּוֹת | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| straying | תֹעֶה | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| tongue | יֶחֱרַץ / לְשֹׁנוֹ / לְמֵאִישׁ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| prophesied | וַיִּתְנַבְּאוּ / הָרוּחַ / וַיָּאצֶל | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| keturah | קְטוּרָה׃ / וַיֹּסֶף / וּשְׁמָהּ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| shattered | שֶׁבֶר / וְעַד / מֵאָדָם | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| sacrificed | וְלַשָּׂרִים / וַיִּזְבַּח / לְבִלְעָם | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| abimelek's | אֲבִימֶלֶךְ / עָצֹר / בְּעַד | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| hanged | תָּלָה / כַּאֲשֶׁר / הָאֹפִים | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| seized | וְהוֹכִחַ / גָּזְלוּ / אֹדוֹת | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| dealt | גְמָלוּךָ / לְפֶשַׁע / בְּדַבְּרָם | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| fields | וַיִּקְבֹּץ / סְבִיבֹתֶיהָ / שְׂדֵה | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| distress | אֲשֵׁמִים / צָרַת / בְּהִתְחַנְנוֹ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| matters | דְּבָרִים / יִגַּשׁ / בַּעַל | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| difficulty | בְּלִדְתָּהּ / בְהַקְשֹׁתָהּ / תִּירְאִי | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| sickness | וּבֵרַךְ / לַחְמְךָ / מִקִּרְבֶּךָ׃ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| vein | גִּיד / הַנָּשֶׁה / הַיָּרֵךְ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| baker | וְהָאֹפֶה / לַמֹּלֶךְ / לַאֲדֹנֵיהֶם | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| goring | נַגָּח / יִשְׁמְרֶנּוּ / מִתְּמוֹל | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| shower | וְהַבָּרָד / וּמָטָר / נִתַּךְ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| hilltop | הַגִּבְעָה / רֹאשׁ / בַּעֲמָלֵק | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| fiery | הַנְּחָשִׁים / וַיְנַשְּׁכוּ / הַשְּׂרֻפִים | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| withhold | חָשַׂכְתָּ / יַעַן / בִּי | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| grace | אַעֲבִיר / טוּבִי / וְחַנֹּתִי | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| help | בְּעֶזְרִי / וַיַּצִּלֵנִי / מֵחֶרֶב | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| whomever | אַעֲבִיר / טוּבִי / וְחַנֹּתִי | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| knees | בִּרְכֵּי / שְׁלֹשִׁים / לְאֶפְרַיִם | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| sunset | הַשֶּׁמֶשׁ / בָּא / חָבֹל | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| horses | בַּסּוּסִים | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| phichol | וַיָּשֻׁבוּ / וּפִיכֹל / צְבָאוֹ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| fence | בְּמִשְׁעוֹל / הַכְּרָמִים / גָּדֵר | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| drawn | וְחַרְבּוֹ / בְּיָדוֹ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| houseful | לַעֲבֹר / וְזָהָב / מְלֹא | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| headrest | מְרַאֲשֹׁתָיו / רֹאשָׁהּ׃ / מֵאַבְנֵי | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| jokshan | וְאֶת | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| flock's | רְחֵלֶיךָ / וְעִזֶּיךָ / שִׁכֵּלוּ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| empty | בּוֹ / וַיַּשְׁלִכוּ / הַבֹּרָה | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| cushite | הַכֻּשִׁית / כֻשִׁית / וַתְּדַבֵּר | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| advise | אִיעָצְךָ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| dough | וַיֹּאפוּ / הַבָּצֵק / עֻגֹת | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| injured | אֵין / וְנִשְׁבַּר / מֵת | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| bribery | תֶחֱזֶה / יִרְאֵי / שֹׂנְאֵי | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| tens | חַיִל / עֲשֶׂרֶת / חֲמִשִּׁים | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| memory | זְכַרְתַּנִי / וְהִזְכַּרְתַּנִי / וְהוֹצֵאתַנִי | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| hattaavah | הַתַּאֲוָה / קִבְרוֹת / הַמִּתְאַוִּים׃ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| potiphera | וּלְיוֹסֵף / אוֹן׃ / תָבוֹא | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| stalk | וְטֹבוֹת׃ / בְּקָנֶה / שִׁבֳּלִים | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| beautiful-looking | וְדַקֹּת / וְהַבְּרִיאֹת / הַמַּרְאֶה | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| weaned | וַיִּגָּמַל / הַגָּמָל / הַיֶּלֶד | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| writing | וְהַלֻּחֹת / וְהַמִּכְתָּב / חָרוּת | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| testing | לְבַעֲבוּר / נַסּוֹת / וּבַעֲבוּר | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| kibroth | הַתַּאֲוָה / קִבְרוֹת / הַמִּתְאַוִּים׃ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| longing | וְהָאסַפְסֻף / הִתְאַוּוּ / וַיִּבְכּוּ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| baskets | הַסַּלִּים / סַלֵּי / חֹרִי | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| fifties | חַיִל / עֲשֶׂרֶת / חֲמִשִּׁים | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| predominate | וְגָבַר / וְכַאֲשֶׁר / יָנִיחַ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| heed | לִבּוֹ / שָׁת / לְזֹאת | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| flax | וְהַפִּשְׁתָּה / וְהַשְּׂעֹרָה / נֻכָּתָה | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| dream's | כְּפִתְרוֹן / חֲלֹמוֹ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| dog | תִּהְיוּן / לַכֶּלֶב / תַּשְׁלִכוּן | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| thin-fleshed | רָעוֹת / הַפָּרוֹת / וְדַקּוֹת | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| dothan | דֹּתָיְנָה / וַיִּמְצָאֵם / בְּדֹתָן׃ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| tendon | גִּיד / הַנָּשֶׁה / הַיָּרֵךְ | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| adversary | לְשָׂטָן | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| sword | חֶרֶב / בֶּחָרֶב | 7 | 12 | 10 | 29 | 4.412 | 5.578 | 1.424 | 0.0927 |  |  |
| snake | הַנָּחָשׁ | 5 | 6 | 0 | 11 | 4.267 | 13.741 | 2.151 | 7.93e-04 | yes |  |
| tablets | לֻחֹת / הַלֻּחֹת / וּשְׁנֵי | 2 | 6 | 3 | 11 | 4.267 | 4.558 | 2.151 | 0.1414 |  |  |
| signs | אֹתֹתַי / הָאֹתֹת / וְאֶת | 2 | 6 | 3 | 11 | 4.267 | 4.558 | 2.151 | 0.1414 |  |  |
| calf | הָעֵגֶל / עֵגֶל / עֵשָׂו | 2 | 6 | 3 | 11 | 4.267 | 4.558 | 2.151 | 0.1414 |  |  |
| egypt's | מִצְרַיִם | 6 | 10 | 7 | 23 | 4.208 | 5.796 | 1.547 | 0.0825 |  |  |
| slaves | עֲבָדִים / מִבֵּית | 1 | 4 | 1 | 6 | 4.171 | 4.517 | 2.758 | 0.1414 |  |  |
| neighbor's | רֵעֵהוּ / בִּמְלֶאכֶת / שָׁלַח | 0 | 4 | 2 | 6 | 4.171 | 5.075 | 2.758 | 0.1250 |  |  |
| please | בִּי / אָנָּא | 2 | 4 | 0 | 6 | 4.171 | 7.960 | 2.758 | 0.0249 | yes |  |
| aren't | הֲלוֹא / אֲלֵיהֶם | 2 | 4 | 0 | 6 | 4.171 | 7.960 | 2.758 | 0.0249 | yes |  |
| numerous | רַב / בִּמְאֹד / עִם | 0 | 4 | 2 | 6 | 4.171 | 5.075 | 2.758 | 0.1250 |  |  |
| degradation | רְאֵה / ענְיִי | 2 | 4 | 0 | 6 | 4.171 | 7.960 | 2.758 | 0.0249 | yes |  |
| swore | נִשְׁבַּע / נִשְׁבַּעְתִּי / וַיִּשָּׁבַע | 8 | 9 | 3 | 20 | 4.139 | 11.354 | 1.634 | 0.0035 | yes |  |
| sound | קוֹל | 4 | 8 | 5 | 17 | 4.106 | 5.025 | 1.749 | 0.1292 |  |  |
| whom | אֲשֶׁר | 20 | 29 | 43 | 92 | 3.981 | 4.507 | 0.804 | 0.1414 |  |  |
| leprous | יְטַמְּאֶנּוּ / נִגְעוֹ׃ / בְּרֹאשׁוֹ | 0 | 3 | 1 | 4 | 3.845 | 4.297 | 3.132 | 0.1585 |  |  |
| rest | וַהֲנִחֹתִי / יֵלְכוּ / יָנוּחַ | 1 | 3 | 0 | 4 | 3.845 | 5.740 | 3.132 | 0.0846 |  |  |
| bank | שְׂפַת | 1 | 3 | 0 | 4 | 3.845 | 5.740 | 3.132 | 0.0846 |  |  |
| answer | וְחָזֵק / יַעֲנֶנּוּ / וְהָאֱלֹהִים | 1 | 3 | 0 | 4 | 3.845 | 5.740 | 3.132 | 0.0846 |  |  |
| letting | אִם / מַשְׁלִיחַ / וּבְבָתֶּיךָ | 1 | 3 | 0 | 4 | 3.845 | 5.740 | 3.132 | 0.0846 |  |  |
| bones | עַצְמֹתַי / יִפְקֹד / מִזֶּה | 1 | 3 | 0 | 4 | 3.845 | 5.740 | 3.132 | 0.0846 |  |  |
| sow | תִּזְרַע / וּזְרַעְתֶּם / אַרְצֶךָ | 0 | 3 | 1 | 4 | 3.845 | 4.297 | 3.132 | 0.1585 |  |  |
| met | וַיִּפְגְּשֵׁהוּ / בְּצֵאתָם / וַיִּפְגְּעוּ | 1 | 3 | 0 | 4 | 3.845 | 5.740 | 3.132 | 0.0846 |  |  |
| oak | אֵלוֹן | 1 | 3 | 0 | 4 | 3.845 | 5.740 | 3.132 | 0.0846 |  |  |
| driven | וַתְּנַהֵג / כִּשְׁבֻיוֹת / לְבָבִי | 0 | 3 | 1 | 4 | 3.845 | 4.297 | 3.132 | 0.1585 |  |  |
| crossed | וַיַּעֲבֹר | 1 | 3 | 0 | 4 | 3.845 | 5.740 | 3.132 | 0.0846 |  |  |
| stoned | יִסָּקֵל | 1 | 3 | 0 | 4 | 3.845 | 5.740 | 3.132 | 0.0846 |  |  |
| growing | דַּקּוֹת / צֹמְחוֹת / שִׁבֳּלִים | 0 | 3 | 1 | 4 | 3.845 | 4.297 | 3.132 | 0.1585 |  |  |
| such | כָזֶה / הֲנִמְצָא / אֱלֹהִים | 1 | 3 | 0 | 4 | 3.845 | 5.740 | 3.132 | 0.0846 |  |  |
| thought | חֲשַׁבְתֶּם / חֲשָׁבָהּ / לְטֹבָה | 1 | 3 | 0 | 4 | 3.845 | 5.740 | 3.132 | 0.0846 |  |  |
| kill | וְהָרְגוּ / וְאָמְרוּ / אִשְׁתִּי | 13 | 13 | 8 | 34 | 3.770 | 11.883 | 1.238 | 0.0025 | yes |  |
| strong | חֲזָקָה׃ / חָזָק / וַיֶּחֱזַק | 9 | 10 | 5 | 24 | 3.749 | 9.897 | 1.444 | 0.0081 | yes |  |
| they've | וְהַבָּנִים / צֹאנִי / לִבְנֵיהֶן | 4 | 5 | 0 | 9 | 3.692 | 11.271 | 2.199 | 0.0037 | yes |  |
| items | הַכֵּלִים / וַיִּשְׁאֲלוּ / כְּלִי | 0 | 5 | 4 | 9 | 3.692 | 5.499 | 2.199 | 0.0955 |  |  |
| thin | דַּק | 0 | 5 | 4 | 9 | 3.692 | 5.499 | 2.199 | 0.0955 |  |  |
| one's | וְשֵׁם / הָאֶחָד | 4 | 5 | 0 | 9 | 3.692 | 11.271 | 2.199 | 0.0037 | yes |  |
| built | וַיִּבֶן | 8 | 9 | 4 | 21 | 3.645 | 9.591 | 1.514 | 0.0099 | yes |  |
| threw | וַיַּשְׁלֵךְ / וַיְהִי | 2 | 6 | 4 | 12 | 3.542 | 3.630 | 1.910 | 0.2230 |  |  |
| matter | דַּבֵּר | 1 | 6 | 5 | 12 | 3.542 | 3.796 | 1.910 | 0.2008 |  |  |
| beth-el | בֵּית | 5 | 6 | 1 | 12 | 3.542 | 9.568 | 1.910 | 0.0099 | yes |  |
| everything | כּל / וְכל | 12 | 24 | 39 | 75 | 3.535 | 3.752 | 0.838 | 0.2067 |  |  |
| festival | חַג | 5 | 7 | 3 | 15 | 3.521 | 6.715 | 1.729 | 0.0480 | yes |  |
| big | גְדֹלָה / גָּדוֹל | 15 | 15 | 13 | 43 | 3.162 | 9.561 | 1.031 | 0.0100 | yes |  |
| drove | וַיִּנְהַג | 2 | 4 | 1 | 7 | 3.124 | 4.611 | 2.272 | 0.1414 |  |  |
| sitting | יֹשֵׁב | 2 | 4 | 1 | 7 | 3.124 | 4.611 | 2.272 | 0.1414 |  |  |
| offspring | שֶׁגֶר / הַזְּכָרִים / עִמָּךְ | 1 | 4 | 2 | 7 | 3.124 | 3.168 | 2.272 | 0.2834 |  |  |
| refused | וַיְמָאֵן / מֵאֵן | 3 | 4 | 0 | 7 | 3.124 | 8.809 | 2.272 | 0.0152 | yes |  |
| seeing | רְאֵה / אֵין / מִנְחָתִי | 2 | 4 | 1 | 7 | 3.124 | 4.611 | 2.272 | 0.1414 |  |  |
| ephraim's | אֶפְרַיִם | 0 | 4 | 3 | 7 | 3.124 | 4.480 | 2.272 | 0.1414 |  |  |
| altars | מִזְבְּחֹת / שִׁבְעָה / וְהַמְּנֹרָה | 1 | 4 | 2 | 7 | 3.124 | 3.168 | 2.272 | 0.2834 |  |  |
| streaked | עֲקֻדִּים / נְקֻדִּים | 3 | 4 | 0 | 7 | 3.124 | 8.809 | 2.272 | 0.0152 | yes |  |
| hasn't | וְלֹא / הֲרַק / הֲלֹא | 2 | 4 | 1 | 7 | 3.124 | 4.611 | 2.272 | 0.1414 |  |  |
| bulls | פָּרִים | 0 | 4 | 3 | 7 | 3.124 | 4.480 | 2.272 | 0.1414 |  |  |
| gone | וּבְנֵי / עֹלָה / הַיֹּצְאִים | 4 | 8 | 7 | 19 | 3.088 | 3.428 | 1.474 | 0.2519 |  |  |
| strike | וְהִכֵּיתִי / יַכֶּה / וְכִי | 10 | 10 | 6 | 26 | 2.955 | 9.342 | 1.258 | 0.0112 | yes |  |
| forever | לְעֹלָם | 3 | 5 | 2 | 10 | 2.952 | 4.685 | 1.910 | 0.1414 |  |  |
| leavened | חָמֵץ | 1 | 5 | 4 | 10 | 2.952 | 3.045 | 1.910 | 0.3042 |  |  |
| since | אֹתִי / וּמֵאָז / בִּשְׁמֶךָ | 5 | 5 | 0 | 10 | 2.952 | 12.425 | 1.910 | 0.0018 | yes |  |
| cup | הַגָּבִיעַ / בְּיָדוֹ | 5 | 5 | 0 | 10 | 2.952 | 12.425 | 1.910 | 0.0018 | yes |  |
| kissed | וַיִּשַּׁק / וַיְנַשֵּׁק | 5 | 5 | 0 | 10 | 2.952 | 12.425 | 1.910 | 0.0018 | yes |  |
| sell | יִמְכֹּר / מָכְרוּ | 2 | 5 | 3 | 10 | 2.952 | 3.242 | 1.910 | 0.2834 |  |  |
| slave | עֶבֶד | 1 | 5 | 4 | 10 | 2.952 | 3.045 | 1.910 | 0.3042 |  |  |
| child | בִּנְךָ / זֶה / בְכֹרִי | 3 | 5 | 2 | 10 | 2.952 | 4.685 | 1.910 | 0.1414 |  |  |
| hivite | הַחִוִּי | 4 | 5 | 1 | 10 | 2.952 | 7.373 | 1.910 | 0.0348 | yes |  |
| edge | בִּקְצֵה / קְצֵה / קָצֵהוּ׃ | 3 | 6 | 4 | 13 | 2.938 | 3.534 | 1.703 | 0.2375 |  |  |
| behind | וַיִּסַּע / מֵאַחֲרֵיהֶם / אַחֲרֵינוּ׃ | 5 | 6 | 2 | 13 | 2.938 | 7.274 | 1.703 | 0.0371 | yes |  |
| listen | שָׁמַע / וְלֹא / תִשְׁמְעוּ | 8 | 15 | 21 | 44 | 2.893 | 2.898 | 0.981 | 0.3223 |  |  |
| more | עוֹד | 12 | 13 | 12 | 37 | 2.816 | 6.975 | 1.050 | 0.0441 | yes |  |
| should | מֵאֶרֶץ / אוֹצִיא / אֵלֵךְ׃ | 5 | 9 | 9 | 23 | 2.806 | 3.183 | 1.300 | 0.2834 |  |  |
| fleeing | מִפְּנֵי | 2 | 3 | 0 | 5 | 2.576 | 6.365 | 2.395 | 0.0586 |  |  |
| epidemic | בְּדַבֵּר | 1 | 3 | 1 | 5 | 2.576 | 2.922 | 2.395 | 0.3223 |  |  |
| weak | עֹלוֹת / תֶהְדַּר / הֶחָזָק | 1 | 3 | 1 | 5 | 2.576 | 2.922 | 2.395 | 0.3223 |  |  |
| alone | לְבַדּוֹ | 1 | 3 | 1 | 5 | 2.576 | 2.922 | 2.395 | 0.3223 |  |  |
| what's | מַה | 1 | 3 | 1 | 5 | 2.576 | 2.922 | 2.395 | 0.3223 |  |  |
| garments | וּשְׂמָלֹת / וּבְנֵי / וּכְלֵי | 2 | 3 | 0 | 5 | 2.576 | 6.365 | 2.395 | 0.0586 |  |  |
| provide | אֲכַלְכֵּל / לִבָּם / אוֹתָם | 2 | 3 | 0 | 5 | 2.576 | 6.365 | 2.395 | 0.0586 |  |  |
| nothing | תִּרְאֶנּוּ / וְכֻלּוֹ / וְקבְנוֹ | 2 | 3 | 0 | 5 | 2.576 | 6.365 | 2.395 | 0.0586 |  |  |
| woke | וַיִּיקַץ | 2 | 3 | 0 | 5 | 2.576 | 6.365 | 2.395 | 0.0586 |  |  |
| feed | יַאֲכִלֵנוּ / יִרְעוּ / יַעֲלֶה | 2 | 3 | 0 | 5 | 2.576 | 6.365 | 2.395 | 0.0586 |  |  |
| feared | הַיָּרֵא / מֵעַבְדֵי / הֵנִיס | 2 | 3 | 0 | 5 | 2.576 | 6.365 | 2.395 | 0.0586 |  |  |
| innocent | וְנִקָּה | 2 | 3 | 0 | 5 | 2.576 | 6.365 | 2.395 | 0.0586 |  |  |
| wipe | אֶמְחֶה / מֵעַל / הָאֲדָמָה | 2 | 3 | 0 | 5 | 2.576 | 6.365 | 2.395 | 0.0586 |  |  |
| young | בִּנְעָרֵינוּ / וּבִזְקֵנֵינוּ / בְּבָנֵינוּ | 2 | 3 | 0 | 5 | 2.576 | 6.365 | 2.395 | 0.0586 |  |  |
| nose | לְאַפָּיו | 2 | 3 | 0 | 5 | 2.576 | 6.365 | 2.395 | 0.0586 |  |  |
| three | שָׁלֹשׁ / שְׁלֹשָׁה / שְׁלֹשֶׁת | 16 | 23 | 37 | 76 | 2.574 | 2.780 | 0.723 | 0.3223 |  |  |
| that's | בּוֹ / אֲשֶׁר / כֹּה | 4 | 7 | 6 | 17 | 2.538 | 3.119 | 1.424 | 0.2906 |  |  |
| word | פִּי / דַּבֵּר | 7 | 14 | 21 | 42 | 2.464 | 2.502 | 0.935 | 0.3223 |  |  |
| man's | וְאִישׁ / אִישׁ / הָאִישׁ | 3 | 6 | 5 | 14 | 2.430 | 2.738 | 1.523 | 0.3223 |  |  |
| gathered | וַיֶּאֱסֹף | 6 | 12 | 17 | 35 | 2.367 | 2.372 | 0.999 | 0.3223 |  |  |
| ask | יִּשְׁאַל / נָא / וְעַל | 3 | 4 | 1 | 8 | 2.362 | 5.252 | 1.909 | 0.1123 |  |  |
| jebusite | וְהַחִתִּי / וְהַיְבוּסִי / וְהָאֱמֹרִי | 4 | 4 | 0 | 8 | 2.362 | 9.940 | 1.909 | 0.0079 | yes |  |
| fish | וּבְכל / דְּגֵי / הַיָּם | 0 | 4 | 4 | 8 | 2.362 | 4.169 | 1.909 | 0.1717 |  |  |
| hebrew | עִבְרִי | 4 | 4 | 0 | 8 | 2.362 | 9.940 | 1.909 | 0.0079 | yes |  |
| case | פֶּן | 5 | 5 | 1 | 11 | 2.358 | 8.383 | 1.669 | 0.0191 | yes |  |
| chief | שַׂר / אַלּוּף | 13 | 16 | 21 | 50 | 2.356 | 3.849 | 0.846 | 0.1938 |  |  |
| treachery | יָזִד / לְהרְגוֹ / בְערְמָה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| communicate | לְבָלָק / יִקָּרֵה / וְהִגַּדְתִּי | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| delaying | בֹשֵׁשׁ / לָרֶדֶת / עָשָׂה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| thirst | וַיִּצְמָא / מִקְנַי / בַּצָּמָא׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| read | סַפֵּר / וְנִשְׁמָע׃ / וַיִּקְרָא | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| spelt | וְהַחִטָּה / וְהַכֻּסֶּמֶת / נֻכּוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| flashes | רֹאִים / הַקּוֹלֹת / הַלַּפִּידִם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| despise | יִשְׂטְמֵנוּ / וְהָשֵׁב / גָּמַלְנוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| second-in-command | וַיַּרְכֵּב / בְּמִרְכֶּבֶת / הַמִּשְׁנֶה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| started | וַתְּחִלֶּינָה / הָאֲרָצוֹת / וּבְכל | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| adversaries | לְשִׁמְצָה / בְּקָמֵיהֶם׃ / פַּרְעֹה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| appease | בַּמִּנְחָה / לְ / הַהֹלֶכֶת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| direction | וַיָּגז / שַׂלְוִים / וַיִּטֹּשׁ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| humble | עָנָו / וְהָאִישׁ / מִכּל | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| opponent | וְאָיַבְתִּי / וְצַרְתִּי / צֹרְרֶיךָ׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| stairs | תַעֲלֶה / בְמַעֲלֹת / מִזִּבְחֵי | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| visions | בְּמַרְאֹת / לְיִשְׂרָאֵל | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| songs | נַחְבֵּאתָ / בְּשִׂמְחָה / וּבְשִׁרִים | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| structure | וְתַחַת / הַסַּפִּיר / וּכְעֶצֶם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| longed | נִכְסֹף / נִכְסַפְתָּה / גָנַבְתָּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| person's | בְּעִירֹה / מֵיטַב / וּמֵיטַב | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| dismal | אֲפֵלָה / שְׁלֹשֶׁת / מִצְרַיִם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| nimbus | הָעֲרָפֶל / נִגַּשׁ / וּמֹשֶׁה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| massah | מַסָּה / וּמְרִיבָה / נַסֹּתָם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| espouse | יְפַתֶּה / אֹרָשָׂה / יִמְהָרֶנָּה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| olam | אֶשֶׁל / עוֹלָם / בְּשֵׁם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| enigmas | בְחִידֹת / וּתְמֻנַת / יַבִּיט | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| conform | יִשַּׁק / הַכִּסֵּא / אֶגְדַּל | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| exhaustion | לוּלֵי / וּפַחַד / יְגִיעַ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| stacked | וּמָצְאָה / קֹצִים / וְנֶאֱכַל | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| merchants | מִדְיָנִים / סֹחֲרִים / וַיִּמְשְׁכוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| onions | זָכַרְנוּ / הַדָּגָה / הַקִּשֻּׁאִים | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| descended | וּבְרֶדֶת / יֵרֵד / הַטַּל | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| hornet | הַצִּרְעָה / וְגֵרְשָׁה / מִלְּפָנֶיךָ׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| camel's | וַתְּשִׂמֵם / וַיְמַשֵּׁשׁ / הַגָּמָל | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| posterity | תִּשְׁקֹר / וּלְנִינִי / וּלְנֶכְדִּי | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| dances | הַנְּבִיאָה / הַתֹּף / וַתֵּצֶאןָ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| lingered | וַיָּנַח / וְאַחֲרָיו / לְפָנָיו | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| odor | וַיִּבְאַשׁ / מֵתָה / וְהַדָּגָה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| surroundings | יְלַחֲכוּ / סְבִיבֹתֵינוּ / כִּלְחֹךְ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| grumblers | כְּמִתְאֹנְנִים / וַתִּבְעַר / וַיְהִי | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| doorpost | וְהִגִּישׁוֹ / הַמְּזוּזָה / וְרָצַע | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| saddle | וַתְּשִׂמֵם / וַיְמַשֵּׁשׁ / הַגָּמָל | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| reminder | וּלְזִכָּרוֹן / בְּפִיךָ / הוֹצִאֲךָ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| penalized | יִנָּצוּ / וְנָגְפוּ / יְלָדֶיהָ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| mute | יָשׂוּם / אִלֵּם / פִקֵּחַ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| sapphire | נֹפֶךְ / סַפִּיר / וְיָהֲלֹם׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| perform | יְבִיאֲךָ / לַאֲבֹתֶיךָ / וְעָבַדְתָּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| ashurim | וְיקְשָׁן / דְּדָן / אַשּׁוּרִם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| goods | וּבַסַּל / הָעֶלְיוֹן / מַעֲשֵׂה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| homers | הַמּחֳרָת / הַמַּמְעִיט / וַיִּשְׁטְחוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| relent | בֶּהָרִים / וּלְכַלֹּתָם / מֵחֲרוֹן | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| wheel | אֹפַן / מַרְכְּבֹתָיו / וַיְנַהֲגֵהוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| bad-figured | דַּלּוֹת / וְרָעוֹת / וְרַקּוֹת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| thrust | וַתַּשְׁלֵךְ / הַשִּׂיחִם׃ / וַיְכֻלּוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| original | וַהֲשִׁיבְךָ / כַּנֶּךָ / הָיִיתָ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| healer | וְהַיָּשָׁר / וְהַאֲזַנְתָּ / לְמִצְוֺתָיו | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| medanites | וְהַמְּדָנִים / לְפוֹטִיפַר / מָכְרוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| divinations | כְּפַעַם / נְחָשִׁים / לְבָרֵךְ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| laughter | צְחֹק / הַשֹּׁמֵעַ / יִצְחָק | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| highest | וּבַסַּל / הָעֶלְיוֹן / מַעֲשֵׂה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| lick | יְלַחֲכוּ / סְבִיבֹתֵינוּ / כִּלְחֹךְ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| shepherded | הִתְהַלְּכוּ / מֵעוֹדִי / הָרָעָה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| testified | מִתְּמֹל / וְהוּעַד / בִּבְעָלָיו | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| garlics | זָכַרְנוּ / הַדָּגָה / הַקִּשֻּׁאִים | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| recalling | חֲטָאַי / מַזְכִּיר / אֲנִי | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| opponents | וְאָיַבְתִּי / וְצַרְתִּי / צֹרְרֶיךָ׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| sustained | וּבְמִקְנֵה / וּבַחֲמֹרִים / וַיְנַהֲלֵם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| work-companies | מִסִּים / עַנֹּתוֹ / מִסְכְּנוֹת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| safe | שַׁלֵּם / פְּנֵי / עִיר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| crops | וְהַחִטָּה / וְהַכֻּסֶּמֶת / נֻכּוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| harvests | בַּתְּבוּאֹת / הַיָּדֹת / וּלְאכְלְכֶם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| father-in-law's | חֹתְנוֹ / אָמַר / לְקוֹל | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| graze | בְּעִירֹה / מֵיטַב / וּמֵיטַב | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| late | וְהַחִטָּה / וְהַכֻּסֶּמֶת / נֻכּוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| blaspheme | בְעַמְּךָ / תְקַלֵּל / תֹּאַר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| happiness | נַחְבֵּאתָ / בְּשִׂמְחָה / וּבְשִׁרִים | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| prophesying | וּמֵידָד / מִתְנַבְּאִים / לְמֹשֶׁה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| blazed | בְּלָבָן / פִּשְׁעִי / דָלַקְתָּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| outer | וַיַּעֲלֵהוּ / בְּמוֹת / בַּעַל | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| shuah | זִמְרָן / יקְשָׁן / מְדָן | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| might | יְדַעְתֶּן / כֹּחִי / אֲבִיכֶן | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| heal | רְפָא / נָא / לָהּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| weeping | הָאַלּוֹן / בָּכוּת׃ / דְּבֹרָה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| medan | זִמְרָן / יקְשָׁן / מְדָן | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| bold | וֶאֱמָץ / אֶהְיֶה / תָּבִיא | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| pethor | פְּתוֹרָה / כִסָּה / מִמֻּלִי׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| looks | הַפְּעוֹר / הַנִּשְׁקָף / הַיְשִׁימֹן׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| clusters | וּבַגֶּפֶן / שָׂרִיגִם / כְפֹרַחַת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| pierce | וְהִגִּישׁוֹ / הַמְּזוּזָה / וְרָצַע | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| foreigners | נכְרִיּוֹת / נֶחְשַׁבְנוּ / מְכָרָנוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| graves | הֲמִבְּלִי / קְבָרִים / לְקַחְתָּנוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| leummim | וְיקְשָׁן / דְּדָן / אַשּׁוּרִם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| undermine | וְשֹׁחַד / הַשֹּׁחַד / יְעַוֵּר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| precipitous | שָׁלוֹשׁ / יָצָאתִי / יָרַט | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| supported | וִידֵי / כְּבֵדִים / תָּמְכוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| forgot | וַיִּשְׁכָּחֵהוּ׃ / זָכָר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| ladder | סֻלָּם / מֻצָּב / מַגִּיעַ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| creamy | שָׁטוּ / וְטָחֲנוּ / בָרֵחַיִם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| distinction | פְדֻת / הָאֹת / וְשַׂמְתִּי | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| survived | הַפְּלֵטָה / הַנִּשְׁאֶרֶת / הַצֹּמֵחַ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| nile's | סְבִיבֹת / מִמֵּימֵי / לִשְׁתֹּת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| greeting | וַיִּשְׂנְאוּ / לְשָׁלֹם׃ / דַּבְּרוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| armed | וַחֲמִשִּׁים / וַיִּסֹּב / עָלוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| tore | וַיִּקְרַע / אֵין / בַּבּוֹר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| vineyards | בְּמִשְׁעוֹל / הַכְּרָמִים / גָּדֵר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| prophets | הַמְקַנֵּא / נְבִיאִים / וּמֵי | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| pathway | בְּמִשְׁעוֹל / הַכְּרָמִים / גָּדֵר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| latter | לְקֹל / וְהֶאֱמִינוּ / הָאַחֲרוֹן׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| dissuaded | בְּשַׁלַּח / נָחָם / יִנָּחֵם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| gal | — | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| teeth | וְאַף / חָרָה / יִכָּרֵת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| zaphenathpaneah | צָפְנַת / פַּעְנֵחַ / אֹן | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| lend | תַּלְוֶה / הֶעָנִי / כְּנֹשֶׁה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| olives | וְהַשְּׁבִיעִת / תִּשְׁמְטֶנָּה / וּנְטַשְׁתָּהּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| reaching | סֻלָּם / מֻצָּב / מַגִּיעַ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| divested | וַיִּתְנַצְּלוּ / חוֹרֵב׃ / עֶדְיָם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| means | לְאֵל / אֶמֶשׁ / יֶשׁ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| cleanness | וּבְנִקְיֹן / לְבָבִי / אָמְרָה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| regularly | הַחֻקָּה / לְמוֹעֲדָהּ / מִיָּמִים | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| beast | בְּעִירֹה / מֵיטַב / וּמֵיטַב | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| humbled | מֵאַנְתָּ / לֵעָנֹת / מִפְּנֵי | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| emptying | מְרִיקִים / שַׂקֵּיהֶם / בְּשַׂקּוֹ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| behalf | וָבָךְ / הִתְפַּלֵּל / מֵעָלֵינוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| revealed | נִגְלוּ / בְּברְחוֹ / לַמָּקוֹם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| well-being | בִּלְעָדָי / יַעֲנֶה / שָׁלוֹם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| orphan | וְיָתוֹם / תְעַנּוּן׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| judged | יְבִיאוּן / יִשְׁפּוּטוּ / הִקְשָׁה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| hit | שְׁלוּפָה / לְהַטֹּתָהּ / וַיַּךְ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| widows | וְחָרָה / וְהָרַגְתִּי / אַלְמָנוֹת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| forgotten | וְנִשְׁכַּח / וְקָמוּ / אַחֲרֵיהֶן | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| thirsted | וַיִּצְמָא / מִקְנַי / בַּצָּמָא׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| relented | לְעַמּוֹ׃ / וַיִּנָּחֶם / הָרָעָה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| tells | יֵרַע / בְּקֹלָהּ / בְיִצְחָק | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| chain | טַבַּעְתּוֹ / רְבִד / וַיָּסַר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| criticized | וְהוֹכִחַ / גָּזְלוּ / אֹדוֹת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| unrecognizable | וַיַּכִּרֵם / וַיִּתְנַכֵּר / בָּאתֶם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| hired | בִּשְׂכָרוֹ׃ / שָׂכִיר / עִמּוֹ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| tones | וַיַּכִּרֵם / וַיִּתְנַכֵּר / בָּאתֶם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| miss | הֵבֵאתִי / אֲחַטֶּנָּה / תְּבַקְשֶׁנָּה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| foods | וּבַסַּל / הָעֶלְיוֹן / מַעֲשֵׂה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| moment | רֶגַע / וְכִלִּיתִיךָ / עֶדְיְךָ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| change | הָסִרוּ / וְהַחֲלִיפוּ / שִׂמְלֹתֵיכֶם׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| ford | שִׁפְחֹתָיו / יְלָדָיו / מֵעֵבֶר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| humiliated | וְאָבִיהָ / בְּפָנֶיהָ / תִכָּלֵם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| angered | בְּלָבָן / פִּשְׁעִי / דָלַקְתָּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| snakes | הַנְּחָשִׁים / וַיְנַשְּׁכוּ / הַשְּׂרֻפִים | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| implored | אֲשֵׁמִים / צָרַת / בְּהִתְחַנְנוֹ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| oh | רְפָא / נָא / לָהּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| dreaming | חֹלֵם / שְׁנָתַיִם / וּפַרְעֹה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| rise | וְנִשְׁכַּח / וְקָמוּ / אַחֲרֵיהֶן | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| prodding | וְהַנֹּגְשִׂים / אָצִים / בִּהְיוֹת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| prestigious | שָׂרִים / וְנִכְבָּדִים / רַבִּים | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| responded | וַיַּעֲנוּ / נַעֲשֶׂה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| five-out | פְּקִדִים / וַיִּפְקֹד / וַחֲמֵשׁ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| toyed | וַאֲבִיכֶן / וְהֶחֱלִף / נִתָּנוּ׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| itself | עֵדֶר / תָּשִׂימוּ / וְרוּחַ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| shepherding | חֹרֵבָה׃ / אַחַר / רָעָה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| huzoth | חֻצוֹת׃ / עִם / קִרְיַת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| ridden | רָכַבְתָּ / מֵעוֹדְךָ / הַהַסְכֵּן | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| essence | וְתַחַת / הַסַּפִּיר / וּכְעֶצֶם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| puah | שִׁפְרָה / פּוּעָה׃ / הָעִבְרִיֹּת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| interpreter | הַמֵּלִיץ / בֵּינֹתָם׃ / שָׁמַע | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| victory | עֲנוֹת / גְּבוּרָה / חֲלוּשָׁה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| neither | מִשִּׁלְשֹׁם / דַּבֶּרְךָ / לָשׁוֹן | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| enlighten | וְהִזְהַרְתָּה / הַתּוֹרֹת / וְהוֹדַעְתָּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| coffin | בָּאָרוֹן / ויישם / וָעֶשֶׂר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| rameses | מִסִּים / עַנֹּתוֹ / מִסְכְּנוֹת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| meets | יִפְגָּשְׁךָ / וִשְׁאֵלְךָ / וּלְמִי | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| absence | — | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| founding | לְמִן / הִוָּסְדָה / מַמְטִיר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| shrubs | וַתַּשְׁלֵךְ / הַשִּׂיחִם׃ / וַיְכֻלּוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| rushed | וַיְרִיצֻהוּ / וַיְגַלַּח / וַיְחַלֵּף | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| zophim | צֹפִים / הַפִּסְגָּה / וַיִּקָּחֻהוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| protect | הָעֵז / וְהַבְּהֵמָה / מִקְנְךָ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| prophetess | הַנְּבִיאָה / הַתֹּף / וַתֵּצֶאןָ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| plotted | זָדוּ / הָאֱלֹהִים / עֲלֵיהֶם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| full-fledged | מְלֹא / וְזַרְעוֹ / הַקָּטֹן | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| memorial | — | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| jeshimon | הַפְּעוֹר / הַנִּשְׁקָף / הַיְשִׁימֹן׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| commandment | וְהַתּוֹרָה / וְהַמִּצְוָה / כָּתַבְתִּי | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| deborah | הָאַלּוֹן / בָּכוּת׃ / דְּבֹרָה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| witch | מְכַשֵּׁפָה / תִחְיֶה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| grazed | בְּעִירֹה / מֵיטַב / וּמֵיטַב | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| pithom | מִסִּים / עַנֹּתוֹ / מִסְכְּנוֹת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| dancing | וּמְחֹלֹת / מִיָּדָו / וַיִּשְׁבֹּר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| permit | נְטַשְׁתַּנִי / לְנַשֵּׁק / הִסְכַּלְתָּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| plot | יָזִד / לְהרְגוֹ / בְערְמָה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| awe | בְּפַחַד / בֵּינֵינוּ / יִשְׁפְּטוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| stubble | לְקֹשֵׁשׁ / קַשׁ / לַתֶּבֶן׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| obliterated | וַתִּכָּחֵד / שָׁלַחְתִּי / וְאַךְ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| master's | לַאדֹנֶיהָ / וְיָלְדָה / וִילָדֶיהָ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| virgins | יְמָאֵן / לְתִתָּהּ / יִשְׁקֹל | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| mahanaim | רָאָם / מַחֲנָיִם׃ / מַחֲנֵה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| moab's | וּקְסָמִים / מִדְיָן / מוֹאָב | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| toy | וְהַעְתַּרְתִּי / יֹסֵף / הֵתֶל | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| asks | יִפְגָּשְׁךָ / וִשְׁאֵלְךָ / וּלְמִי | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| wrung | וַיִּסְפֹּק / קְרָאתִיךָ / כַּפָּיו | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| chewed | וְאַף / חָרָה / יִכָּרֵת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| loss | שַׂלְמָה / יַרְשִׁיעֻן / לְרֵעֵהוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| riding | רֶכֶב / וַיִּתְיַצֵּב / אֱלֹהִים | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| orphans | וְחָרָה / וְהָרַגְתִּי / אַלְמָנוֹת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| creditor | תַּלְוֶה / הֶעָנִי / כְּנֹשֶׁה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| gal-ed | גִּלְעָד / בֵּינִי / קָרָא | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| stylus | בַּחֶרֶט / וַיַּעֲשֵׂהוּ / וַיִּצֶר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| stewardship | מַשְׁקֵהוּ׃ / הַכּוֹס / כַּף | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| tamarisk | אֶשֶׁל / עוֹלָם / בְּשֵׁם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| strayed | וְחֵמַת / וַיְשַׁלְּחֶהָ / וַתֵּתַע | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| stick | וַתִּרְבַּץ / בַּמַּקֵּל׃ / וַתֵּרֶא | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| oppression | צַעֲקַת / הַלַּחַץ / לֹחֲצִים | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| foolish | נְטַשְׁתַּנִי / לְנַשֵּׁק / הִסְכַּלְתָּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| heaviness | אֹפַן / מַרְכְּבֹתָיו / וַיְנַהֲגֵהוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| taberah | תַּבְעֵרָה / בָעֲרָה / בָּם׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| pisgah | צֹפִים / הַפִּסְגָּה / וַיִּקָּחֻהוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| viewpoint | לְבָלָק / יִקָּרֵה / וְהִגַּדְתִּי | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| shouting | בְּרָעָה / בַּמַּחֲנֶה׃ / מִלְחָמָה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| forget | נַשַּׁנִי / עֲמָלִי / הַבְּכוֹר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| bribe | וְשֹׁחַד / הַשֹּׁחַד / יְעַוֵּר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| believed | וַיַּאֲמֵן / ענְיָם / וְכִי | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| obliterate | וֶהֱבִיאֲךָ / וְהִכְחַדְתִּיו׃ / מַלְאֲכֵי | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| section | בְּמֵאָה / קְשִׂיטָה׃ / חֶלְקַת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| fistfuls | לִקְמָצִים׃ / וַתַּעַשׂ / בְּשֶׁבַע | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| recurrence | הִשָּׁנוֹת / וּמְמַהֵר / לַעֲשֹׂתוֹ׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| bowman | קֶשֶׁת / רַבָּה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| eldaah | עֵיפָה / וַחֲנֹךְ / וַאֲבִידָע | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| assigned | וַיִּפְקֹד / וַיְשָׁרֶת / וַיִּהְיוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| graced | חָנָן / הַיְלָדִים / מִי | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| joshua's | מָחֹה / זִכָּרוֹן / וְשִׂים | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| hardened | לְשַׁלְּחֵנוּ / וַיַּהֲרֹג / אֶפְדֶּה׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| rephidim | בִּרְפִידִם׃ / עִם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| midian's | וּקְסָמִים / מִדְיָן / מוֹאָב | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| betrayal | יְעָדָהּ / נכְרִי / לְמכְרָהּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| flashing | מִתְלַקַּחַת / וְאֵשׁ / בְּתוֹךְ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| defeat | עֲנוֹת / גְּבוּרָה / חֲלוּשָׁה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| weigh | יְמָאֵן / לְתִתָּהּ / יִשְׁקֹל | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| offend | לָקוּם / לוֹא / מִפָּנֶיךָ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| hates | שֹׂנַאֲךָ / וְחָדַלְתָּ / מֵעֲזֹב | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| melons | זָכַרְנוּ / הַדָּגָה / הַקִּשֻּׁאִים | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| spawn | הַמַּלְאָךְ / הַגֹּאֵל / וְיִדְגּוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| blooming | וּבַגֶּפֶן / שָׂרִיגִם / כְפֹרַחַת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| bottom | בְּתַחְתִּית / וַיּוֹצֵא / וַיִּתְיַצְּבוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| commemorate | תַזְכִּירוּ / יִשְׁמַע / תִּשְׁמְרוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| buying | וַיְלַקֵּט / וּבְאֶרֶץ / בַּשֶּׁבֶר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| conciliated | יֶחֱרֶה / הוֹצֵאתָ / בְּכֹחַ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| bud | וְהַפִּשְׁתָּה / וְהַשְּׂעֹרָה / נֻכָּתָה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| storage | מִסִּים / עַנֹּתוֹ / מִסְכְּנוֹת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| subsided | וַתִּשְׁקַע / הָאֵשׁ / וַיִּתְפַּלֵּל | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| clarity | וְתַחַת / הַסַּפִּיר / וּכְעֶצֶם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| compensate | וְהִתְהַלֵּךְ / מִשְׁעַנְתּוֹ / שִׁבְתּוֹ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| shackled | מֵאִתָּם / מֵעֲלֵיהֶם / וַיֶּאְסֹר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| sea's | וּמָצָא / יִשְׁחַט / וּבָקָר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| beautiful-figured | וָיֶפֶת / בְּרִיאוֹת / תֹּאַר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| drums | הַנְּבִיאָה / הַתֹּף / וַתֵּצֶאןָ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| indigent | וְהַשְּׁבִיעִת / תִּשְׁמְטֶנָּה / וּנְטַשְׁתָּהּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| bethlehem | לֶחֶם / בֵּית / וַתִּקָּבֵר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| expect | פִלָּלְתִּי / פָנֶיךָ / אֹתִי | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| commanders | מִסִּים / עַנֹּתוֹ / מִסְכְּנוֹת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| hungered | וַתִּרְעַב / לַלָּחֶם / יֹאמַר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| smoking | רֹאִים / הַקּוֹלֹת / הַלַּפִּידִם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| eagles | נְשָׁרִים / כַּנְפֵי / וָאֶשָּׂא | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| mills | שָׁטוּ / וְטָחֲנוּ / בָרֵחַיִם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| suckling | הֶאָנֹכִי / הָרִיתִי / יְלִדְתִּיהוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| afterwards | אַחֲרֵי / מִפְּנֵי / יִוָּדַע | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| ben-oni | אוֹנִי / בְּצֵאת / מֵתָה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| pace | אֶתְנָהֲלָה / לְאִטִּי / וּלְרֶגֶל | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| shdta | שָׂהֲדוּתָא / יְגַר / גִּלְעָד | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| hire | בִּשְׂכָרוֹ׃ / שָׂכִיר / עִמּוֹ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| hygiene | וְעָנְתָה / יִגָּרַע / שְׁאֵרָהּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| thunder | הַמָּטָר / וְהַקֹּלֹת / לַחֲטֹא | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| yards | הַחֲצֵרֹת / הַשָּׂדֹת׃ / וּמִן | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| conspired | וּבְטֶרֶם / וַיִּתְנַכְּלוּ / לַהֲמִיתוֹ׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| fearful | וַיָּקץ / וַיָּגר / רַב | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| accustomed | רָכַבְתָּ / מֵעוֹדְךָ / הַהַסְכֵּן | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| lets | אָבִיא / כְּשַׁלְּחוֹ / יְגָרֵשׁ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| pounded | שָׁטוּ / וְטָחֲנוּ / בָרֵחַיִם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| transported | וַיָּגז / שַׂלְוִים / וַיִּטֹּשׁ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| bundle | מְרִיקִים / שַׂקֵּיהֶם / בְּשַׂקּוֹ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| vindicate | תִּרְחָק / וְנָקִי / וְצַדִּיק | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| telling | וַיִּגְנֹב / בְּלִי / הִגִּיד | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| ice | אֲכָלַנִי / וְקֶרַח / וַתִּדַּד | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| falls | יְרִיבֻן / בְאֶגְרֹף / וְהִכָּה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| soul's | אֲשֵׁמִים / צָרַת / בְּהִתְחַנְנוֹ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| devastated | אַדְמָתֵנוּ / וְנִהְיֶה / וְהָאֲדָמָה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| envision | תֶחֱזֶה / יִרְאֵי / שֹׂנְאֵי | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| revulsion | מֵאַפְּכֶם / לְזָרָא / וַתִּבְכּוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| quails | וַיָּגז / שַׂלְוִים / וַיִּטֹּשׁ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| birthday | הֻלֶּדֶת / וַיִּשָּׂא / לְכל | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| requirement | כִלִּיתֶם / חקְכֶם / וַיֻּכּוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| blaze | וּמָצְאָה / קֹצִים / וְנֶאֱכַל | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| bow-shot | כִּמְטַחֲוֵי / קֹלָהּ / וַתֵּבְךְּ׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| terrified | לַעֲנוֹת / נִבְהֲלוּ / מִפָּנָיו׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| qesita | בְּמֵאָה / קְשִׂיטָה׃ / חֶלְקַת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| justified | וּלְשָׂרָה / כְּסוּת / וְנֹכָחַת׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| lighter | מֵעָלֶיךָ / וְהַקֹּל / יָבִיאוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| firstborn's | נַשַּׁנִי / עֲמָלִי / הַבְּכוֹר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| knock | יַפִּיל / שִׁנּוֹ׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| evidence | חָפַרְתִּי / לָעֵדָה / בַּעֲבוּר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| cleft | וְשַׂמְתִּיךָ / בְּנִקְרַת / וְשַׂכֹּתִי | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| denigration | לְשִׁמְצָה / בְּקָמֵיהֶם׃ / פַּרְעֹה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| meanings | פִּתְרֹנִים / סַפְּרוּ / הֲלוֹא | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| stashed | הַנְּזָמִים / וַיִּטְמֹן / בְּיָדָם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| showing | הֶעֱמַדְתִּיךָ / הַרְאֹתְךָ / סַפֵּר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| overseers | פְּקִדִים / וַיִּפְקֹד / וַחֲמֵשׁ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| foolishly | נוֹאַלְנוּ / תָּשֶׁת / בִּי | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| fallow | וְהַשְּׁבִיעִת / תִּשְׁמְטֶנָּה / וּנְטַשְׁתָּהּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| awl | וְהִגִּישׁוֹ / הַמְּזוּזָה / וְרָצַע | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| sacks | מְרִיקִים / שַׂקֵּיהֶם / בְּשַׂקּוֹ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| hurrying | הִשָּׁנוֹת / וּמְמַהֵר / לַעֲשֹׂתוֹ׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| implicate | שַׂלְמָה / יַרְשִׁיעֻן / לְרֵעֵהוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| licks | יְלַחֲכוּ / סְבִיבֹתֵינוּ / כִּלְחֹךְ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| asking | מְבַקְשִׁים / וַיְגָרֶשׁ / הַגְּבָרִים | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| jether | הַעוֹדָם / יֶתֶר / וְאֶרְאֶה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| forceful | וַתֶּחֱזַק / לְמַהֵר / מֵתִים׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| blossom | וּבַגֶּפֶן / שָׂרִיגִם / כְפֹרַחַת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| dig | יִפְתַּח / בּוֹר / יִכְרֶה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| bunch | אֲגֻדַּת / וּטְבַלְתֶּם / בַּסַּף | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| join | שָׁוְא / תָּשֶׁת / חָמָס | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| letushim | וְיקְשָׁן / דְּדָן / אַשּׁוּרִם | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| previous | כְּפַעַם / נְחָשִׁים / לְבָרֵךְ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| standard | נִסִּי׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| abida | עֵיפָה / וַחֲנֹךְ / וַאֲבִידָע | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| mill | הַשִּׁפְחָה / הָרֵחָיִם / אַחַר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| showered | וַתִּהֲלַךְ / וַיַּמְטֵר / אֵשׁ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| zimran | זִמְרָן / יקְשָׁן / מְדָן | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| showering | לְמִן / הִוָּסְדָה / מַמְטִיר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| steals | וְנִמְצָא / וּמְכָרוֹ / וְגֹנֵב | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| leek | זָכַרְנוּ / הַדָּגָה / הַקִּשֻּׁאִים | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| lent | וַיַּשְׁאִלוּם / וַיְנַצְּלוּ / וַיהֹוָה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| helping | שֹׂנַאֲךָ / וְחָדַלְתָּ / מֵעֲזֹב | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| malevolent | שָׁוְא / תָּשֶׁת / חָמָס | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| envisioned | אֲצִילֵי / וַיֶּחֱזוּ / שָׁלַח | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| hitting | וַתִּלָּחֵץ / לְהַכֹּתָהּ׃ / הַקִּיר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| ox's | וּבַעַל / נָקִי / יֹאכַל | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| sick | חֹלֶה / לְיוֹסֵף / מְנַשֶּׁה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| scrawny-fleshed | דַּלּוֹת / וְרָעוֹת / וְרַקּוֹת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| defeated | וַיַּחֲלֹשׁ / עִמּוֹ / לְפִי | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| seize | יָרֵאתִי / בְּנוֹתֶיךָ / מֵעִמִּי׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| weary | וּבָאַשׁ / וְנִלְאוּ / תָּמוּת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| perhaps | בְּעַד / אֲכַפְּרָה / אוּלַי | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| cucumbers | זָכַרְנוּ / הַדָּגָה / הַקִּשֻּׁאִים | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| pilgrimages | תָּחֹג / רְגָלִים | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| rebel | לְפִשְׁעֲכֶם / וְשָׁמַע / מִפָּנָיו׃ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| pull | מִשְׁכוּ / לְמִשְׁפְּחֹתֵיכֶם / וּקְחוּ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| shiphrah | שִׁפְרָה / פּוּעָה׃ / הָעִבְרִיֹּת | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| narrow | עֲבוֹר / צֹר / וְיוֹסֵף | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| epher | עֵיפָה / וַחֲנֹךְ / וַאֲבִידָע | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| deceive | יְפַתֶּה / אֹרָשָׂה / יִמְהָרֶנָּה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| rejoiced | וַיִּחַדְּ / הִצִּילוֹ / לְיִשְׂרָאֵל | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| betrothed | יְפַתֶּה / אֹרָשָׂה / יִמְהָרֶנָּה | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| bundles | מְרִיקִים / שַׂקֵּיהֶם / בְּשַׂקּוֹ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| commemorated | וְזָבַחְתָּ / עֹלֹתֶיךָ / שְׁלָמֶיךָ | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| yh's | כֵּס / יָהּ / מִדֹּר | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| bitten | הַנָּשׁוּךְ / שָׂרַף / נָס | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| ygar | שָׂהֲדוּתָא / יְגַר / גִּלְעָד | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| ishbak | זִמְרָן / יקְשָׁן / מְדָן | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| turn | יָמִין / וּשְׂמֹאול / וַהֲסִרֹתִי | 8 | 11 | 13 | 32 | 2.192 | 3.091 | 1.007 | 0.2959 |  |  |
| them | אֹתָם / לָהֶם | 143 | 188 | 467 | 798 | 2.165 | 4.907 | 0.215 | 0.1372 |  |  |
| firstborn | בְּכוֹר | 15 | 19 | 29 | 63 | 2.087 | 2.883 | 0.719 | 0.3223 |  |  |
| field | הַשָּׂדֶה / בַּשָּׂדֶה | 24 | 26 | 41 | 91 | 2.086 | 4.333 | 0.604 | 0.1554 |  |  |
| manasseh's | מְנַשֶּׁה / יְמִינוֹ | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| seashore | שְׂפַת / הַיָּם | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| asenath | אָסְנַת / פּוֹטִי / פֶרַע | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| doorposts | הַמְּזוּזֹת / הַמַּשְׁקוֹף / וְעַל | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| hurt | כְּוִיָּה / פֶּצַע / חַבּוּרָה | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| house's | — | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| bit | וַיְשִׂמֵהוּ / הַנֵּס / וְהִבִּיט | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| vision | אֲדַבֵּר / נְבִיאֲכֶם / בַּמַּרְאָה | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| males | אֱלֹהֵי / יֵרָאֶה / זְכוּרְךָ | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| treat | יַעֲשֶׂה / הרְגֵנִי / בְּרָעָתִי׃ | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| she-goats | מָאתַיִם / וּתְיָשִׁים / רְחֵלִים | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| brick | נִלְבְּנָה / וְנִשְׂרְפָה / לִשְׂרֵפָה | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| provisions | צֵדָה / לַדָּרֶךְ׃ | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| dedan | וּבְנֵי | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| taste | וְטַעְמוֹ / כְּצַפִּיחִת / בִּדְבָשׁ׃ | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| wound | כְּוִיָּה / פֶּצַע / חַבּוּרָה | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| heart's | בְּתם / גַּם / זֹאת | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| labor | בְּלִדְתָּהּ / עִצְּבוֹנֵךְ / וְהֵרֹנֵךְ | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| midwife | הַמְיַלֶּדֶת | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| slave's | וְכִי / תַעֲבֹד / עֶבֶד | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| pillars | וּשְׁתֵּים / מַצֵּבָה / שִׁבְטֵי | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| sleep | לְבַדָּהּ / שִׂמְלָתוֹ / לְעֹרוֹ | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| pole | וָחַי / וְהָיָה | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| nursing | הַאֵלֵךְ / וְתֵינִק / וְקָרָאתִי | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| prophet | נְבִיאֶךָ׃ / נְתַתִּיךָ / נָבִיא | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| bride-price | מֵהַר / הַרְבּוּ / וּמַתָּן | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| further | עוֹד | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| lintel | הַמְּזוּזֹת / הַמַּשְׁקוֹף / וְעַל | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| watchful | הִשָּׁמֶר / בְּקִרְבְּךָ | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| without | בְּכל / וּבִלְעָדֶיךָ / יָרִים | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| lies | שָׁכַב / וְהַשֹּׁכֵב / וְהָאֹכֵל | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| delay | מְלֵאָתְךָ / וְדִמְעֲךָ / תְאַחֵר | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| trap | לְמוֹקֵשׁ / אֱלֹהֵיהֶם | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| vine | גֶפֶן / לְיוֹסֵף / בַּחֲלוֹמִי | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| worthy | מִכּל | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| lead | נְחֵה / פּקְדִי / וּפָקַדְתִּי | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| start | עַד / הַיּוֹם | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| fed | הֶאֱכַלְתִּי / בְּהוֹצִיאִי / יִרְאוּ | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| state | בְּרָע / וְהִזִּיר / הָרִאשֹׁנִים | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| embraced | וַיְחַבֶּק / לִקְרָאתוֹ / וַיְחַבְּקֵהוּ | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| stop | כְּצֵאתִי / אֶפְרֹשׂ / יֶחְדָּלוּן | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| at | עַל | 78 | 79 | 159 | 316 | 2.079 | 5.098 | 0.331 | 0.1235 |  |  |
| into | אֶל | 17 | 22 | 36 | 75 | 2.070 | 2.574 | 0.660 | 0.3223 |  |  |
| finish | וְכִלָּה | 1 | 6 | 8 | 15 | 2.000 | 2.980 | 1.362 | 0.3163 |  |  |
| show | הַפָּנִים׃ | 3 | 6 | 6 | 15 | 2.000 | 2.131 | 1.362 | 0.3444 |  |  |
| morning | בַּבֹּקֶר / בָּקָר | 12 | 20 | 36 | 68 | 1.912 | 1.976 | 0.667 | 0.3776 |  |  |
| vegetation | עֵשֶׂב | 2 | 5 | 5 | 12 | 1.875 | 1.882 | 1.462 | 0.4021 |  |  |
| do | תַּעֲשֶׂה / תַעֲשׂוּ / אֶעֱשֶׂה | 48 | 65 | 145 | 258 | 1.863 | 2.157 | 0.347 | 0.3389 |  |  |
| sinned | חָטָא / חָטָאתִי | 3 | 7 | 9 | 19 | 1.796 | 1.812 | 1.173 | 0.4202 |  |  |
| doing | עָשָׂה | 4 | 7 | 8 | 19 | 1.796 | 1.970 | 1.173 | 0.3788 |  |  |
| lift | וְהֵרִים | 1 | 4 | 4 | 9 | 1.782 | 1.875 | 1.620 | 0.4038 |  |  |
| el | שַׁדַּי / וְאֶל | 0 | 4 | 5 | 9 | 1.782 | 4.042 | 1.620 | 0.1796 |  |  |
| pressed | כָּתִית / וַיִּפְצַר / הָאֶחָד | 2 | 4 | 3 | 9 | 1.782 | 2.073 | 1.620 | 0.3573 |  |  |
| rock | הַצּוּר / הַסֶּלַע / וַיֵּצְאוּ | 0 | 4 | 5 | 9 | 1.782 | 4.042 | 1.620 | 0.1796 |  |  |
| placed | וַיָּשֶׂם / וְהוּא / נָתַתָּה | 4 | 4 | 1 | 9 | 1.782 | 6.203 | 1.620 | 0.0639 |  |  |
| degrade | וְעִנִּיתֶם / נַפְשֹׁתֵיכֶם / תְּעַנֶּה | 0 | 4 | 5 | 9 | 1.782 | 4.042 | 1.620 | 0.1796 |  |  |
| getting | וַתַּשְׁקֶיןָ / וַתִּשְׁכַּב / בְּשִׁכְבָהּ | 3 | 3 | 0 | 6 | 1.771 | 7.455 | 1.909 | 0.0330 | yes |  |
| regard | אוֹדֹת / וַיֵּרַע | 0 | 3 | 3 | 6 | 1.771 | 3.127 | 1.909 | 0.2897 |  |  |
| tested | נִסָּה / וְהָאֱלֹהִים / חַי | 3 | 3 | 0 | 6 | 1.771 | 7.455 | 1.909 | 0.0330 | yes |  |
| required | בַיֶּלֶד / שְׁמַעְתֶּם / נִדְרָשׁ׃ | 0 | 3 | 3 | 6 | 1.771 | 3.127 | 1.909 | 0.2897 |  |  |
| horn | הַשֹּׁפָר / שׁוֹפַר / אַרְצְכֶם | 1 | 3 | 2 | 6 | 1.771 | 1.815 | 1.909 | 0.4201 |  |  |
| instruct | אֶהְיֶה / וְאָנֹכִי / וּלְהוֹרֹת | 0 | 3 | 3 | 6 | 1.771 | 3.127 | 1.909 | 0.2897 |  |  |
| burdens | וְלָקַחְתִּי / סִבְלוֹת / וְהָיִיתִי | 1 | 3 | 2 | 6 | 1.771 | 1.815 | 1.909 | 0.4201 |  |  |
| camped | וַיִּחַן | 1 | 3 | 2 | 6 | 1.771 | 1.815 | 1.909 | 0.4201 |  |  |
| strength | בְּחֹזֶק / יָד / הוֹצִיאָנוּ | 3 | 3 | 0 | 6 | 1.771 | 7.455 | 1.909 | 0.0330 | yes |  |
| sand | כְּחוֹל | 2 | 3 | 1 | 6 | 1.771 | 3.258 | 1.909 | 0.2822 |  |  |
| camp | הַמַּחֲנֶה / לַמַּחֲנֶה | 8 | 27 | 63 | 98 | 1.696 | 9.260 | 0.531 | 0.0118 | yes |  |
| yours | לְךָ | 1 | 8 | 14 | 23 | 1.668 | 4.589 | 1.043 | 0.1414 |  |  |
| top | רֹאשׁ | 5 | 6 | 5 | 16 | 1.633 | 3.367 | 1.218 | 0.2622 |  |  |
| foot | רַגְלוֹ | 3 | 6 | 7 | 16 | 1.633 | 1.668 | 1.218 | 0.4455 |  |  |
| enemies | אֹיְבֵיכֶם | 2 | 7 | 11 | 20 | 1.494 | 2.203 | 1.062 | 0.3294 |  |  |
| can | וַאֲנִי / וּפֹתֵר / מֵאֲשֶׁר | 3 | 5 | 5 | 13 | 1.477 | 1.786 | 1.281 | 0.4260 |  |  |
| gather | וְאָסַפְתָּ | 2 | 5 | 6 | 13 | 1.477 | 1.488 | 1.281 | 0.4719 |  |  |
| cross | עֹבְרִים / יַעַבְרוּ / חָלוּץ | 0 | 5 | 8 | 13 | 1.477 | 5.093 | 1.281 | 0.1238 |  |  |
| spoken | דַּבֵּר | 6 | 12 | 21 | 39 | 1.463 | 1.688 | 0.772 | 0.4455 |  |  |
| spirit | רוּחַ | 4 | 8 | 12 | 24 | 1.408 | 1.429 | 0.953 | 0.4910 |  |  |
| other | וּשְׁנֵי / אֲחֵרוֹת | 5 | 8 | 11 | 24 | 1.408 | 1.516 | 0.953 | 0.4642 |  |  |
| from | מִן | 215 | 227 | 552 | 994 | 1.390 | 1.752 | 0.156 | 0.4360 |  |  |
| flowing | זָבַת / וּדְבָשׁ / חֵלֶב | 4 | 4 | 2 | 10 | 1.333 | 4.306 | 1.379 | 0.1579 |  |  |
| moved | רוּחוֹ / נְדִיב / יְבִיאֶהָ | 2 | 4 | 4 | 10 | 1.333 | 1.420 | 1.379 | 0.4938 |  |  |
| throw | וְהִשְׁלִיךְ / הַבֵּן / הַיִּלּוֹד | 2 | 4 | 4 | 10 | 1.333 | 1.420 | 1.379 | 0.4938 |  |  |
| womb | רֶחֶם / פֶּטֶר | 5 | 6 | 6 | 17 | 1.322 | 2.572 | 1.086 | 0.3223 |  |  |
| wilderness | בַּמִּדְבָּר | 9 | 19 | 40 | 68 | 1.317 | 2.731 | 0.566 | 0.3223 |  |  |
| oxen | בָּקָר / וּבָקָר / הַבָּקָר | 10 | 12 | 18 | 40 | 1.281 | 2.035 | 0.721 | 0.3645 |  |  |
| traveled | וַיִּסַּע | 7 | 7 | 7 | 21 | 1.232 | 3.658 | 0.958 | 0.2189 |  |  |
| manna | הַמָּן / אכְלוֹ / בֹּאָם׃ | 1 | 3 | 3 | 7 | 1.215 | 1.220 | 1.547 | 0.5610 |  |  |
| collect | לִקְטוּ / תִּלְקְטֻהוּ / לִלְקֹט | 0 | 3 | 4 | 7 | 1.215 | 3.023 | 1.547 | 0.3074 |  |  |
| wicked | רָשָׁע / הָרְשָׁעִים׃ / הַצַּדִּיק | 3 | 3 | 1 | 7 | 1.215 | 4.106 | 1.547 | 0.1784 |  |  |
| journey | דֶּרֶךְ / נָסַע | 2 | 3 | 2 | 7 | 1.215 | 1.908 | 1.547 | 0.3951 |  |  |
| hur | וְחוּר / חוּר / אָמַר | 0 | 3 | 4 | 7 | 1.215 | 3.023 | 1.547 | 0.3074 |  |  |
| loose | פֶרַע / תַּפְרִיעוּ / מִמַּעֲשָׂיו | 0 | 3 | 4 | 7 | 1.215 | 3.023 | 1.547 | 0.3074 |  |  |
| stars | כְּכוֹכְבֵי | 3 | 3 | 1 | 7 | 1.215 | 4.106 | 1.547 | 0.1784 |  |  |
| love | וְאָהַבְתָּ / כָּמוֹךָ / אָהַבְתִּי | 2 | 3 | 2 | 7 | 1.215 | 1.908 | 1.547 | 0.3951 |  |  |
| quarrel | רִיב / תִּרְגְּזוּ | 3 | 3 | 1 | 7 | 1.215 | 4.106 | 1.547 | 0.1784 |  |  |
| angels | מַלְאֲכֵי / הַמַּלְאָכִים / וַיִּפְגְּעוּ | 2 | 2 | 0 | 4 | 1.181 | 4.970 | 1.909 | 0.1316 |  |  |
| bound | יִלָּוֶה / יָלַדְתִּי / כְּבֹאִי | 2 | 2 | 0 | 4 | 1.181 | 4.970 | 1.909 | 0.1316 |  |  |
| avenged | יֻקָּם / יוֹמָיִם / יַעֲמֹד | 2 | 2 | 0 | 4 | 1.181 | 4.970 | 1.909 | 0.1316 |  |  |
| steal | וּטְבָחוֹ / הֱשִׁיבֹנוּ / נִגְנֹב | 1 | 2 | 1 | 4 | 1.181 | 1.527 | 1.909 | 0.4616 |  |  |
| households | וּקְחוּ / בָּתֵּיכֶם / וּבָאוּ | 1 | 2 | 1 | 4 | 1.181 | 1.527 | 1.909 | 0.4616 |  |  |
| heat | וָאֶשָּׂא / יַחֵם / עֵינֵי | 2 | 2 | 0 | 4 | 1.181 | 4.970 | 1.909 | 0.1316 |  |  |
| grave | קְבֻרָתָהּ / קְבֻרַת / עַד | 0 | 2 | 2 | 4 | 1.181 | 2.085 | 1.909 | 0.3545 |  |  |
| abib | הָאָבִיב / צִוִּיתִךָ / יָצָאתָ | 2 | 2 | 0 | 4 | 1.181 | 4.970 | 1.909 | 0.1316 |  |  |
| barley | שְׂעֹרִים / מַזְכֶּרֶת / קִרְבֶּנָה | 0 | 2 | 2 | 4 | 1.181 | 2.085 | 1.909 | 0.3545 |  |  |
| terror | חִתַּת / סְבִיבוֹתֵיהֶם / רָדְפוּ | 1 | 2 | 1 | 4 | 1.181 | 1.527 | 1.909 | 0.4616 |  |  |
| sack | שַׂקּוֹ / כַּסְפּוֹ / כַּסְפֵּיהֶם | 1 | 2 | 1 | 4 | 1.181 | 1.527 | 1.909 | 0.4616 |  |  |
| hadn't | זֶה / וַתִּרְאַנִי / נָטְתָה | 2 | 2 | 0 | 4 | 1.181 | 4.970 | 1.909 | 0.1316 |  |  |
| swallowed | הַשִּׁבֳּלִים / וַתִּבְלַע / וַתִּבְלַעְןָ | 1 | 2 | 1 | 4 | 1.181 | 1.527 | 1.909 | 0.4616 |  |  |
| commander | שַׂר / וּפִיכֹל / צְבָאוֹ | 2 | 2 | 0 | 4 | 1.181 | 4.970 | 1.909 | 0.1316 |  |  |
| tonight | הַלַּיְלָה | 2 | 2 | 0 | 4 | 1.181 | 4.970 | 1.909 | 0.1316 |  |  |
| wealth | הַכָּבֵד / וּמֵאֲשֶׁר / לְאָבִינוּ | 1 | 2 | 1 | 4 | 1.181 | 1.527 | 1.909 | 0.4616 |  |  |
| reeds | הַיְאֹר / וַתִּרְעֶינָה / בָּאָחוּ׃ | 2 | 2 | 0 | 4 | 1.181 | 4.970 | 1.909 | 0.1316 |  |  |
| rachel's | רָחֵל | 0 | 2 | 2 | 4 | 1.181 | 2.085 | 1.909 | 0.3545 |  |  |
| causing | לְאַשְׁמַת / יֶחֱטָא / מַשְׁלִיחַ | 0 | 2 | 2 | 4 | 1.181 | 2.085 | 1.909 | 0.3545 |  |  |
| crying | בֹּכֶה / צֹעֲקִים / לְמִשְׁפְּחֹתָיו | 2 | 2 | 0 | 4 | 1.181 | 4.970 | 1.909 | 0.1316 |  |  |
| resided | בָּהּ / וַיָּגר / מְגֻרֵיהֶם | 0 | 2 | 2 | 4 | 1.181 | 2.085 | 1.909 | 0.3545 |  |  |
| striking | מַכֵּה | 1 | 2 | 1 | 4 | 1.181 | 1.527 | 1.909 | 0.4616 |  |  |
| rested | וּבְנֻחֹה / שׁוּבָה / רִבְבוֹת | 1 | 2 | 1 | 4 | 1.181 | 1.527 | 1.909 | 0.4616 |  |  |
| flaring | חֲרוֹן / בְּרַגְלֶיךָ / בּחֳרִי | 1 | 2 | 1 | 4 | 1.181 | 1.527 | 1.909 | 0.4616 |  |  |
| speaks | הַמִּדְבָּר / רְאוֹת / עֵינֵיכֶם | 1 | 2 | 1 | 4 | 1.181 | 1.527 | 1.909 | 0.4616 |  |  |
| in | אֶת / אֲשֶׁר / בְּאֶרֶץ | 346 | 397 | 1040 | 1783 | 1.177 | 3.098 | 0.109 | 0.2946 |  |  |
| sign | אוֹת / לְאוֹת / בֵּינִי | 1 | 5 | 8 | 14 | 1.150 | 2.131 | 1.121 | 0.3444 |  |  |
| times | פְּעָמִים | 5 | 12 | 24 | 41 | 1.115 | 2.202 | 0.671 | 0.3296 |  |  |
| next | מִמּחֳרָת | 1 | 6 | 11 | 18 | 1.056 | 2.956 | 0.966 | 0.3210 |  |  |
| were | וַיִּהְיוּ / הָיוּ / בְּנֵי | 75 | 86 | 204 | 365 | 0.992 | 0.992 | 0.218 | 0.5969 |  |  |
| hagar | הָגָר | 3 | 4 | 4 | 11 | 0.981 | 1.576 | 1.172 | 0.4480 |  |  |
| money | כֶּסֶף | 1 | 8 | 17 | 26 | 0.975 | 4.981 | 0.788 | 0.1316 |  |  |
| away | וַיָּסַר / יְסִירֶנָּה׃ / יָסִיר | 11 | 11 | 16 | 38 | 0.957 | 2.701 | 0.652 | 0.3223 |  |  |
| been | הָיָה / הָיְתָה | 12 | 16 | 31 | 59 | 0.894 | 0.910 | 0.511 | 0.5969 |  |  |
| sacrifices | זְבָחִים / מִזִּבְחֵי / שַׁלְמֵיהֶם | 2 | 5 | 8 | 15 | 0.880 | 1.066 | 0.977 | 0.5969 |  |  |
| darkness | הָאוֹר / הַחֹשֶׁךְ / חֹשֶׁךְ | 1 | 3 | 4 | 8 | 0.817 | 0.909 | 1.257 | 0.5969 |  |  |
| mountains | הֶהָרִים / גָּבְרוּ / וְהַמַּיִם | 3 | 3 | 2 | 8 | 0.817 | 2.550 | 1.257 | 0.3223 |  |  |
| reached | וַיֵּט | 1 | 3 | 4 | 8 | 0.817 | 0.909 | 1.257 | 0.5969 |  |  |
| shoulder | טֶרֶם / שִׁכְמָהּ / וְכַדָּהּ | 2 | 3 | 3 | 8 | 0.817 | 1.107 | 1.257 | 0.5969 |  |  |
| belong | לְמִי / תִּהְיֶינָה / נַחֲלָתָן | 2 | 3 | 3 | 8 | 0.817 | 1.107 | 1.257 | 0.5969 |  |  |
| wise | חֲכַם / וַיַּעֲשׂוּ | 0 | 4 | 8 | 12 | 0.704 | 4.319 | 0.992 | 0.1566 |  |  |
| paran | פָּארָן / מִמִּדְבַּר | 0 | 2 | 3 | 5 | 0.667 | 2.022 | 1.424 | 0.3666 |  |  |
| raise | וּבְתוֹכָם / תִּתְנַשְּׂאוּ / כֻּלָּם | 1 | 2 | 2 | 5 | 0.667 | 0.710 | 1.424 | 0.6285 |  |  |
| gracious | חַנַּנִי / וְכִי / הֵבֵאתָ | 2 | 2 | 1 | 5 | 0.667 | 2.153 | 1.424 | 0.3398 |  |  |
| aramean | הָאֲרַמִּי | 0 | 2 | 3 | 5 | 0.667 | 2.022 | 1.424 | 0.3666 |  |  |
| mass | הֲמוֹן / לְאַב / בָּעָם | 1 | 2 | 2 | 5 | 0.667 | 0.710 | 1.424 | 0.6285 |  |  |
| setting | כַּלּוֹת / לְהָקִים / וַיִּמְשָׁחֵם | 0 | 2 | 3 | 5 | 0.667 | 2.022 | 1.424 | 0.3666 |  |  |
| move | יִדְּבֶנּוּ / תְּרוּמָתִי׃ / תִּצְעַק | 0 | 2 | 3 | 5 | 0.667 | 2.022 | 1.424 | 0.3666 |  |  |
| instructions | וְתוֹרֹתָי׃ / הַחֻקִּים / וְהַתּוֹרֹת | 1 | 2 | 2 | 5 | 0.667 | 0.710 | 1.424 | 0.6285 |  |  |
| molten | מַסֵּכָה | 1 | 2 | 2 | 5 | 0.667 | 0.710 | 1.424 | 0.6285 |  |  |
| short | וַתִּקְצַר / יַחְסְרוּן / הֲתַשְׁחִית | 1 | 2 | 2 | 5 | 0.667 | 0.710 | 1.424 | 0.6285 |  |  |
| corrupted | שַׁחֵת / נִשְׁחָתָה / הִשְׁחִית | 0 | 2 | 3 | 5 | 0.667 | 2.022 | 1.424 | 0.3666 |  |  |
| caught | וַיַּשִּׂגֵם / וַיַּשֵּׂג / תָּקַע | 1 | 2 | 2 | 5 | 0.667 | 0.710 | 1.424 | 0.6285 |  |  |
| blind | עוֹר | 0 | 2 | 3 | 5 | 0.667 | 2.022 | 1.424 | 0.3666 |  |  |
| kingdom | מַמְלֶכֶת / מַמְלַכְתִּי / מַעֲשִׂים | 1 | 2 | 2 | 5 | 0.667 | 0.710 | 1.424 | 0.6285 |  |  |
| build | נִבְנֶה / וְשִׁבְעָה / בְּנָהּ | 1 | 2 | 2 | 5 | 0.667 | 0.710 | 1.424 | 0.6285 |  |  |
| leah's | לֵאָה | 2 | 2 | 1 | 5 | 0.667 | 2.153 | 1.424 | 0.3398 |  |  |
| wherever | לָרֹב / תִּמְצָאוּ / מֵעֲבֹדַתְכֶם | 1 | 2 | 2 | 5 | 0.667 | 0.710 | 1.424 | 0.6285 |  |  |
| manner | כַּמִּשְׁפָּט / יַעֲשֶׂה | 0 | 2 | 3 | 5 | 0.667 | 2.022 | 1.424 | 0.3666 |  |  |
| hard | קְשֵׁה / קָשׁוֹת | 1 | 2 | 2 | 5 | 0.667 | 0.710 | 1.424 | 0.6285 |  |  |
| most | מִכּל / אָהַב / וְיִשְׂרָאֵל | 0 | 2 | 3 | 5 | 0.667 | 2.022 | 1.424 | 0.3666 |  |  |
| hittite | הַחִתִּי | 3 | 5 | 8 | 16 | 0.658 | 0.659 | 0.845 | 0.6501 |  |  |
| war | לַמִּלְחָמָה / מִלְחָמָה | 1 | 5 | 10 | 16 | 0.658 | 2.238 | 0.845 | 0.3223 |  |  |
| women | הַנָּשִׁים / נָשִׁים | 3 | 5 | 8 | 16 | 0.658 | 0.659 | 0.845 | 0.6501 |  |  |
| stone | אֶבֶן / הָאֶבֶן | 6 | 8 | 14 | 28 | 0.642 | 0.711 | 0.639 | 0.6285 |  |  |
| roam | הִתְעוּ / תַּעֲשִׂי / אִמְרִי | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| faithful | נֶאֱמָן / בֵּיתִי / עַבְדֵי | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| alongside | נִסְעָה / לְנֶגְדֶּךָ׃ / וְנֵלֵכָה | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| bdellium | הַבְּדֹלַח / וְזָהָב / וְאֶבֶן | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| sets | בִּשְׁבֻעַת / וְלִשְׁבֻעָה / יְרֵכֵךְ | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| attended | וַיְשָׁרֶת / וַיַּפְקִדֵהוּ / וַיִּמְצָא | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| nahor's | נָחוֹר | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| deliver | וְהַחֲרַמְתִּי / תִּתֵּן / נָתַן | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| false | תִּגְנֹבוּ / תְכַחֲשׁוּ / תְשַׁקְּרוּ | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| invoke | בְּשֵׁם / הוּחַל / לִקְרֹא | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| holding | וְעוֹדְךָ / מַחֲזִיק / בָּם׃ | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| herds | תְּדַבְּרוּן / בְּמֹצַאֲכֶם / הָעֲדָרִים | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| blew | וַיִּיצֶר / וַיִּפַּח / הָ | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| gershom | הָיִיתִי / גֵּרְשֹׁם / נכְרִיָּה׃ | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| test | וְנִשְׁתֶּה / תְּרִיבוּן / תְּנַסּוּן | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| official | סְרִיס / וַיִּקְנֵהוּ / פּוֹטִיפַר | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| implements | כֵלֶיךָ / תֶּלְיְךָ / וְקַשְׁתֶּךָ | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| sinning | קַמְתֶּם / תַּרְבּוּת / חַטָּאִים | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| shear | צֹאנוֹ / חָמִיךְ / לָגֹז | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| he-asses | וּלְאַבְרָם / הֵיטִיב / בַּעֲבוּרָהּ | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| killing | וַתְּמָאֵן / לְשַׁלְּחוֹ / הֹרֵג | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| risen | זָרְחָה / בִּגְנֵבָתוֹ׃ / דָּמִים | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| sang | וַתַּעַן / יָשִׁיר / הַשִּׁירָה | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| halt | לְאֹת / וְרָאִיתִי / וּפָסַחְתִּי | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| slept | וַיִּישָׁן / בְּרִיאוֹת / עֹלוֹת | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| scheme | לְיָדוֹ / אָנָה / וְהָאֱלֹהִים | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| shatter | תעבְדֵם / כְּמַעֲשֵׂיהֶם / הָרֵס | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| divination | וּקְסָמִים / מִדְיָן / מוֹאָב | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| falsely | בִשְׁמִי / וְחִלַּלְתָּ / לַשֶּׁקֶר | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| conveyed | לְיָדוֹ / אָנָה / וְהָאֱלֹהִים | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| coriander | גָד / כְּזֶרַע | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| dark | וַתֶּחְשַׁךְ / הוֹתִיר / בָּעֵץ | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| face-to-face | פָּנִים | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| destroyer | לְאֹת / וְרָאִיתִי / וּפָסַחְתִּי | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| fulfill | מְשַׁכֵּלָה / וַעֲקָרָה / אֲמַלֵּא׃ | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| containers | כֵּן / וּלְהָשִׁיב / כְּלֵיהֶם | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| remains | וְהַנִּשְׁאָר / יִמָּצֵה / בַּדָּם | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| searched | וַיְחַפֵּשׂ | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| suddenly | פִּתְאֹם / שְׁלשְׁתְּכֶם / שְׁלשְׁתָּם׃ | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| enemy | רָעָתוֹ׃ / אוֹיֵב׃ / וַיִּפֹּל | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| deaf | חֶרֶשׂ | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| quail | הַשְּׂלָו | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| testify | לְרָעֹת / לִנְטֹת / לְהַטֹּת׃ | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| save | הַצִּילֵנִי / וְהִכַּנִי / מִיַּד | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| lyre | נַחְבֵּאתָ / בְּשִׂמְחָה / וּבְשִׁרִים | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| kiss | וּשְׁקָה / גְּשָׁה / בְּנֵי | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| walked | לְפָנָיו / הִתְהַלַּכְתִּי / וְהִצְלִיחַ | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| man-asseh | הַנּוֹלָדִים / וּמְנַשֶּׁה / כִּרְאוּבֵן | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| perished | וַיֹּאבְדוּ / עֲלֵיהֶם / הֲטֶרֶם | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| pointed | הַטִּי / כַדֵּךְ / וְאֶשְׁתֶּה | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| sagging | בִּשְׁבֻעַת / וְלִשְׁבֻעָה / יְרֵכֵךְ | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| restrain | לְהִתְאַפֵּק / הַנִּצָּבִים / בְּהִתְוַדַּע | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| staying | וְהִתְהַלֵּךְ / מִשְׁעַנְתּוֹ / שִׁבְתּוֹ | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| picked | וַיִּתְקָעֵהוּ / וַיַּהֲפֹךְ / וַיִּשָּׂא | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| spit | יֶרֶק / בַּטָּהוֹר / וְכִי | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| awesome | נּוֹרָא / וַיִּירָא | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| second's | צִלָּה / הַשֵּׁנִית / הָאֶחָת | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| thorns | תוֹרִישׁוּ / לְשִׂכִּים / וְלִצְנִינִם | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| jabbok | יַבֹּק׃ | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| stink | הִבְאִישׁ / וְרִמָּה / וַיַּנִּיחוּ | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| shaved | הִתְגַּלְּחוֹ / בֻּשָּׁלָה / הַזָּרַע | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| embalmed | וַיַּחַנְטוּ | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| potiphar | סְרִיס / וַיִּקְנֵהוּ / פּוֹטִיפַר | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| conceive | הֶאָנֹכִי / הָרִיתִי / יְלִדְתִּיהוּ | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| ass's | הִכִּיתַנִי / לְבִלְעָם / הָאָתוֹן | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| daytime | הַמִּקְנֶה / הַשְׁקוּ / רְעוּ׃ | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| elevating | הֲנִיפְכֶם / וַעֲשִׂיתֶם / מִסְתּוֹלֵל | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| fooling | מְצַחֵק׃ | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| myself | לְבַדִּי / מִמֶּנִּי / וָאֶקַּח | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| wrapped | בְּצֵקוֹ / יֶחְמָץ / מִשְׁאֲרֹתָם | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| deposit | לְפִקָּדוֹן / בָּרָעָב׃ / לָשֹׂבַע | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| refreshed | וְיִנָּפֵשׁ / שֵׁשֶׁת | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| descend | תַּרְדֵּמָה / מִצַּלְעֹתָיו / תַּחְתֶּנָּה | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| deal | הָאֹמֵר / לְאַרְצְךָ / וְאֵיטִיבָה | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| odious | הִבְאַשְׁתֶּם / רֵיחֵנוּ / לְהרְגֵנוּ׃ | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| prisoner | בַּחֲצִי / הַבּוֹר / הַשְּׁבִי | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| heavens | בַּאֲשֶׁר / הַנַּעַר / הַשָּׁמַיִם | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| alien's | תִלְחָץ / וְאַתֶּם / יְדַעְתֶּם | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| truth | הֵאָסְרוּ / וְיִבָּחֲנוּ / הָאֱמֶת | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| designate | נְקֵבָה / עָלַי / וְאֶתְּנָה | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| amorite's | הָאֱמֹרִי / בְּחַרְבִּי / וּבְקַשְׁתִּי׃ | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| booths | הַסֻּכּוֹת / בַּחֲמִשָּׁה / סֻכֹּתָה | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| kneel | צֵאת / הַשֹּׁאֲבֹת׃ / וַיְבָרֶךְ | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| fruits | הַקָּצִיר / בְּאסְפְּךָ / בְּצֵאת | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| worn | נָבֹל / עֲשֹׂהוּ / תֶּבֶל | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| served | יְדַעְתֶּן / כֹּחִי / אֲבִיכֶן | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| seeking | מְבַקֵּשׁ | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| happy | וְרָאֲךָ / וְשָׂמַח / בְּמֹשֶׁה | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| pot | מוּתֵנוּ / בְּשִׁבְתֵּנוּ / סִיר | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| eliezer | אֱלִיעֶזֶר׃ | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| increase | הַחֲמִישִׁת / לְהוֹסִיף / תְּבוּאָתוֹ | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| enemy's | תִפְגַּע / אֹיִבְךָ / תְּשִׁיבֶנּוּ | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| treasure | סְגֻלָּה / מַטְמוֹן / בְּאַמְתְּחֹתֵיכֶם | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| passing | וּמִזַּרְעֲךָ / לְהַעֲבִיר / תְחַלֵּל | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| tumult | בְּאַשְׁמֹרֶת / וַיָּהם / וְעָנָן | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| honored | הִתְפָּאֵר / לְמָתַי / אַעְתִּיר | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| hide | הַעְלֵם / יַעְלִימוּ / בְּתִתּוֹ | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| tenting | לִשְׁבָטָיו / שֹׁכֵן / וַתְּהִי | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| hardship | הַתְּלָאָה / מְצָאָתַם / וַיַּצִּלֵם | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| inscribed | מְפֻתָּחֹת / וְהַלֻּחֹת / וְהַמִּכְתָּב | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| mixture | וָצֹאן / עֶרֶב / וּבָקָר | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| fourteen | בְּצֹאנֶךָ / וַתַּחֲלֵף / בַשְּׁתִי | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| future | לְעַמִּי / בְּאַחֲרִית / לְעַמֶּךָ׃ | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| pulled | כְּמֵשִׁיב / פָּרַצְתָּ / עָלֶיךָ | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| choose | וְשִׂימוּ / וּתְנוּ / עֲלֵיהֶן | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| plagues | מַגֵּפֹתַי / לִבְּךָ / וּבַעֲבָדֶיךָ | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| thing | הַדָּבָר | 25 | 31 | 72 | 128 | 0.548 | 0.593 | 0.280 | 0.6796 |  |  |
| free | חִנָּם / נְקִיִּם׃ | 3 | 3 | 3 | 9 | 0.528 | 1.568 | 1.016 | 0.4504 |  |  |
| strikes | מַכֵּה / וּמַכֵּה / יְשַׁלְּמֶנָּה | 0 | 3 | 6 | 9 | 0.528 | 3.240 | 1.016 | 0.2834 |  |  |
| reach | יָדְךָ / נְטֵה | 0 | 3 | 6 | 9 | 0.528 | 3.240 | 1.016 | 0.2834 |  |  |
| herd | הַבָּקָר | 1 | 3 | 5 | 9 | 0.528 | 0.782 | 1.016 | 0.6009 |  |  |
| food | אֹכֶל / לְאכְלָה | 8 | 8 | 13 | 29 | 0.507 | 1.407 | 0.571 | 0.4983 |  |  |
| bread | לֶחֶם | 17 | 24 | 57 | 98 | 0.492 | 0.924 | 0.305 | 0.5969 |  |  |
| order | לְמַעַן | 3 | 4 | 6 | 13 | 0.488 | 0.619 | 0.831 | 0.6682 |  |  |
| own | מִלִּבִּי׃ / הַמַּעֲשִׂים / תֵּדְעוּן | 4 | 4 | 5 | 13 | 0.488 | 1.406 | 0.831 | 0.4983 |  |  |
| fear | וְיָרֵאתָ / מֵּאֱלֹהֶיךָ / תִּירָאוּ | 4 | 6 | 11 | 21 | 0.481 | 0.482 | 0.656 | 0.7300 |  |  |
| between | בֵּין / וּבֵין | 12 | 18 | 43 | 73 | 0.402 | 0.945 | 0.325 | 0.5969 |  |  |
| consumed | וַתֹּאכַל / אֵשׁ | 1 | 2 | 3 | 6 | 0.352 | 0.357 | 1.061 | 0.7931 |  |  |
| greater | וְגָדֵל / גָדַל / הָלוֹךְ | 2 | 2 | 2 | 6 | 0.352 | 1.045 | 1.061 | 0.5969 |  |  |
| baked | תֵאָפֶה / אָפָה / חֶלְקָם | 1 | 2 | 3 | 6 | 0.352 | 0.357 | 1.061 | 0.7931 |  |  |
| understanding | נָבוֹן / וְחָכָם / וִישִׁיתֵהוּ | 1 | 2 | 3 | 6 | 0.352 | 0.357 | 1.061 | 0.7931 |  |  |
| hundreds | הָאֲלָפִים / הַמֵּאוֹת / וְשָׂרֵי | 0 | 2 | 4 | 6 | 0.352 | 2.160 | 1.061 | 0.3385 |  |  |
| collected | הָעֹמֶר / נְשִׂיאֵי / לְאֶחָד | 0 | 2 | 4 | 6 | 0.352 | 2.160 | 1.061 | 0.3385 |  |  |
| quarreled | וַיָּרֶב / עִם | 2 | 2 | 2 | 6 | 0.352 | 1.045 | 1.061 | 0.5969 |  |  |
| healed | נִרְפָּא | 0 | 2 | 4 | 6 | 0.352 | 2.160 | 1.061 | 0.3385 |  |  |
| onto | — | 1 | 2 | 3 | 6 | 0.352 | 0.357 | 1.061 | 0.7931 |  |  |
| poor | לֶעָנִי / תַּעֲזֹב | 0 | 2 | 4 | 6 | 0.352 | 2.160 | 1.061 | 0.3385 |  |  |
| sold | וְנִמְכַּר / מָכַר / מְכַרְתֶּם | 5 | 6 | 11 | 22 | 0.350 | 0.458 | 0.565 | 0.7415 |  |  |
| gate | שַׁעַר | 5 | 6 | 11 | 22 | 0.350 | 0.458 | 0.565 | 0.7415 |  |  |
| sit | תֵּשֵׁב / תֵּשְׁבוּ / פֶּה | 1 | 3 | 6 | 10 | 0.320 | 0.785 | 0.810 | 0.6000 |  |  |
| cloud | הֶעָנָן | 9 | 9 | 18 | 36 | 0.237 | 0.630 | 0.376 | 0.6633 |  |  |
| torn | טָרֹף / נְבֵלָה / טְרֵפָה | 3 | 4 | 8 | 15 | 0.196 | 0.196 | 0.556 | 0.8809 |  |  |
| flee | שָׁמָּה / לָנוּס / בְּרַח | 4 | 4 | 7 | 15 | 0.196 | 0.536 | 0.556 | 0.7067 |  |  |
| just | אַךְ | 5 | 7 | 16 | 28 | 0.184 | 0.259 | 0.390 | 0.8445 |  |  |
| quickly | מֵהַר | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| levite | הַלֵּוִי / וּבְתוֹךְ / וְעֶבֶד | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| luz | בֵּית / כְּנָעַן / לוּזָה | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| plants | דֶּשֶׁא / מַזְרִיעַ / זַרְעוֹ | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| better | טוֹב | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| either | קֹב / תִקֳּבֶנּוּ / תְבָרְכֶנּוּ׃ | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| fulfillment | מְלֹאת / יָבִיא | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| interest | נֶשֶׁךְ׃ / בְּנֶשֶׁךְ / וּבְמַרְבִּית | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| kiriath | חֶבְרוֹן / קִרְיַת | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| last | אֶמֶשׁ / שָׁכַבְתִּי / נַשְׁקֶנּוּ | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| cooked | וּבָשֵׁל / מְבֻשָּׁל / נָא | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| spreading | פֹּרְשֵׂי / כְנָפַיִם / סֹכְכִים | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| write | כְּתֹב / בַּסֵּפֶר | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| simeon's | שִׁמְעוֹן / שִׁכַּלְתֶּם / כֻלָּנָה׃ | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| curses | וּמְקַלֵּל / יְקַלֵּל / אֱלֹהָיו | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| pursue | אַחֲרֵי | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| mortar | וַיְמָרְרוּ / חַיֵּיהֶם / וּבִלְבֵנִים | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| inherit | יִירַשׁ / הָאָמָה / בְּנָהּ | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| disgusted | וְנַפְשֵׁנוּ / הַקְּלֹקֵל׃ / בֵאלֹהִים | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| counting | בִּפְקֹד / וְנָתְנוּ / בָּהֶם | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| putting | נִטְמְאוּ / מְשַׁלֵּחַ / מִפְּנֵיכֶם | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| least | הַמַּרְבֶּה / וְהַמַּמְעִיט׃ / וַיִּלְקְטוּ | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| sheba | שְׁבָא | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| breaking | בַּמַּחְתֶּרֶת / וְהִכָּה / דָּמִים | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| devastation | שְׁמָמָה / וּרְבֵה / עָלֶיךָ | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| hang | וְתָלָה / בְּשָׂרְךָ / מֵעָלֶיךָ | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| wheat | חִטִּים / וְלֶחֶם / וְחַלַּת | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| depart | יָמִישׁ / וְעַמּוּד / יָסֻרוּ | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| walk | וְהִתְהַלַּכְתִּי / וְאַתֶּם / תִּהְיוּ | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| lost | מָצָא | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| beor | בָּעוֹר | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| serving | לְבַב / שִׁלַּחְנוּ / מֵעבְדֵנוּ׃ | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| uncovered | הֶעֱרָה / שְׁאֵרוֹ / וַאֲחוֹת | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| halted | וַתֵּעָצַר / הַחַיִּים / הַמַּגֵּפָה | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| wrote | וַיִּכְתֹּב / וּמַיִם / אֹכֶל | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| carried | וַיִּשְׂאוּ / וַיִּשָּׂא / וְנָסְעוּ | 3 | 3 | 5 | 11 | 0.175 | 0.483 | 0.629 | 0.7295 |  |  |
| bought | קָנָה / וַיִּקֶן | 1 | 3 | 7 | 11 | 0.175 | 0.884 | 0.629 | 0.5969 |  |  |
| anymore | עוֹד | 2 | 3 | 6 | 11 | 0.175 | 0.186 | 0.629 | 0.8865 |  |  |
| hold | יָדְךָ / בּוֹ / וַיהֹוָה | 2 | 3 | 6 | 11 | 0.175 | 0.186 | 0.629 | 0.8865 |  |  |
| small | הַמְעַט | 3 | 3 | 5 | 11 | 0.175 | 0.483 | 0.629 | 0.7295 |  |  |
| grapes | עֲנָבִים׃ | 2 | 2 | 3 | 7 | 0.160 | 0.451 | 0.772 | 0.7447 |  |  |
| remembered | וַיִּזְכֹּר | 1 | 2 | 4 | 7 | 0.160 | 0.253 | 0.772 | 0.8475 |  |  |
| dried | חָרְבוּ / יָבְשָׁה / מֵעַל | 1 | 2 | 4 | 7 | 0.160 | 0.253 | 0.772 | 0.8475 |  |  |
| woman's | הָאִשָּׁה / מִיַּד | 2 | 2 | 3 | 7 | 0.160 | 0.451 | 0.772 | 0.7447 |  |  |
| dry | בַּיַּבָּשָׁה׃ / בְּתוֹךְ | 1 | 2 | 4 | 7 | 0.160 | 0.253 | 0.772 | 0.8475 |  |  |
| heart | לֵב / לִבּוֹ | 11 | 13 | 31 | 55 | 0.158 | 0.166 | 0.255 | 0.8980 |  |  |
| within | בְּתוֹךְ | 5 | 5 | 10 | 20 | 0.132 | 0.350 | 0.415 | 0.7969 |  |  |
| peace | בְּשָׁלוֹם / שָׁלוֹם / הַשְּׁלָמִים | 4 | 5 | 11 | 20 | 0.132 | 0.132 | 0.415 | 0.9180 |  |  |
| hands | יְדֵיהֶם / כְּפִי | 9 | 11 | 27 | 47 | 0.113 | 0.161 | 0.243 | 0.9011 |  |  |
| ones | וַיּוּשַׁב / וּמֵי / הַהֹלְכִים | 3 | 4 | 9 | 16 | 0.105 | 0.121 | 0.435 | 0.9243 |  |  |
| midian | מִדְיָן | 4 | 4 | 8 | 16 | 0.105 | 0.280 | 0.435 | 0.8330 |  |  |
| kept | עָלֶיהָ / הֶחֱיִתָנוּ / נִמְצָא | 3 | 4 | 9 | 16 | 0.105 | 0.121 | 0.435 | 0.9243 |  |  |
| under | תַּחַת | 11 | 13 | 33 | 57 | 0.077 | 0.136 | 0.189 | 0.9157 |  |  |
| mine | לִי | 4 | 4 | 9 | 17 | 0.045 | 0.115 | 0.324 | 0.9283 |  |  |
| inside | מִבֵּית | 6 | 7 | 18 | 31 | 0.032 | 0.064 | 0.202 | 0.9586 |  |  |
| pursued | וַיִּרְדְּפוּ / וַיִּרְדֹּף / אַחֲרֵיהֶם | 1 | 1 | 2 | 4 | 0.026 | 0.070 | 0.687 | 0.9549 |  |  |
| offer | יָלִין / זִבְחִי / תִסְּכוּ | 1 | 1 | 2 | 4 | 0.026 | 0.070 | 0.687 | 0.9549 |  |  |
| dressed | וַיַּלְבִּשֵׁם / וַיַּלְבֵּשׁ | 1 | 1 | 2 | 4 | 0.026 | 0.070 | 0.687 | 0.9549 |  |  |
| virgin | בְּתוּלָה | 1 | 1 | 2 | 4 | 0.026 | 0.070 | 0.687 | 0.9549 |  |  |
| field's | הַשָּׂדֶה | 1 | 1 | 2 | 4 | 0.026 | 0.070 | 0.687 | 0.9549 |  |  |
| widow | אַלְמָנָה / וּגְרוּשָׁה | 1 | 1 | 2 | 4 | 0.026 | 0.070 | 0.687 | 0.9549 |  |  |
| practice | וְעָשִׂיתָ | 1 | 1 | 2 | 4 | 0.026 | 0.070 | 0.687 | 0.9549 |  |  |
| pitch | תֵּבַת | 1 | 1 | 2 | 4 | 0.026 | 0.070 | 0.687 | 0.9549 |  |  |
| apart | כְּשֵׁשׁ / מִטָּף׃ / הַגְּבָרִים | 1 | 1 | 2 | 4 | 0.026 | 0.070 | 0.687 | 0.9549 |  |  |
| designated | וְהֶפְדָּהּ / נִקְּבוּ / בָּשְׂמַת | 1 | 1 | 2 | 4 | 0.026 | 0.070 | 0.687 | 0.9549 |  |  |
| celebrate | וְיָחֹגּוּ / וְחַגֹּתֶם / תְּחגֻּהוּ׃ | 1 | 1 | 2 | 4 | 0.026 | 0.070 | 0.687 | 0.9549 |  |  |
| red | סוּף / יָם | 3 | 3 | 7 | 13 | 0.023 | 0.058 | 0.324 | 0.9622 |  |  |
| offensive | הַתּוֹעֵבֹת / תּוֹעֵבָה / אַנְשֵׁי | 2 | 2 | 5 | 9 | 0.006 | 0.013 | 0.324 | 0.9922 |  |  |
| but | לֹא / כִּי | 18 | 18 | 49 | 85 | 0.001 | 0.001 | 0.042 | 0.9994 |  |  |

### All words assigned to P (1,980 types)

The assignment is the source with the largest positive source-vs-rest information score. **Do not treat a one-off as strong evidence**: use source info bits, global bits, total count, and q-value together.

| word | Hebrew | J | E | P | n | source info bits | global bits | source WoE bits | q | FDR<.05 | artifact? |
| --- | :---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: | :---: |
| shall | — | 56 | 199 | 1736 | 1991 | 593.203 | 655.593 | 2.345 | 1.91e-194 | yes |  |
| of | — | 611 | 669 | 3336 | 4616 | 302.364 | 304.708 | 0.967 | 2.69e-89 | yes |  |
| offering | קרְבָּנוֹ / קרְבַּן / לַיהֹוָה | 3 | 19 | 412 | 434 | 228.251 | 237.727 | 3.755 | 2.94e-69 | yes |  |
| the | הַ־ | 1324 | 1335 | 5388 | 8047 | 207.550 | 207.712 | 0.610 | 2.13e-60 | yes |  |
| n | — | 3 | 0 | 250 | 253 | 178.340 | 181.318 | 5.717 | 1.41e-52 | yes | ⚠ |
| priest | הַכֹּהֵן | 1 | 4 | 244 | 249 | 164.236 | 165.648 | 5.029 | 6.52e-48 | yes |  |
| its | ־וֹ / ־ָהּ | 35 | 46 | 457 | 538 | 133.944 | 135.106 | 2.046 | 7.65e-39 | yes |  |
| holy | קֹדֶשׁ / הַקֹּדֶשׁ | 1 | 2 | 191 | 194 | 132.743 | 132.996 | 5.328 | 3.05e-38 | yes |  |
| impure | יִטְמָא / טָמֵא / וְטָמֵא | 0 | 0 | 167 | 167 | 132.337 | 132.337 | 7.942 | 4.47e-38 | yes |  |
| l | — | 0 | 0 | 165 | 165 | 130.752 | 130.752 | 7.924 | 1.25e-37 | yes | ⚠ |
| children | בְּנֵי | 28 | 65 | 427 | 520 | 101.601 | 112.791 | 1.749 | 2.66e-32 | yes |  |
| forward | וְהִקְרִיב / וַיַּקְרֵב / וַיִּקְרְבוּ | 0 | 0 | 108 | 108 | 85.583 | 85.583 | 7.314 | 2.47e-24 | yes |  |
| their | ־ָם / ־ֶן | 94 | 56 | 512 | 662 | 81.034 | 87.779 | 1.324 | 5.59e-25 | yes |  |
| make | וְעָשִׂיתָ / תַּעֲשֶׂה | 27 | 29 | 289 | 345 | 77.855 | 77.922 | 1.912 | 4.42e-22 | yes |  |
| e | — | 4 | 0 | 124 | 128 | 77.552 | 81.523 | 4.343 | 3.75e-23 | yes | ⚠ |
| congregation | הָעֵדָה / עֲדַת | 0 | 0 | 92 | 92 | 72.904 | 72.904 | 7.083 | 1.35e-20 | yes |  |
| d | — | 0 | 1 | 99 | 100 | 71.614 | 72.622 | 5.604 | 1.56e-20 | yes | ⚠ |
| tribe | לְמַטֵּה / מַטֵּה | 0 | 0 | 88 | 88 | 69.734 | 69.734 | 7.019 | 9.96e-20 | yes |  |
| r | — | 2 | 0 | 101 | 103 | 68.291 | 70.276 | 4.895 | 7.00e-20 | yes | ⚠ |
| atonement | וְכִפֶּר / לְכַפֵּר | 0 | 1 | 93 | 94 | 66.949 | 67.957 | 5.514 | 3.34e-19 | yes |  |
| tabernacle | הַמִּשְׁכָּן | 0 | 0 | 80 | 80 | 63.395 | 63.395 | 6.883 | 6.96e-18 | yes |  |
| any | כּל / וְכל / מִכּל | 3 | 7 | 129 | 139 | 62.784 | 64.001 | 3.177 | 4.76e-18 | yes |  |
| ho | — | 0 | 0 | 74 | 74 | 58.640 | 58.640 | 6.771 | 1.60e-16 | yes | ⚠ |
| y | — | 0 | 0 | 74 | 74 | 58.640 | 58.640 | 6.771 | 1.60e-16 | yes | ⚠ |
| oil | שֶׁמֶן | 0 | 2 | 88 | 90 | 58.383 | 60.397 | 4.697 | 4.97e-17 | yes |  |
| counts | פְּקֻדֵיהֶם / אֶלֶף / וּפְקֻדֵיהֶם | 0 | 0 | 71 | 71 | 56.263 | 56.263 | 6.711 | 7.90e-16 | yes |  |
| meeting | מוֹעֵד / אֹהֶל | 0 | 6 | 103 | 109 | 55.563 | 61.607 | 3.545 | 2.31e-17 | yes |  |
| pure | טָהוֹר | 4 | 0 | 93 | 97 | 54.617 | 58.588 | 3.929 | 1.63e-16 | yes |  |
| hundred | מֵאוֹת | 6 | 7 | 127 | 140 | 54.361 | 54.424 | 2.792 | 2.66e-15 | yes |  |
| for | אֶת / לוֹ / לָכֶם | 187 | 172 | 825 | 1184 | 51.775 | 52.124 | 0.757 | 1.23e-14 | yes |  |
| family | מִשְׁפַּחַת | 3 | 0 | 84 | 87 | 51.466 | 54.444 | 4.145 | 2.66e-15 | yes |  |
| levites | הַלְוִיִּם | 0 | 0 | 64 | 64 | 50.716 | 50.716 | 6.563 | 3.19e-14 | yes |  |
| thousand | אֶלֶף | 0 | 4 | 85 | 89 | 48.785 | 52.814 | 3.800 | 7.76e-15 | yes |  |
| families | לְמִשְׁפְּחֹתָם / מִשְׁפַּחַת | 4 | 2 | 91 | 97 | 47.094 | 47.570 | 3.367 | 2.51e-13 | yes |  |
| work | עֲבֹדַת / מְלָאכָה / לַעֲבֹד | 12 | 6 | 131 | 149 | 46.955 | 48.383 | 2.382 | 1.47e-13 | yes |  |
| affliction | הַנֶּגַע / נֶגַע | 0 | 0 | 59 | 59 | 46.754 | 46.754 | 6.446 | 4.37e-13 | yes |  |
| s | — | 2 | 13 | 119 | 134 | 45.168 | 51.751 | 2.499 | 1.58e-14 | yes | ⚠ |
| o | — | 0 | 0 | 55 | 55 | 43.584 | 43.584 | 6.346 | 3.40e-12 | yes | ⚠ |
| bases | וְאַדְנֵיהֶם / אֲדֹנִי | 0 | 0 | 55 | 55 | 43.584 | 43.584 | 6.346 | 3.40e-12 | yes |  |
| by | עַל | 76 | 63 | 393 | 532 | 43.286 | 44.072 | 1.050 | 2.53e-12 | yes |  |
| front | לִפְנֵי | 16 | 39 | 218 | 273 | 43.206 | 50.531 | 1.530 | 3.53e-14 | yes |  |
| army | צָבָא׃ / לַצָּבָא | 1 | 2 | 72 | 75 | 42.611 | 42.863 | 3.924 | 5.49e-12 | yes |  |
| aaron | אַהֲרֹן | 2 | 35 | 172 | 209 | 41.502 | 67.519 | 1.754 | 4.33e-19 | yes |  |
| te | — | 0 | 0 | 52 | 52 | 41.207 | 41.207 | 6.265 | 1.61e-11 | yes | ⚠ |
| sin | לְחַטָּאת׃ / הַחַטָּאת / חַטָּאת | 5 | 17 | 131 | 153 | 40.250 | 45.327 | 2.099 | 1.11e-12 | yes |  |
| altar | הַמִּזְבֵּחַ / מִזְבַּח | 7 | 20 | 144 | 171 | 40.057 | 44.861 | 1.946 | 1.51e-12 | yes |  |
| sons | בְּנֵי / בָּנָיו | 36 | 21 | 214 | 271 | 39.291 | 42.064 | 1.452 | 9.17e-12 | yes |  |
| aa | — | 0 | 0 | 49 | 49 | 38.829 | 38.829 | 6.180 | 7.53e-11 | yes | ⚠ |
| five | וַחֲמֵשׁ / חֲמִשָּׁה / חָמֵשׁ | 7 | 2 | 88 | 97 | 37.685 | 39.771 | 2.771 | 4.13e-11 | yes |  |
| a | אֶת / לַיהֹוָה / כִּי | 289 | 331 | 1203 | 1823 | 37.550 | 39.923 | 0.514 | 3.75e-11 | yes |  |
| it | אֹתוֹ / אֹתָהּ | 198 | 275 | 958 | 1431 | 36.824 | 46.478 | 0.574 | 5.23e-13 | yes |  |
| shekels | שֶׁקֶל | 0 | 1 | 54 | 55 | 36.823 | 37.830 | 4.734 | 1.47e-10 | yes |  |
| wash | וְרָחַץ / יְכַבֵּס / וְכִבֶּס | 4 | 0 | 66 | 70 | 35.151 | 39.122 | 3.437 | 6.20e-11 | yes |  |
| eternal | עוֹלָם | 0 | 0 | 44 | 44 | 34.867 | 34.867 | 6.027 | 1.05e-09 | yes |  |
| equipment | כֵּלָיו / כְּלִי | 0 | 0 | 44 | 44 | 34.867 | 34.867 | 6.027 | 1.05e-09 | yes |  |
| blood | הַדָּם / דַּם | 7 | 15 | 119 | 141 | 33.549 | 35.756 | 1.961 | 5.93e-10 | yes |  |
| t | מֵעוֹלָם / הָ / הַשֵּׁם | 6 | 0 | 71 | 77 | 33.317 | 39.274 | 3.011 | 5.68e-11 | yes | ⚠ |
| eleazar | אֶלְעָזָר | 0 | 0 | 41 | 41 | 32.490 | 32.490 | 5.926 | 5.13e-09 | yes |  |
| one | אֶחָד | 81 | 66 | 376 | 523 | 32.446 | 33.445 | 0.906 | 2.73e-09 | yes |  |
| li | — | 0 | 0 | 39 | 39 | 30.905 | 30.905 | 5.855 | 1.47e-08 | yes | ⚠ |
| an | לַיהֹוָה | 31 | 64 | 271 | 366 | 30.443 | 39.129 | 1.060 | 6.20e-11 | yes |  |
| ti | — | 0 | 0 | 37 | 37 | 29.320 | 29.320 | 5.780 | 4.20e-08 | yes | ⚠ |
| burn | וְהִקְטִיר | 1 | 2 | 53 | 56 | 28.849 | 29.102 | 3.485 | 4.79e-08 | yes |  |
| commanded | צִוָּה | 12 | 11 | 111 | 134 | 27.905 | 27.929 | 1.798 | 1.03e-07 | yes |  |
| cubits | אַמָּה / בָּאַמָּה | 1 | 1 | 47 | 49 | 27.674 | 27.674 | 3.799 | 1.20e-07 | yes |  |
| fire | אֵשׁ / בָּאֵשׁ / אִשָּׁה | 9 | 10 | 100 | 119 | 27.464 | 27.510 | 1.917 | 1.33e-07 | yes |  |
| four | וְאַרְבַּע / אַרְבַּע | 2 | 3 | 58 | 63 | 26.978 | 27.130 | 2.962 | 1.69e-07 | yes |  |
| columns | וְאַדְנֵיהֶם / עַמֻּדֵיהֶם | 0 | 0 | 34 | 34 | 26.943 | 26.943 | 5.659 | 1.88e-07 | yes |  |
| skin | בָּעוֹר / עוֹר | 1 | 1 | 45 | 47 | 26.212 | 26.212 | 3.737 | 3.01e-07 | yes |  |
| peace-offering | הַשְּׁלָמִים | 0 | 1 | 40 | 41 | 26.157 | 27.165 | 4.306 | 1.66e-07 | yes |  |
| donation | תְּרוּמַת / תְּרוּמָה / הַתְּרוּמָה | 0 | 0 | 33 | 33 | 26.150 | 26.150 | 5.617 | 3.07e-07 | yes |  |
| frames | הַקְּרָשִׁים / קְרָשִׁים | 0 | 0 | 33 | 33 | 26.150 | 26.150 | 5.617 | 3.07e-07 | yes |  |
| person | נֶפֶשׁ / הַנֶּפֶשׁ | 1 | 4 | 56 | 61 | 25.636 | 27.048 | 2.912 | 1.78e-07 | yes |  |
| impurity | נִדָּה / טְמֵאָה / עָלָיו | 0 | 0 | 32 | 32 | 25.358 | 25.358 | 5.573 | 5.24e-07 | yes |  |
| legacy | נַחֲלָתוֹ / נַחֲלָה / נַחֲלַת | 1 | 2 | 47 | 50 | 24.600 | 24.852 | 3.313 | 7.36e-07 | yes |  |
| poles | בַּדָּיו / הַבַּדִּים | 0 | 0 | 31 | 31 | 24.565 | 24.565 | 5.528 | 8.66e-07 | yes |  |
| pho | — | 0 | 0 | 31 | 31 | 24.565 | 24.565 | 5.528 | 8.66e-07 | yes |  |
| burnt | הָעֹלָה / לְעֹלָה׃ / עֹלָה | 0 | 18 | 92 | 110 | 24.546 | 42.678 | 1.873 | 6.11e-12 | yes |  |
| chieftain | נָשִׂיא / לִבְנֵי / וְנָשִׂיא | 1 | 1 | 42 | 44 | 24.030 | 24.030 | 3.638 | 1.24e-06 | yes |  |
| side | הָאֶחָת / צֶלַע / וּמִזֶּה | 0 | 7 | 60 | 67 | 23.881 | 30.932 | 2.563 | 1.45e-08 | yes |  |
| testimony | הָעֵדֻת | 0 | 0 | 29 | 29 | 22.981 | 22.981 | 5.433 | 2.42e-06 | yes |  |
| incense | קְטֹרֶת | 0 | 0 | 29 | 29 | 22.981 | 22.981 | 5.433 | 2.42e-06 | yes |  |
| leprosy | צָרַעַת | 0 | 0 | 29 | 29 | 22.981 | 22.981 | 5.433 | 2.42e-06 | yes |  |
| be | יִהְיֶה / וְהָיָה | 141 | 184 | 647 | 972 | 22.947 | 27.383 | 0.547 | 1.45e-07 | yes |  |
| guilt | הָאָשָׁם / אֲשָׁמוֹ / אָשָׁם | 1 | 0 | 35 | 36 | 22.385 | 23.378 | 4.115 | 1.90e-06 | yes |  |
| blu | — | 0 | 0 | 28 | 28 | 22.188 | 22.188 | 5.383 | 3.93e-06 | yes | ⚠ |
| elevation | תְּנוּפָה | 0 | 0 | 28 | 28 | 22.188 | 22.188 | 5.383 | 3.93e-06 | yes |  |
| ri | — | 0 | 0 | 28 | 28 | 22.188 | 22.188 | 5.383 | 3.93e-06 | yes |  |
| leather | עוֹר | 0 | 0 | 28 | 28 | 22.188 | 22.188 | 5.383 | 3.93e-06 | yes |  |
| israel | יִשְׂרָאֵל | 52 | 72 | 300 | 424 | 22.132 | 24.617 | 0.824 | 8.47e-07 | yes |  |
| fifty | חֲמִשִּׁים | 4 | 0 | 47 | 51 | 21.987 | 25.957 | 2.951 | 3.48e-07 | yes |  |
| clothes | בְּגָדָיו / בִּגְדֵי | 11 | 2 | 74 | 87 | 21.862 | 26.745 | 2.015 | 2.10e-07 | yes |  |
| on | עַל | 147 | 187 | 655 | 989 | 21.583 | 25.345 | 0.525 | 5.26e-07 | yes |  |
| gs | — | 0 | 0 | 27 | 27 | 21.396 | 21.396 | 5.332 | 6.55e-06 | yes | ⚠ |
| emission | הַזָּב | 0 | 0 | 27 | 27 | 21.396 | 21.396 | 5.332 | 6.55e-06 | yes |  |
| mixed | בַשֶּׁמֶן / בְּלוּלָה | 0 | 0 | 27 | 27 | 21.396 | 21.396 | 5.332 | 6.55e-06 | yes |  |
| bronze | נְחֹשֶׁת | 1 | 2 | 42 | 45 | 21.109 | 21.361 | 3.153 | 6.68e-06 | yes |  |
| names | שְׁמוֹת | 5 | 0 | 49 | 54 | 21.008 | 25.972 | 2.721 | 3.46e-07 | yes |  |
| sabbath | הַשַּׁבָּת / שַׁבַּת | 0 | 0 | 26 | 26 | 20.603 | 20.603 | 5.278 | 1.08e-05 | yes |  |
| courtyard's | הֶחָצֵר | 0 | 0 | 26 | 26 | 20.603 | 20.603 | 5.278 | 1.08e-05 | yes |  |
| unblemished | תָּמִים | 0 | 0 | 26 | 26 | 20.603 | 20.603 | 5.278 | 1.08e-05 | yes |  |
| acacia | שִׁטִּים | 0 | 0 | 26 | 26 | 20.603 | 20.603 | 5.278 | 1.08e-05 | yes |  |
| dais | הַכַּפֹּרֶת | 0 | 0 | 26 | 26 | 20.603 | 20.603 | 5.278 | 1.08e-05 | yes |  |
| two | שְׁנֵי / שְׁתֵּי | 28 | 43 | 196 | 267 | 20.446 | 22.860 | 1.011 | 2.60e-06 | yes |  |
| nudity | עֶרְוַת / תְגַלֵּה / עֶרְוָתָהּ׃ | 0 | 1 | 32 | 33 | 20.135 | 21.143 | 3.988 | 7.68e-06 | yes |  |
| year | בַּשָּׁנָה / בָּקָר | 4 | 8 | 67 | 79 | 19.452 | 20.462 | 1.984 | 1.18e-05 | yes |  |
| flour | סֹלֶת | 1 | 0 | 31 | 32 | 19.388 | 20.381 | 3.943 | 1.24e-05 | yes |  |
| fine | סֹלֶת | 1 | 0 | 31 | 32 | 19.388 | 20.381 | 3.943 | 1.24e-05 | yes |  |
| flesh | בָּשָׂר / בְּשָׂרוֹ | 7 | 3 | 61 | 71 | 19.126 | 20.284 | 2.101 | 1.32e-05 | yes |  |
| ram | אַיִל / הָאַיִל / וְאַיִל | 1 | 4 | 46 | 51 | 19.064 | 20.477 | 2.630 | 1.17e-05 | yes |  |
| g | — | 0 | 0 | 24 | 24 | 19.018 | 19.018 | 5.165 | 2.92e-05 | yes | ⚠ |
| pavilion | לַפָּרֹכֶת / הַפָּרֹכֶת / פָּרֹכֶת | 0 | 0 | 24 | 24 | 19.018 | 19.018 | 5.165 | 2.92e-05 | yes |  |
| month | לַחֹדֶשׁ / חֹדֶשׁ / בַּחֹדֶשׁ | 3 | 5 | 54 | 62 | 18.335 | 18.715 | 2.232 | 3.55e-05 | yes |  |
| curtains | יְרִיעֹת / הַיְרִיעֹת | 0 | 0 | 23 | 23 | 18.226 | 18.226 | 5.105 | 4.89e-05 | yes |  |
| bull | פַּר | 0 | 4 | 41 | 45 | 17.986 | 22.015 | 2.756 | 4.37e-06 | yes |  |
| years | שָׁנָה / שְׁנַיִם | 12 | 21 | 113 | 146 | 17.979 | 19.839 | 1.312 | 1.77e-05 | yes |  |
| evening | הָעָרֶב׃ / עֶרֶב | 5 | 2 | 50 | 57 | 17.689 | 18.625 | 2.302 | 3.76e-05 | yes |  |
| tent | מוֹעֵד / אֹהֶל / בְּאֹהֶל | 12 | 31 | 133 | 176 | 17.645 | 24.054 | 1.169 | 1.22e-06 | yes |  |
| menorah | הַמְּנֹרָה | 0 | 0 | 22 | 22 | 17.434 | 17.434 | 5.042 | 7.84e-05 | yes |  |
| tpla | — | 0 | 0 | 22 | 22 | 17.434 | 17.434 | 5.042 | 7.84e-05 | yes | ⚠ |
| connected | חֹבְרֹת / וַיְחַבֵּר / עָלֶיךָ | 0 | 0 | 22 | 22 | 17.434 | 17.434 | 5.042 | 7.84e-05 | yes |  |
| holies | קדָשִׁים / הַקֳּדָשִׁים | 0 | 0 | 22 | 22 | 17.434 | 17.434 | 5.042 | 7.84e-05 | yes |  |
| ca | — | 0 | 0 | 22 | 22 | 17.434 | 17.434 | 5.042 | 7.84e-05 | yes |  |
| shekel | בְּשֶׁקֶל / הַקֹּדֶשׁ | 0 | 0 | 22 | 22 | 17.434 | 17.434 | 5.042 | 7.84e-05 | yes |  |
| bre | — | 0 | 0 | 22 | 22 | 17.434 | 17.434 | 5.042 | 7.84e-05 | yes |  |
| curtain | הַיְרִיעָה / הָאֶחָת | 0 | 0 | 21 | 21 | 16.641 | 16.641 | 4.977 | 1.30e-04 | yes |  |
| pu | — | 0 | 0 | 21 | 21 | 16.641 | 16.641 | 4.977 | 1.30e-04 | yes | ⚠ |
| table | הַשֻּׁלְחָן | 0 | 0 | 21 | 21 | 16.641 | 16.641 | 4.977 | 1.30e-04 | yes |  |
| jubilee | הַיֹּבֵל / שְׁנַת / הַיּוֹבֵל | 0 | 0 | 21 | 21 | 16.641 | 16.641 | 4.977 | 1.30e-04 | yes |  |
| identify | וְטִהֲרוֹ / וְטִמְּאוֹ / וְרָאָהוּ | 0 | 0 | 21 | 21 | 16.641 | 16.641 | 4.977 | 1.30e-04 | yes |  |
| ple | — | 0 | 0 | 21 | 21 | 16.641 | 16.641 | 4.977 | 1.30e-04 | yes |  |
| woven | משְׁזָר | 0 | 0 | 21 | 21 | 16.641 | 16.641 | 4.977 | 1.30e-04 | yes |  |
| appraisal | עֶרְכְּךָ | 0 | 0 | 21 | 21 | 16.641 | 16.641 | 4.977 | 1.30e-04 | yes |  |
| will | כִּי / אֲשֶׁר / יִהְיֶה | 123 | 261 | 708 | 1092 | 16.574 | 54.177 | 0.436 | 3.11e-15 | yes |  |
| or | אוֹ | 39 | 48 | 213 | 300 | 16.272 | 17.012 | 0.839 | 1.03e-04 | yes |  |
| old | מִבֶּן / בֶּן / שָׁנָה | 19 | 4 | 87 | 110 | 16.148 | 23.708 | 1.448 | 1.53e-06 | yes |  |
| le | — | 0 | 0 | 20 | 20 | 15.849 | 15.849 | 4.908 | 2.13e-04 | yes | ⚠ |
| chieftains | נְשִׂיאֵי / וּנְשִׂיאֵי | 0 | 0 | 20 | 20 | 15.849 | 15.849 | 4.908 | 2.13e-04 | yes |  |
| second | הַשֵּׁנִי / הַשֵּׁנִית | 2 | 5 | 46 | 53 | 15.305 | 16.285 | 2.183 | 1.63e-04 | yes |  |
| seventh | הַשְּׁבִיעִי | 1 | 4 | 40 | 45 | 15.263 | 16.676 | 2.431 | 1.30e-04 | yes |  |
| carcass | טְמֵאִים / מִנִּבְלָתָם / לָכֶם | 0 | 0 | 19 | 19 | 15.056 | 15.056 | 4.836 | 3.45e-04 | yes |  |
| expose | תְגַלֵּה / עֶרְוַת / עֶרְוָתָהּ׃ | 0 | 0 | 19 | 19 | 15.056 | 15.056 | 4.836 | 3.45e-04 | yes |  |
| item | כְּלִי | 0 | 0 | 19 | 19 | 15.056 | 15.056 | 4.836 | 3.45e-04 | yes |  |
| thirty | שְׁלֹשִׁים | 2 | 2 | 36 | 40 | 14.738 | 14.738 | 2.570 | 4.28e-04 | yes |  |
| fat | הַחֵלֶב / חֵלֶב | 5 | 5 | 53 | 63 | 14.655 | 14.655 | 1.900 | 4.51e-04 | yes |  |
| animals | הַבְּהֵמָה / וּמִן | 5 | 1 | 42 | 48 | 14.646 | 16.717 | 2.260 | 1.26e-04 | yes |  |
| smoke | הַמִּזְבֵּחָה | 5 | 0 | 39 | 44 | 14.643 | 19.606 | 2.395 | 2.04e-05 | yes |  |
| law | חֻקַּת / לְחק / חק | 0 | 5 | 39 | 44 | 14.643 | 19.680 | 2.395 | 1.96e-05 | yes |  |
| is | הוּא | 134 | 138 | 517 | 789 | 14.453 | 14.529 | 0.478 | 4.89e-04 | yes |  |
| kind | לְמִינֵהוּ | 3 | 0 | 32 | 35 | 14.315 | 17.294 | 2.766 | 8.61e-05 | yes |  |
| ce | — | 0 | 0 | 18 | 18 | 14.264 | 14.264 | 4.760 | 5.69e-04 | yes | ⚠ |
| gad | גָד | 0 | 0 | 18 | 18 | 14.264 | 14.264 | 4.760 | 5.69e-04 | yes |  |
| lambs | כְּבָשִׂים / בְּנֵי / שָׁנָה | 0 | 0 | 18 | 18 | 14.264 | 14.264 | 4.760 | 5.69e-04 | yes |  |
| se | — | 0 | 0 | 18 | 18 | 14.264 | 14.264 | 4.760 | 5.69e-04 | yes | ⚠ |
| persons | נֶפֶשׁ / נְפָשֹׁת | 0 | 0 | 18 | 18 | 14.264 | 14.264 | 4.760 | 5.69e-04 | yes |  |
| horns | קַרְנֹתָיו / קַרְנוֹת | 0 | 0 | 18 | 18 | 14.264 | 14.264 | 4.760 | 5.69e-04 | yes |  |
| generations | לְדֹרֹתָם׃ / לְדֹרֹתֵיכֶם | 4 | 0 | 35 | 39 | 14.100 | 18.070 | 2.530 | 5.37e-05 | yes |  |
| sprinkle | וְהִזָּה | 0 | 0 | 17 | 17 | 13.471 | 13.471 | 4.680 | 9.22e-04 | yes |  |
| records | תּוֹלְדֹתָם / לִבְנֵי / שֵׁמֹת | 0 | 0 | 17 | 17 | 13.471 | 13.471 | 4.680 | 9.22e-04 | yes |  |
| innards | הַקֶּרֶב | 0 | 0 | 17 | 17 | 13.471 | 13.471 | 4.680 | 9.22e-04 | yes |  |
| finger | בְּאֶצְבָּעוֹ | 0 | 0 | 17 | 17 | 13.471 | 13.471 | 4.680 | 9.22e-04 | yes |  |
| width | וְרֹחַב | 1 | 0 | 23 | 24 | 13.471 | 14.464 | 3.520 | 5.09e-04 | yes |  |
| aaron's | אַהֲרֹן | 0 | 1 | 23 | 24 | 13.471 | 14.479 | 3.520 | 5.05e-04 | yes |  |
| full | אַחַת | 2 | 2 | 33 | 37 | 12.836 | 12.836 | 2.447 | 0.0014 | yes |  |
| cover | מָסַךְ | 1 | 3 | 33 | 37 | 12.836 | 13.605 | 2.447 | 8.63e-04 | yes |  |
| length | אֹרֶךְ | 1 | 0 | 22 | 23 | 12.742 | 13.734 | 3.457 | 7.95e-04 | yes |  |
| kidneys | הַכָּבֵד / הַכְּלָיֹת / הַיֹּתֶרֶת | 0 | 0 | 16 | 16 | 12.679 | 12.679 | 4.595 | 0.0015 | yes |  |
| korah | קֹרַח | 0 | 0 | 16 | 16 | 12.679 | 12.679 | 4.595 | 0.0015 | yes |  |
| head | רֹאשׁ / רֹאשׁוֹ | 2 | 12 | 59 | 73 | 12.671 | 18.461 | 1.588 | 4.20e-05 | yes |  |
| six | שֵׁשׁ / וְשֵׁשׁ / שֵׁשֶׁת | 2 | 6 | 44 | 52 | 12.599 | 14.139 | 1.939 | 6.12e-04 | yes |  |
| lamb | כֶּבֶשׂ / שְׁנָתוֹ | 2 | 1 | 29 | 32 | 12.345 | 12.582 | 2.626 | 0.0016 | yes |  |
| heads | רָאשֵׁי / רֹאשׁ / אֲבוֹת | 1 | 1 | 25 | 27 | 12.010 | 12.010 | 2.901 | 0.0023 | yes |  |
| charge | מִשְׁמֶרֶת | 2 | 0 | 25 | 27 | 12.010 | 13.996 | 2.901 | 6.70e-04 | yes |  |
| frame | הַקֶּרֶשׁ / הָאֶחָד / אֲדָנִים | 0 | 0 | 15 | 15 | 11.887 | 11.887 | 4.504 | 0.0025 | yes |  |
| d's | — | 0 | 0 | 15 | 15 | 11.887 | 11.887 | 4.504 | 0.0025 | yes |  |
| bars | לְקַרְשֵׁי / וַאֲדָנָיו׃ / קְרָשָׁיו | 0 | 0 | 15 | 15 | 11.887 | 11.887 | 4.504 | 0.0025 | yes |  |
| eats | הָאֹכֶלֶת / אֹכֶל / אכְלוֹ | 0 | 0 | 15 | 15 | 11.887 | 11.887 | 4.504 | 0.0025 | yes |  |
| lamps | נֵרֹתֶיהָ / הַנֵּרֹת | 0 | 0 | 15 | 15 | 11.887 | 11.887 | 4.504 | 0.0025 | yes |  |
| priest's | הַכֹּהֵן / כַּף / לַכֹּהֵן | 0 | 0 | 15 | 15 | 11.887 | 11.887 | 4.504 | 0.0025 | yes |  |
| hangings | קַלְעֵי / קְלָעִים | 0 | 0 | 15 | 15 | 11.887 | 11.887 | 4.504 | 0.0025 | yes |  |
| plate | וְצִפִּיתָ | 0 | 0 | 15 | 15 | 11.887 | 11.887 | 4.504 | 0.0025 | yes |  |
| dan | דָן | 0 | 0 | 14 | 14 | 11.094 | 11.094 | 4.408 | 0.0039 | yes |  |
| kohath | קְהָת | 0 | 0 | 14 | 14 | 11.094 | 11.094 | 4.408 | 0.0039 | yes |  |
| ends | קְצוֹת | 0 | 0 | 14 | 14 | 11.094 | 11.094 | 4.408 | 0.0039 | yes |  |
| desecrate | קדְשֵׁי / וְלֹא / יְחַלֵּל | 0 | 0 | 14 | 14 | 11.094 | 11.094 | 4.408 | 0.0039 | yes |  |
| plated | וַיְצַף | 0 | 0 | 14 | 14 | 11.094 | 11.094 | 4.408 | 0.0039 | yes |  |
| tabernacle's | הַמִּשְׁכָּן | 0 | 0 | 14 | 14 | 11.094 | 11.094 | 4.408 | 0.0039 | yes |  |
| fragrances | הַסַּמִּים | 0 | 0 | 14 | 14 | 11.094 | 11.094 | 4.408 | 0.0039 | yes |  |
| cherubs | הַכְּרֻבִים / כְּרֻבִים | 0 | 0 | 14 | 14 | 11.094 | 11.094 | 4.408 | 0.0039 | yes |  |
| pan | מְלֵאָה / כַּף | 0 | 0 | 14 | 14 | 11.094 | 11.094 | 4.408 | 0.0039 | yes |  |
| hair | שַׁעַר | 3 | 0 | 27 | 30 | 11.053 | 14.032 | 2.524 | 6.57e-04 | yes |  |
| being | נֶפֶשׁ | 4 | 4 | 41 | 49 | 10.969 | 10.969 | 1.838 | 0.0043 | yes |  |
| possession | אֲחֻזַּת / אֲחֻזָּתוֹ / לַאֲחֻזָּה | 9 | 0 | 43 | 52 | 10.693 | 19.628 | 1.746 | 2.02e-05 | yes |  |
| basin | הַכִּיֹּר / כַּנּוֹ׃ | 0 | 2 | 23 | 25 | 10.657 | 12.671 | 2.783 | 0.0015 | yes |  |
| covering | מִכְסֵה / הַמָּסָךְ / וְכִסּוּ | 1 | 1 | 23 | 25 | 10.657 | 10.657 | 2.783 | 0.0051 | yes |  |
| linen | שֵׁשׁ | 0 | 1 | 19 | 20 | 10.571 | 11.578 | 3.251 | 0.0030 | yes |  |
| counted | וַיִּפְקֹד / התְפָּקְדוּ / פָּקַד | 1 | 0 | 19 | 20 | 10.571 | 11.564 | 3.251 | 0.0030 | yes |  |
| who | אֲשֶׁר | 85 | 74 | 313 | 472 | 10.511 | 10.983 | 0.527 | 0.0042 | yes |  |
| male | זָכָר | 9 | 1 | 45 | 55 | 10.463 | 15.714 | 1.666 | 2.31e-04 | yes |  |
| everyone | כּל | 5 | 8 | 52 | 65 | 10.434 | 10.960 | 1.510 | 0.0043 | yes |  |
| goat | שְׂעִיר / עִזִּים | 5 | 0 | 32 | 37 | 10.430 | 15.394 | 2.113 | 2.79e-04 | yes |  |
| half | וָחֵצִי | 2 | 3 | 32 | 37 | 10.430 | 10.583 | 2.113 | 0.0054 | yes |  |
| ng | — | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes | ⚠ |
| scab | הַנֶּתֶק | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| anointing | הַמִּשְׁחָה | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| hooks | וָוֵיהֶם / עַמּוּדֵי / וָוֵי | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| intercourse | שִׁכְבַת / זֶרַע / תֵצֵא | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| nazirite | נִזְרוֹ / הַנָּזִיר | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| merari | מְרָרִי | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| tenth | בֶּעָשׂוֹר / הָעֲשִׂירִי / הַכִּפֻּרִים | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| per | לַגֻּלְגֹּלֶת / לַיּוֹם / הַכִּפֻּרִים | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| murderer | הָרֹצֵחַ | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| altar's | הַמִּזְבֵּחַ | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| row | וְהַטּוּר | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| dish | וּמֵאָה / מִשְׁקָלָהּ / מִזְרָק | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| cattle | בָּקָר / בֶּן | 4 | 3 | 37 | 44 | 10.204 | 10.300 | 1.872 | 0.0063 | yes |  |
| smell | נִיחֹחַ / רֵיחַ / לְרֵיחַ | 1 | 1 | 22 | 24 | 9.987 | 9.987 | 2.720 | 0.0077 | yes |  |
| bring | וְהֵבִיא / לַיהֹוָה / אֶל | 28 | 37 | 151 | 216 | 9.819 | 10.788 | 0.761 | 0.0047 | yes |  |
| spread | פָשָׂה | 0 | 3 | 25 | 28 | 9.784 | 12.806 | 2.415 | 0.0014 | yes |  |
| twenty | עֶשְׂרִים | 5 | 6 | 46 | 57 | 9.783 | 9.856 | 1.566 | 0.0083 | yes |  |
| ithamar | אִיתָמָר | 0 | 0 | 12 | 12 | 9.509 | 9.509 | 4.194 | 0.0101 | yes |  |
| legs | וְעַל / וּכְרָעָיו / וְקִרְבּוֹ | 0 | 0 | 12 | 12 | 9.509 | 9.509 | 4.194 | 0.0101 | yes |  |
| shut | וְהִסְגִּיר / וְהִסְגִּירוֹ / שִׁבְעַת | 0 | 0 | 12 | 12 | 9.509 | 9.509 | 4.194 | 0.0101 | yes |  |
| hammered | מִקְשָׁה | 0 | 0 | 12 | 12 | 9.509 | 9.509 | 4.194 | 0.0101 | yes |  |
| bright | בֶּהָרֹת | 0 | 0 | 12 | 12 | 9.509 | 9.509 | 4.194 | 0.0101 | yes |  |
| function | לַכֹּהֵן / לְכַהֲנוֹ | 0 | 0 | 12 | 12 | 9.509 | 9.509 | 4.194 | 0.0101 | yes |  |
| loops | לֻלָאֹת / בַּמַּחְבֶּרֶת / שְׂפַת | 0 | 0 | 12 | 12 | 9.509 | 9.509 | 4.194 | 0.0101 | yes |  |
| attain | תַּשִּׂיג / יָדוֹ | 0 | 0 | 12 | 12 | 9.509 | 9.509 | 4.194 | 0.0101 | yes |  |
| blue | תְּכֵלֶת | 0 | 0 | 12 | 12 | 9.509 | 9.509 | 4.194 | 0.0101 | yes |  |
| gershon | גֵרְשׁוֹן | 0 | 0 | 12 | 12 | 9.509 | 9.509 | 4.194 | 0.0101 | yes |  |
| swarming | שֶׁרֶץ / הַשֶּׁרֶץ | 0 | 0 | 12 | 12 | 9.509 | 9.509 | 4.194 | 0.0101 | yes |  |
| pleasant | נִיחֹחַ / רֵיחַ / לְרֵיחַ | 2 | 0 | 21 | 23 | 9.323 | 11.308 | 2.655 | 0.0036 | yes |  |
| add | יֹסֵף / וַיֹּסֶף | 1 | 1 | 21 | 23 | 9.323 | 9.323 | 2.655 | 0.0113 | yes |  |
| cut | הַהוּא / וְנִכְרְתָה / מִקֶּרֶב | 4 | 5 | 40 | 49 | 9.166 | 9.254 | 1.642 | 0.0118 | yes |  |
| instruction | תּוֹרַת / זֹאת | 1 | 2 | 24 | 27 | 9.158 | 9.411 | 2.358 | 0.0108 | yes |  |
| purified | הַמִּטַּהֵר | 0 | 1 | 17 | 18 | 9.142 | 10.149 | 3.095 | 0.0069 | yes |  |
| anointed | הַמָּשִׁיחַ / וַיִּמְשַׁח / אֹתוֹ | 0 | 1 | 17 | 18 | 9.142 | 10.149 | 3.095 | 0.0069 | yes |  |
| asher | אֲשֶׁר | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| expiation | יִתְחַטָּא / מִי / לְטַהֲרָם | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| fabric | בֶּגֶד | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| assembly | מִקְרָא | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| group | לֻלָאֹת / בַּמַּחְבֶּרֶת / שְׂפַת | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| ornament | לְשֵׁשֶׁת / הַקָּנִים / הַיֹּצְאִים | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| naphtali | נַפְתָּלִי | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| liver | הַכָּבֵד / הַכְּלָיֹת / הַיֹּתֶרֶת | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| sabbaths | שַׁבְּתֹתַי | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| ephron | עֶפְרוֹן | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| breast | הֶחָזֶה / חֲזֵה / הַתְּנוּפָה | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| ordination | הַמִּלֻּאִים | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| elevate | וְהֵנִיף | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| bull's | הַפָּר | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| detestable | שֶׁקֶץ | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| issachar | יִשָּׂשכָר | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| anoint | וּמָשַׁחְתָּ / וְקִדַּשְׁתָּ | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| courtyard | בַּחֲצַר / וְלַמִּזְבֵּחַ / וְעַל | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| cu | — | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| always | תָּמִיד׃ | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| height | קֹמָתוֹ׃ | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| fling | וְזָרְקוּ / דָּמוֹ | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| bald | בְּקָרַחְתּוֹ / בְגַבַּחְתּוֹ׃ | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| bi | — | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| container | כְּלִי | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| refuge | מִקְלָטוֹ / תִּהְיֶינָה / מִקְלָט | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| around | סָבִיב׃ | 7 | 11 | 59 | 77 | 8.711 | 9.387 | 1.236 | 0.0109 | yes |  |
| all | כּל | 137 | 133 | 477 | 747 | 8.398 | 8.417 | 0.372 | 0.0187 | yes |  |
| above | מִלְמָעְלָה | 2 | 0 | 19 | 21 | 8.013 | 9.999 | 2.514 | 0.0076 | yes |  |
| touches | הַנֶּגַע | 2 | 0 | 19 | 21 | 8.013 | 9.999 | 2.514 | 0.0076 | yes |  |
| fire-holders | מַחְתֹּת / וּקְחוּ / וּנְתַתֶּם | 0 | 0 | 10 | 10 | 7.924 | 7.924 | 3.942 | 0.0250 | yes |  |
| pegs | יִתְדֹת | 0 | 0 | 10 | 10 | 7.924 | 7.924 | 3.942 | 0.0250 | yes |  |
| citizen | כָּאֶזְרָח / הָאֶזְרָח | 0 | 0 | 10 | 10 | 7.924 | 7.924 | 3.942 | 0.0250 | yes |  |
| outsider | זֵר / וְהַזָּר / וְזָר | 0 | 0 | 10 | 10 | 7.924 | 7.924 | 3.942 | 0.0250 | yes |  |
| minister | יְשָׁרְתוּ / לְשָׁרֵת / בַּקֹּדֶשׁ | 0 | 0 | 10 | 10 | 7.924 | 7.924 | 3.942 | 0.0250 | yes |  |
| zebulun | זְבוּלֻן | 0 | 0 | 10 | 10 | 7.924 | 7.924 | 3.942 | 0.0250 | yes |  |
| ke | — | 0 | 0 | 10 | 10 | 7.924 | 7.924 | 3.942 | 0.0250 | yes | ⚠ |
| cubit | וְאַמָּה / אַמָּתַיִם | 0 | 0 | 10 | 10 | 7.924 | 7.924 | 3.942 | 0.0250 | yes |  |
| clasps | קַרְסֵי / הַקְּרָסִים / בַּקְּרָסִים | 0 | 0 | 10 | 10 | 7.924 | 7.924 | 3.942 | 0.0250 | yes |  |
| flag | דֶּגֶל / מַחֲנֵה / לְצִבְאֹתָם | 0 | 0 | 10 | 10 | 7.924 | 7.924 | 3.942 | 0.0250 | yes |  |
| base | יְסוֹד | 0 | 0 | 10 | 10 | 7.924 | 7.924 | 3.942 | 0.0250 | yes |  |
| slaughter | וְשָׁחַט | 1 | 4 | 27 | 32 | 7.600 | 9.012 | 1.872 | 0.0138 | yes |  |
| entrance | פֶּתַח | 8 | 9 | 54 | 71 | 7.533 | 7.583 | 1.189 | 0.0306 | yes |  |
| rams | אֵילִם | 0 | 4 | 24 | 28 | 7.422 | 11.451 | 1.995 | 0.0033 | yes |  |
| branches | וּשְׁלֹשָׁה / מִמֶּנָּה / הָאֶחָד | 0 | 2 | 18 | 20 | 7.369 | 9.384 | 2.438 | 0.0109 | yes |  |
| through | לְדֹרֹתֵיכֶם | 18 | 9 | 73 | 100 | 7.250 | 9.390 | 0.969 | 0.0109 | yes |  |
| vows | נְדָרֶיהָ / הֵנִיא / יָקוּם | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| armies | לְצִבְאֹתָם / דֶּגֶל / מַחֲנֵה | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| evenings | הָעַרְבַּיִם | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| flesh's | בְּשָׂרוֹ / הַבָּשָׂר | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| anah | עֲנָה / וְאֵלֶּה | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| paddan | פַּדֶּנָה / אֲרָם / בְּפַדַּן | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| woof | בָּעֶרֶב / בַשְּׁתִי / הַשְּׁתִי | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| pigeons | תֹרִים / יוֹנָה / בְּנֵי | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| space | בִּרְקִיעַ / לָרָקִיעַ / רָקִיעַ | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| corners | הַטַּבָּעֹת / הַפֵּאֹת / לְאַרְבַּע | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| visitor | תּוֹשָׁב / וְתוֹשָׁב / עִמָּךְ | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| shave | וְגִלַּח / שְׂעָרוֹ / יְגַלֵּחַ | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| lobe | הַכָּבֵד / הַכְּלָיֹת / הַיֹּתֶרֶת | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| crown | נֵזֶר / אֱלֹהָיו | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| ceasing | שַׁבָּתוֹן | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| equipped | יַעַבְרוּ / חָלוּץ / חֲלוּצִים | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| spot | הַמִּכְוָה / לְבָנָה / וְהוּא | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| warp | בָּעֶרֶב / בַשְּׁתִי / הַשְּׁתִי | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| turtledoves | תֹרִים / יוֹנָה / בְּנֵי | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| frankincense | לְבָנָה / עָלֶיהָ | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| wood | עֲצֵי | 0 | 10 | 38 | 48 | 7.100 | 17.173 | 1.425 | 9.30e-05 | yes |  |
| part | מִמֶּנּוּ | 1 | 0 | 14 | 15 | 7.036 | 8.029 | 2.823 | 0.0239 | yes |  |
| burned | וַיַּקְטֵר / בָּאֵשׁ / יִשָּׂרֵף׃ | 1 | 3 | 23 | 27 | 6.856 | 7.626 | 1.935 | 0.0300 | yes |  |
| spoke | וַיְדַבֵּר | 22 | 25 | 108 | 155 | 6.776 | 6.937 | 0.743 | 0.0451 | yes |  |
| husband | אִישָׁהּ | 0 | 2 | 17 | 19 | 6.733 | 8.747 | 2.358 | 0.0154 | yes |  |
| every | כּל / וְכל | 29 | 28 | 125 | 182 | 6.658 | 6.664 | 0.677 | 0.0491 | yes |  |
| redemption | גְאֻלָּתוֹ׃ / תִּהְיֶה / גְּאֻלָּה | 0 | 1 | 13 | 14 | 6.347 | 7.354 | 2.720 | 0.0352 | yes |  |
| designer's | חֹשֵׁב | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| rim | לְבָתִּים / לְבַדִּים | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| blow | יִתְקְעוּ / וְנוֹעֲדוּ / אֵלֶיךָ | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| boil | הַשְּׁחִין / שְׁחִין | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| swelling | שְׂאֵת | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| sale | מִמְכָּרוֹ / מִמְכַּר / לַאֲחֻזָּתוֹ׃ | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| cups | גְבִעִים / מְשֻׁקָּדִים / כַּפְתֹּרֶיהָ | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| designed | אֲפֻדָּתוֹ / כְּמַעֲשֵׂהוּ / וְחִשַּׁב | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| dre | — | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  | ⚠ |
| expired | וַיִּגְוַע / עַמָּיו / וּשְׁבַע | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| priesthood | כְּהֻנַּתְכֶם / וּבָנֶיךָ / וְאַתָּה | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| lighting | הַמָּאוֹר / וְשֶׁמֶן | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| theirs | וּלְכֹל / מִנְחָתָם / חַטָּאתָם | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| wisdom | חכְמָה / בְּחכְמָה | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| earlobe | תְּנוּךְ / בֹּהֶן / אֹזֶן | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| shoulder-pieces | כִּתְפֹת | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| arrange | יַעֲרֹךְ / מֵעֶרֶב / וְעָרְכוּ | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| purification | טהֳרָתוֹ / לְטהֳרָתוֹ / וְכִי | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| white | לָבָן | 3 | 1 | 22 | 26 | 6.300 | 7.040 | 1.872 | 0.0422 | yes |  |
| service | עֲבֹדַת / עֲבֹדָתוֹ / הָעֲבֹדָה | 0 | 3 | 19 | 22 | 6.142 | 9.164 | 2.028 | 0.0126 | yes |  |
| living | הַחַיָּה / נֶפֶשׁ / חַיָּה | 6 | 1 | 29 | 36 | 6.094 | 8.916 | 1.526 | 0.0142 | yes |  |
| day | בַּיּוֹם | 36 | 47 | 165 | 248 | 5.812 | 6.949 | 0.538 | 0.0448 | yes |  |
| skins | עֹרֹת / מְאדָּמִים / תְּחָשִׁים | 1 | 0 | 12 | 13 | 5.666 | 6.658 | 2.609 | 0.0492 | yes |  |
| sides | צַלְעֹת / מִזֶּה / בַּטַּבָּעֹת | 0 | 1 | 12 | 13 | 5.666 | 6.673 | 2.609 | 0.0489 | yes |  |
| heth | חֵת | 1 | 0 | 12 | 13 | 5.666 | 6.658 | 2.609 | 0.0492 | yes |  |
| poured | וַיִּצֹק / יָצַק | 0 | 1 | 12 | 13 | 5.666 | 6.673 | 2.609 | 0.0489 | yes |  |
| guilty | וְאָשֵׁם׃ / מִכּל | 0 | 1 | 12 | 13 | 5.666 | 6.673 | 2.609 | 0.0489 | yes |  |
| sins | מִכּל / חַטֹּאתֵיכֶם׃ / חַטָּאתָם | 0 | 1 | 12 | 13 | 5.666 | 6.673 | 2.609 | 0.0489 | yes |  |
| among | בְּתוֹךְ / מִתּוֹךְ / בְּתוֹכָם | 29 | 23 | 112 | 164 | 5.572 | 6.030 | 0.650 | 0.0713 |  |  |
| does | אֵין | 1 | 2 | 18 | 21 | 5.566 | 5.819 | 1.952 | 0.0813 |  |  |
| creep | הָרֹמֵשׂ / וּבַבְּהֵמָה | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| settings | מִשְׁבְּצֹת / הַמִּשְׁבְּצֹת׃ / וּשְׁתֵּי | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| ornaments | מִמֶּנָּה / כַּפְתֹּרֵיהֶם / וּקְנֹתָם | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| clear | זַכָּה / וְהָאִשָּׁה / מֵעָוֺן | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| deeper | עָמֹק / מִן / הָעוֹר | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| toe | תְּנוּךְ / בֹּהֶן / אֹזֶן | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| forehead | בְּקָרַחְתּוֹ / בְגַבַּחְתּוֹ׃ | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| representative | אַזְכָּרָתָהּ | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| establish | וַהֲקִמֹתִי / לִבְרִית | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| restriction | אִסָּר | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| makes | מְקַדִּשְׁכֶם׃ | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| housings | בָּתִּים / לְבַדִּים / לַבְּרִיחִם | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| jephunneh | יְפֻנֶּה | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| measure | עֶשְׂרֹנִים / בָּלוּל / שְׁנֵי | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| thumb | תְּנוּךְ / בֹּהֶן / אֹזֶן | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| flung | וַיִּזְרֹק / זֹרַק | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| resides | הָגָר / בְּתוֹכְכֶם | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| construction | הָעֲבֹדָה / לַעֲשֹׂת / הֵבִיאוּ | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| libation | וְנֵסֶךְ / כְּמִנְחַת / וּכְנִסְכָּהּ | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| cud | גֵּרָה / מַעֲלֵה | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| jericho | יְרֵחוֹ / יַרְדֵּן | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| pans | כַּפּוֹת / שְׁתֵּים / הַכַּף | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| ammihud | עַמִּיהוּד׃ | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| israelite | הַיִּשְׂרְאֵלִית / יִשְׂרְאֵלִית / וַיִּנָּצוּ | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| stones | הָאֲבָנִים / אַבְנֵי / אֲבָנִים | 1 | 5 | 25 | 31 | 5.292 | 7.421 | 1.522 | 0.0337 | yes |  |
| cities | הֶעָרִים / עָרֵי | 8 | 5 | 40 | 53 | 5.253 | 5.736 | 1.135 | 0.0847 |  |  |
| some | מִן | 18 | 7 | 63 | 88 | 5.222 | 8.755 | 0.867 | 0.0154 | yes |  |
| twelve | עָשָׂר / שְׁנַיִם | 2 | 2 | 20 | 24 | 5.218 | 5.218 | 1.738 | 0.1144 |  |  |
| these | אֵלֶּה | 37 | 32 | 139 | 208 | 5.212 | 5.439 | 0.556 | 0.0994 |  |  |
| then | וְאִם | 34 | 31 | 132 | 197 | 5.135 | 5.215 | 0.567 | 0.1146 |  |  |
| become | בָּהּ / וְהָיָה / וְהָיְתָה | 18 | 10 | 68 | 96 | 5.073 | 6.687 | 0.816 | 0.0486 | yes |  |
| community | הַקָּהָל / קְהַל | 2 | 1 | 17 | 20 | 5.002 | 5.240 | 1.872 | 0.1130 |  |  |
| plague | נֶגֶף / הַמַּגֵּפָה / בַּמַּגֵּפָה | 0 | 1 | 11 | 12 | 4.994 | 6.001 | 2.489 | 0.0725 |  |  |
| ishmael | יִשְׁמָעֵאל | 1 | 0 | 11 | 12 | 4.994 | 5.986 | 2.489 | 0.0731 |  |  |
| eighth | הַשְּׁמִינִי | 0 | 1 | 11 | 12 | 4.994 | 6.001 | 2.489 | 0.0725 |  |  |
| alien | גֵּר / וְלַגֵּר | 1 | 4 | 22 | 27 | 4.981 | 6.394 | 1.583 | 0.0586 |  |  |
| which | אֲשֶׁר | 24 | 23 | 101 | 148 | 4.981 | 4.990 | 0.646 | 0.1315 |  |  |
| bringing | מֵבִיא / יִהְיוּ | 1 | 1 | 14 | 16 | 4.882 | 4.882 | 2.086 | 0.1393 |  |  |
| tribes | הַמַּטּוֹת / מַטּוֹת / הַמַּטֶּה | 0 | 2 | 14 | 16 | 4.882 | 6.897 | 2.086 | 0.0463 | yes |  |
| goats | עִזִּים / וְעִזִּים׃ | 2 | 0 | 14 | 16 | 4.882 | 6.868 | 2.086 | 0.0471 | yes |  |
| portion | לְמָנָה׃ / חֵלֶק | 1 | 1 | 14 | 16 | 4.882 | 4.882 | 2.086 | 0.1393 |  |  |
| judgments | מִשְׁפָּטַי / הַמִּשְׁפָּטִים | 0 | 2 | 14 | 16 | 4.882 | 6.897 | 2.086 | 0.0463 | yes |  |
| offerings | מֵאִשֵּׁי / אִשֵּׁי | 0 | 6 | 24 | 30 | 4.816 | 10.860 | 1.465 | 0.0045 | yes |  |
| anyone | כּל | 5 | 1 | 24 | 30 | 4.816 | 6.887 | 1.465 | 0.0465 | yes |  |
| smaller | תַּמְעִיט / תַּרְבֶּה / לְפִי | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| plains | יַרְדֵּן / בְּעַרְבֹת / יְרֵחוֹ | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| sa | — | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  | ⚠ |
| tax | לַיהֹוָה / וּמִכְסָם / מֶכֶס | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| complaints | תְּלֻנֹּתֵיכֶם / וְנַחְנוּ | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| zibeon | צִבְעוֹן | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| avenger | גֹּאֵל | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| covers | הַמְכַסֶּה / הַקֶּרֶב | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| contribution | נְדָבָה | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| clay | חֶרֶשׂ | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| almond-shaped | גְבִעִים / מְשֻׁקָּדִים | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| amminadab | עַמִּינָדָב׃ / נַחְשׁוֹן | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| rear | וּלְיַרְכְּתֵי / שִׁשָּׁה / לַיַּרְכָתַיִם | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| spoil | בָּזְזוּ / לָבַז / הַצָּבָא | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| brings | הַמַּקְרִיב | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| creature | תִטַּמְּאוּ / בְּכל / לְכל | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| beings | נֶפֶשׁ / וְנֶפֶשׁ / תּוֹצֵא | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| purple | וְתוֹלַעַת / וְאַרְגָּמָן / וְשֵׁשׁ | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| legacies | לִנְחֹל / תִּתְנֶחָלוּ׃ / מִמַּטֶּה | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| congregation's | הָעֵדָה | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| spilled | שֶׁפֶךְ | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| ministering | לְשָׁרֵת / בַּקֹּדֶשׁ | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| fire-holder | מַחְתָּתוֹ / עֲלֵיהֶם / וַיָּשִׂימוּ | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| lower | יִרְאֶנָּה / וּשְׁפָלָה / אֵינֶנָּה | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| cedarwood | אֶרֶז / עֵץ / וּשְׁנֵי | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| nahshon | עַמִּינָדָב׃ / נַחְשׁוֹן | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| batter | רָגוֹם / בָּאֲבָנִים / לִרְגּוֹם | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| zin | צִן | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| signet | פִּתּוּחֵי / חֹתָם / חוֹתָם | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| uncircumcised | עֲרַל / שְׂפָתָיִם׃ | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| skirts | שׁוּלֵי / זָהָב | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| sixteen | שִׁשָּׁה / עָשָׂר | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| lips | שְׂפָתֶיהָ / שְׂפָתָיִם׃ / תִשָּׁבַע | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| machpelah | הַמַּכְפֵּלָה / מְעָרַת / שְׂדֵה | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| fourteenth | עָשָׂר / בְּאַרְבָּעָה | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| commemoration | זִכָּרוֹן / לִבְנֵי | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| vital | חַי / הַבָּשָׂר / הַחַי | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| surrounding | וּמִגְרָשׁ / סְבִיבֹתֵיהֶם / וּשְׂדֵה | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| coats | כְּתֹנֶת | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| basemath | בָּשְׂמַת | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| projections | יְדֹתָיו / לִשְׁתֵּי | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| employee | כְּשָׂכִיר / וְשָׂכִיר / כְּתוֹשָׁב | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| cursing | הַמְאָרְרִים / וּבָאוּ | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| eliasaph | אֶלְיָסָף | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| eliphaz | אֱלִיפַז | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| ne | — | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| embroiderer's | רֹקֵם׃ / מַעֲשֵׂה | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| bezalel | בְּצַלְאֵל | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| mind | וַעֲשִׂיתֶם / תִּזְכְּרוּ / לֵאלֹהֵיכֶם | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| reddish | אֲדַמְדֶּמֶת | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| yx | — | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| dyed | מְאדָּמִים / תְּחָשִׁים / וְעֹרֹת | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| fats | הַחֲלָבִים | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| made | וַיַּעַשׂ / עָשָׂה | 37 | 39 | 148 | 224 | 4.707 | 4.761 | 0.508 | 0.1414 |  |  |
| eaten | יֹאכַל | 1 | 6 | 26 | 33 | 4.699 | 7.594 | 1.371 | 0.0306 | yes |  |
| sacrifice | זֶבַח | 4 | 13 | 46 | 63 | 4.577 | 8.262 | 0.960 | 0.0208 | yes |  |
| number | בְּמִסְפַּר | 6 | 3 | 30 | 39 | 4.561 | 5.275 | 1.233 | 0.1107 |  |  |
| count | תִּפְקֹד / תִּפְקְדֵם׃ / פָּקַד | 3 | 0 | 16 | 19 | 4.451 | 7.429 | 1.787 | 0.0336 | yes |  |
| priests | הַכֹּהֲנִים | 2 | 4 | 23 | 29 | 4.351 | 4.856 | 1.404 | 0.1414 |  |  |
| humans | הָאָדָם | 0 | 1 | 10 | 11 | 4.332 | 5.340 | 2.357 | 0.1061 |  |  |
| forgiven | וְנִסְלַח | 1 | 0 | 10 | 11 | 4.332 | 5.325 | 2.357 | 0.1070 |  |  |
| cave | וְהַמְּעָרָה / קֶבֶר / מֵאֵת | 1 | 0 | 10 | 11 | 4.332 | 5.325 | 2.357 | 0.1070 |  |  |
| domestic | הַבְּהֵמָה / מִכּל / הַחַיָּה | 2 | 0 | 13 | 15 | 4.289 | 6.274 | 1.983 | 0.0611 |  |  |
| south | תֵּימָנָה / לִפְאַת | 2 | 0 | 13 | 15 | 4.289 | 6.274 | 1.983 | 0.0611 |  |  |
| not | לֹא | 108 | 176 | 465 | 749 | 4.226 | 16.588 | 0.262 | 1.34e-04 | yes |  |
| unleavened | מַצּוֹת / הַמַּצּוֹת | 3 | 5 | 27 | 35 | 4.193 | 4.572 | 1.244 | 0.1414 |  |  |
| female | נְקֵבָה / וּנְקֵבָה | 4 | 0 | 18 | 22 | 4.185 | 8.156 | 1.590 | 0.0222 | yes |  |
| fathers | אֲבֹתָם / לְבֵית | 9 | 13 | 54 | 76 | 4.156 | 4.713 | 0.827 | 0.1414 |  |  |
| extent | וְהָיוּ / תוֹצְאֹתָיו / הַגְּבוּל | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| robe's | הַמְּעִיל | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| dung | עֹרוֹ / פִּרְשׁוֹ / תִּשָּׂרֵף׃ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| zuar | נְתַנְאֵל / צוּעָר׃ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| trumpets | וְהָיוּ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| tops | רָאשֵׁיהֶם / וְצִפָּה | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| harshness | בְּפָרֶךְ׃ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| flower | כַּפְתֹּר / וָפֶרַח / בְּקָנֶה | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| amount | מְעַט / שָׁנָיו / נִשְׁאַר | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| zelophehad's | צְלפְחָד | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| devoted | חֵרֶם / יחֳרָם | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| units | לְצִבְאֹתָם | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| lice | הַכִּנָּם / וַתְּהִי / בָּאָדָם | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| elizur | אֱלִיצוּר / שְׁדֵיאוּר׃ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| leper | צָרוּעַ / זָב / וַיְשַׁלְּחוּ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| dress | וְהִלְבַּשְׁתָּ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| talents | כִּכָּר | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| hin | הַהִין / רְבִיעִת / וְעִשָּׂרֹן | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| blasting | תְּרוּעָה / וְנָסְעוּ / הַחֹנִים | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| hezron | חֶצְרֹן / וּבְנֵי | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| uzziel | עֻזִּיאֵל / וּבְנֵי | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| seventy-five | וְשִׁבְעִים / חָמֵשׁ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| walls | בְּקִירֹת / וְשָׁב | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| shedeur | אֱלִיצוּר / שְׁדֵיאוּר׃ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| ochran | פַּגְעִיאֵל / עכְרָן׃ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| molech | לַמֹּלֶךְ / מִזַּרְעוֹ / בָּאִישׁ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| ahira | אֲחִירַע / עֵינָן׃ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| pomegranate | וְרִמּוֹן / פַּעֲמֹן | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| image | בְּצֶלֶם / בְּצַלְמוֹ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| continual | תָּמִיד׃ / הַתָּמִיד | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| rash | הַמִּסְפַּחַת / מִסְפַּחַת / וְלַשְׂאֵת | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| kohathite | הַקְּהָתִי | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| opening | כְּפִי / בְּתוֹכוֹ / לְפִיו | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| whore | לִזְנוֹת / אַחֲרֵיהֶם / וּבְמִשְׁפַּחְתּוֹ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| glo | — | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  | ⚠ |
| sanctify | לָקַח / לְקַדֵּשׁ / וְזֶה | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| elishama | אֱלִישָׁמָע | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| meet | אִוָּעֵד / שָׁמָּה | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| jealousy | קִנְאָה / וְקִנֵּא / תַעֲבֹר | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| ammishadday | אֲחִיעֶזֶר / עַמִּישַׁדָּי׃ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| zurishadday | שְׁלֻמִיאֵל / צוּרִישַׁדָּי׃ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| hor | הָהָר | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| sister-piece | אֲחֹתָהּ / אִשָּׁה | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| loins | הַכְּסָלִים / הַכְּלָיוֹת / יְסִירֶנָּה׃ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| libations | וְנִסְכֵּיהֶם / וּמִנְחָתָם | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| helon | חֵלֹן׃ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| creatures | הָעוֹף / וּבַחַיָּה / וַיִּגְוַע | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| enan | אֲחִירַע / עֵינָן׃ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| responsibility | פְּקֻדַּת / וּפְקֻדַּת / הַלֵּוִי | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| corner | — | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| reuben's | רְאוּבֵן | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| menorah's | וְשִׁשָּׁה / מִצִּדֶּיהָ / קְנֵי | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| ahiezer | אֲחִיעֶזֶר / עַמִּישַׁדָּי׃ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| log | וְלָקַח / לֹג / הַשֶּׁמֶן | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| nethanel | נְתַנְאֵל / צוּעָר׃ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| defiance | עַמִּי / קֶרִי / בְּקֶרִי | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| string | פְּתִיל | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| amram | עַמְרָם | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| appraise | וְהֶעֱרִיךְ / וּבֵין / וְהֶעֱרִיכוֹ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| oholiab | נָתַן / אהֳלִיאָב / וְאהֳלִיאָב | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| pagiel | פַּגְעִיאֵל / עכְרָן׃ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| gamaliel | גַּמְלִיאֵל / פְּדָהצוּר׃ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| gideoni | אֲבִידָן / גִּדְעֹנִי׃ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| acceptable | לְרָצוֹן / תַּקְרִיבוּ / תִזְבְּחוּ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| abidan | אֲבִידָן / גִּדְעֹנִי׃ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| de | — | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| pedahzur | גַּמְלִיאֵל / פְּדָהצוּר׃ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| purchased | מִקְנַת / יְלִיד / וּמִקְנַת | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| acceptance | לִרְצֹנְכֶם / בַּבֹּקֶר / לְרָצוֹן | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| thirty-two | וּשְׁלֹשִׁים / שְׁנַיִם | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| size | מִדָּה | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| shelumiel | שְׁלֻמִיאֵל / צוּרִישַׁדָּי׃ | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| vow | נֶדֶר | 1 | 2 | 15 | 18 | 3.914 | 4.166 | 1.697 | 0.1719 |  |  |
| am | אֲנִי | 12 | 22 | 74 | 108 | 3.832 | 6.059 | 0.661 | 0.0700 |  |  |
| bear | יִשְׂאוּ / תִשָּׂא / וְנָשָׂא | 1 | 7 | 26 | 34 | 3.781 | 7.477 | 1.191 | 0.0327 | yes |  |
| scarlet | שְׁנֵי / תּוֹלַעַת | 2 | 0 | 12 | 14 | 3.711 | 5.696 | 1.872 | 0.0857 |  |  |
| yhwh's | יְהֹוָה | 22 | 20 | 87 | 129 | 3.693 | 3.748 | 0.592 | 0.2069 |  |  |
| command | צַו / וְצִוָּה | 2 | 2 | 17 | 21 | 3.690 | 3.690 | 1.510 | 0.2147 |  |  |
| touch | יִגַּע / תִגַּע | 2 | 2 | 17 | 21 | 3.690 | 3.690 | 1.510 | 0.2147 |  |  |
| mistake | בִּשְׁגָגָה | 1 | 0 | 9 | 10 | 3.684 | 4.677 | 2.213 | 0.1414 |  |  |
| carrying | מַשָּׂא / וּפְקֻדָיו / מַשָּׂאוֹ | 1 | 0 | 9 | 10 | 3.684 | 4.677 | 2.213 | 0.1414 |  |  |
| parts | לִנְתָחָיו / הָרֹאשׁ | 0 | 1 | 9 | 10 | 3.684 | 4.692 | 2.213 | 0.1414 |  |  |
| first | הָרִאשׁוֹן | 11 | 12 | 54 | 77 | 3.633 | 3.672 | 0.764 | 0.2172 |  |  |
| ark | הַתֵּבָה / הָאָרֹן | 16 | 0 | 41 | 57 | 3.555 | 19.439 | 0.881 | 2.27e-05 | yes |  |
| stand | וְהֶעֱמִיד / יָקוּם / וְהַעֲמַדְתָּ | 3 | 12 | 39 | 54 | 3.513 | 7.750 | 0.900 | 0.0280 | yes |  |
| manasseh | מְנַשֶּׁה | 0 | 6 | 21 | 27 | 3.463 | 9.507 | 1.276 | 0.0101 | yes |  |
| gold | זָהָב | 10 | 10 | 48 | 68 | 3.457 | 3.457 | 0.793 | 0.2495 |  |  |
| grain | הַמִּנְחָה / מִנְחָה | 12 | 16 | 62 | 90 | 3.421 | 3.864 | 0.683 | 0.1918 |  |  |
| weight | מִשְׁקָלָהּ / מִזְרָק / מְלֵאִים | 3 | 0 | 14 | 17 | 3.393 | 6.371 | 1.601 | 0.0586 |  |  |
| light | אוֹר | 2 | 1 | 14 | 17 | 3.393 | 3.631 | 1.601 | 0.2229 |  |  |
| commandments | מִצְוֺתַי / מַצּוֹת / תֵעָשֶׂינָה | 2 | 1 | 14 | 17 | 3.393 | 3.631 | 1.601 | 0.2229 |  |  |
| end | מִקֵּץ / מִקָּצָה / תֹּם | 3 | 5 | 25 | 33 | 3.382 | 3.762 | 1.135 | 0.2055 |  |  |
| outside | מִחוּץ | 11 | 5 | 40 | 56 | 3.243 | 4.863 | 0.846 | 0.1411 |  |  |
| are | אֵלֶּה / הֵם / וְאֵלֶּה | 55 | 46 | 179 | 280 | 3.224 | 3.740 | 0.373 | 0.2078 |  |  |
| cherub | כְּרוּב / וּכְרוּב / קְצוֹתָיו׃ | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| residences | אֶרֶץ / מְגוּרֵי / לְרִשְׁתְּךָ | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| donate | יָרִימוּ / תְּרוּמַת / מִמֶּנּוּ | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| regurgitates | וּפַרְסָה / גֵּרָה / מַעֲלַת | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| dan's | דָן | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| flowers | כַּפְתֹּרֶיהָ / וּפְרָחֶיהָ | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| ishmael's | יִשְׁמָעֵאל / וְאֵלֶּה | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| chains | עֲבֹת / מַעֲשֵׂה / שַׁרְשְׁרֹת | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| ceased | מְלַאכְתּוֹ / שַׁבַּת / וַיִּשְׁבְּתוּ | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| beard | בְזָקָן׃ / בְּרֹאשׁ | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| belted | וַיַּחְגֹּר / בָּאַבְנֵט / וַיֶּאְפֹּד | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| owl | וְאֶת | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| spirits | הָרוּחֹת / לְכל / אֱלֹהֵי | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| charms | בְּלָטֵיהֶם / וַיַּעֲשׂוּ | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| wafer | וְרָקִיק / וְחַלַּת / אַחַת | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| astray | תִשְׂטֶה / אִישֵׁךְ / שָׂטִית | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| rope | עֲבֹת / מַעֲשֵׂה / שַׁרְשְׁרֹת | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| izhar | יִצְהָר / קְהָת / וּבְנֵי | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| elon | אֵילוֹן / נָשָׁיו / וְאֶת | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| gerah | גֵּרָה / הַשֶּׁקֶל / חֲמֵשֶׁת | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| wool | צֶמֶר / פִּשְׁתִּים׃ / הַצֶּמֶר | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| reap | קְצִירְךָ / וּקְצַרְתֶּם / קְצִירָהּ | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| basis | מֵעֶרְכֶּךָ / פִּי / וְנִגְרַע | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| swarms | וְנִטְמֵתֶם / בָּם׃ / הַשֶּׁרֶץ | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| cutting | וּבַחֲרֹשֶׁת / לְמַלֹּאת / עֵץ | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| human's | אָדָם | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| chase | וְנָפְלוּ / לֶחָרֶב׃ | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| thanks | תּוֹדָה / תּוֹדַת / יַקְרִיב | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| ash | פִּיחַ / הַשָּׁמַיְמָה / הַדֶּשֶׁן | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| perversion | זִמָּה | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| head's | רֹאשׁ / נִזְרוֹ / וְגִלַּח | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| ark's | בַּטַּבָּעֹת / הָאָרֹן | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| developed | פָּרָחָה׃ / בַּשְּׁחִין / בַּמִּכְוָה | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| zohar | צֹחַר׃ | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| azazel | לַעֲזָאזֵל | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| gra | — | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| gme | — | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  | ⚠ |
| dishes | קְּעָרֹתָיו / יֻסַּךְ / בֹּהֶן | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| scouted | קָרְעוּ / בִגְדֵיהֶם / הַתֹּרִים | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| thirty-seven | וּשְׁלֹשִׁים / וַתְּהִי | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| seas | בַּיַּמִּים | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| cake | וְרָקִיק / וְחַלַּת / אַחַת | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| bake | תֹּאפוּ / תְּבַשְּׁלוּ / אַפּוֹ׃ | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| donated | תָמוּתוּ / תְחַלְּלוּ / הֵרִימוּ | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| eighty | וּשְׁמֹנִים / שְׁמֹנִים | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| low | יָמוּךְ / עִמָּךְ / וְכִי | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| ram's | וּבָנָיו / הָאַיִל / וַיִּסְמְכוּ | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| atone | לְכַפֵּר / כִּפֻּרִים / לְאַשְׁמָה | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| dedication | חֲנֻכַּת / הִמָּשַׁח / קרְבָּנָם | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| unfitting | זָרָה | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| gershonite | הַגֵּרְשֻׁנִּי | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| dishon | דִּשֹׁן | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| th | — | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| omer | לִקְטוּ | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| creeps | וּבְעוֹף / וּבְכל / אֵינֶנָּה | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| scales | סְנַפִּיר / וְקַשְׂקֶשֶׂת / לוֹ | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| commemorative | לִבְנֵי / לְזִכָּרֹן׃ / וְנָשָׂא | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| completion | מְלֹאת / יְמֵי | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| panel | הַכָּתֵף / לַכָּתֵף / וַחֲמֵשׁ | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| phinehas | פִּינְחָס | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| po | — | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| ju | — | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| lizard | בַּשֶּׁרֶץ / הַחֹלֶד / וְהָעַכְבָּר | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| na | — | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| ropes | הָעֲבֹתֹת / וְנָתַתָּה / עֲבֹתֹת | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| homeborn | יְלִיד / וּמִקְנַת / יִמּוֹל | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| flying | הָעוֹף / אַרְבַּע | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| plating | צִפּוּי / מַחְתּוֹת / לַמִּזְבֵּחַ | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| jealousies | מִנְחַת / הַקְּנָאֹת | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| aside | וּמִלְּבַד / מַתְּנוֹתֵיכֶם / נִדְרֵיכֶם | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| inscriptions | פִּתּוּחֵי / וּפִתַּחְתָּ / חֹתָם | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| grate | מִכְבַּר / לוֹ / הַנְּחֹשֶׁת | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| hats | אַבְנֵט / לָהֶם / וְחָגַרְתָּ | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| ephod | הָאֵפֹד | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| kinds | בְּהֶמְתְּךָ / תַרְבִּיעַ / כִּלְאַיִם | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| deuel | דְּעוּאֵל׃ | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| wafers | בְּלוּלֹת / וּרְקִיקֵי / מְשֻׁחִים | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| connect | וְחִבַּרְתָּ / הָאֹהֶל / קַרְסֵי | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| manslayer | הָרֹצֵחַ / שָׁמָּה | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| goat's | הַשָּׂעִיר | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| trade | הָמֵר / וּתְמוּרָתוֹ / יַחֲלִיפֶנּוּ | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| homes | מוֹשְׁבֹתֵיכֶם / בְּכל / מֹשְׁבֹתֵיכֶם׃ | 1 | 1 | 11 | 13 | 3.150 | 3.150 | 1.752 | 0.2866 |  |  |
| produce | תְּבוּאָתָהּ׃ | 1 | 1 | 11 | 13 | 3.150 | 3.150 | 1.752 | 0.2866 |  |  |
| esau's | עֵשָׂו | 2 | 0 | 11 | 13 | 3.150 | 5.135 | 1.752 | 0.1207 |  |  |
| sinai | סִינַי | 5 | 0 | 18 | 23 | 3.103 | 8.066 | 1.300 | 0.0234 | yes |  |
| as | כַּאֲשֶׁר | 87 | 65 | 256 | 408 | 3.063 | 5.210 | 0.301 | 0.1148 |  |  |
| according | כְּכֹל | 8 | 10 | 43 | 61 | 3.053 | 3.229 | 0.784 | 0.2834 |  |  |
| tithe | מַעְשַׂר | 0 | 1 | 8 | 9 | 3.053 | 4.060 | 2.053 | 0.1796 |  |  |
| wear | וְלָבַשׁ / לִלְבֹּשׁ׃ | 0 | 1 | 8 | 9 | 3.053 | 4.060 | 2.053 | 0.1796 |  |  |
| ashes | הַדֶּשֶׁן | 1 | 0 | 8 | 9 | 3.053 | 4.045 | 2.053 | 0.1796 |  |  |
| relative | לִשְׁאֵרוֹ / שְׂאֹר / בְּשָׂרוֹ | 0 | 1 | 8 | 9 | 3.053 | 4.060 | 2.053 | 0.1796 |  |  |
| fellow | עֲמִיתֶךָ / בַּעֲמִיתוֹ | 0 | 1 | 8 | 9 | 3.053 | 4.060 | 2.053 | 0.1796 |  |  |
| appearance | עָמֹק / הָפַךְ / וּמַרְאֵה | 0 | 3 | 13 | 16 | 2.890 | 5.912 | 1.498 | 0.0767 |  |  |
| fruitful | פְּרוּ / וּרְבוּ / וְהִפְרֵיתִי | 1 | 2 | 13 | 16 | 2.890 | 3.142 | 1.498 | 0.2876 |  |  |
| passover | הַפֶּסַח / פֶּסַח | 1 | 2 | 13 | 16 | 2.890 | 3.142 | 1.498 | 0.2876 |  |  |
| travel | יִסְעוּ | 1 | 2 | 13 | 16 | 2.890 | 3.142 | 1.498 | 0.2876 |  |  |
| put | וַיִּתֵּן / וְנָתַתָּ | 37 | 48 | 151 | 236 | 2.766 | 3.878 | 0.376 | 0.1903 |  |  |
| laws | חֻקֹּתַי / תֵּלְכוּ / וַעֲשִׂיתֶם | 1 | 3 | 15 | 19 | 2.749 | 3.519 | 1.334 | 0.2398 |  |  |
| observe | וּשְׁמַרְתֶּם / תִּשְׁמְרוּ | 1 | 6 | 21 | 28 | 2.623 | 5.518 | 1.070 | 0.0944 |  |  |
| redeemed | יִגָּאֵל | 0 | 2 | 10 | 12 | 2.609 | 4.624 | 1.620 | 0.1414 |  |  |
| basket | בַּסָּל / סַל | 0 | 2 | 10 | 12 | 2.609 | 4.624 | 1.620 | 0.1414 |  |  |
| committed | חָטָא / חַטָּאתוֹ | 0 | 2 | 10 | 12 | 2.609 | 4.624 | 1.620 | 0.1414 |  |  |
| hyssop | וְלָקַח / אֶרֶז / עֵץ | 0 | 1 | 7 | 8 | 2.441 | 3.448 | 1.872 | 0.2499 |  |  |
| sixty | שִׁשִּׁים | 1 | 0 | 7 | 8 | 2.441 | 3.434 | 1.872 | 0.2510 |  |  |
| pour | וַיִּצֹק / וְיָצַקְתָּ / יָצַק | 0 | 1 | 7 | 8 | 2.441 | 3.448 | 1.872 | 0.2499 |  |  |
| act | עֲבֹדָה / מְלֶאכֶת / תַעֲשׂוּ | 0 | 1 | 7 | 8 | 2.441 | 3.448 | 1.872 | 0.2499 |  |  |
| hoof | פַּרְסָה | 0 | 1 | 7 | 8 | 2.441 | 3.448 | 1.872 | 0.2499 |  |  |
| m | מֵעוֹלָם / הָ / הַשֵּׁם | 1 | 0 | 7 | 8 | 2.441 | 3.434 | 1.872 | 0.2510 |  | ⚠ |
| assembled | וַיַּקְהֵל / וַיִּקָּהֲלוּ / וְעַל | 0 | 1 | 7 | 8 | 2.441 | 3.448 | 1.872 | 0.2499 |  |  |
| cast | וַיִּצֹק / וְיָצַקְתָּ | 0 | 1 | 7 | 8 | 2.441 | 3.448 | 1.872 | 0.2499 |  |  |
| camping | וְהַחֹנִים / עָלָיו / חֹנֶה | 0 | 1 | 7 | 8 | 2.441 | 3.448 | 1.872 | 0.2499 |  |  |
| burning | תּוּקַד / תִכְבֶּה / מִקְטַר | 1 | 0 | 7 | 8 | 2.441 | 3.434 | 1.872 | 0.2510 |  |  |
| faces | פְּנֵיהֶם / פְּנֵיכֶם | 0 | 3 | 12 | 15 | 2.408 | 5.430 | 1.387 | 0.0998 |  |  |
| fifth | עָלָיו / חֲמִישִׁי | 0 | 3 | 12 | 15 | 2.408 | 5.430 | 1.387 | 0.0998 |  |  |
| meat | בָּשָׂר / הַבָּשָׂר | 1 | 10 | 28 | 39 | 2.385 | 8.617 | 0.860 | 0.0164 | yes |  |
| until | עַד | 22 | 19 | 79 | 120 | 2.377 | 2.515 | 0.488 | 0.3223 |  |  |
| levi's | וּמְרָרִי׃ / וּקְהָת / לֵוִי | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| pallu | חֲנוֹךְ | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| crimes | וְשִׁלַּח | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| shaft | יְרֵכָהּ | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| banded | מְחֻשָּׁקִים / הָאֶלֶף / וָוִים | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| ninth | הַשְּׁמִינִת / הַתְּשִׁיעִת / יָשָׁן | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| jamin | שִׁמְעוֹן / יְמוּאֵל / וְיָמִין | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| rage | קֶצֶף / וְהַלְוִיִּם | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| settled | וַיְכַסֵּהוּ / שֹׁכֵן / וַיִּשְׁכֹּן | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| concentration | מִקְוֵה / לַיַּבָּשָׁה / וּלְמִקְוֵה | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| jars | קְּעָרֹתָיו / יֻסַּךְ / בֹּהֶן | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| flags | לְדִגְלֵיהֶם׃ | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| assemble | וְהִקְהַלְתָּ / הַקָּהָל / וְהַקְהֵל | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| doubled | כָּפוּל / זֶרֶת / וְזֶרֶת | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| restricted | עָלֶיהָ / מִבְטָא | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| gifts | מַתְּנֹתֵיכֶם / מְקַדְּשׁוֹ׃ / תָּרִימוּ | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| assemblies | מוֹעֲדֵי / מִקְרָאֵי / תִּקְרְאוּ | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| complain | תלונו / תַלִּינוּ / עָלָיו | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| spots | לִבְנֹת / בְּשָׂרָם | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| talent | כִּכָּר / אֹתָהּ / הַכֵּלִים | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| yellow | צָהֹב / וּבוֹ / נֶתֶק | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| proclaim | וּקְרָאתֶם / בְּמוֹעֲדָם׃ | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| sash | אַבְנֵט / מִצְנֶפֶת / וְאַבְנֵט | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| uri | אוּרִי / בְּשֵׁם / חוּר | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| shovels | הַיָּעִים / הַמִּזְרָקֹת / הַמִּזְלָגֹת | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| idols | תַעֲשׂוּ / הָאֱלִילִם / תִּפְנוּ | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| conceptions | מַחֲשָׁבֹת / בַּזָּהָב / וּבַכֶּסֶף | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| restrictions | שָׁמְעוּ / נְדָרֶיהָ / הַחֲרֵשׁ | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| ahisamach | אֲחִיסָמָךְ | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| zelophehad | צְלפְחָד / לִבְנֹתָיו׃ / וַאדֹנִי | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| jeush | יְעוּשׁ / יַעְלָם / יעיש | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| produces | פְּרִי / זֶרַע / בּוֹ | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| naaman | וְנַעֲמָן | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| network | מִכְבַּר / רֶשֶׁת / מַעֲשֵׂה | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| source | דָּמֶיהָ / מִמְּקֹר / הַיֹּלֶדֶת | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| bird's | הַשְּׁחֻטָה / הָאֶרֶז / הַתּוֹלַעַת | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| gives | קֳדָשָׁיו / בִּשְׁמֹעַ / מַלִּינִם | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| deep | תְּהוֹם | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| beriah | בְרִיעָה / מִשְׁפַּחַת | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| limb | שָׂרוּעַ׃ / וְקָלוּט / וּלְנֵדֶר | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| thus | כָּכָה / תְּמַלֵּא / אֹתָכָה | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| functioning | הַשְּׂרָד / לְאַהֲרֹן / לַכֹּהֵן | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| tirzah | מַחְלָה / וְחגְלָה / וּמִלְכָּה | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| scorn | תִגְעַל / וְנָתַתִּי / מִשְׁכָּנִי | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| carmi | וּפַלּוּא / וְכַרְמִי׃ / בֵּית | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| asher's | אֲשֶׁר | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| husband's | אִישָׁהּ / הַבְּתוּלָה / הַקְּרוֹבָה | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| hoglah | מַחְלָה / וְחגְלָה / וּמִלְכָּה | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| purify | תִּטְהָרוּ׃ / לָטֹהַר׃ / עֲלֵיכֶם | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| breastplate | הַחֹשֶׁן | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| hearts | אֹתָנָה / נָשָׂא / הַנָּשִׁים | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| confess | וְהִתְוַדָּה / חַטָּאתָם | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| seeds | וַתּוֹצֵא / וְעֵץ / מִגֶּפֶן | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| terah | תֶּרַח / הָרָן | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| daughter's | הִנֵּה / עֶרְוָתְךָ / בִּתְּךָ | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| oven | בַּתַּנּוּר | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| watching | לְמִשְׁמֶרֶת | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| glorified | בְּפַרְעֹה / וְיָדְעוּ | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| slaughters | יִשְׁחַט / הַכֶּבֶשׂ / בַּמַּחֲנֶה׃ | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| twenty-two | וְעֶשְׂרִים / שְׁנַיִם | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| forks | הַיָּעִים / הַמִּזְרָקֹת / הַמִּזְלָגֹת | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| commit | וְעָשְׂתָה / תֶחֱטָא / יָדַע | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| inspired | נְשָׂאוֹ / וּלְבִגְדֵי / וּלְכֹל | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| ointment-maker | רֹקַח / מַעֲשֵׂה | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| ezer | אֵצֶר / וְדִשׁוֹן / וְאֵצֶר | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| presented | וַיִּזְרְקֵהוּ / וַיִּמְצְאוּ / הִמְצִיאוּ | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| extend | הַבְּרִיחַ / לִבְרֹחַ | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| imnah | לְיִמְנָה / הַיִּמְנָה / לְיִשְׁוִי | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| griddle | מַחֲבַת / תִּהְיֶה / הַמַּחֲבַת | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| black | שָׁחֹר / וְשֵׂעָר / יֵרָאֶה | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| fifty-three | שְׁלֹשָׁה / וַחֲמִשִּׁים | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| remainder | וְהַנּוֹתֶרֶת | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| northern | צָפוֹן | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| redeemer | גֹּאֵל / וְהִשִּׂיגָה / כְּדֵי | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| malignant | מַמְאֶרֶת | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| harvest's | קְצִירְךָ | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| evaluation | בְּעֶרְכְּךָ / לְאָשָׁם | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| weaver's | אֹרֵג / מַעֲשֵׂה | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| hooves | מַפְרֶסֶת / שֶׁסַע / וְשִׁסַּע | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| exodus | מֵאֶרֶץ / לְצֵאתָם | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| lights | וְהָיוּ / מְאֹרֹת / לְאֹתֹת | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| jalam | יְעוּשׁ / יַעְלָם / יעיש | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| rows | טוּר / פִּטְדָה / וּבָרֶקֶת | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| cannot | בְּטהֳרָתוֹ׃ / לִשְׁתֵּי / לִשְׁנֵי | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| once | אַחַת | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| headdress | הַמִּצְנֶפֶת | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| twisted | עֲבֹת / מַעֲשֵׂה / שַׁרְשְׁרֹת | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| distributed | תֵּחָלֵק / לָאֵלֶּה / יֵחָלֵק | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| fins | סְנַפִּיר / וְקַשְׂקֶשֶׂת / לוֹ | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| purchase | מִקְנֵה / לְפִיהֶן / מִכֶּסֶף | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| hepher | חֵפֶר / וְתִרְצָה׃ / וּצְלפְחָד | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| horites | אַלּוּפֵי / הַחֹרִי | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| pursuing | בָּכֶם / רְדֹף / וְאֵין | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| nebaioth | נְבָיוֹת / אֲחוֹת / יִשְׁמָעֵאל | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| western | יָם / וּגְבוּל / הַגָּדוֹל | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| suet | הַנְּתָחִים / הַפָּדֶר / הָעֵצִים | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| two-tenths | שְׁתֵּים / שְׁנֵי / עֶשְׂרֹנִים | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| community's | הַקָּהָל / הָעֵדָה / יִשְׁגּוּ | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| design | מַרְאֶה / תַּבְנִית / אוֹתְךָ | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| southern | נֶגֶב / פְּאַת / יָדִי | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| masses | מֵאֶרֶץ / צִבְאוֹתֵיכֶם / צִבְאוֹת | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| jachin | שִׁמְעוֹן / יְמוּאֵל / וְיָמִין | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| becomes | בַּקֳּדָשִׁים / מִזֶּרַע / יִטְהָר | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| revenge | נִקְמַת / הֵחָלְצוּ / לָתֵת | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| dishan | דִישָׁן | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| lotan | לוֹטָן | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| exchange | חֵלֶף / עֲבָדִים / וְלִבְנֵי | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| tent's | הָאֹהֶל | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| juxtaposition | לְעֻמַּת / הַמִּסְגֶּרֶת | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| larger | תַּרְבּוּ / יִתֵּן / וְלַמְעַט | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| eastward | קֵדְמָה / יִזֶּה | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| fringe | לְצִיצִת / וּזְכַרְתֶּם / תָתוּרוּ | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| tongs | וּמַלְקָחֶיהָ / וּמַחְתֹּתֶיהָ / מַלְקָחֶיהָ | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| mahlah | מַחְלָה / וְחגְלָה / וּמִלְכָּה | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| mate | לְרִבְעָהּ / וְהָרַגְתָּ / תִּקְרַב | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| fifty-seven | וַחֲמִשִּׁים / שִׁבְעָה / וּפְקֻדָיו | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| rinsed | בּוֹ / וְיָדָיו / שָׁטַף | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| shobal | שׁוֹבָל / הַחֹרִי | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| transformed | קָרַן | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| bells | שׁוּלָיו / רִמֹּנֵי / וּפַעֲמֹנֵי | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| corpse | בַּחֲלַל | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| rainbow | בֶּעָנָן / הַקֶּשֶׁת / בְּעַנְנִי | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| beside | אֵצֶל | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| crop | יְבוּלָהּ / וְעֵץ / יִתֵּן | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| mark | תְּתָאוּ / וְזֶה / הַגָּדֹל | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| gershonites | הַגֵּרְשֻׁנִּי | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| foreigner | נֵכָר / בֶּן | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| impurities | מִטֻּמְאֹת | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| cow | הַפָּרָה / לְעֵינָיו / עֹרָהּ | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| aunt | דֹּדָתוֹ / דֹּדָתְךָ / תִּקְרַב | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| water | בַּמַּיִם / מַיִם / הַמַּיִם | 37 | 19 | 103 | 159 | 2.375 | 6.493 | 0.424 | 0.0551 |  |  |
| fill | יָדָם / וּמִלְאוּ / יֶדְכֶם | 1 | 3 | 14 | 18 | 2.309 | 3.078 | 1.238 | 0.2976 |  |  |
| clothing | הַבֶּגֶד / בַּבֶּגֶד / וְהַבֶּגֶד | 0 | 5 | 16 | 21 | 2.263 | 7.299 | 1.135 | 0.0365 | yes |  |
| making | מַקְרִיב / יָדוֹ / וְהַשְּׁלָמִים׃ | 5 | 1 | 18 | 24 | 2.248 | 4.319 | 1.059 | 0.1566 |  |  |
| has | אֲשֶׁר / לֹא | 40 | 62 | 173 | 275 | 2.203 | 5.816 | 0.310 | 0.0814 |  |  |
| creeping | רֶמֶשׂ | 2 | 0 | 9 | 11 | 2.093 | 4.078 | 1.476 | 0.1796 |  |  |
| bitter | הַמָּרִים / מִי | 2 | 0 | 9 | 11 | 2.093 | 4.078 | 1.476 | 0.1796 |  |  |
| enough | דֵּי / וְאֶחָד | 1 | 1 | 9 | 11 | 2.093 | 2.093 | 1.476 | 0.3532 |  |  |
| wild | חַיָּה / רָעָה / חַיַּת | 3 | 0 | 11 | 14 | 1.950 | 4.928 | 1.266 | 0.1353 |  |  |
| rings | טַבְּעֹת | 0 | 3 | 11 | 14 | 1.950 | 4.972 | 1.266 | 0.1316 |  |  |
| injury | מוּם | 1 | 2 | 11 | 14 | 1.950 | 2.203 | 1.266 | 0.3294 |  |  |
| slaughtered | וַיִּשְׁחָט | 2 | 1 | 11 | 14 | 1.950 | 2.188 | 1.266 | 0.3326 |  |  |
| each | אִישׁ | 16 | 29 | 83 | 128 | 1.948 | 4.791 | 0.426 | 0.1414 |  |  |
| fall | יִפֹּל / וְנָפַל / לִפְנֵיכֶם | 3 | 1 | 13 | 17 | 1.891 | 2.631 | 1.135 | 0.3223 |  |  |
| he-goats | עַתֻּדִים / וּלְזֶבַח / קרְבַּן | 1 | 3 | 13 | 17 | 1.891 | 2.660 | 1.135 | 0.3223 |  |  |
| bird | עוֹף / הַחַיָּה / הַצִּפֹּר | 4 | 0 | 13 | 17 | 1.891 | 5.861 | 1.135 | 0.0792 |  |  |
| birds | הָעוֹף | 4 | 2 | 17 | 23 | 1.881 | 2.357 | 0.979 | 0.3223 |  |  |
| jordan | הַיַּרְדֵּן | 6 | 0 | 17 | 23 | 1.881 | 7.838 | 0.979 | 0.0265 | yes |  |
| take | וְלָקַחְתָּ / קַח / תִּקַּח | 48 | 38 | 146 | 232 | 1.875 | 2.644 | 0.311 | 0.3223 |  |  |
| aholibamah | אהֳלִיבָמָה / וְאהֳלִיבָמָה | 1 | 0 | 6 | 7 | 1.855 | 2.848 | 1.665 | 0.3223 |  |  |
| cords | מֵיתְרֵיהֶם׃ / מֵיתָרָיו / וִיתֵדֹתָם | 1 | 0 | 6 | 7 | 1.855 | 2.848 | 1.665 | 0.3223 |  |  |
| sixth | הַשִּׁשִּׁי | 1 | 0 | 6 | 7 | 1.855 | 2.848 | 1.665 | 0.3223 |  |  |
| price | מִקְנָתוֹ / וּפְדוּיָו / בַּכֶּסֶף | 1 | 0 | 6 | 7 | 1.855 | 2.848 | 1.665 | 0.3223 |  |  |
| dip | וְטָבַל / בַּדָּם | 0 | 1 | 6 | 7 | 1.855 | 2.863 | 1.665 | 0.3223 |  |  |
| square | רָבוּעַ / וְאַמָּתַיִם | 1 | 0 | 6 | 7 | 1.855 | 2.848 | 1.665 | 0.3223 |  |  |
| share | שֹׁמְרֵי / הַחֲמִשִּׁים / מִשְׁמֶרֶת | 0 | 1 | 6 | 7 | 1.855 | 2.863 | 1.665 | 0.3223 |  |  |
| someone | תַּחַת / וְכִי / אִישֵׁךְ | 0 | 1 | 6 | 7 | 1.855 | 2.863 | 1.665 | 0.3223 |  |  |
| tomb | קֶבֶר / לַאֲחֻזַּת | 1 | 0 | 6 | 7 | 1.855 | 2.848 | 1.665 | 0.3223 |  |  |
| breach | מֵעַל / בַּיהֹוָה | 1 | 0 | 6 | 7 | 1.855 | 2.848 | 1.665 | 0.3223 |  |  |
| bands | וָוֵי / וַחֲשֻׁקֵיהֶם / וַחֲשׁוּקֵיהֶם | 0 | 1 | 6 | 7 | 1.855 | 2.863 | 1.665 | 0.3223 |  |  |
| scout | לָתוּר | 1 | 0 | 6 | 7 | 1.855 | 2.848 | 1.665 | 0.3223 |  |  |
| machir | מָכִיר | 0 | 1 | 6 | 7 | 1.855 | 2.863 | 1.665 | 0.3223 |  |  |
| horsemen | רִכְבּוֹ / בְּרִכְבּוֹ / וּבְפָרָשָׁיו׃ | 1 | 0 | 6 | 7 | 1.855 | 2.848 | 1.665 | 0.3223 |  |  |
| branch | גְּבִיעֶיהָ / וְקָנָהּ / כַּפְתֹּר | 1 | 0 | 6 | 7 | 1.855 | 2.848 | 1.665 | 0.3223 |  |  |
| close | הַקֶּרֶב | 6 | 6 | 28 | 40 | 1.847 | 1.847 | 0.739 | 0.4115 |  |  |
| keep | וְשָׁמְרוּ | 6 | 3 | 22 | 31 | 1.673 | 2.387 | 0.794 | 0.3223 |  |  |
| eat | תֹּאכְלוּ / יֹאכַל / תֹּאכַל | 31 | 23 | 95 | 149 | 1.622 | 2.423 | 0.360 | 0.3223 |  |  |
| reuben | רְאוּבֵן | 3 | 5 | 20 | 28 | 1.622 | 2.001 | 0.820 | 0.3719 |  |  |
| wall | חֹמָה / מִימִינָם / וּמִשְּׂמֹאלָם׃ | 0 | 2 | 8 | 10 | 1.605 | 3.620 | 1.316 | 0.2240 |  |  |
| spill | יִשְׁפֹּךְ / קַרְנֹת | 0 | 2 | 8 | 10 | 1.605 | 3.620 | 1.316 | 0.2240 |  |  |
| property | רְכוּשָׁם / רָכָשׁוּ / מִקְנֵיהֶם | 0 | 2 | 8 | 10 | 1.605 | 3.620 | 1.316 | 0.2240 |  |  |
| eight | שְׁמֹנַת / שְׁמֹנֶה | 2 | 0 | 8 | 10 | 1.605 | 3.591 | 1.316 | 0.2285 |  |  |
| right | הַיָּמִין / הַיְמָנִית / כֵּן | 7 | 9 | 34 | 50 | 1.604 | 1.800 | 0.614 | 0.4230 |  |  |
| malchiel | בְרִיעָה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| gad's | גָד | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| keeps | וְהֶחֱרִישׁ / וְאָסְרָה / יָקֻמוּ׃ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| year-old | שָׁנָה / הַכְּבָשִׂים / וְזֶה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| herbs | יֹאכְלֻהוּ׃ / וּמְרֹרִים / יַעֲשׂוּ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| loaf | וְכִכַּר / מִסַּל | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| drained | קִיר | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| hamath | חֲמַת / לְבֹא | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| mushi | מַחְלִי / וּמוּשִׁי / וּבְנֵי | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| guni | נַפְתָּלִי / יַחְצְאֵל / וְגוּנִי | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| whichever | תַּשִּׂיג / וּשְׁתֵּי / וְהָאֶחָד | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| worth | הוּא / וּבֵינֶךָ / מֵאֵת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| sered | זְבֻלוּן / סֶרֶד / וְאֵלוֹן | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| scraped | יַקְצִעַ / וְשָׁפְכוּ / הִקְצוּ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| wronged | תֵּפֶן / הֲרֵעֹתִי / נָשָׂאתִי | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| pieces | פִּתִּים / פָּתוֹת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| hamul | וַיִּהְיוּ / פֶרֶץ / וְשֵׁלָה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| regulation | הַמְּאֹרֹת / לְמֶמְשֶׁלֶת / הַכּוֹכָבִים | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| streams | — | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| jezer | וְשִׁלֵּם׃ / יַחְצְאֵל / וְגוּנִי | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| parched | וְקָלִי / וְכַרְמֶל / עֶצֶם | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| jahleel | זְבֻלוּן / סֶרֶד / וְאֵלוֹן | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| cozbi | כּזְבִּי / הַמַּכֶּה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| ledge | עַד / מִלְּמַטָּה / כַּרְכֻּבּוֹ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| connection | מַחְבַּרְתּוֹ / לְחֵשֶׁב / לְעֻמַּת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| timna | וְתִמְנַע / לֶאֱלִיפַז / הָיְתָה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| sir | מֵתֶךָ׃ / אֲדֹנִי / קֶבֶר | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| repugnant | פִּגּוּל / יֵרָצֶה / הָאֹכֶל | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| including | וְזֶה / כְּמַרְאֵה / עַד | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| omar | אוֹמָר / צְפוֹ / אֱלִיפַז | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| prune | תִּזְמֹר / שָׂדְךָ / תִּזְרַע | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| spun | טָווּ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| di | — | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  | ⚠ |
| purity | תֵּשֵׁב / טְהֹרָה / יוֹם | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| violence | חָמָס / וַתִּשָּׁחֵת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| zerahites | לְזֶרַח / הַזַּרְחִי | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| kohath's | וְיִצְהָר / וְעֻזִּיאֵל | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| scheming | הִשְׁלִיךְ / עָלָיו | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| swell | וּבָאוּ / וַתִּמְעֹל / בְּאִישָׁהּ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| thirty-five | חֲמִשָּׁה / וּשְׁלֹשִׁים | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| broke | מוֹצָא / לִנְדָרֶיהָ / וּלְאִסַּר | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| elzaphan | מִישָׁאֵל / אֶלְצָפָן / דֹּד | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| chance | בְּפֶתַע | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| ys | — | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  | ⚠ |
| lifetime | מוֹלַדְתּוֹ / בְּאוּר / פְּנֵי | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| animal's | לָעוֹף / וְלַבְּהֵמָה׃ / בְּהֵמָה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| gatam | גַּעְתָּם / אֱלִיפַז / אַלּוּפֵי | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| parallel | בַּיְרִיעָה / מַקְבִּילֹת / הַלֻּלָאֹת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| sixty-one | וְשִׁשִּׁים / אֶחָד | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| aberration | תֶּבֶל / שְׁכבְתְּךָ / וּבְכל | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| suffice | הָיָה / נָשָׂא / מִשֶּׁבֶת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| net | הָרֶשֶׁת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| baal-zephon | בַּעַל / הַחִירֹת / צְפֹן | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| adjacent | שְׂפָתוֹ / עֵבֶר / בֵּיתָה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| discipline | לְיַסְּרָה / בַּחֲמַת / וְיִסַּרְתִּי | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| hollow | נְבוּב / לֻחֹת / אִתְּךָ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| breasts | הֶחָזוֹת / הֵנִיף / וַיָּשִׂימוּ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| ard | וְנַעֲמָן | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| re | — | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  | ⚠ |
| integrated | וְיַחְדָּו / לִשְׁנֵיהֶם / הַמִּקְצֹעֹת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| sag | וּבָאוּ / וַתִּמְעֹל / בְּאִישָׁהּ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| nine | לְתִשְׁעַת / הַמַּטֶּה / הִתְהַלֵּךְ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| arose | הַגּוֹרָל / עֹלָה / וְעָשָׂהוּ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| zepho | אוֹמָר / צְפוֹ / אֱלִיפַז | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| express | יַפְלִא / לְפַלֵּא / לִנְדָבָה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| yields | תְבוּאֹת / תִקְנֶה / שְׁנֵי | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| azmon | וְנָסַב / מֵעַצְמוֹן / הַיָּמָּה׃ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| nahath | נַחַת / שָׁמָּה / וְאֵלֶּה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| fifty-nine | תִּשְׁעָה / וּשְׁלֹשׁ / וַחֲמִשִּׁים | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| groats | מִגִּרְשָׂהּ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| jochebed | יוֹכֶבֶד / לְלֵוִי / לְעַמְרָם | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| devastate | וַהֲשִׁמֹּתִי / וְשָׁמְמוּ / הַיֹּשְׁבִים | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| reubenites | הָראוּבֵנִי | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| handfuls | מְלֹא / חפְנֵיכֶם / כִּבְשָׁן | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| injustice | עָוֶל / בַּמִּשְׁפָּט / תַעֲשׂוּ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| develop | פָּרוֹחַ / תִּפְרַח / וְכִסְּתָה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| shimei | וְשִׁמְעִי / לִבְנֵי / גֵרְשׁוֹן | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| pools | בְּמַטֶּךָ / הַנְּהָרֹת / הַיְאֹרִים | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| seventeenth | בְּשִׁבְעָה / עָשָׂר / יוֹם | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| regurgitate | מַעֲלֵה / שֹׁסַעַת / וְגֵרָה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| tola | תּוֹלָע | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| holiness | צִיץ / הַקֹּדֶשׁ / קֹדֶשׁ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| vomit | תָקִיא / אֶתְכֶם | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| scar | תַּחְתֶּיהָ / הַבַּהֶרֶת / צָרֶבֶת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| shuni | גָד | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| hawk | הַתִּנְשֶׁמֶת / הַקָּאָת / הָרָחָם׃ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| mo | — | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  | ⚠ |
| scabbed | גָרָב / יַלֶּפֶת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| sprinkled | וַיַּז / לְקַדְּשָׁם׃ / מִשֶּׁמֶן | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| razor | תַּעַר / וְהֶעֱבִירוּ / וְכֹה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| inspect | יְבַקֵּר / הַצָּהֹב / לְשַׁעַר | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| twenty-eight | שְׁמֹנֶה / וְעֶשְׂרִים / לְכל | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| mahli | מַחְלִי / וּמוּשִׁי / וּבְנֵי | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| omer-ful | הָעֹמֶר / מְלֹא / צִנְצֶנֶת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| aligned | לַקֶּרֶשׁ / מְשֻׁלָּבֹת / לְכל | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| ashbel | בִנְיָמִן | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| firstling | יְבֻכַּר / בְּכוֹר / בַּבְּהֵמָה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| becher | לְשׁוּתֶלַח / הַשֻּׁתַלְחִי / לְבֶכֶר | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| divorc | — | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| hairless | יִמָּרֵט / קֹרַח / מִפְּאַת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| hori | שָׁפָט / חוֹרִי׃ / וְהֵימָם | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| amen | בְּמֵעַיִךְ / לַצְבּוֹת / בֶּטֶן | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| engravings | וְהָאֲבָנִים / שֵׁבֶט / שְׁמֹתָם | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| winepress | וְנֶחְשַׁב / תְּרוּמַתְכֶם / כַּדָּגָן | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| sidewalls | לְזֵרוֹ / צַלְעֹתָיו / צִדָּיו | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| yl | — | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  | ⚠ |
| pollute | תַחֲנִיפוּ / יַחֲנִיף / וְלָאָרֶץ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| kadesh-barnea | בַּרְנֵעַ / בְּשׁלְחִי / מִקְדַּשׁ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| layer | שִׁכְבַת / וַתַּעַל / הַטַּל | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| shuthelah | מִשְׁפַּחַת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| ataroth | וַיִּבְנוּ / דִּיבֹן / עֲטָרֹת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| ointment | מִרְקַחַת / וְעָשִׂיתָ / רֹקַח | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| jas | — | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| profanes | וְנֹקֵב / בְּנקְבוֹ / יִרְגְּמוּ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| closest | הַקֶּרֶב / מִמִּשְׁפַּחְתּוֹ / לְאָבִיו | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| pe | — | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  | ⚠ |
| thirty-three | וּבְנוֹתָיו / וּשְׁלֹשׁ / שְׁלֹשִׁים | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| doubles | וְיַחְדָּו / לִשְׁנֵיהֶם / הַמִּקְצֹעֹת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| winged | כָּנָף | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| entirely | כְּלִיל / תּקְטָר׃ / וְהַכֹּהֵן | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| untrimmed | שְׁנַת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| drawers | וּמִכְנְסֵי / יִלְבַּשׁ / בַּד | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| falsehood | יִשָּׁבַע / וַחֲמִשִׁתָיו / יִתְּנֶנּוּ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| mail | כְּפִי / בְּתוֹכוֹ / לְפִיו | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| gleaning | וּבְקֻצְרְכֶם / תְכַלֶּה / וְלֶקֶט | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| serpent | לְתַנִּין׃ / וְלִפְנֵי | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| choice | בְּתוֹכֵנוּ / בְּמִבְחַר / קְבָרֵינוּ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| buys | יִקְנֶה / קִנְיַן / וִילִיד | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| sworn | לֶאְסֹר / יַחֵל / מִפִּיו | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| prominent | קריאי / קְרוּאֵי / אֲבוֹתָם | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| detest | תְּשַׁקְּצוּ / וְשֶׁקֶץ / נִבְלָתָם | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| sits | הַכְּלִי / וְהַיֹּשֵׁב / יֹשֵׁב | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| pushed | הִשְׁלִיךְ / עָלָיו | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| afflict | וְהִכִּיתֶם / צְרוֹר / הַמִּדְיָנִים | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| accept | שַׁבְּתֹתֶיהָ / וְהִרְצָת / תִּרְצֶה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| fifty-four | וַחֲמִשִּׁים / אַרְבָּעָה / וּפְקֻדָיו | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| fifteenth | עָשָׂר / לַיהֹוָה / וּבַחֲמִשָּׁה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| twenty-four | וְעֶשְׂרִים / אַרְבָּעָה / וְאַרְבָּעָה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| wooden | עֵץ / שַׂק / יוּבָא | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| amram's | יוֹכֶבֶד / לְלֵוִי / לְעַמְרָם | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| inward | שְׂפָתוֹ / עֵבֶר / בֵּיתָה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| korahites | הַקּרְחִי׃ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| seventy-three | הַשְּׁלֹשָׁה / וְהַשִּׁבְעִים / וְהַמָּאתָיִם | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| nebo | נְבוֹ / שִׂבְמָה / מוּסַבֹּת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| villages | הַחֲצֵרִים / וּבַיֹּבֵל / יֵחָשֵׁב | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| pi-hahiroth | בַּעַל / הַחִירֹת / צְפֹן | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| horse | סוּס / וּפָרָשָׁיו / תּוֹךְ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| sixty-two | וְשִׁשִּׁים / וּשְׁבַע / שְׁנַיִם | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| hazar-enan | עֵינָן׃ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| arba | — | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| ewe-lamb | וְכַבְשָׂה / שְׁנָתָהּ / בַּת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| ra | — | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  | ⚠ |
| donations | וּלְבָנֶיךָ / תְּרוּמָתִי׃ / לְמשְׁחָה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| object | בִּכְלִי / יָד | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| adultery | יִנְאַף / הַנֹּאֵף / וְהַנֹּאָפֶת׃ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| shammah | נַחַת / שָׁמָּה / וְאֵלֶּה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| shem's | שָׁם / לְגוֹיֵהֶם׃ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| b | — | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  | ⚠ |
| embroiderer | חֶרֶשׂ / וְרֹקֵם / בַּתְּכֵלֶת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| rebelled | מְרִיתֶם / לְמִי / עַמָּיו | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| dibon | וַיִּבְנוּ / דִּיבֹן / עֲטָרֹת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| vain | לָרִיק / וְתַם / כֹּחֲכֶם | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| burns | וְהַשֹּׂרֵף / יָבוֹא / יְכַבֵּס | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| appearing | נִרְאָה / אֲלֵיכֶם / וּמִנְחָה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| ninety | תִּשְׁעִים | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| attend | וְשֵׁרְתוּ / יְשָׁרְתֻהוּ / וְסָבִיב | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| jahzeel | נַפְתָּלִי / יַחְצְאֵל / וְגוּנִי | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| twos | שְׁנַיִם / הַבָּשָׂר / מִכּל | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| appendage | עֲלֵיהֶן / וְהָאַלְיָה / וְהִקְטַרְתָּ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| collecting | מְקֹשֵׁשׁ / עֵצִים / הַמֹּצְאִים | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| vinegar | מִיַּיִן / וְחֹמֶץ / וַעֲנָבִים | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| designer | חֶרֶשׂ / וְרֹקֵם / בַּתְּכֵלֶת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| subdued | וְנִכְבְּשָׁה / לַאֲחֻזָּה / וּמִיִּשְׂרָאֵל | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| shuhamites | הַשּׁוּחָמִי | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| midianites | הַמִּדְיָנִים / נָקֹם / תֵּאָסֵף׃ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| frame's | הָאָמָה / רֹחַב / אֱמֶת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| z | — | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  | ⚠ |
| decontaminate | לַחֲטֹא / וְחִטֵּא / וּבַצִּפֹּר | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| seventy-four | אַרְבָּעָה / וְשִׁבְעִים | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| areli | צִפְיוֹן / וְחַגִּי / שׁוּנִי | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| greenish | יְרַקְרַק / וְהרְאָה / אֲדַמְדָּם | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| aromatic | מר / וְקִנְּמן / מַחֲצִיתוֹ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| vintage | וְהִשִּׂיג / דַּיִשׁ / בָּצִיר | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| pots | הַסִּירֹת / סִּירֹתָיו / לְדַשְּׁנוֹ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| arrangement | עֵרֶךְ / וַיַּעֲרֹךְ / וְעָרַכְתָּ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| canals | בְּמַטֶּךָ / הַנְּהָרֹת / הַיְאֹרִים | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| shorts | מִכְנְסֵי / פַּאֲרֵי / הַמִּגְבָּעֹת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| jaci | — | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| ru | — | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| fountains | מַעְיְנֹת / וַאֲרֻבֹּת / וַיִּסָּכְרוּ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| hezronites | לְחֶצְרֹן | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| mountings | תַּרְשִׁישׁ / וְיָשְׁפֵה / בְּמִלֻּאֹתָם׃ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| faith | וָמַעְלָה / בּוֹ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| elizaphan | אֱלִיצָפָן / אָב / לְמִשְׁפְּחֹת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| forty-six | שִׁשָּׁה / וְאַרְבָּעִים / וּפְקֻדָיו | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| encampments | טִירֹתָם / שָׂרְפוּ / עָרֵיהֶם | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| cow's | הַפָּרָה / אֵפֶר / וְהָיְתָה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| forty-one | אֶחָד / וְאַרְבָּעִים | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| libni | וְשִׁמְעִי / לִבְנֵי / גֵרְשׁוֹן | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| handbreadth | מִסְגֶּרֶת / טֹפַח / לְמִסְגַּרְתּוֹ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| uncle | מִשְּׁאֵר / הִשִּׂיגָה / וְנִגְאָל׃ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| sores | פֹּרֵחַ / אֲבַעְבֻּעֹת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| traded | הָמֵר / וּתְמוּרָתוֹ / יַחֲלִיפֶנּוּ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| scurvied | גָרָב / יַלֶּפֶת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| wring | וּמָלַק | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| issachar's | יִשָּׂשכָר | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| blast | הַצַּר / הַצֹּרֵר / וַהֲרֵעֹתֶם | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| one-year-olds | תְּמִימִם / שָׁנָה / וְעֵגֶל | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| developing | פֹּרַחַת / תִרְאֶה / תִּשְׂרְפֶנּוּ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| kohathites | הַקְּהָתִים / וְהֵקִימוּ / בֹּאָם׃ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| detached | וְיִרְכְּסוּ / בִּפְתִיל / יִזַּח | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| ham's | חָם | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| menstruation | תַזְרִיעַ / נִדַּת / דְּוֺתָהּ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| residing | מְגֻרֶיךָ / וְהָיִיתִי / לַאֲחֻזַּת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| simeonites | הַשִּׁמְעֹנִי / וּמָאתָיִם׃ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| uncle's | דֹּדוֹ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| ohad | יְמוּאֵל / וְיָמִין / וְאֹהַד | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| serah | שָׂרַח׃ / וְשֵׁם / בַּת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| pa | — | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| lamp | זָךְ / לְהַעֲלֹת / נֵר | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| slain | בְקָבֶר / בְּעֶצֶם / אֵזוֹב | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| cleared | הִנָּקִי / מִמֵּי / וְהִשְׁבִּיעַ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| shepham | וְהִתְאַוִּיתֶם / מֵחֲצַר / שְׁפָמָה׃ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| affliction's | בַּנֶּגַע / מֵעוֹר / כְּמַרְאֵה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| shillem | וְשִׁלֵּם׃ / יַחְצְאֵל / וְגוּנִי | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| ghosts | הָאֹבֹת / הַיִּדְּעֹנִים / וְאֶל | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| nobah | וְנֹבַח / קְנָת / נֹבַח | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| eri | צִפְיוֹן / וְחַגִּי / שׁוּנִי | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| fences | וּגְדֵרֹת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| elongated | שָׂרוּעַ׃ / וְקָלוּט / וּלְנֵדֶר | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| washing | לְרחְצָה / שָׁמָּה / כִּיּוֹר | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| fellow's | עֲמִיתֶךָ / לְזֶרַע / שְׁכבְתְּךָ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| urim | הָאוּרִים / וְשָׁאַל / פִּיו | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| ga | — | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| merarite | מְרָרִי | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| offenses | לְכל / חַטָּאתָם | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| permanently | תִמָּכֵר / לִצְמִתֻת / וְתוֹשָׁבִים | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| hoshea | הוֹשֵׁעַ / לְהוֹשֵׁעַ / שָׁלַח | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| naphtali's | נַפְתָּלִי | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| ruin | חֹרֵבָה׃ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| rub | וּמָחָה / וְכָתַב / הָאָלֹת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| rivers | בְּמַטֶּךָ / הַנְּהָרֹת / הַיְאֹרִים | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| beam | הַמּוֹט׃ / וְנָתְנוּ / הַשָּׁרֵת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| leftover | וְהָאַמָּה / בָּעֹדֵף / סָרוּחַ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| menstrual | וְהַדָּוָה / וְהַזָּב / וּלְאִישׁ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| mishael | מִישָׁאֵל / אֶלְצָפָן / דֹּד | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| observed | לֵיל / לְהוֹצִיאָם / שִׁמֻּרִים | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| apertures | מַעְיְנֹת / וַאֲרֻבֹּת / וַיִּסָּכְרוּ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| jemuel | יְמוּאֵל / וְיָמִין / וְאֹהַד | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| accounts | פְּקוּדֵי / וְאֶלֶף | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| divorced | גְּרוּשָׁה / מֵאִישָׁהּ / לֵאלֹהָיו׃ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| fire-roasted | צְלִי / אֵשׁ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| boards | נְבוּב / לֻחֹת / אִתְּךָ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| elealeh | אֶלְעָלֵא / קִרְיָתָיִם׃ / בְּנוֹ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| visitors | הַתּוֹשָׁבִים / וּמִמִּשְׁפַּחְתָּם / הוֹלִידוּ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| inscribe | וּפִתַּחְתָּ / עֲלֵיהֶם / שְׁתֵּי | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| contributions | נִדְרֵיהֶם / נִדְבוֹתָם / וּלְכֹל | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| diminish | הֶעָשִׁיר / וְהַדַּל / יַמְעִיט | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| shimron | וּפֻוָה / וְיוֹב / וְשִׁמְרֹן׃ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| strengthened | וַיֶּחֱזַק / רָמָה׃ / אַחֲרֵי | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| eagle | הַנֶּשֶׁר / הַפֶּרֶס / הָעזְנִיָּה׃ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| seventy-two | וְשִׁבְעִים / שְׁנַיִם / וּבָקָר | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| ishvi | לְיִמְנָה / הַיִּמְנָה / לְיִשְׁוִי | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| serpents | וַיַּשְׁלִיכוּ / לְתַנִּינִם / וַיִּבְלַע | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| consecrates | הַמַּקְדִּישׁ / חֲמִשִׁית / וְקָם | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| zur | צוּר | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| quantities | תַעֲשׂוּ / בְּמַתְכֻּנְתָּהּ / וְהִקְטַרְתָּ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| acquaintances | הָאֹבֹת / הַיִּדְּעֹנִים / וְאֶל | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| carved | אֱלִילִם / וּפֶסֶל / וּמַצֵּבָה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| bar | הַתִּיכֹן / הַקָּצֶה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| sixty-four | וְשִׁשִּׁים / אַרְבָּעָה / לִפְקֻדֵיהֶם | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| raven | עֶרֶב / לְמִינוֹ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| vomited | בְּטַמַּאֲכֶם / קָאָה / לִפְנֵיכֶם | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| languages | לִלְשֹׁנֹתָם / בְּאַרְצֹתָם | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| vulture | הַנֶּשֶׁר / הַפֶּרֶס / הָעזְנִיָּה׃ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| thirty-six | שִׁשָּׁה / וּשְׁלֹשִׁים / וּבָקָר | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| battered | וַיִּרְגְּמוּ / וַיֹּצִיאוּ / וַיּוֹצִיאוּ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| boiled | וּמֹרַק / וְשֻׁטַּף / בֻּשָּׁלָה | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| zebulun's | זְבוּלֻן | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| northward | צָפֹנָה / יֶרֶךְ | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| spatter | יִזֶּה / בִּבְשָׂרָהּ / וַאֲשֶׁר | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| pphi | — | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| instant | כְּרָגַע׃ / וְאֹכֵלָה / הַזֹּאת | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| lay | וְסָמַךְ | 5 | 2 | 18 | 25 | 1.575 | 2.512 | 0.853 | 0.3223 |  |  |
| so | כֵּן | 41 | 48 | 148 | 237 | 1.573 | 2.023 | 0.281 | 0.3666 |  |  |
| seventy | שִׁבְעִים | 1 | 5 | 16 | 22 | 1.536 | 3.666 | 0.894 | 0.2180 |  |  |
| aram | אֲרָם | 3 | 0 | 10 | 13 | 1.520 | 4.499 | 1.135 | 0.1414 |  |  |
| nun | נוּן | 0 | 3 | 10 | 13 | 1.520 | 4.542 | 1.135 | 0.1414 |  |  |
| washed | וַיִּרְחַץ / וַיְכַבְּסוּ / רָחַץ | 3 | 0 | 10 | 13 | 1.520 | 4.499 | 1.135 | 0.1414 |  |  |
| herself | נַפְשָׁהּ / אָסְרָה | 3 | 0 | 10 | 13 | 1.520 | 4.499 | 1.135 | 0.1414 |  |  |
| comes | בְּבֹאוֹ | 2 | 3 | 14 | 19 | 1.509 | 1.661 | 0.949 | 0.4455 |  |  |
| yourselves | נַפְשֹׁתֵיכֶם / לָכֶם / תַעֲשׂוּ | 1 | 3 | 12 | 16 | 1.499 | 2.268 | 1.024 | 0.3223 |  |  |
| death | מוֹת / יוּמָת׃ | 8 | 9 | 35 | 52 | 1.447 | 1.497 | 0.571 | 0.4691 |  |  |
| covenant | בְּרִית / בְּרִיתִי | 9 | 7 | 33 | 49 | 1.375 | 1.542 | 0.572 | 0.4585 |  |  |
| consecrated | וַיְקַדֵּשׁ / הַכֹּתִי / הִקְדַּשְׁתִּי | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| desecrated | וְאֹכְלָיו / חִלֵּל / לְהֵחַלּוֹ׃ | 0 | 1 | 5 | 6 | 1.305 | 2.312 | 1.424 | 0.3223 |  |  |
| acquired | רָכַשׁ / קִנְיָנוֹ / מִקְנֵהוּ | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| laid | וַיִּסְמֹךְ / וַיְצַוֵּהוּ / וַיִּגַּשׁ | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| fifteen | עֲשָׂרָה / חָמֵשׁ / וְלַכָּתֵף | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| tail | הָאַלְיָה | 0 | 1 | 5 | 6 | 1.305 | 2.312 | 1.424 | 0.3223 |  |  |
| addition | לְבֹנָתָהּ / מִיָּדָם / עַל | 0 | 1 | 5 | 6 | 1.305 | 2.312 | 1.424 | 0.3223 |  |  |
| separate | מַבְדִּיל / לָמָיִם / הַשְּׂמֹאל | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| subtracted | יִגָּרַע / אֵין | 0 | 1 | 5 | 6 | 1.305 | 2.312 | 1.424 | 0.3223 |  |  |
| carcasses | פִּגְרֵיכֶם | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| established | הֲקִמֹתִי / וַיָּקם | 0 | 1 | 5 | 6 | 1.305 | 2.312 | 1.424 | 0.3223 |  |  |
| prey | הַמַּלְקוֹחַ / וּבַבְּהֵמָה | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| facing | פְּנֵי / שְׂדֵה | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| hidden | וְנֶעְלַם / וְהוּא | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| broken | הַפָּר / וְעָרֵל / יִשָּׁבֵר | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| robe | מְעִיל / כְּלִיל / הַבְּגָדִים | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| leaven | שְׂאֹר / חָמֵץ | 0 | 1 | 5 | 6 | 1.305 | 2.312 | 1.424 | 0.3223 |  |  |
| ephah | עֲשִׂירִת / הָאֵפָה / הָאֵיפָה | 0 | 1 | 5 | 6 | 1.305 | 2.312 | 1.424 | 0.3223 |  |  |
| shadday | שַׁדַּי / וְאֶל | 0 | 1 | 5 | 6 | 1.305 | 2.312 | 1.424 | 0.3223 |  |  |
| travels | מַסְעֵיהֶם׃ / לְמַסְעֵיהֶם׃ / בְּכל | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| kings | לְגוֹיִם / וּמְלָכִים / מִמְּךָ | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| wings | פֹּרְשֵׂי / כְנָפַיִם / סֹכְכִים | 0 | 1 | 5 | 6 | 1.305 | 2.312 | 1.424 | 0.3223 |  |  |
| accepted | יֵרָצֶה / תִּזְבָּחֻהוּ׃ / תִזְבְּחוּ | 0 | 1 | 5 | 6 | 1.305 | 2.312 | 1.424 | 0.3223 |  |  |
| redeem | תִּפְדֶּה / יִגָּאֵל / הַטְּמֵאָה | 3 | 4 | 17 | 24 | 1.268 | 1.379 | 0.772 | 0.5053 |  |  |
| off | וְנִכְרְתָה / הַהוּא / מִקֶּרֶב | 8 | 12 | 39 | 59 | 1.249 | 1.859 | 0.496 | 0.4081 |  |  |
| appointed | בְּמֹעֲדוֹ / לְמוֹעֵד / מוֹעֲדֵי | 3 | 3 | 15 | 21 | 1.216 | 1.216 | 0.804 | 0.5624 |  |  |
| mount | בְּהַר / הַר | 5 | 1 | 15 | 21 | 1.216 | 3.287 | 0.804 | 0.2767 |  |  |
| silver | כֶּסֶף | 20 | 16 | 64 | 100 | 1.179 | 1.471 | 0.372 | 0.4773 |  |  |
| simeon | שִׁמְעוֹן | 3 | 2 | 13 | 18 | 1.171 | 1.309 | 0.845 | 0.5284 |  |  |
| circumcised | הִמּוֹל / בְּנוֹ / וַיָּמל | 5 | 0 | 13 | 18 | 1.171 | 6.135 | 0.845 | 0.0668 |  |  |
| abihu | נָדָב / וַאֲבִיהוּא | 0 | 2 | 7 | 9 | 1.154 | 3.169 | 1.135 | 0.2834 |  |  |
| caleb | כָּלֵב / יְפֻנֶּה | 2 | 0 | 7 | 9 | 1.154 | 3.140 | 1.135 | 0.2878 |  |  |
| magicians | הַחַרְטֻמִּים / חַרְטֻמֵּי | 0 | 2 | 7 | 9 | 1.154 | 3.169 | 1.135 | 0.2834 |  |  |
| hebron | חֶבְרוֹן | 1 | 1 | 7 | 9 | 1.154 | 1.154 | 1.135 | 0.5853 |  |  |
| nadab | נָדָב / וַאֲבִיהוּא | 0 | 2 | 7 | 9 | 1.154 | 3.169 | 1.135 | 0.2834 |  |  |
| open | פְּנֵי / וְשִׁלַּח / הַשָּׂדֶה | 1 | 1 | 7 | 9 | 1.154 | 1.154 | 1.135 | 0.5853 |  |  |
| north | צָפוֹן | 2 | 0 | 7 | 9 | 1.154 | 3.140 | 1.135 | 0.2878 |  |  |
| carry | לָשֵׂאת | 5 | 4 | 20 | 29 | 1.118 | 1.191 | 0.660 | 0.5711 |  |  |
| whose | אֲשֶׁר | 8 | 0 | 18 | 26 | 1.051 | 8.993 | 0.672 | 0.0139 | yes |  |
| ephraim | אֶפְרַיִם | 0 | 5 | 12 | 17 | 0.864 | 5.901 | 0.734 | 0.0772 |  |  |
| gilead | הַגִּלְעָד׃ / גִּלְעָד | 1 | 3 | 10 | 14 | 0.811 | 1.580 | 0.772 | 0.4468 |  |  |
| shed | לְהָאִיר | 1 | 0 | 4 | 5 | 0.803 | 1.795 | 1.135 | 0.4236 |  |  |
| statutory | חקְךָ / וְחק / בָּנֶיךָ | 0 | 1 | 4 | 5 | 0.803 | 1.810 | 1.135 | 0.4202 |  |  |
| salt | מֶלַח׃ | 1 | 0 | 4 | 5 | 0.803 | 1.795 | 1.135 | 0.4236 |  |  |
| forty-five | חֲמִשָּׁה / וְאַרְבָּעִים | 1 | 0 | 4 | 5 | 0.803 | 1.795 | 1.135 | 0.4236 |  |  |
| body | בְּמֵת | 0 | 1 | 4 | 5 | 0.803 | 1.810 | 1.135 | 0.4202 |  |  |
| distinguished | הִבְדַּלְתִּי / אֶתְכֶם / וּבַמֶּה | 0 | 1 | 4 | 5 | 0.803 | 1.810 | 1.135 | 0.4202 |  |  |
| carries | וְהַנֹּשֵׂא / יְכַבֵּס / הַנֹּשֵׂא | 0 | 1 | 4 | 5 | 0.803 | 1.810 | 1.135 | 0.4202 |  |  |
| basins | בָּאַגָּנֹת / זֹרַק / מִזְרְקֵי | 0 | 1 | 4 | 5 | 0.803 | 1.810 | 1.135 | 0.4202 |  |  |
| separation | לַיהֹוָה / יְמֵי / הַזִּירוֹ | 1 | 0 | 4 | 5 | 0.803 | 1.795 | 1.135 | 0.4236 |  |  |
| new | חֹדֶשׁ / תִּסְפְּרוּ / חֲדָשָׁה | 0 | 1 | 4 | 5 | 0.803 | 1.810 | 1.135 | 0.4202 |  |  |
| therefore | לָכֵן | 1 | 0 | 4 | 5 | 0.803 | 1.795 | 1.135 | 0.4236 |  |  |
| elevated | וַיְנִיפֵהוּ / לְמֹשֶׁה / וַיָּנֶף | 0 | 1 | 4 | 5 | 0.803 | 1.810 | 1.135 | 0.4202 |  |  |
| span | כָּפוּל / זֶרֶת / וְזֶרֶת | 0 | 1 | 4 | 5 | 0.803 | 1.810 | 1.135 | 0.4202 |  |  |
| born | יָלַד | 6 | 2 | 17 | 25 | 0.802 | 2.283 | 0.592 | 0.3223 |  |  |
| seed's | כְּהֻנַּת / לֵאלֹהָיו׃ / וַיְכַפֵּר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| starvation | מוּתֵנוּ / בְּשִׁבְתֵּנוּ / סִיר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| havvoth-jair | וְיָאִיר / חַוֺּתֵיהֶם / חַוֺּת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| mounted | טוּרֵי / וַיִּמְלְאוּ / אֶבֶן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| compound | יִרְקַח / וַאֲשֶׁר / מֵעַמָּיו׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| receded | וַיַּחְסְרוּ / וּמְאַת / יוֹם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ejecting | בְּחֻקֹּת / וָאָקֻץ / מִפְּנֵיכֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| crossing | תנואון / תְנִיאוּן / מֵעֵבֶר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| mirrors | הַצֹּבְאֹת / בְּמַרְאֹת / צְבָאוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| sha | — | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  | ⚠ |
| haste | וְכָכָה / מתְנֵיכֶם / חֲגֻרִים | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| morning's | מִלְּבַד / כַּפּוֹ / מִמֶּנָּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| estimate | מָךְ / וְהֶעֱמִידוֹ / הַנֹּדֵר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| faraway | רְחֹקָה / בַּדֶּרֶךְ / וְעָשָׂה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| inter-course | הַטַּף / בַּנָּשִׁים / הַחֲיוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| hupham | לִשְׁפוּפָם / הַשּׁוּפָמִי / לְחוּפָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| generate | תַּדְשֵׁא / לְמִינוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| togarmah | אַשְׁכְּנַז / וְרִיפַת / וְתֹגַרְמָה׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| abarim | הָעִבְרִים / לִבְנֵי / הַר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| arod | לַאֲרוֹד / הָאַרְוָדִי / לְאַרְאֵלִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| harvesting | לִקְצֹר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ararat | הָרֵי / אֲרָרָט׃ / וַתָּנַח | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| powder | לְאָבָק / לִשְׁחִין / וְעַל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| shelomith | וַיִּקֹּב / וַיְקַלֵּל / שְׁלֹמִית | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| leg | רֶגֶל / יָד / שֶׁבֶר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| mushites | הוֹלִד / הַמַּחְלִי / הַמּוּשִׁי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| spear | רֹמַח / בְּיָדוֹ / מִתּוֹךְ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| galbanum | — | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| hemdan | חֶמְדָּן / וְאֶשְׁבָּן / וְיִתְרָן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| afflicts | הַצַּר / הַצֹּרֵר / וַהֲרֵעֹתֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| point | רִאשׁוֹנָה / ערְפּוֹ / יַבְדִּיל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| relatives | וּבִתָּהּ / בִּתָּהּ / שְׁאֵרָהּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| elonites | לְסֶרֶד / הַסַּרְדִּי / לְאֵלוֹן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| bukki | בֻּקִּי / יגְלִי׃ / וּלְמַטֵּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| sibmah | נְבוֹ / שִׂבְמָה / מוּסַבֹּת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| subdue | וְכַבְשָׂה / הָרֹמֶשֶׂת / חַיָּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| inherits | יֹרֶשֶׁת / מִמַּטּוֹת / יִירְשׁוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| towns | וְנֹבַח / קְנָת / נֹבַח | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| migdol | וְיַחֲנוּ / מִגְדֹּל / נִכְחוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| patterned | וְאֵפוֹד / וּמְעִיל / וּכְתֹנֶת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| leaks | בְּזוֹבוֹ / רָר / הֶחְתִּים | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| coated | חִלֵּץ / הִטּוֹחַ׃ / הַקְּצָוֺת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| secular | הֵחֵל / הַטָּהוֹר / וּלְהַבְדִּיל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| hazar-addar | עַקְרַבִּים / צִנָה / אַדָּר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| brass | וּמֹרַק / וְשֻׁטַּף / בֻּשָּׁלָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| rival | לִצְרֹר / בְּחַיֶּיהָ׃ / אֲחֹתָהּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| quantity | בַּמִּדָּה / וּבַמְּשׂוּרָה׃ / בַּמִּשְׁקָל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| mizzah | מִזֶּה / אַלּוּפֵי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| profaned | וַיִּקֹּב / וַיְקַלֵּל / שְׁלֹמִית | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| coals | גַּחֲלֵי / חפְנָיו / דַּקָּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| moons | שִׂמְחַתְכֶם / וּבְמוֹעֲדֵיכֶם / וּבְרָאשֵׁי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| murdered | יִרְצַח / עֶדְיָם / יַעֲנֶה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| bat | הַחֲסִידָה / הָאֲנָפָה / הַדּוּכִיפַת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| circumcise | וּמַלְתָּה / אָז / בּוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| alert | וְהִזַּרְתֶּם / מִטֻּמְאָתָם / בְּטֻמְאָתָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| nemuelites | לִנְמוּאֵל / הַנְּמוּאֵלִי / לְיָמִין | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| naamites | הָאַרְדִּי / לְנַעֲמָן / הַנַּעֲמִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| oneself | יְקִימֶנּוּ / וְאִישָׁהּ / יְפֵרֶנּוּ׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| paws | כַּפָּיו / הַהֹלֶכֶת / הוֹלֵךְ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| beams | וָאֶשְׁבֹּר / מֹטֹת / וָאוֹלֵךְ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| foe | הַצַּר / הַצֹּרֵר / וַהֲרֵעֹתֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| belt | אֲפֻדָּתוֹ / כְּמַעֲשֵׂהוּ / וְחִשַּׁב | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| tithes | מַעְשְׂרֹתֵיכֶם / תָּרִימוּ / מִכּל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| beeri | יְהוּדִית / בְּאֵרִי / אֵילֹן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| salted | רוֹקֵחַ / מְמֻלָּח / אֹתָהּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| stumbling | מִכְשֹׁל / תְקַלֵּל / תִּתֵּן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| arelites | לַאֲרוֹד / הָאַרְוָדִי / לְאַרְאֵלִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| elam | עֵילָם / וְאַשּׁוּר / וְלוּד | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| figures | מַשְׂכִּיֹּתָם / צַלְמֵי / מַסֵּכֹתָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| jaminites | לִנְמוּאֵל / הַנְּמוּאֵלִי / לְיָמִין | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| testicles | גִבֵּן / תְּבַלֻּל / בְּעֵינוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| meshech | וּמָגוֹג / וּמָדַי / וְיָוָן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| wonder | מוֹפֵת / וְהַשְׁלֵךְ / אֲלֵכֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| bruised | וּמָעוּךְ / וְכָתוּת / וְנָתוּק | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| vophsi | נַחְבִּי / ופְסִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| aroer | עֲטָרֹת / וַיִּבְנוּ / דִּיבֹן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| el-isha | יָוָן / אֱלִישָׁה / וְתַרְשִׁישׁ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| zoan | אֲחִימַן / שֵׁשַׁי / וְתַלְמַי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| lots | גֹּרָלוֹת / גּוֹרָל / וְגוֹרָל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| tree's | מִזֶּרַע / הָעֵץ / וְכל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| hanging | וְסֶרַח / בִּירִיעֹת / הָעֹדֶפֶת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| murder | וְרָצַח / וּמָצָא / לִגְבוּל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| wagon | עֶגְלֹת / צָב / עֶגְלָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| shine | — | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| abiasaph | אַסִּיר / וְאֶלְקָנָה / וַאֲבִיאָסָף | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| double-fold | וְכָפַלְתָּ / הַשִּׁשִּׁית / לְבָד | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| requiring | וְהִשִּׂיאוּ / אַשְׁמָה / בְּאכְלָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| offshoot | וּמָךְ / לְגֵר / לְעֵקֶר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| rock-badger | הַשָּׁפָן / יַפְרִיס / מַעֲלֵה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| principal | וְהִתְוַדּוּ / וַחֲמִישִׁתוֹ / בְּרֹאשׁוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| tetter | כֵּהוֹת / בֹּהַק / פֹּרֵחַ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| farther | נִנְחַל / וָהָלְאָה / בָּאָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| elidad | אֱלִידָד / כִּסְלוֹן׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| teemed | וַיִּשְׁרְצוּ / וַיַּעַצְמוּ / וּבְנֵי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| atnez | — | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| eighty-six | וְשֵׁשֶׁת / וּשְׁמֹנִים / רִאשֹׁנָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| freedom | נֶחֱרֶפֶת / נִפְדָּתָה / חֻפְשָׁה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| likeness | בְּצַלְמֵנוּ / כִּדְמוּתֵנוּ / וַיֵּרְדוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ghost | אוֹב / יִדְּעֹנִי / דְּמֵיהֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| desecrating | תֵחֵל / מְחַלֶּלֶת / הִיא | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| extracted | חִלֵּץ / הִטּוֹחַ׃ / הַקְּצָוֺת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| frustration | תַּרְתֶּם / לַשָּׁנָה / עֲוֺנֹתֵיכֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| threads | וַיְרַקְּעוּ / פַּחֵי / וְקִצֵּץ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| rains | גִשְׁמֵיכֶם / בְּעִתָּם / וְנָתַתִּי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ain | מִשְּׁפָם / הָרִבְלָה / לָעָיִן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| zebulunites | הַזְּבוּלֹנִי / לִפְקֻדֵיהֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| punites | הַתּוֹלָעִי / לְפֻוָה / הַפּוּנִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| expiate | וְחִטְּאוֹ / הַטָּמֵא / הַטָּהֹר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| eleventh | עַשְׁתֵּי / עָשָׂר / יוֹם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| afflicting | צֹרְרִים / בְּנִכְלֵיהֶם / נִכְּלוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| gether | וְחוּל / וְגֶתֶר / וָמַשׁ׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| liberty | וְשַׁבְתֶּם / יֹשְׁבֶיהָ׃ / דְּרוֹר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| stories | צֹהַר / לַתֵּבָה / תְּכַלֶּנָּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| grieving | וְהִפְקַדְתִּי / בֶּהָלָה / הַשַּׁחֶפֶת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| mouths | לְצֹנַאֲכֶם / וְהַיֹּצֵא / מִפִּיכֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| he-lambs | וּשְׁלֹשָׁה / תְּמִימִם / כְּבָשִׂים | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| haggites | לִצְפוֹן / הַצְּפוֹנִי / לְחַגִּי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| exploited | בְּפִקָּדוֹן / בִתְשׂוּמֶת / בְגָזֵל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| geuel | גְּאוּאֵל / מָכִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| failed | וּבְדֶרֶךְ / וְחָדַל / וְהָאִישׁ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| inhabitants | וְשַׁבְתֶּם / יֹשְׁבֶיהָ׃ / דְּרוֹר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| adbeel | נְבָיֹת / וְקֵדָר / וְאַדְבְּאֵל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| gomer's | אַשְׁכְּנַז / וְרִיפַת / וְתֹגַרְמָה׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| decreased | וַיָּשֹׁכּוּ / בַּתֵּבָה׃ / וַיַּעֲבֹר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| hemam | וְהֵימָם / חֹרִי / תִּמְנָע׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| deposited | הַגְּזֵלָה / גָּזָל / הָעֹשֶׁק | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| rekem | חַלְלֵיהֶם / אֱוִי / רֶבַע | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| substantial | עָצוּם / וּמִקְנֶה / וְלִבְנֵי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| kenath | וְנֹבַח / קְנָת / נֹבַח | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| pallu's | פַלּוּא / וּבְנֵי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| grieve | בְּקִרְיַת / לִסְפֹּד / וְלִבְכֹּתָהּ׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| shemidaites | וּשְׁמִידָע / הַשְּׁמִידָעִי / וְחֵפֶר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| selling | וּלְפִי / מָכַר / הַשָּׁנִים | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| fistful | יַשְׁקֶה / וְקָמַץ / וְאַחַר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| asriel | וְאַשְׂרִיאֵל / הָאַשְׂרִאֵלִי / הַשִּׁכְמִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| sown | זֵרוּעַ / יִזָּרֵעַ / מִנִּבְלָתָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| chooses | וַיֵּדַע / הַקָּדוֹשׁ / יִבְחַר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| tolaites | הַתּוֹלָעִי / לְפֻוָה / הַפּוּנִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| inaccessible | עֲוֺנֹתָם / גְּזֵרָה / וְנָשָׂא | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| bereave | וְהִשְׁלַחְתִּי / וְשִׁכְּלָה / וְהִכְרִיתָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| desolation | שָׁבְתָה / בְּשַׁבְּתֹתֵיכֶם / בְּשִׁבְתְּכֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| izharite | וְלִקְהָת / הַעַמְרָמִי / הַיִּצְהָרִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| southward | נֶגְבָּה / יֶרֶךְ / נֹכַח | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| conveyance | הַמֶּרְכָּב / יִרְכַּב / עָלָיו | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| fifty-one | וְשָׁנִים / וְאֶחָד | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| scoured | וּמֹרַק / וְשֻׁטַּף / בֻּשָּׁלָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| one-year-old | וַעֲשִׂיתֶם / לִזְבֹּחַ / וּשְׁנֵי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| becherites | לְשׁוּתֶלַח / הַשֻּׁתַלְחִי / לְבֶכֶר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| employee's | תַעֲשֹׁק / תָלִין / פְּעֻלַּת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| mahlite | הַמַּחְלִי / הַמּוּשִׁי / וּמִשְׁפַּחַת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| raamah | סְבָא / וַחֲוִילָה / וְסַבְתָּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| zedad | תּוֹצְאֹת / צְדָדָה׃ / הַגְּבֻל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| gathers | הֵאָסֵף / לִבְנֵי / לְחֻקַּת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| oznites | לְאזְנִי / הָאזְנִי / לְעֵרִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| shuham | לְשׁוּחָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| fire-holder-full | גַּחֲלֵי / חפְנָיו / דַּקָּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| zuriel | צוּרִיאֵל / אֲבִיחָיִל / אָב | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| handiwork | מֵאִתָּם / מַעֲשֵׂה / הַזָּהָב | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| multiplying | מַפְרְךָ / וְהִרְבִּיתִךָ / וּנְתַתִּיךָ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| mouse | בַּשֶּׁרֶץ / הַחֹלֶד / וְהָעַכְבָּר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| muddled | נְבֻכִים / עֲלֵיהֶם / וָאֹמַר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| lael | לַגֵּרְשֻׁנִּי / לְאֵל / אָב | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| gaddiel | גַּדִּיאֵל / סוֹדִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| beard's | תַקִּפוּ / רֹאשְׁכֶם / תַשְׁחִית | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| head-opening | פִּי / רֹאשׁוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| madai | וּמָגוֹג / וּמָדַי / וְיָוָן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| heberites | הַחֶבְרִי / לְמַלְכִּיאֵל / הַמַּלְכִּיאֵלִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| indicates | לְמַטּוֹת / לְמִשְׁפְּחֹתֵיכֶם / וְהִתְנַחַלְתֶּם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| requiting | וְנֶאֱסַפְתֶּם / אוֹיֵב׃ / וְשָׁלַחְתִּי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| tarshish | יָוָן / אֱלִישָׁה / וְתַרְשִׁישׁ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| divide | בִכְנָפָיו / וְשִׁסַּע / יַבְדִּיל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| dodanim | יָוָן / אֱלִישָׁה / וְתַרְשִׁישׁ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| seredites | לְסֶרֶד / הַסַּרְדִּי / לְאֵלוֹן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| adulterer | יִנְאַף / הַנֹּאֵף / וְהַנֹּאָפֶת׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| poti-phera | לְיוֹסֵף / וַיִּוָּלֵד / אֹן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| fifty-two | וּשְׁבַע / שְׁנַיִם / וַחֲמִשִּׁים | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| final | מְאַסֵּף / לְכל / וְנָסַע | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| streaks | שְׁקַעֲרוּרֹת / יְרַקְרַקֹּת / הַקִּיר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| granddaughters | הֵבִיא / וּבְנוֹת / וּבְנֵי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| tin | הַבַּרְזֶל / הָעֹפָרֶת׃ / הִבְדִּיל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| partial | בְּצֶדֶק / תִּשְׁפֹּט / דַּל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ebal | עַלְוָן / וְעֵיבָל / שְׁפוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| widow's | וְנֵדֶר / אַלְמָנָה / וּגְרוּשָׁה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| hot | וְנָמָס׃ / וְחָם / וַיִּלְקְטוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| acquaintance | אוֹב / יִדְּעֹנִי / דְּמֵיהֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| palluites | הַחֲנֹכִי / לְפַלּוּא / הַפַּלֻּאִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| occasion | שִׂמְחַתְכֶם / וּבְמוֹעֲדֵיכֶם / וּבְרָאשֵׁי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| sithri | וְאֶלְצָפָן / וְסִתְרִי׃ / וּבְנֵי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| menstruating | דָּוָה / וְגִלָּה / מְקֹרָהּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| merarites | לִקְהָת / הַמְּרָרִי׃ / לְגֵרְשׁוֹן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| accumulated | בְחָרָן / לָלֶכֶת / עֵשָׂו | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| rooms | גֹפֶר / וְכָפַרְתָּ / בַּכֹּפֶר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| jetur | חֲדַד / וְתֵימָא / יְטוּר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| fastened | פָתוּחַ / צָמִיד / פְּתִיל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| pick | קָדֵשׁוּ׃ / וַיָּרֶם / הָלְאָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| overthrowing | בְּשַׁחֵת / הַהֲפֵכָה / בַּהֲפֹךְ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| warriors | וְחָצִיתָ / תֹּפְשֵׂי / הַמִּלְחָמָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| wide | רֹחַב / רָבוּעַ / וּשְׁלֹשׁ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| stove | וְכִירַיִם / יֻתָּץ / וּטְמֵאִים | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| heron | הַחֲסִידָה / הָאֲנָפָה / הַדּוּכִיפַת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| hatred | בְּשִׂנְאָה / יֶהְדֳּפֶנּוּ / בִּצְדִיָּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| rich | הֶעָשִׁיר / וְהַדַּל / יַמְעִיט | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| tahanites | לְשׁוּתֶלַח / הַשֻּׁתַלְחִי / לְבֶכֶר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| gershon's | וְאֵלֶּה / גֵרְשׁוֹן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| baal-meon | — | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| sashes | אַבְנֵטִים / וּמִגְבָּעוֹת / וְלִבְנֵי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| voices | קוֹלָם / וַיִּתְּנוּ / וַתִּשָּׂא | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| convocation | עֲצֶרֶת / תַּקְרִיבוּ / וְהִקְרַבְתֶּם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| souls | תִּמְאָסוּ / לְהַפְרְכֶם / נַפְשְׁכֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| cassia | וְקִדָּה / הִין׃ / וְשֶׁמֶן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| elderly | שֵׂיבָה / תָּקוּם / וְהָדַרְתָּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| trim | תַקִּפוּ / רֹאשְׁכֶם / תַשְׁחִית | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| gomer | וּמָגוֹג / וּמָדַי / וְיָוָן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| merari's | מְרָרִי / הֵם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| virginity | בִבְתוּלֶיהָ / וְהוּא / יִקַּח | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| extending | וְהַבְּרִיחַ / מַבְרִחַ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| walled | מוֹשַׁב / חוֹמָה / וְהָיְתָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| shame | עֶרְוָתוֹ / חֶסֶד / וְהִיא | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| pronouncement | וְשָׁמְעָה / יַגִּיד / לוֹא | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| strip | תְעוֹלֵל / וּפֶרֶט / כַּרְמְךָ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| uncles | וַתִּהְיֶינָה / דֹדֵיהֶן / תִּרְצֶה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| jair | וְיָאִיר / חַוֺּתֵיהֶם / חַוֺּת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| kenizzite | הַקְּנִזִּי / מִלְאוּ / בִּלְתִּי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| jointed | כְרָעַיִם / לְנַתֵּר / בֹּהֶן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| kedmah | חֲדַד / וְתֵימָא / יְטוּר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| daughter-in-law's | כַּלָּתֶךָ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| uzzielite | וְלִקְהָת / הַעַמְרָמִי / הַיִּצְהָרִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| elkanah | אַסִּיר / וְאֶלְקָנָה / וַאֲבִיאָסָף | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| sixty-five | לָקַח / וְשִׁשִּׁים / חֲמִשָּׁה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| machirites | הַמָּכִירִי / וּמָכִיר / לְגִלְעָד | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| pride | וְשָׁבַרְתִּי / גְּאוֹן / עֻזְּכֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| judith | יְהוּדִית / בְּאֵרִי / אֵילֹן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| stork | הַחֲסִידָה / הָאֲנָפָה / הַדּוּכִיפַת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| tended | בִּרְעֹתוֹ / לְצִבְעוֹן / הַיֵּמִם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| eranites | שׁוּתָלַח / לְעֵרָן / הָעֵרָנִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ephron's | בַּמַּכְפֵּלָה / גְּבֻלוֹ / עֶפְרוֹן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| thirteen | שָׁלֹשׁ / עֲשָׂרָה / בְּהִמֹּלוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| forty-three | שְׁלֹשָׁה / וְאַרְבָּעִים / וּשְׁבַע | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| thighs | לְכַסּוֹת / מִמּתְנַיִם / יְרֵכַיִם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| rehob | רֹחַב / וְיָתֻרוּ / עַד | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| wages | תַעֲשֹׁק / תָלִין / פְּעֻלַּת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| gadites | הַגְּדִי / וּמַטֵּה / נַחֲלָתָם׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| compensation | וּבֵיתְכֶם / עֲבֹדַתְכֶם / שֵׁכָר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| forth | יָצוֹא / יְבֹשֶׁת / וָשׁוֹב | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| fly | יִשְׁרְצוּ / וְעוֹף / יְעוֹפֵף | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| beth-nimrah | נִמְרָה / מִבְצָר׃ / הָרָן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| magog | וּמָגוֹג / וּמָדַי / וְיָוָן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| sheets | וַיְרַקְּעוּ / פַּחֵי / וְקִצֵּץ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| sebam | עֲטָרוֹת / וְדִיבֹן / וְיַעְזֵר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| libnite | הַשִּׁמְעִי / הַלִּבְנִי / וּמִשְׁפַּחַת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| burners | מַחְתּוֹת / עֲדָתוֹ / לָכֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| strengthen | וְחִזַּקְתִּי / וְרָדַף / אַחֲרֵיהֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| perezites | הַשֵּׁלָנִי / לְפֶרֶץ / הַפַּרְצִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| consumption | וְהִפְקַדְתִּי / בֶּהָלָה / הַשַּׁחֶפֶת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| coerced | הַגְּזֵלָה / גָּזָל / הָעֹשֶׁק | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ardites | הָאַרְדִּי / לְנַעֲמָן / הַנַּעֲמִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| beth-haran | נִמְרָה / מִבְצָר׃ / הָרָן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| cripple | חֵרֶם / פֶּסַח / יִקְרַב | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| akrabim | עַקְרַבִּים / צִנָה / אַדָּר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| jogli | בֻּקִּי / יגְלִי׃ / וּלְמַטֵּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| beriites | לְיִמְנָה / הַיִּמְנָה / לְיִשְׁוִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| abominable | מֵחֻקּוֹת / נַעֲשׂוּ / עֲשׂוֹת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| eliphaz's | וְגַעְתָּם / וּקְנַז׃ / וַיִּהְיוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| desolated | וְהִשְׁלַחְתִּי / וְשִׁכְּלָה / וְהִכְרִיתָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| hare | הָאַרְנֶבֶת / הִפְרִיסָה / טְמֵאָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| perish | וַאֲבַדְתֶּם / וְאֹכֵלָה / בַגּוֹיִם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| helek | אִיעֶזֶר / הָאִיעֶזְרִי / לְחֵלֶק | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| crimson | וּתְכֵלֶת / וְעִזִּים׃ / וְשֵׁשׁ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| overs | הַמְכַסֶּה / מִזְבַּח | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| mustache | וְהַצָּרוּעַ / פְרֻמִים / פָרוּעַ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| samuel | שְׁמוּאֵל / וּלְמַטֵּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ishvah | וְיִשְׁוָה / וְיִשְׁוִי / וּבְרִיעָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| hunchback | גִבֵּן / תְּבַלֻּל / בְּעֵינוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| tubal | וּמָגוֹג / וּמָדַי / וְיָוָן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| recorded | הִקְהִילוּ / וַיִּתְיַלְדוּ / מִשְׁפְּחֹתָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| pronouncing | הֵרָאֹתוֹ / לְטהֳרָתוֹ / וְנִרְאָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| leavening | תַקְטִירוּ / דְּבַשׁ / תַּקְרִיבוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| islands | אִיֵּי / לִלְשֹׁנוֹ / מֵאֵלֶּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| column's | וְהָאֲדָנִים / לָעַמֻּדִים / וְהֵם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| satyrs | יִזְבְּחוּ / לַשְּׂעִירִם / זֹנִים | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| clouds | קַשְׁתִּי / וְהָיְתָה / לְאוֹת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| obstructed | בְּזוֹבוֹ / רָר / הֶחְתִּים | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| zimri | זִמְרִי / סָלוּא / לַשִּׁמְעֹנִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| beriah's | וְיִשְׁוָה / וְיִשְׁוִי / וּבְרִיעָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| gileadites | הַמָּכִירִי / וּמָכִיר / לְגִלְעָד | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| twenty-nine | הֶעָשׂוּי / תֵּשַׁע / לַמְּלָאכָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| measured | וַיָּמֹדּוּ / בָעֹמֶר / הֶעְדִּיף | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| repute | וַאֲנָשִׁים / קְרִאֵי / עָדָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ishvites | לְיִמְנָה / הַיִּמְנָה / לְיִשְׁוִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| worms | וַיּוֹתִרוּ / תּוֹלָעִים / וַיָּרֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| gaddi | סוּסִי׃ / גְּדִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| horite | וְשׁוֹבָל / וְצִבְעוֹן / יֹשְׁבֵי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| adulteress | יִנְאַף / הַנֹּאֵף / וְהַנֹּאָפֶת׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| silent | בִּקְרֹבַי / אֶכָּבֵד / וַיִּדֹּם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| cutter | בְּתוֹלַעַת / וְאֹרֵג / וְחֹשְׁבֵי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| footing | וְכָשְׁלוּ / כְּמִפְּנֵי / תְּקוּמָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| amramite | וְלִקְהָת / הַעַמְרָמִי / הַיִּצְהָרִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| dread | וּמוֹרַאֲכֶם / וְחִתְּכֶם / נִתָּנוּ׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| gecko | וְהָאֲנָקָה / וְהַכֹּחַ / וְהַלְּטָאָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| regulate | וְלִמְשֹׁל / וּבַלַּיְלָה / וּלְהַבְדִּיל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| supervise | וּפְקַדְתֶּם / בְּמִשְׁמֶרֶת / עֲלֵהֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| weaver | בְּתוֹלַעַת / וְאֹרֵג / וְחֹשְׁבֵי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| announcement | וַיַּעֲבִירוּ / לִתְרוּמַת / מֵהָבִיא׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ashkenaz | אַשְׁכְּנַז / וְרִיפַת / וְתֹגַרְמָה׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| mishma | וּמִשְׁמָע / וְדוּמָה / וּמַשָּׂא׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| hebronites | הוֹלִד / הַמַּחְלִי / הַמּוּשִׁי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| zichri | וָנֶפֶג / וְזִכְרִי׃ / וּבְנֵי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| groaned | וַיֵּאָנְחוּ / וַיִּזְעָקוּ / שַׁוְעָתָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| melted | וְנָמָס׃ / וְחָם / וַיִּלְקְטוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| jogbehah | עֲטָרֹת / שׁוֹפָן / וְיגְבְּהָה׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| engraver | וּבְתוֹלַעַת / וְאֹתוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| jahzeelites | לְיַחְצְאֵל / הַיַּחְצְאֵלִי / לְגוּנִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| elisheba | אֱלִישֶׁבַע / אֲבִיהוּא / אֲחוֹת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| twenty-first | בָּרִאשֹׁן / הָאֶחָד / וְעֶשְׂרִים | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| slashed | שָׁבוּר / חָרוּץ / יַבֶּלֶת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| floodwaters | מַבּוּל / מִמֵּי / יִכָּרֵת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| puts | וּבְהַעֲלֹת / יַקְטִירֶנָּה׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| reba | חַלְלֵיהֶם / אֱוִי / רֶבַע | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| tema | חֲדַד / וְתֵימָא / יְטוּר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| piece | מַעֲשֵׂה / עֵץ / תִּתְחַטְּאוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| desires | חָפֵץ / וּנְתָנָהּ / בְּנוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| plates | הַחַטָּאִים / בְּנַפְשֹׁתָם / רִקֻּעֵי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| evi | — | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| shephupham | לִשְׁפוּפָם / הַשּׁוּפָמִי / לְחוּפָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| shemida | וּשְׁמִידָע / הַשְּׁמִידָעִי / וְחֵפֶר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ammiel | עַמִּיאֵל / גְּמַלִּי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| raamah's | סְבָא / וַחֲוִילָה / וְסַבְתָּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| tu | — | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  | ⚠ |
| outstretched | סִבְלֹת / וְהִצַּלְתִּי / מֵעֲבֹדָתָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| hovering | תֹהוּ / וָבֹהוּ / וְחֹשֶׁךְ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| aged | שֵׂיבָה / תָּקוּם / וְהָדַרְתָּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| igal | יִגָּאֵל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| shammua | זָכוֹר / שָׁמוֹעַ / שְׁמוֹתָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| nemuel | לִנְמוּאֵל / הַנְּמוּאֵלִי / לְיָמִין | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| stumble | וְכָשְׁלוּ / כְּמִפְּנֵי / תְּקוּמָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| concentrated | יִקָּווּ / וְתֵרָאֶה / הַיַּבָּשָׁה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| atroth-shophan | עֲטָרֹת / שׁוֹפָן / וְיגְבְּהָה׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| belaites | לְבֶלַע / הַבַּלְעִי / לְאַשְׁבֵּל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| spice | הַבֹּשֶׂם / וּלְשֶׁמֶן / לַמָּאוֹר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| mash | וְחוּל / וְגֶתֶר / וָמַשׁ׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ziphion | צִפְיוֹן / וְחַגִּי / שׁוּנִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| gunites | לְיַחְצְאֵל / הַיַּחְצְאֵלִי / לְגוּנִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| restricting | מוֹצָא / לִנְדָרֶיהָ / וּלְאִסַּר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| outsider's | בִּתְרוּמַת / לְאִישׁ / וּבַת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| inheritance | וּמוֹלַדְתְּךָ / הוֹלַדְתָּ / אֲחֵיהֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| chronic | נוֹשֶׁנֶת / יַסְגִּרֶנּוּ / וְטִמְּאוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| paltiel | פַּלְטִיאֵל / עַזָּן׃ / וּלְמַטֵּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| sanctuary | וּמִקְדָּשִׁי / תִּירָאוּ / שַׁבְּתֹתַי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| outward | וּמִגְרְשֵׁי / מִקִּיר / וָחוּצָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| arodi | צִפְיוֹן / וְחַגִּי / שׁוּנִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| shaphat | שָׁפָט / חוֹרִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| determined | פֹרַשׁ / וַיַּנִּיחוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| shunites | לִצְפוֹן / הַצְּפוֹנִי / לְחַגִּי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| sanctified | וְנִקְדַּשְׁתִּי / תְחַלְּלוּ / קדְשֵׁי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| eighty-three | בְּדַבְּרָם / וּמֹשֶׁה / שָׁלֹשׁ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| mibsam | נְבָיֹת / וְקֵדָר / וְאַדְבְּאֵל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| eshban | חֶמְדָּן / וְאֶשְׁבָּן / וְיִתְרָן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| riblah | מִשְּׁפָם / הָרִבְלָה / לָעָיִן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| tattoo | וְשֶׂרֶט / וּכְתֹבֶת / קַעֲקַע | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| meant | דִּמִּיתִי / לַעֲשׂוֹת / אֶעֱשֶׂה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| array | וְכָל־צְבָאָם / וְהָאָרֶץ / וַיְכֻלּוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| cush's | סְבָא / וַחֲוִילָה / וְסַבְתָּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| mahalath | מָחֲלַת / נָשָׁיו / לְאִשָּׁה׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| cost | הַחַטָּאִים / בְּנַפְשֹׁתָם / רִקֻּעֵי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| devote | וּבְהֵמָה / וּמִשְּׂדֵה / יִמְכֹּר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| revolt | תִּמְרֹדוּ / לַחְמֵנוּ / צִלָּם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| faintness | וְהַנִּשְׁאָרִים / מֹרֶךְ / בִּלְבָבָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| reparation | נֶחֱרֶפֶת / נִפְדָּתָה / חֻפְשָׁה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| text | וַיִּכְתְּבוּ / מִכְתַּב / וַיַּעֲשׂוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| hepherites | וּשְׁמִידָע / הַשְּׁמִידָעִי / וְחֵפֶר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| hushim | חֻשִׁים׃ / וּבְנֵי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| attends | בְּהֵיטִיבוֹ / יַקְטִירֶנָּה׃ / סַמִּים | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| dumah | וּמִשְׁמָע / וְדוּמָה / וּמַשָּׂא׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| liquid | מַשְׁקֶה / הָאֹכֶל / יִשְׁתֶּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| roads | וְהִשְׁלַחְתִּי / וְשִׁכְּלָה / וְהִכְרִיתָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| lud | עֵילָם / וְאַשּׁוּר / וְלוּד | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| consume | מִדּוֹ / תֹּאכַל / וְשָׂמוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| rate | וַיִּשְׁקֹל / לְעֶפְרֹן / לַסֹּחֵר׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| abihail | צוּרִיאֵל / אֲבִיחָיִל / אָב | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| hamulites | הַחֶצְרֹנִי / לְחָמוּל / הֶחָמוּלִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| scab's | הָיָה / וּמַרְאֵה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| shuthelahites | לְשׁוּתֶלַח / הַשֻּׁתַלְחִי / לְבֶכֶר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| talmai | אֲחִימַן / שֵׁשַׁי / וְתַלְמַי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| shiphtan | שִׁפְטָן׃ / וּלְמַטֵּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| customs | מֵחֻקּוֹת / נַעֲשׂוּ / עֲשׂוֹת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| pound | וְשָׁחַקְתָּ / הָדֵק / מִמֶּנָּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| loosen | וּפָרַע / כַּפֶּיהָ / הַזִּכָּרוֹן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| male's | הַטַּף / בַּנָּשִׁים / הַחֲיוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| exhausting | וְהִפְקַדְתִּי / בֶּהָלָה / הַשַּׁחֶפֶת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| bitterness | וַתִּהְיֶיןָ / מֹרַת / וּלְרִבְקָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| twenty-three | וְעֶשְׂרִים / שְׁלֹשָׁה / התְפָּקְדוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| haggai | צִפְיוֹן / וְחַגִּי / שׁוּנִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| puvah | וּפֻוָה / וְיוֹב / וְשִׁמְרֹן׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| hung | וְהָאַמָּה / בָּעֹדֵף / סָרוּחַ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| machi | גְּאוּאֵל / מָכִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| hul | וְחוּל / וְגֶתֶר / וָמַשׁ׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| zaavan | בִּלְהָן / וְזַעֲוָן / וַעֲקָן׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| robbery | בְּפִקָּדוֹן / בִתְשׂוּמֶת / בְגָזֵל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| worm | הִבְאִישׁ / וְרִמָּה / וַיַּנִּיחוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| purifying | וְאַתֶּם / וְהֶעֱמִיד / הָאִישׁ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| attached | מִטַּבְּעֹתָיו / לִהְיֹת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ascent | עַקְרַבִּים / צִנָה / אַדָּר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| michael | סְתוּר / מִיכָאֵל׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| zephonites | לִצְפוֹן / הַצְּפוֹנִי / לְחַגִּי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| oven-baked | מַאֲפֵה / תִּקְרַב / תַנּוּר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| alerted | וְיִנָּזְרוּ / מַקְדִּשִׁים / מִקּדְשֵׁי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| belongs | מֵאִתּוֹ / לַאֲשֶׁר / קֹנֵהוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| malchielites | הַחֶבְרִי / לְמַלְכִּיאֵל / הַמַּלְכִּיאֵלִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| conspiracies | צֹרְרִים / בְּנִכְלֵיהֶם / נִכְּלוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| avenger's | וְהִצִּילוּ / מָשַׁח / וְהֵשִׁיבוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| eran | שׁוּתָלַח / לְעֵרָן / הָעֵרָנִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| sheds | שֶׁפֶךְ / יִשְׁפֹּךְ / בָּאָדָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| disperse | קָדֵשׁוּ׃ / וַיָּרֶם / הָלְאָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| job | וּפֻוָה / וְיוֹב / וְשִׁמְרֹן׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| desecrates | מְחַלְלֶיהָ / עַמֶּיהָ׃ / בָּהּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| burying | בְּתוֹכֵנוּ / בְּמִבְחַר / קְבָרֵינוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| heber | הַחֶבְרִי / לְמַלְכִּיאֵל / הַמַּלְכִּיאֵלִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| mushite | הַמַּחְלִי / הַמּוּשִׁי / וּמִשְׁפַּחַת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| bottoms | פַּעֲמֹתָיו / צַלְעוֹ / וּשְׁתֵּי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| takes | קַצְתִּי / בְחַיַּי / לָקַח | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ziphron | זִפְרֹנָה / הַגְּבֻל / חֲצַר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| dispossesses | הוֹרִישׁוֹ / וְעָבַר / מִפָּנָיו׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| sore | שָׁבוּר / חָרוּץ / יַבֶּלֶת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| libnites | הוֹלִד / הַמַּחְלִי / הַמּוּשִׁי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| homer | בַּחֲמִשִּׁים / חֲמֹר / לְפִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| defile | וְהִזַּרְתֶּם / מִטֻּמְאָתָם / בְּטֻמְאָתָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| loosed | וְהַצָּרוּעַ / פְרֻמִים / פָרוּעַ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| grasshopper | הַסּלְעָם / הַחַרְגֹּל / הֶחָגָב | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| pattern | וְשִׁבַּצְתָּ / מִצְנֶפֶת / וְאַבְנֵט | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| stank | וַיּוֹתִרוּ / תּוֹלָעִים / וַיָּרֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| intercede | שְׁמָעוּנִי / וּפִגְעוּ / בְּעֶפְרוֹן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| flaw | יֵרָצוּ / נֵכָר / משְׁחָתָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| vowed | בְּשִׁבְעָה / נִדְרָהּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| extract | וְחִלְּצוּ / וְהִשְׁלִיכוּ / בֹּהֶן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| earrings | חָח / וָנֶזֶם / וְטַבַּעַת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| shechemites | וְאַשְׂרִיאֵל / הָאַשְׂרִאֵלִי / הַשִּׁכְמִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| nahbi | נַחְבִּי / ופְסִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| raphu | פַּלְטִי / רָפוּא׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| aram's | וְחוּל / וְגֶתֶר / וָמַשׁ׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| clothed | וְכָכָה / מתְנֵיכֶם / חֲגֻרִים | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| sorcerers | לַחֲכָמִים / וְלַמְכַשְּׁפִים / בְּלַהֲטֵיהֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| yawan | וּמָגוֹג / וּמָדַי / וְיָוָן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| sethur | סְתוּר / מִיכָאֵל׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| aran | וַאֲרָן׃ / דִישָׁן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| nazirite's | הִתְגַּלְּחוֹ / בֻּשָּׁלָה / הַזָּרַע | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| producing | נָתַתִּי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| reckoned | וָאֶפְקֹד / וַתָּקִא / עֲוֺנָהּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| iscah | וְנָחוֹר / וַאֲבִי / יִסְכָּה׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| protection | תִּמְרֹדוּ / לַחְמֵנוּ / צִלָּם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| rob | תַעֲשֹׁק / תָלִין / פְּעֻלַּת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| feathers | וְהֵסִיר / מֻרְאָתוֹ / בְּנֹצָתָהּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| strengthening | מְחַזֵּק / וַאֲנִי / וַיָּבֹאוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| border's | תּוֹצְאֹת / צְדָדָה׃ / הַגְּבֻל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| slander | רָכִיל / בְּעַמֶּיךָ / תֵלֵךְ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| current | וַיִּשְׁקֹל / לְעֶפְרֹן / לַסֹּחֵר׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| riphath | אַשְׁכְּנַז / וְרִיפַת / וְתֹגַרְמָה׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| perez's | וְשֵׁלָה / וָפֶרֶץ / וְחָמוּל׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| functioned | בְּהַקְרִבָם / וַיְכַהֵן / וּבָנִים | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| assembling | וּבְהַקְהִיל / תִּתְקְעוּ / תָרִיעוּ׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| tremendous | סִבְלֹת / וְהִצַּלְתִּי / מֵעֲבֹדָתָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| slipping | וְהֶחֱזַקְתָּ / וּמַטֵּה / וְתוֹשָׁב | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| twenty-seventh | וּבַחֹדֶשׁ / בְּשִׁבְעָה / וְעֶשְׂרִים | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| position | יָדוֹ / וְנָסַע / יַחֲנוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| harden | אַקְשֶׁה / מוֹפְתַי / וַאֲנִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ride | הַמֶּרְכָּב / יִרְכַּב / עָלָיו | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| jashub | לְיָשׁוּב / הַיָּשֻׁבִי / לְשִׁמְרֹן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| exceeded | וַיָּמֹדּוּ / בָעֹמֶר / הֶעְדִּיף | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| shuphamites | לִשְׁפוּפָם / הַשּׁוּפָמִי / לְחוּפָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| soothsaying | תְנַחֲשׁוּ / תְעוֹנֵנוּ׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| mizzeh | וּמִזֶּה / וָזֶרַח / הָיוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| shillemites | לְיֵצֶר / הַיִּצְרִי / הַשִּׁלֵּמִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| cheran | חֶמְדָּן / וְאֶשְׁבָּן / וְיִתְרָן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| shortage | מִקֹּצֶר / וּמֵעֲבֹדָה / כֵּן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| helekites | אִיעֶזֶר / הָאִיעֶזְרִי / לְחֵלֶק | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| shelanites | הַשֵּׁלָנִי / לְפֶרֶץ / הַפַּרְצִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| clans | בְּחַצְרֵיהֶם / וּבְטִירֹתָם / לְאֻמֹּתָם׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| raw | וּבָשֵׁל / מְבֻשָּׁל / נָא | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| scaly | מְחֻסְפָּס / כַּכְּפֹר / הָאָרֶץ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| mi | — | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| gopher | גֹפֶר / וְכָפַרְתָּ / בַּכֹּפֶר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| sowing | זֵרוּעַ / יִזָּרֵעַ / מִנִּבְלָתָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| inscription | וְשֶׂרֶט / וּכְתֹבֶת / קַעֲקַע | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| witnesses | יִרְצַח / עֶדְיָם / יַעֲנֶה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| inquired | דָּרֹשׁ / הַנּוֹתָרִם / שָׂרַף | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| flings | הַזֹּרֵק / מִכּל / מִמֶּנּוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| huphamites | לִשְׁפוּפָם / הַשּׁוּפָמִי / לְחוּפָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| alvan | עַלְוָן / וְעֵיבָל / שְׁפוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| leap | כְרָעַיִם / לְנַתֵּר / בֹּהֶן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| erites | לְאזְנִי / הָאזְנִי / לְעֵרִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| frost | מְחֻסְפָּס / כַּכְּפֹר / הָאָרֶץ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| sabtah | סְבָא / וַחֲוִילָה / וְסַבְתָּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ehi | וָאָרְדְּ׃ / וָבֶכֶר / וְאַשְׁבֵּל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| iezer | אִיעֶזֶר / הָאִיעֶזְרִי / לְחֵלֶק | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| stacte | — | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| mounting | טוּרִים / מְלֹאת / וּמִלֵּאתָ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| demolished | וְכִירַיִם / יֻתָּץ / וּטְמֵאִים | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| asrielites | וְאַשְׂרִיאֵל / הָאַשְׂרִאֵלִי / הַשִּׁכְמִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| levy | וַהֲרֵמֹתָ / מֵחֲמֵשׁ / הַמֵּאוֹת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| toil | סִבְלֹת / וְהִצַּלְתִּי / מֵעֲבֹדָתָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| retribution | וְנֶאֱסַפְתֶּם / אוֹיֵב׃ / וְשָׁלַחְתִּי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| formless | תֹהוּ / וָבֹהוּ / וְחֹשֶׁךְ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| year-by-year | יָרַדְנוּ / בַּשָּׁנָה / לְעֵינֶיךָ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| calling | חֲצוֹצְרֹת / לְמִקְרָא / וּלְמַסַּע | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| elohim | — | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| weave | וְשִׁבַּצְתָּ / מִצְנֶפֶת / וְאַבְנֵט | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| consistently | וְקֹמָה / בַּחֲמִשִּׁים / מֵאָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| flay | וְהִפְשִׁיט / לִנְתָחֶיהָ׃ / וְנִתַּח | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| jachinites | לִנְמוּאֵל / הַנְּמוּאֵלִי / לְיָמִין | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| huppim | וָאָרְדְּ׃ / וָבֶכֶר / וְאַשְׁבֵּל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| orders | מִשְּׁמֹתָם / הַשִּׁשָּׁה / כְּתוֹלְדֹתָם׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| rip | וְקָרַע / הֻכַּבֵּס | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| assir | אַסִּיר / וְאֶלְקָנָה / וַאֲבִיאָסָף | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| gera | וָאָרְדְּ׃ / וָבֶכֶר / וְאַשְׁבֵּל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| seeding | וְהִשִּׂיג / דַּיִשׁ / בָּצִיר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| twelfth | עָשָׂר / שְׁנַיִם / יוֹם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| overthrow | בְּשַׁחֵת / הַהֲפֵכָה / בַּהֲפֹךְ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| onam | עַלְוָן / וְעֵיבָל / שְׁפוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| pelican | הַתִּנְשֶׁמֶת / הַקָּאָת / הָרָחָם׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| yawan's | יָוָן / אֱלִישָׁה / וְתַרְשִׁישׁ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| unsheathe | אֱזָרֶה / וַהֲרִיקֹתִי / וְעָרֵיכֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| expressly | לִנְדֹּר / נָזִיר / לְהַזִּיר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| cricket | הַסּלְעָם / הַחַרְגֹּל / הֶחָגָב | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| first-born | בְּכֹר / לְגֻלְגְּלֹתָם׃ / וַיִּהְיוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| respect | שֵׂיבָה / תָּקוּם / וְהָדַרְתָּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| puwah | הַתּוֹלָעִי / לְפֻוָה / הַפּוּנִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| spotting | גִבֵּן / תְּבַלֻּל / בְּעֵינוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| figured | הַחֲצֵרִים / וּבַיֹּבֵל / יֵחָשֵׁב | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| parnach | פַּרְנָךְ׃ / וּלְמַטֵּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| deterioration | פְּחֶתֶת / עֵינוֹ / תִּשְׂרְפֶנּוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| earring | אֶצְעָדָה / וְצָמִיד / עָגִיל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| dropped | רָעָתוֹ׃ / אוֹיֵב׃ / וַיִּפֹּל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| cormorant | הַשָּׁלָךְ / הַיַּנְשׁוּף׃ / הַכּוֹס | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| hanniel | חַנִּיאֵל / אֵפֹד | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| shepho | עַלְוָן / וְעֵיבָל / שְׁפוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| pedahel | פְּדַהְאֵל / וּלְמַטֵּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| grapevine | מִגֶּפֶן / מֵחַרְצַנִּים / זָג | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| akan | בִּלְהָן / וְזַעֲוָן / וַעֲקָן׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ahiram | לְבֶלַע / הַבַּלְעִי / לְאַשְׁבֵּל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| mountaintop | כְּאֵשׁ / אֹכֶלֶת / בְּרֹאשׁ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| expire | יִגְוָע / וַאֲנִי / מִתַּחַת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| settlements | בְּחַצְרֵיהֶם / וּבְטִירֹתָם / לְאֻמֹּתָם׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| flight | וְהַנִּשְׁאָרִים / מֹרֶךְ / בִּלְבָבָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| forty-eight | וּשְׁמֹנֶה / מִגְרְשֵׁיהֶן׃ / אֶתְהֶן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| susi | סוּסִי׃ / גְּדִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| twentieth | בְּעֶשְׂרִים / נַעֲלֶה / מִשְׁכַּן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| nighthawk | הַיַּעֲנָה / הַתַּחְמָס / הַשָּׁחַף | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| wise-hearted | וּבְלֵב / צִוִּיתִךָ / וַאֲנִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| seba | סְבָא / וַחֲוִילָה / וְסַבְתָּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| remove | סִּירֹתָיו / לְדַשְּׁנוֹ / וְיָעָיו | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ashbelites | לְבֶלַע / הַבַּלְעִי / לְאַשְׁבֵּל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| fewer | מֵאֲחֻזַּת / הָרַב / תַּמְעִיטוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| mahlites | הוֹלִד / הַמַּחְלִי / הַמּוּשִׁי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| brooches | חָח / וָנֶזֶם / וְטַבַּעַת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| cinnamon | מר / וְקִנְּמן / מַחֲצִיתוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| palti | פַּלְטִי / רָפוּא׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| juice | מִיַּיִן / וְחֹמֶץ / וַעֲנָבִים | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| model | וַהֲקֵמֹתָ / כְּמִשְׁפָּטוֹ / הרְאֵיתָ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| lotan's | וְהֵימָם / חֹרִי / תִּמְנָע׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| fragrance | כָמוֹהָ / לְהָרִיחַ / יַעֲשֶׂה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| kittim | יָוָן / אֱלִישָׁה / וְתַרְשִׁישׁ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| rosh | וָאָרְדְּ׃ / וָבֶכֶר / וְאַשְׁבֵּל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| expiated | וְטָהֵר׃ / יָבֹא / בְּמֵי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| moaning | נַאֲקָתָם / בְּרִיתוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| arodites | לַאֲרוֹד / הָאַרְוָדִי / לְאַרְאֵלִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| eyebrows | זְקָנוֹ / גַּבֹּת / עֵינָיו | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| growths | תִזְרָעוּ / תִקְצְרוּ / סְפִיחֶיהָ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| block | מִכְשֹׁל / תְקַלֵּל / תִּתֵּן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ninety-nine | וְתֵשַׁע / תִּשְׁעִים / בְּהִמֹּלוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| naphish | חֲדַד / וְתֵימָא / יְטוּר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| engraver's | תְּפַתַּח / מִשְׁבְּצוֹת / חֶרֶשׂ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| twenty-five | בַּעֲבֹדַת / וְעֶשְׂרִים / חָמֵשׁ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| establishing | מֵקִים / אַחֲרֵיכֶם / זַרְעֲכֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| nepheg | וָנֶפֶג / וְזִכְרִי׃ / וּבְנֵי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| fowl | צִפּוֹר / הֵמָּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| tributes | הָרְבִיעִת / הִלּוּלִים / וּבַשָּׁנָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| exploit | תַעֲשֹׁק / תָלִין / פְּעֻלַּת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| creating | בְּרֵאשִׁית / בָּרָא / אֱלֹהִים | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| shouted | וַיָּרֹנּוּ / מִלִּפְנֵי / וַתֵּצֵא | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| consuming | כְּאֵשׁ / אֹכֶלֶת / בְּרֹאשׁ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| chameleon | וְהָאֲנָקָה / וְהַכֹּחַ / וְהַלְּטָאָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| eastern | וּמַדֹּתֶם / וְהָעִיר / מִגְרְשֵׁי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| tall | וָאֶשְׁבֹּר / מֹטֹת / וָאוֹלֵךְ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| coating | הִטֹּחַ / בָּא / בְּבֵית | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| seagull | הַיַּעֲנָה / הַתַּחְמָס / הַשָּׁחַף | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| one-tenth | מַשֶּׂגֶת / לִתְנוּפָה / וְעִשָּׂרוֹן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| nimrah | עֲטָרוֹת / וְדִיבֹן / וְיַעְזֵר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| horn-blasting | תְּרוּעָה / בְּאֶחָד | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| gemalli | עַמִּיאֵל / גְּמַלִּי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| seventy-six | שִׁשָּׁה / וְשִׁבְעִים / לִפְקֻדֵיהֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| duration | וּמוֹשַׁב / יֵשְׁבוּ / בְּמִצְרַיִם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| criticize | תִשְׂנָא / בִּלְבָבֶךָ / הוֹכֵחַ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| mutilated | חֵרֶם / פֶּסַח / יִקְרַב | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| vineyard's | תְעוֹלֵל / וּפֶרֶט / כַּרְמְךָ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| grate's | בְּאַרְבַּע / לְמִכְבַּר / הַקְּצָוֺת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| beon | עֲטָרוֹת / וְדִיבֹן / וְיַעְזֵר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| determine | לִפְרֹשׁ / וַיַּנִּיחֵהוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| sabteca | סְבָא / וַחֲוִילָה / וְסַבְתָּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| stomach | הַקֻּבָּה / וַיִּדְקֹר / קֳבָתָהּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| shimeite | הַשִּׁמְעִי / הַלִּבְנִי / וּמִשְׁפַּחַת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| hoopoe | הַחֲסִידָה / הָאֲנָפָה / הַדּוּכִיפַת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| measurement | בַּמִּדָּה / וּבַמְּשׂוּרָה׃ / בַּמִּשְׁקָל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| rat | בַּשֶּׁרֶץ / הַחֹלֶד / וְהָעַכְבָּר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| complaining | מַלִּינִים / תְּלֻנּוֹת / הֵמָּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| armlet | אֶצְעָדָה / וְצָמִיד / עָגִיל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| yielded | וַיּוֹתִרוּ / תּוֹלָעִים / וַיָּרֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| foil | וַיְרַקְּעוּ / פַּחֵי / וְקִצֵּץ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| disciplined | תִוָּסְרוּ / בְּאֵלֶּה / וַהֲלַכְתֶּם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| massa | וּמִשְׁמָע / וְדוּמָה / וּמַשָּׂא׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| dibri | וַיִּקֹּב / וַיְקַלֵּל / שְׁלֹמִית | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| sixty-six | שִׁשִּׁים / וְשֵׁשׁ / יֹצְאֵי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| returns | וְזֶרַע / וְשָׁבָה / כִּנְעוּרֶיהָ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| individual | וַהֲרֵמֹתָ / מֵחֲמֵשׁ / הַמֵּאוֹת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| yaphet's | וּמָגוֹג / וּמָדַי / וְיָוָן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| tummim | הַתֻּמִּים | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| shapeless | תֹהוּ / וָבֹהוּ / וְחֹשֶׁךְ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| bracelet | אֶצְעָדָה / וְצָמִיד / עָגִיל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| staffs | וַיַּשְׁלִיכוּ / לְתַנִּינִם / וַיִּבְלַע | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| fever | וְהִפְקַדְתִּי / בֶּהָלָה / הַשַּׁחֶפֶת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| sacrificial | הִקְרִיבוּ / זִבְחוּ / מִמֶּנּוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| haggi | לִצְפוֹן / הַצְּפוֹנִי / לְחַגִּי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| moves | הַשֹּׁרֶצֶת / וְהָעוֹף / הָרֹמֶשֶׂת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| enslaving | נַאֲקַת / מַעֲבִדִים / וָאֶזְכֹּר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| casting | לָצֶקֶת / לִמְאַת / לָאָדֶן׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| enclosure | הַקֻּבָּה / וַיִּדְקֹר / קֳבָתָהּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ripe | קָלוּי / כַּרְמֶל / בִּכּוּרֶיךָ׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| grandson | חָרָן / אַרְצָה / וַיָּשֻׁבוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| azzan | פַּלְטִיאֵל / עַזָּן׃ / וּלְמַטֵּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| kiriathaim | אֶלְעָלֵא / קִרְיָתָיִם׃ / בְּנוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| dwarf | גִבֵּן / תְּבַלֻּל / בְּעֵינוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| sodi | גַּדִּיאֵל / סוֹדִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| onycha | נָטָף / וּשְׁחֵלֶת / וְחֶלְבְּנָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| three-tenths | וּשְׁלֹשָׁה / תְּמִימִם / כְּבָשִׂים | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ozni | לְאזְנִי / הָאזְנִי / לְעֵרִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| kedar | נְבָיֹת / וְקֵדָר / וְאַדְבְּאֵל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| sticks | תוֹרִישׁוּ / לְשִׂכִּים / וְלִצְנִינִם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| chew | הַחֲזִיר / יְגַר / וְהוּא | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| hanochites | הַחֲנֹכִי / לְפַלּוּא / הַפַּלֻּאִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ephod's | הָאֵפֹד | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| jashubites | לְיָשׁוּב / הַיָּשֻׁבִי / לְשִׁמְרֹן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| scouting | מִתּוּר / וַיָּשֻׁבוּ / יוֹם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ahihud | אֲחִיהוּד / שַׁלְמֵי / וּלְמַטֵּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ezbon | צִפְיוֹן / וְחַגִּי / שׁוּנִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| pig | הַחֲזִיר / יְגַר / וְהוּא | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| manahath | עַלְוָן / וְעֵיבָל / שְׁפוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| carmites | הַחֶצְרוֹנִי / לְכַרְמִי / הַכַּרְמִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| salu | זִמְרִי / סָלוּא / לַשִּׁמְעֹנִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ajah | בִּרְעֹתוֹ / לְצִבְעוֹן / הַיֵּמִם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| yarn | בְּיָדֶיהָ / מַטְוֶה / חַכְמַת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| backbone | — | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| commands | מְצַוָּה / יַעֲשׂוּ / וּבְנֵי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| zaccur | זָכוֹר / שָׁמוֹעַ / שְׁמוֹתָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| tahan | לְשׁוּתֶלַח / הַשֻּׁתַלְחִי / לְבֶכֶר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| roving | זְנוּתֵיכֶם / וּבְנֵיכֶם / רָעִים | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| appears | וְהִגִּיד / כְּנֶגַע / נִרְאָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| rebels | נוֹצִיא / הַמָּן / הַמָּרִים | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| kite | הַדָּאָה / הָאַיָּה / לְמִינָהּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| grandsons | הֵבִיא / וּבְנוֹת / וּבְנֵי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| putiel | פּוּטִיאֵל / אֲבוֹת / לְאִשָּׁה׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| attach | מִטַּבְּעֹתָו / לִהְיוֹת / הָאֵפוֹד | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| flows | חָפֵץ / וּנְתָנָהּ / בְּנוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| muppim | וָאָרְדְּ׃ / וָבֶכֶר / וְאַשְׁבֵּל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| receding | וְחָסוֹר / בָּעֲשִׂירִי / נִרְאוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| turtledove | וּבִמְלֹאת / תֹר / יוֹנָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| reed | מר / וְקִנְּמן / מַחֲצִיתוֹ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| eminence | מֵהוֹדְךָ / יִשְׁמְעוּ / וְנָתַתָּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| jahleelites | לְסֶרֶד / הַסַּרְדִּי / לְאֵלוֹן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| jezerites | לְיֵצֶר / הַיִּצְרִי / הַשִּׁלֵּמִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ahiramites | לְבֶלַע / הַבַּלְעִי / לְאַשְׁבֵּל | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| loaves | וְאָפִיתָ / הַחַלָּה / הָאֶחָת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| atoning | יוּבָא / לְכַפֵּר / תִּשָּׂרֵף׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| robbed | הַגְּזֵלָה / גָּזָל / הָעֹשֶׁק | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| chiefdoms | לְאַלֻּפֵיהֶם / אֵצֶר | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| korah's | בְחֶטְאוֹ / קֹרַח / וּבָנִים | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| chislon | אֱלִידָד / כִּסְלוֹן׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| bilhan | בִּלְהָן / וְזַעֲוָן / וַעֲקָן׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| iezerites | אִיעֶזֶר / הָאִיעֶזְרִי / לְחֵלֶק | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| merchant's | וַיִּשְׁקֹל / לְעֶפְרֹן / לַסֹּחֵר׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| zephon | לִצְפוֹן / הַצְּפוֹנִי / לְחַגִּי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| hever | וְיִשְׁוָה / וְיִשְׁוִי / וּבְרִיעָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| hundredth | לְחַיֵּי / נִבְקְעוּ / נִפְתָּחוּ׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| sprinkles | הַנִּדָּה / וּמִזֶּה / בְּמֵי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| foreigner's | יֵרָצוּ / נֵכָר / משְׁחָתָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| tombs | בְּתוֹכֵנוּ / בְּמִבְחַר / קְבָרֵינוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| shimronites | לְיָשׁוּב / הַיָּשֻׁבִי / לְשִׁמְרֹן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| excluded | הָהֵמָּה / נִגְרָע / לְבִלְתִּי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| lacking | נִפְקַד / נְשָׂאוֹ / מִמֶּנּוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| conceived | מַחֲשָׁבֹת / מְלֶאכֶת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| scraping | חִלֵּץ / הִטּוֹחַ׃ / הַקְּצָוֺת | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| hebronite | וְלִקְהָת / הַעַמְרָמִי / הַיִּצְהָרִי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| images | מַשְׂכִּיֹּתָם / צַלְמֵי / מַסֵּכֹתָם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| weighed | וַיִּשְׁקֹל / לְעֶפְרֹן / לַסֹּחֵר׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| swarmed | הַתַּנִּינִם / לְמִינֵהֶם / שָׁרְצוּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| kinneret | מִשְּׁפָם / הָרִבְלָה / לָעָיִן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| prostitution | לְהַזְנוֹתָהּ / תִזְנֶה / וּמָלְאָה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| cistern | מַעְיָן / וּבוֹר / וּנְגֹעַ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| senior | יוּצַק / יִפְרָע / יִפְרֹם׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ithran | חֶמְדָּן / וְאֶשְׁבָּן / וְיִתְרָן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| tiras | וּמָגוֹג / וּמָדַי / וְיָוָן | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| shelomi | אֲחִיהוּד / שַׁלְמֵי / וּלְמַטֵּה | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| saulites | לְשָׁאוּל / הַשָּׁאוּלִי׃ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| murderer's | רָשָׁע / לְנֶפֶשׁ / רֹצֵחַ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| falcon | הַדָּאָה / הָאַיָּה / לְמִינָהּ | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| forty-two | הַמִּקְלָט / לָנֻס / וַעֲלֵיהֶם | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| forty-nine | וְסָפַרְתָּ / תֵּשַׁע / וְאַרְבָּעִים | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| sheshai | אֲחִימַן / שֵׁשַׁי / וְתַלְמַי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| ahiman | אֲחִימַן / שֵׁשַׁי / וְתַלְמַי | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| fourth | הָרְבִיעִי | 3 | 0 | 8 | 11 | 0.768 | 3.746 | 0.830 | 0.2069 |  |  |
| lands | הָאֲרָצֹת / הָאֵל | 2 | 1 | 8 | 11 | 0.768 | 1.006 | 0.830 | 0.5969 |  |  |
| whether | בֵּין | 2 | 1 | 8 | 11 | 0.768 | 1.006 | 0.830 | 0.5969 |  |  |
| haran | חָרָנָה׃ / מֵחָרָן׃ / הָרָן | 3 | 0 | 8 | 11 | 0.768 | 3.746 | 0.830 | 0.2069 |  |  |
| camps | הַמַּחֲנֹת / הַמַּחֲנוֹת / מִזָּכָר | 3 | 0 | 8 | 11 | 0.768 | 3.746 | 0.830 | 0.2069 |  |  |
| bed | הַמִּשְׁכָּב / הַמַּטֶּה | 1 | 2 | 8 | 11 | 0.768 | 1.021 | 0.830 | 0.5969 |  |  |
| mamre | מַמְרֵא | 2 | 0 | 6 | 8 | 0.749 | 2.735 | 0.928 | 0.3223 |  |  |
| same | כַּגֵּר / וְטִהֲרוֹ / מִשְׁפַּט | 2 | 0 | 6 | 8 | 0.749 | 2.735 | 0.928 | 0.3223 |  |  |
| foreskin | ערְלָתוֹ׃ / יִמּוֹל | 2 | 0 | 6 | 8 | 0.749 | 2.735 | 0.928 | 0.3223 |  |  |
| aliens | הָגָר / וּמִן / גֵרִים | 0 | 2 | 6 | 8 | 0.749 | 2.764 | 0.928 | 0.3223 |  |  |
| high | הַגָּדֹל / בָּעִיר | 1 | 1 | 6 | 8 | 0.749 | 0.749 | 0.928 | 0.6138 |  |  |
| eliab | אֱלִיאָב | 2 | 0 | 6 | 8 | 0.749 | 2.735 | 0.928 | 0.3223 |  |  |
| dim | כֵהָה | 2 | 0 | 6 | 8 | 0.749 | 2.735 | 0.928 | 0.3223 |  |  |
| goes | הַהֹלֵךְ / קוֹלוֹ / וּבְצֵאתוֹ | 2 | 0 | 6 | 8 | 0.749 | 2.735 | 0.928 | 0.3223 |  |  |
| reuel | רְעוּאֵל | 2 | 0 | 6 | 8 | 0.749 | 2.735 | 0.928 | 0.3223 |  |  |
| lives | נַפְשֹׁתֵיכֶם | 2 | 0 | 6 | 8 | 0.749 | 2.735 | 0.928 | 0.3223 |  |  |
| near | יִגַּשׁ / מִזֶּרַע / יָמֻתוּ | 1 | 1 | 6 | 8 | 0.749 | 0.749 | 0.928 | 0.6138 |  |  |
| levi | לֵוִי | 5 | 2 | 15 | 22 | 0.732 | 1.668 | 0.597 | 0.4455 |  |  |
| except | אַךְ / אִם | 3 | 4 | 15 | 22 | 0.732 | 0.842 | 0.597 | 0.5969 |  |  |
| consecrate | יַקְדִּישׁ | 3 | 2 | 11 | 16 | 0.593 | 0.731 | 0.614 | 0.6215 |  |  |
| anything | בְּכל / מְאוּמָה / יִקְדָּשׁ׃ | 4 | 4 | 16 | 24 | 0.580 | 0.580 | 0.507 | 0.6854 |  |  |
| buried | וַיִּקְבְּרוּ / קָבְרוּ / קֶבֶר | 1 | 3 | 9 | 13 | 0.526 | 1.295 | 0.628 | 0.5333 |  |  |
| west | יָמָּה | 3 | 1 | 9 | 13 | 0.526 | 1.266 | 0.628 | 0.5439 |  |  |
| while | וְאַתֶּם / וְטֻמְאָתוֹ | 3 | 1 | 9 | 13 | 0.526 | 1.266 | 0.628 | 0.5439 |  |  |
| animal | בְּהֵמָה / הַבְּהֵמָה | 12 | 13 | 42 | 67 | 0.491 | 0.528 | 0.287 | 0.7102 |  |  |
| distinguish | הַטָּמֵא / וּבֵין / לְהַבְדִּיל | 0 | 3 | 7 | 10 | 0.462 | 3.484 | 0.650 | 0.2453 |  |  |
| land's | הָאָרֶץ | 1 | 2 | 7 | 10 | 0.462 | 0.714 | 0.650 | 0.6284 |  |  |
| below | מִלְּמַטָּה | 0 | 3 | 7 | 10 | 0.462 | 3.484 | 0.650 | 0.2453 |  |  |
| cakes | חַלֹּת / מֻרְבֶּכֶת / בְּלוּלֹת | 1 | 2 | 7 | 10 | 0.462 | 0.714 | 0.650 | 0.6284 |  |  |
| judgment | מִשְׁפַּט / וְהָיוּ | 0 | 3 | 7 | 10 | 0.462 | 3.484 | 0.650 | 0.2453 |  |  |
| dead | מֵת | 3 | 8 | 20 | 31 | 0.429 | 2.167 | 0.384 | 0.3374 |  |  |
| zerah | זֶרַח | 2 | 0 | 5 | 7 | 0.405 | 2.391 | 0.687 | 0.3223 |  |  |
| having | תַגִּיעַ / לֶחָצֵר / לַפֵּאָה | 1 | 1 | 5 | 7 | 0.405 | 0.405 | 0.687 | 0.7680 |  |  |
| figure | וְחִשַּׁב | 2 | 0 | 5 | 7 | 0.405 | 2.391 | 0.687 | 0.3223 |  |  |
| judah's | יְהוּדָה | 2 | 0 | 5 | 7 | 0.405 | 2.391 | 0.687 | 0.3223 |  |  |
| spices | לְשֶׁמֶן / בְּשָׂמִים / וְלִקְטֹרֶת | 1 | 0 | 3 | 4 | 0.375 | 1.367 | 0.772 | 0.5077 |  |  |
| borders | לִגְבֻלֹתֶיהָ׃ / תִּפֹּל / בָּאִים | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| ransom | כֹּפֶר / נַפְשׁוֹ | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| beer | וְשֵׁכָר / בְּבֹאֲכֶם / תָּשֶׁת | 1 | 0 | 3 | 4 | 0.375 | 1.367 | 0.772 | 0.5077 |  |  |
| hanoch | חֲנוֹךְ / וּבְנֵי | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| iron | בַרְזֶל / בִּכְלִי / וְאֶת | 1 | 0 | 3 | 4 | 0.375 | 1.367 | 0.772 | 0.5077 |  |  |
| persecute | תוֹנוּ / וְכִי | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| perez | פֶרֶץ | 1 | 0 | 3 | 4 | 0.375 | 1.367 | 0.772 | 0.5077 |  |  |
| jazer | יַעְזֵר | 1 | 0 | 3 | 4 | 0.375 | 1.367 | 0.772 | 0.5077 |  |  |
| plant | יֶרֶק / כְּיֶרֶק / וּלְכֹל | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| tear | — | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| task | מַשָּׂאָם / עֲבֹדָתָם / מִשְׁמֶרֶת | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| large | הַגּוֹרָל / וְלַמְעַט / לָרֹב | 1 | 0 | 3 | 4 | 0.375 | 1.367 | 0.772 | 0.5077 |  |  |
| used | תֹאכְלֻהוּ׃ / וְחֵלֶב / וְאָכַל | 1 | 0 | 3 | 4 | 0.375 | 1.367 | 0.772 | 0.5077 |  |  |
| bowls | קְּעָרֹתָיו / יֻסַּךְ / בֹּהֶן | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| added | וְנוֹסַף | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| fist | קֻמְצוֹ / וֶהֱבִיאָהּ / מְלוֹא | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| passes | הָעֹבֵר / הַפְּקֻדִים / יִתְּנוּ | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| meribah | מְרִיבָה / מִי | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| hears | נִדְרָהּ | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| hips | גּוֹי / וּקְהַל / מֵחֲלָצֶיךָ | 1 | 0 | 3 | 4 | 0.375 | 1.367 | 0.772 | 0.5077 |  |  |
| u | — | 1 | 0 | 3 | 4 | 0.375 | 1.367 | 0.772 | 0.5077 |  | ⚠ |
| olive | זַיִת | 1 | 0 | 3 | 4 | 0.375 | 1.367 | 0.772 | 0.5077 |  |  |
| separated | וַיַּבְדֵּל / מֵעַל / וַיִּפָּרְדוּ | 1 | 0 | 3 | 4 | 0.375 | 1.367 | 0.772 | 0.5077 |  |  |
| form | מַחֲשָׁבֹת / בַּזָּהָב / וּבַכֶּסֶף | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| when | כִּי | 50 | 48 | 147 | 245 | 0.373 | 0.390 | 0.133 | 0.7764 |  |  |
| glory | כְּבוֹד | 3 | 2 | 10 | 15 | 0.363 | 0.501 | 0.483 | 0.7212 |  |  |
| leave | מִמֶּנּוּ / תוֹתִירוּ | 4 | 3 | 13 | 20 | 0.318 | 0.414 | 0.398 | 0.7636 |  |  |
| filled | וַיְמַלֵּא / מְלֹא / וַתְּמַלֵּא | 4 | 3 | 13 | 20 | 0.318 | 0.414 | 0.398 | 0.7636 |  |  |
| thigh | שׁוֹק | 6 | 3 | 16 | 25 | 0.295 | 1.008 | 0.346 | 0.5969 |  |  |
| split | רֵעֵהוּ / וַיִּבָּקְעוּ / וַיְבַתֵּר | 2 | 2 | 8 | 12 | 0.290 | 0.290 | 0.468 | 0.8273 |  |  |
| yhwh | יְהֹוָה | 213 | 209 | 600 | 1022 | 0.286 | 0.292 | 0.058 | 0.8265 |  |  |
| sea | הַיָּם | 7 | 6 | 22 | 35 | 0.275 | 0.323 | 0.287 | 0.8106 |  |  |
| border | גְּבוּל / זֵר | 8 | 7 | 25 | 40 | 0.271 | 0.313 | 0.268 | 0.8162 |  |  |
| with | עִם / אֹתוֹ / עִמּוֹ | 162 | 167 | 469 | 798 | 0.253 | 0.351 | 0.061 | 0.7966 |  |  |
| after | אַחֲרֵי / וְאַחֲרֵי | 27 | 21 | 73 | 121 | 0.242 | 0.742 | 0.150 | 0.6170 |  |  |
| opposite | מוּל / פְּנֵי | 3 | 5 | 14 | 22 | 0.230 | 0.609 | 0.320 | 0.6725 |  |  |
| multiply | וְהִרְבֵּיתִי / וּרְבוּ | 4 | 3 | 12 | 19 | 0.167 | 0.264 | 0.287 | 0.8422 |  |  |
| saying | לֵאמֹר | 54 | 51 | 152 | 257 | 0.151 | 0.193 | 0.082 | 0.8827 |  |  |
| eleven | עֲשָׂרָה / עַשְׁתֵּי / לְאֹהֶל | 1 | 1 | 4 | 6 | 0.145 | 0.145 | 0.398 | 0.9101 |  |  |
| appoint | נִתְּנָה / וְנָשׁוּבָה / רֹאשׁ | 1 | 1 | 4 | 6 | 0.145 | 0.145 | 0.398 | 0.9101 |  |  |
| complained | וַיִּלֹּנוּ / וְעַל | 1 | 1 | 4 | 6 | 0.145 | 0.145 | 0.398 | 0.9101 |  |  |
| cook | בַּשֵּׁלוּ / וּבִשַּׁלְתָּ / בְּמָקֹם | 1 | 1 | 4 | 6 | 0.145 | 0.145 | 0.398 | 0.9101 |  |  |
| over | עַל / וְעַל / עָלָיו | 49 | 49 | 139 | 237 | 0.059 | 0.060 | 0.052 | 0.9608 |  |  |
| middle | בְּתוֹךְ | 1 | 2 | 5 | 8 | 0.054 | 0.307 | 0.202 | 0.8189 |  |  |
| shown | הֶרְאָה | 1 | 2 | 5 | 8 | 0.054 | 0.307 | 0.202 | 0.8189 |  |  |
| chariots | אַחֲרֵיהֶם / וַיָּשֻׁבוּ | 2 | 1 | 5 | 8 | 0.054 | 0.292 | 0.202 | 0.8265 |  |  |
| seir | שְׂעִיר | 1 | 2 | 5 | 8 | 0.054 | 0.307 | 0.202 | 0.8189 |  |  |
| lifted | מֵעַל / יִסְעוּ / קֶדֶם׃ | 2 | 1 | 5 | 8 | 0.054 | 0.292 | 0.202 | 0.8265 |  |  |
| firstfruits | בִּכּוּרֵי | 2 | 1 | 5 | 8 | 0.054 | 0.292 | 0.202 | 0.8265 |  |  |
| peoples | עַמִּים / הָעַמִּים / וִהְיִיתֶם | 2 | 1 | 5 | 8 | 0.054 | 0.292 | 0.202 | 0.8265 |  |  |
| angry | וְעַל / וַיִּקְצֹף / וַאֲדַבֵּרָה | 2 | 2 | 6 | 10 | 0.015 | 0.015 | 0.080 | 0.9906 |  |  |
| midianite | הַמִּדְיָנִית | 1 | 1 | 3 | 5 | 0.008 | 0.008 | 0.035 | 0.9949 |  |  |
| inquire | לִדְרֹשׁ / לְחֹתְנוֹ | 1 | 1 | 3 | 5 | 0.008 | 0.008 | 0.035 | 0.9949 |  |  |
| across | לַיַּרְדֵּן / מֵעֵבֶר | 1 | 1 | 3 | 5 | 0.008 | 0.008 | 0.035 | 0.9949 |  |  |

---

## Machine-readable companion

The companion CSV/JSON contain every word and all calculated fields, including normalized rates, expected counts, shares, smoothed enrichment, source-vs-rest WoE, source-specific signed information, all pairwise J/E/P WoE and signed-information contrasts, global surprise bits, G², p-value, BH q-value, and artifact/reliability flags.

The JSON additionally embeds the corpus totals, formulas, metric definitions, caveats, and corpus-level statistics used in this report.
