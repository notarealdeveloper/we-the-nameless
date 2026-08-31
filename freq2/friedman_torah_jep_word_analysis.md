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

**J:** interpersonal, familial, embodied narrative. Its strongest ordinary-language contrasts include `father`, `she`, `her`, `brother`, `servant`, `city`, `woman`, `down`, `ground`, `pregnant`, and a great deal of story motion and conversation (`went`, `came`, `said`). Relative to E specifically, the family/women/household signal gets even clearer.

**E:** `God`, `people`, `Egypt`, `Pharaoh`, `Moses`, `dream`, `hand`, `elders`, `serve`, plus a more deictic/dialogic set (`here`, `now`, `this`, `you'll`, `would`, `go`, `set`). Proper names such as `Balaam` and `Balak` are spectacular classifiers, but those are obviously topic/location-of-story evidence rather than prose style.

**P:** a qualitatively different register. Ritual/legal/technical vocabulary dominates (`offering`, `priest`, `holy`, `impure`, `congregation`, `atonement`, `tabernacle`, `oil`, `pure`, `blood`), alongside genealogy/administration/counting (`tribe`, `family`, `families`, `counts`, `hundred`, `thousand`). Even the high-frequency grammatical texture differs: `shall`, `of`, `the`, `its`, `their`, `any`, `for`, and `by` are strongly P-heavy. The combination strongly suggests **prescriptive + classificatory + nominal + enumerative prose**, not merely different subject matter.

That last point is the most interesting bottom-up result in the English: **P is distinguishable not only by what it talks about, but by the machinery of the sentences used to talk about it.**

---

## Method: “surprise bits”

Raw counts cannot be compared directly because P contains 2.72× as many tokens as J and 2.75× as many as E.

For a word with counts `c_J, c_E, c_P`, let `n` be the word's total count. The null expectation is simply the corpus source prior

`q = (N_J/N, N_E/N, N_P/N)`.

The observed source distribution for that word is

`p = (c_J/n, c_E/n, c_P/n)`.

The main score is:

**global surprise bits = n × D_KL(p || q)**

or explicitly:

`I(word) = Σ_s c_s log2[(c_s/n)/(N_s/N)]`.

This has an unusually useful interpretation: it is the **total number of bits by which the observed source allocation of the word surprises us**, compared with randomly drawing its occurrences in proportion to corpus size.

This automatically solves the one-off problem. An exclusive word occurring once is perfectly “pure” but supplies only a few bits. A word repeated dozens or hundreds of times in the wrong proportions can supply enormous evidence.

### Source-specific evidence

For each source I also compute a signed binary KL score, source-vs-rest:

`source_info_bits = ± n × D_KL(observed source share || corpus source share)`.

Positive means enriched; negative means depleted. `characteristic_source` is whichever source has the largest positive source-information score.

### Cryptanalytic weight of evidence

For each source I also report a Jeffreys-corrected **log2 odds ratio** (`WoE bits`) comparing occurrence in that source against occurrence in the other two sources. This acts like a cryptanalytic/naive-Bayes “how many bits should this token shift my odds?” statistic.

- **WoE** = discriminatory strength per occurrence.
- **source info bits** = amount of source-specific evidence accumulated across occurrences.
- **global surprise bits** = total three-way discrepancy.

Use all three together. Rare exclusive words often have impressive WoE but little accumulated evidence.

### Significance reference

`G² = 2 ln(2) × global surprise bits`, with a χ²(2) reference distribution. I compute nominal p-values and Benjamini–Hochberg q-values across all 4,302 word types.

**Important caveat:** token independence is false in continuous texts. Words cluster by story, law, genealogy, and passage. Therefore these p/q values are anti-conservative and should not be treated as formal authorship probabilities. The information scores are the primary ranking measures. A truly inferential version should permute or bootstrap at verse/pericope/block level.

---

## Strongest discrepancies in the entire corpus

| word           |    J |    E |    P | characteristic | global surprise bits |         q |
| -------------- | ---: | ---: | ---: | :------------: | -------------------: | --------: |
| `shall`        |   56 |  199 | 1736 |       P        |               655.59 | 1.91e-194 |
| `said`         |  380 |  329 |  115 |       J        |               493.90 | 4.50e-146 |
| `of`           |  611 |  669 | 3336 |       P        |               304.71 |  2.69e-89 |
| `offering`     |    3 |   19 |  412 |       P        |               237.73 |  2.94e-69 |
| `my`           |  224 |  190 |  105 |       J        |               222.32 |  1.02e-64 |
| `the`          | 1324 | 1335 | 5388 |       P        |               207.71 |  2.13e-60 |
| `me`           |  198 |  188 |  109 |       J        |               189.65 |  5.00e-55 |
| `priest`       |    1 |    4 |  244 |       P        |               165.65 |  6.52e-48 |
| `and`          | 2612 | 2311 | 5074 |       J        |               153.61 |  2.48e-44 |
| `people`       |   97 |  174 |   87 |       E        |               135.83 |  5.06e-39 |
| `its`          |   35 |   46 |  457 |       P        |               135.11 |  7.65e-39 |
| `holy`         |    1 |    2 |  191 |       P        |               133.00 |  3.05e-38 |
| `impure`       |    0 |    0 |  167 |       P        |               132.34 |  4.47e-38 |
| `was`          |  297 |  190 |  278 |       J        |               118.45 |  5.92e-34 |
| `father`       |  107 |   31 |   29 |       J        |               114.62 |  7.95e-33 |
| `children`     |   28 |   65 |  427 |       P        |               112.79 |  2.66e-32 |
| `here`         |  100 |  114 |   60 |       E        |               106.44 |  2.06e-30 |
| `us`           |   74 |   64 |   18 |       J        |               105.70 |  3.27e-30 |
| `to`           |  878 |  865 | 1563 |       J        |               105.38 |  3.87e-30 |
| `i'll`         |   87 |   75 |   31 |       J        |               103.70 |  1.18e-29 |
| `pharaoh`      |   24 |   92 |   23 |       E        |               103.57 |  1.24e-29 |
| `went`         |   99 |   73 |   38 |       J        |               103.23 |  1.50e-29 |
| `balaam`       |    0 |   45 |    1 |       E        |                95.09 |  4.09e-27 |
| `god`          |   54 |  183 |  150 |       E        |                95.03 |  4.10e-27 |
| `joseph`       |   52 |   70 |   17 |       E        |                92.62 |  2.09e-26 |
| `you'll`       |   56 |   72 |   20 |       E        |                91.90 |  3.33e-26 |
| `their`        |   94 |   56 |  512 |       P        |                87.78 |  5.59e-25 |
| `forward`      |    0 |    0 |  108 |       P        |                85.58 |  2.47e-24 |
| `egypt`        |   63 |  123 |   71 |       E        |                83.50 |  1.01e-23 |
| `now`          |   31 |   43 |    2 |       E        |                81.69 |  3.45e-23 |
| `make`         |   27 |   29 |  289 |       P        |                77.92 |  4.42e-22 |
| `him`          |  263 |  190 |  310 |       J        |                72.97 |  1.33e-20 |
| `congregation` |    0 |    0 |   92 |       P        |                72.90 |  1.35e-20 |
| `lord`         |   50 |   15 |    5 |       J        |                72.83 |  1.39e-20 |
| `servant`      |   41 |    8 |    1 |       J        |                71.90 |  2.50e-20 |
| `we`           |   69 |   33 |   21 |       J        |                71.38 |  3.50e-20 |
| `she`          |  112 |   33 |   71 |       J        |                71.32 |  3.56e-20 |
| `up`           |   95 |  138 |  112 |       E        |                70.61 |  5.68e-20 |
| `tribe`        |    0 |    0 |   88 |       P        |                69.73 |  9.96e-20 |
| `atonement`    |    0 |    1 |   93 |       P        |                67.96 |  3.34e-19 |

A few examples show why normalization matters:

- `shall` is the single strongest lexical discrepancy in the corpus: J=56, E=199, P=1,736.
- `said` runs in the opposite register: J=380, E=329, P=115. It is fundamentally a **J/E narrative vs P** discriminator; its J-over-E difference is much smaller.
- `offering` is J=3, E=19, P=412.
- `father` is J=107, E=31, P=29.
- `God` is J=54, E=183, P=150; after normalization E's rate is far higher than either J or P.
- `people` is J=97, E=174, P=87; again E is much denser despite P's much larger corpus.

The top 10 clean tokens account for 10.3% of all non-artifact lexical source information; the top 50 account for 23.2%. So source signal is concentrated, but not confined to a tiny keyword list.

---

## What defines J?

### Headline J-characteristic words

| word       |    J |    E |    P | rate/10k in source | log2 enrich. | source-info bits | global surprise bits | WoE bits |         q |
| ---------- | ---: | ---: | ---: | -----------------: | -----------: | ---------------: | -------------------: | -------: | --------: |
| `said`     |  380 |  329 |  115 |             155.71 |         1.12 |           181.91 |               493.90 |     1.68 | 4.50e-146 |
| `father`   |  107 |   31 |   29 |              43.85 |         1.59 |           102.51 |               114.62 |     2.73 |  7.95e-33 |
| `and`      | 2612 | 2311 | 5074 |            1070.32 |         0.30 |            97.92 |               153.61 |     0.43 |  2.48e-44 |
| `my`       |  224 |  190 |  105 |              91.79 |         1.02 |            90.33 |               222.32 |     1.50 |  1.02e-64 |
| `was`      |  297 |  190 |  278 |             121.70 |         0.87 |            87.87 |               118.45 |     1.25 |  5.92e-34 |
| `she`      |  112 |   33 |   71 |              45.89 |         1.28 |            70.38 |                71.32 |     2.00 |  3.56e-20 |
| `me`       |  198 |  188 |  109 |              81.13 |         0.91 |            64.26 |               189.65 |     1.31 |  5.00e-55 |
| `servant`  |   41 |    8 |    1 |              16.80 |         1.92 |            60.74 |                71.90 |     4.02 |  2.50e-20 |
| `lord`     |   50 |   15 |    5 |              20.49 |         1.73 |            58.23 |                72.83 |     3.19 |  1.39e-20 |
| `her`      |  140 |   57 |  136 |              57.37 |         0.98 |            52.52 |                53.08 |     1.43 |  6.54e-15 |
| `we`       |   69 |   33 |   21 |              28.27 |         1.39 |            51.15 |                71.38 |     2.24 |  3.50e-20 |
| `him`      |  263 |  190 |  310 |             107.77 |         0.70 |            51.08 |                72.97 |     0.97 |  1.33e-20 |
| `went`     |   99 |   73 |   38 |              40.57 |         1.15 |            50.02 |               103.23 |     1.73 |  1.50e-29 |
| `down`     |   52 |   18 |   11 |              21.31 |         1.58 |            50.00 |                61.45 |     2.72 |  2.52e-17 |
| `brother`  |   63 |   16 |   31 |              25.82 |         1.42 |            48.69 |                49.58 |     2.31 |  6.54e-14 |
| `camels`   |   22 |    2 |    0 |               9.01 |         2.05 |            39.93 |                43.74 |     5.06 |  3.11e-12 |
| `i'll`     |   87 |   75 |   31 |              35.65 |         1.08 |            39.33 |               103.70 |     1.61 |  1.18e-29 |
| `well`     |   45 |   22 |    7 |              18.44 |         1.50 |            39.09 |                61.02 |     2.52 |  3.34e-17 |
| `to`       |  878 |  865 | 1563 |             359.78 |         0.32 |            38.17 |               105.38 |     0.44 |  3.87e-30 |
| `us`       |   74 |   64 |   18 |              30.32 |         1.16 |            37.95 |               105.70 |     1.75 |  3.27e-30 |
| `won't`    |   53 |   31 |   13 |              21.72 |         1.35 |            37.23 |                63.59 |     2.16 |  6.20e-18 |
| `name`     |   68 |   33 |   41 |              27.86 |         1.17 |            35.67 |                43.54 |     1.77 |  3.47e-12 |
| `rebekah`  |   22 |    0 |    4 |               9.01 |         1.95 |            34.45 |                36.24 |     4.21 |  4.31e-10 |
| `ground`   |   34 |   10 |    8 |              13.93 |         1.60 |            33.81 |                38.61 |     2.79 |  8.71e-11 |
| `came`     |   89 |   63 |   59 |              36.47 |         0.99 |            33.70 |                58.26 |     1.44 |  2.01e-16 |
| `cain`     |   15 |    0 |    0 |               6.15 |         2.15 |            33.53 |                33.53 |     6.85 |  2.59e-09 |
| `brothers` |   50 |   24 |   20 |              20.49 |         1.32 |            33.19 |                44.15 |     2.08 |  2.43e-12 |
| `jacob`    |   68 |   51 |   29 |              27.86 |         1.11 |            32.25 |                66.84 |     1.66 |  6.77e-19 |
| `pregnant` |   18 |    2 |    0 |               7.38 |         2.02 |            31.54 |                35.35 |     4.78 |  7.71e-10 |
| `city`     |   33 |    5 |   15 |              13.52 |         1.53 |            29.98 |                30.00 |     2.60 |  2.69e-08 |
| `youngest` |   13 |    0 |    0 |               5.33 |         2.13 |            29.06 |                29.06 |     6.65 |  4.87e-08 |
| `garden`   |   13 |    0 |    0 |               5.33 |         2.13 |            29.06 |                29.06 |     6.65 |  4.87e-08 |
| `esau`     |   35 |    9 |   17 |              14.34 |         1.42 |            27.15 |                27.72 |     2.31 |  1.17e-07 |
| `sodom`    |   12 |    0 |    0 |               4.92 |         2.12 |            26.82 |                26.82 |     6.54 |  2.02e-07 |
| `birth`    |   44 |   17 |   26 |              18.03 |         1.24 |            26.17 |                28.58 |     1.93 |  6.71e-08 |
| `his`      |  393 |  296 |  717 |             161.04 |         0.40 |            25.53 |                27.87 |     0.53 |  1.07e-07 |
| `abram`    |   27 |    0 |   16 |              11.06 |         1.54 |            24.92 |                32.08 |     2.63 |  6.66e-09 |
| `there`    |   91 |   67 |   83 |              37.29 |         0.83 |            24.60 |                40.68 |     1.18 |  2.28e-11 |
| `you're`   |   26 |   11 |    4 |              10.65 |         1.55 |            24.44 |                34.64 |     2.67 |  1.22e-09 |
| `he`       |  450 |  412 |  798 |             184.40 |         0.35 |            23.22 |                46.15 |     0.47 |  6.40e-13 |
| `gave`     |   45 |   16 |   34 |              18.44 |         1.15 |            23.00 |                23.50 |     1.74 |  1.76e-06 |
| `ruled`    |   10 |    0 |    0 |               4.10 |         2.10 |            22.35 |                22.35 |     6.28 |  3.64e-06 |
| `joseph's` |   18 |    6 |    1 |               7.38 |         1.72 |            21.26 |                29.00 |     3.19 |  5.05e-08 |
| `lord's`   |   17 |    6 |    0 |               6.97 |         1.75 |            21.02 |                32.45 |     3.32 |  5.23e-09 |
| `told`     |   25 |   16 |    1 |              10.24 |         1.46 |            20.84 |                46.29 |     2.44 |  5.88e-13 |
| `called`   |   53 |   44 |   27 |              21.72 |         1.01 |            20.81 |                48.71 |     1.47 |  1.18e-13 |
| `again`    |   15 |    0 |    4 |               6.15 |         1.83 |            20.80 |                22.59 |     3.68 |  3.11e-06 |
| `sent`     |   31 |   20 |    7 |              12.70 |         1.32 |            20.79 |                39.74 |     2.09 |  4.17e-11 |
| `your`     |  270 |  258 |  418 |             110.64 |         0.43 |            20.22 |                50.66 |     0.57 |  3.27e-14 |
| `i've`     |   45 |   30 |   26 |              18.44 |         1.06 |            19.74 |                32.76 |     1.58 |  4.30e-09 |

### J as language, not merely topic

The most persuasive J signals are not the proper names. They are the **human-scale narrative words**. J is strongly enriched for personal and kinship vocabulary (`father`, `she`, `her`, `brother`, `daughter`, `woman`), first-person interaction (`my`, `me`, `we`, `us`), and ordinary physical/narrative motion (`went`, `came`, `down`). `ground`, `earth`, `city`, and concrete household/pastoral nouns reinforce the same texture.

`said` is enormously informative globally, but it should be interpreted carefully: it chiefly says “this is narrative rather than P.” J and E both use it heavily. The J-vs-E table below is better for isolating what separates those two.

### Selected ordinary-language J markers

| word | J | E | P | source rate/10k | source info bits | global bits |
|---|---:|---:|---:|---:|---:|---:|
| `said` | 380 | 329 | 115 | 155.71 | 181.91 | 493.90 |
| `father` | 107 | 31 | 29 | 43.85 | 102.51 | 114.62 |
| `she` | 112 | 33 | 71 | 45.89 | 70.38 | 71.32 |
| `her` | 140 | 57 | 136 | 57.37 | 52.52 | 53.08 |
| `brother` | 63 | 16 | 31 | 25.82 | 48.69 | 49.58 |
| `servant` | 41 | 8 | 1 | 16.80 | 60.74 | 71.90 |
| `city` | 33 | 5 | 15 | 13.52 | 29.98 | 30.00 |
| `was` | 297 | 190 | 278 | 121.70 | 87.87 | 118.45 |
| `earth` | 54 | 16 | 65 | 22.13 | 17.52 | 19.06 |
| `camels` | 22 | 2 | 0 | 9.01 | 39.93 | 43.74 |
| `daughter` | 30 | 6 | 41 | 12.29 | 8.98 | 12.88 |
| `woman` | 32 | 7 | 51 | 13.11 | 7.00 | 12.37 |
| `down` | 52 | 18 | 11 | 21.31 | 50.00 | 61.45 |
| `ground` | 34 | 10 | 8 | 13.93 | 33.81 | 38.61 |
| `pregnant` | 18 | 2 | 0 | 7.38 | 31.54 | 35.35 |
| `name` | 68 | 33 | 41 | 27.86 | 35.67 | 43.54 |
| `went` | 99 | 73 | 38 | 40.57 | 50.02 | 103.23 |
| `came` | 89 | 63 | 59 | 36.47 | 33.70 | 58.26 |
| `we` | 69 | 33 | 21 | 28.27 | 51.15 | 71.38 |
| `won't` | 53 | 31 | 13 | 21.72 | 37.23 | 63.59 |

---

## What defines E?

### Headline E-characteristic words

| word            |   J |   E |   P | rate/10k in source | log2 enrich. | source-info bits | global surprise bits | WoE bits |        q |
| --------------- | --: | --: | --: | -----------------: | -----------: | ---------------: | -------------------: | -------: | -------: |
| `people`        |  97 | 174 |  87 |              72.03 |         1.21 |            96.33 |               135.83 |     1.84 | 5.06e-39 |
| `god`           |  54 | 183 | 150 |              75.75 |         1.17 |            95.01 |                95.03 |     1.76 | 4.10e-27 |
| `pharaoh`       |  24 |  92 |  23 |              38.08 |         1.65 |            94.69 |               103.57 |     2.88 | 1.24e-29 |
| `balaam`        |   0 |  45 |   1 |              18.63 |         2.19 |            94.63 |                95.09 |     6.83 | 4.09e-27 |
| `balak`         |   1 |  32 |   0 |              13.25 |         2.16 |            65.87 |                67.77 |     6.35 | 3.73e-19 |
| `egypt`         |  63 | 123 |  71 |              50.91 |         1.18 |            65.70 |                83.50 |     1.79 | 1.01e-23 |
| `up`            |  95 | 138 | 112 |              57.12 |         0.93 |            45.99 |                70.61 |     1.33 | 5.68e-20 |
| `here`          | 100 | 114 |  60 |              47.19 |         0.98 |            42.56 |               106.44 |     1.43 | 2.06e-30 |
| `joseph`        |  52 |  70 |  17 |              28.98 |         1.25 |            41.99 |                92.62 |     1.93 | 2.09e-26 |
| `you'll`        |  56 |  72 |  20 |              29.80 |         1.21 |            39.95 |                91.90 |     1.83 | 3.33e-26 |
| `hail`          |   0 |  17 |   0 |               7.04 |         2.17 |            38.25 |                38.25 |     7.04 | 1.11e-10 |
| `ass`           |   5 |  25 |   1 |              10.35 |         1.90 |            36.32 |                42.34 |     3.88 | 7.65e-12 |
| `i`             | 139 | 203 | 272 |              84.03 |         0.65 |            34.52 |                41.42 |     0.90 | 1.41e-11 |
| `dream`         |   5 |  23 |   0 |               9.52 |         1.92 |            34.49 |                43.97 |     4.01 | 2.69e-12 |
| `now`           |  31 |  43 |   2 |              17.80 |         1.42 |            32.93 |                81.69 |     2.29 | 3.45e-23 |
| `this`          | 118 | 145 | 145 |              60.02 |         0.76 |            32.76 |                60.87 |     1.06 | 3.65e-17 |
| `nile`          |   4 |  21 |   0 |               8.69 |         1.95 |            32.75 |                40.33 |     4.17 | 2.88e-11 |
| `because`       | 124 | 148 | 150 |              61.26 |         0.74 |            31.84 |                62.35 |     1.03 | 1.41e-17 |
| `meaning`       |   0 |  13 |   0 |               5.38 |         2.15 |            29.25 |                29.25 |     6.66 | 4.35e-08 |
| `heavy`         |   9 |  23 |   0 |               9.52 |         1.74 |            27.38 |                44.44 |     3.22 | 2.01e-12 |
| `hand`          |  55 |  95 | 100 |              39.32 |         0.85 |            27.01 |                30.97 |     1.21 | 1.42e-08 |
| `owner`         |   0 |  12 |   0 |               4.97 |         2.14 |            27.00 |                27.00 |     6.55 | 1.82e-07 |
| `cows`          |   0 |  12 |   0 |               4.97 |         2.14 |            27.00 |                27.00 |     6.55 | 1.82e-07 |
| `ears`          |   2 |  20 |   4 |               8.28 |         1.83 |            26.78 |                26.86 |     3.57 | 1.98e-07 |
| `serve`         |   3 |  19 |   2 |               7.86 |         1.86 |            26.73 |                28.46 |     3.74 | 7.22e-08 |
| `out`           |  69 | 119 | 154 |              49.26 |         0.73 |            24.85 |                26.15 |     1.01 | 3.07e-07 |
| `elders`        |   3 |  18 |   2 |               7.45 |         1.84 |            24.83 |                26.56 |     3.66 | 2.38e-07 |
| `pit`           |   0 |  11 |   0 |               4.55 |         2.13 |            24.75 |                24.75 |     6.43 | 7.83e-07 |
| `drive`         |   0 |  11 |   0 |               4.55 |         2.13 |            24.75 |                24.75 |     6.43 | 7.83e-07 |
| `go`            | 109 | 134 | 157 |              55.47 |         0.67 |            24.08 |                41.84 |     0.93 | 1.06e-11 |
| `set`           |  14 |  56 |  61 |              23.18 |         1.02 |            22.53 |                24.54 |     1.49 | 8.80e-07 |
| `yesterday`     |   0 |  10 |   0 |               4.14 |         2.12 |            22.50 |                22.50 |     6.30 | 3.30e-06 |
| `moses`         |  48 | 178 | 351 |              73.68 |         0.55 |            21.99 |                60.00 |     0.75 | 6.44e-17 |
| `would`         |  26 |  49 |  36 |              20.28 |         1.07 |            21.46 |                26.16 |     1.57 | 3.07e-07 |
| `servants`      |  30 |  38 |  10 |              15.73 |         1.20 |            21.15 |                50.06 |     1.84 | 4.75e-14 |
| `father-in-law` |   3 |  14 |   0 |               5.80 |         1.90 |            21.09 |                26.77 |     3.96 | 2.08e-07 |
| `bad`           |  19 |  33 |  12 |              13.66 |         1.28 |            20.85 |                32.42 |     2.00 | 5.31e-09 |
| `jethro`        |   0 |   9 |   0 |               3.73 |         2.11 |            20.25 |                20.25 |     6.16 | 1.34e-05 |
| `boys`          |   1 |  11 |   0 |               4.55 |         2.02 |            20.12 |                22.02 |     4.85 | 4.37e-06 |
| `angel`         |   8 |  18 |   0 |               7.45 |         1.68 |            20.07 |                35.23 |     3.03 | 8.36e-10 |
| `let`           |  70 |  74 |  54 |              30.63 |         0.83 |            19.92 |                54.45 |     1.17 | 2.66e-15 |
| `abraham`       |  31 |  51 |  39 |              21.11 |         1.00 |            19.74 |                26.76 |     1.46 | 2.09e-07 |
| `they'll`       |  12 |  24 |   5 |               9.93 |         1.46 |            19.65 |                29.79 |     2.40 | 3.09e-08 |
| `ox`            |   2 |  22 |  12 |               9.11 |         1.51 |            19.56 |                20.49 |     2.54 | 1.17e-05 |
| `gods`          |   8 |  19 |   2 |               7.86 |         1.60 |            19.20 |                28.04 |     2.80 | 9.60e-08 |
| `pharaoh's`     |  15 |  27 |   8 |              11.18 |         1.34 |            18.81 |                29.41 |     2.14 | 3.98e-08 |
| `eyes`          |  48 |  53 |  30 |              21.94 |         0.94 |            18.27 |                47.79 |     1.36 | 2.18e-13 |
| `pile`          |   0 |   8 |   0 |               3.31 |         2.09 |            18.00 |                18.00 |     6.00 | 5.61e-05 |
| `pray`          |   0 |   8 |   0 |               3.31 |         2.09 |            18.00 |                18.00 |     6.00 | 5.61e-05 |
| `pay`           |   8 |  24 |  11 |               9.93 |         1.39 |            17.89 |                19.36 |     2.24 | 2.38e-05 |

### E as language, not merely topic

E has two layers of signal.

First is **story inventory**: `Balaam`, `Balak`, `Pharaoh`, `Egypt`, `Joseph`, `Moses`. These are powerful source classifiers in this partition, but weak evidence for a general authorial dialect because a different story necessarily names different people and places.

Second is a more reusable lexical texture: `God`, `people`, `dream`, `hand`, `elders`, `serve`, `here`, `now`, `this`, `because`, `go`, `set`, `would`, plus strong first/second-person dialogue. `dream` is especially clean: it appears 5× in J, 23× in E, and 0× in P.

The divine-name signal is also impossible to miss bottom-up. But it is **not independent confirmation** of the source partition: divine naming was historically part of the evidence used to construct source divisions, and the English translation can sharpen that distinction.

### Selected ordinary-language E markers

| word | J | E | P | source rate/10k | source info bits | global bits |
|---|---:|---:|---:|---:|---:|---:|
| `god` | 54 | 183 | 150 | 75.75 | 95.01 | 95.03 |
| `people` | 97 | 174 | 87 | 72.03 | 96.33 | 135.83 |
| `up` | 95 | 138 | 112 | 57.12 | 45.99 | 70.61 |
| `here` | 100 | 114 | 60 | 47.19 | 42.56 | 106.44 |
| `you'll` | 56 | 72 | 20 | 29.80 | 39.95 | 91.90 |
| `i` | 139 | 203 | 272 | 84.03 | 34.52 | 41.42 |
| `dream` | 5 | 23 | 0 | 9.52 | 34.49 | 43.97 |
| `now` | 31 | 43 | 2 | 17.80 | 32.93 | 81.69 |
| `this` | 118 | 145 | 145 | 60.02 | 32.76 | 60.87 |
| `because` | 124 | 148 | 150 | 61.26 | 31.84 | 62.35 |
| `heavy` | 9 | 23 | 0 | 9.52 | 27.38 | 44.44 |
| `hand` | 55 | 95 | 100 | 39.32 | 27.01 | 30.97 |
| `serve` | 3 | 19 | 2 | 7.86 | 26.73 | 28.46 |
| `elders` | 3 | 18 | 2 | 7.45 | 24.83 | 26.56 |
| `go` | 109 | 134 | 157 | 55.47 | 24.08 | 41.84 |
| `set` | 14 | 56 | 61 | 23.18 | 22.53 | 24.54 |
| `would` | 26 | 49 | 36 | 20.28 | 21.46 | 26.16 |
| `angel` | 8 | 18 | 0 | 7.45 | 20.07 | 35.23 |
| `if` | 51 | 94 | 155 | 38.91 | 12.54 | 12.89 |

---

## What defines P?

### Headline P-characteristic words

| word | J | E | P | rate/10k in source | log2 enrich. | source-info bits | global surprise bits | WoE bits | q |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `shall` | 56 | 199 | 1736 | 261.67 | 0.59 | 593.20 | 655.59 | 2.35 | 1.91e-194 |
| `of` | 611 | 669 | 3336 | 502.85 | 0.32 | 302.36 | 304.71 | 0.97 | 2.69e-89 |
| `offering` | 3 | 19 | 412 | 62.10 | 0.71 | 228.25 | 237.73 | 3.75 | 2.94e-69 |
| `the` | 1324 | 1335 | 5388 | 812.16 | 0.21 | 207.55 | 207.71 | 0.61 | 2.13e-60 |
| `priest` | 1 | 4 | 244 | 36.78 | 0.76 | 164.24 | 165.65 | 5.03 | 6.52e-48 |
| `its` | 35 | 46 | 457 | 68.89 | 0.55 | 133.94 | 135.11 | 2.05 | 7.65e-39 |
| `holy` | 1 | 2 | 191 | 28.79 | 0.76 | 132.74 | 133.00 | 5.33 | 3.05e-38 |
| `impure` | 0 | 0 | 167 | 25.17 | 0.78 | 132.34 | 132.34 | 7.94 | 4.47e-38 |
| `children` | 28 | 65 | 427 | 64.36 | 0.51 | 101.60 | 112.79 | 1.75 | 2.66e-32 |
| `forward` | 0 | 0 | 108 | 16.28 | 0.78 | 85.58 | 85.58 | 7.31 | 2.47e-24 |
| `their` | 94 | 56 | 512 | 77.18 | 0.42 | 81.03 | 87.78 | 1.32 | 5.59e-25 |
| `make` | 27 | 29 | 289 | 43.56 | 0.53 | 77.85 | 77.92 | 1.91 | 4.42e-22 |
| `congregation` | 0 | 0 | 92 | 13.87 | 0.78 | 72.90 | 72.90 | 7.08 | 1.35e-20 |
| `tribe` | 0 | 0 | 88 | 13.26 | 0.78 | 69.73 | 69.73 | 7.02 | 9.96e-20 |
| `atonement` | 0 | 1 | 93 | 14.02 | 0.76 | 66.95 | 67.96 | 5.51 | 3.34e-19 |
| `tabernacle` | 0 | 0 | 80 | 12.06 | 0.77 | 63.39 | 63.39 | 6.88 | 6.96e-18 |
| `any` | 3 | 7 | 129 | 19.44 | 0.67 | 62.78 | 64.00 | 3.18 | 4.76e-18 |
| `oil` | 0 | 2 | 88 | 13.26 | 0.74 | 58.38 | 60.40 | 4.70 | 4.97e-17 |
| `counts` | 0 | 0 | 71 | 10.70 | 0.77 | 56.26 | 56.26 | 6.71 | 7.90e-16 |
| `meeting` | 0 | 6 | 103 | 15.53 | 0.70 | 55.56 | 61.61 | 3.55 | 2.31e-17 |
| `pure` | 4 | 0 | 93 | 14.02 | 0.72 | 54.62 | 58.59 | 3.93 | 1.63e-16 |
| `hundred` | 6 | 7 | 127 | 19.14 | 0.64 | 54.36 | 54.42 | 2.79 | 2.66e-15 |
| `for` | 187 | 172 | 825 | 124.36 | 0.27 | 51.77 | 52.12 | 0.76 | 1.23e-14 |
| `family` | 3 | 0 | 84 | 12.66 | 0.73 | 51.47 | 54.44 | 4.15 | 2.66e-15 |
| `levites` | 0 | 0 | 64 | 9.65 | 0.77 | 50.72 | 50.72 | 6.56 | 3.19e-14 |
| `thousand` | 0 | 4 | 85 | 12.81 | 0.71 | 48.79 | 52.81 | 3.80 | 7.76e-15 |
| `families` | 4 | 2 | 91 | 13.72 | 0.69 | 47.09 | 47.57 | 3.37 | 2.51e-13 |
| `work` | 12 | 6 | 131 | 19.75 | 0.60 | 46.96 | 48.38 | 2.38 | 1.47e-13 |
| `affliction` | 0 | 0 | 59 | 8.89 | 0.77 | 46.75 | 46.75 | 6.45 | 4.37e-13 |
| `bases` | 0 | 0 | 55 | 8.29 | 0.77 | 43.58 | 43.58 | 6.35 | 3.40e-12 |
| `by` | 76 | 63 | 393 | 59.24 | 0.35 | 43.29 | 44.07 | 1.05 | 2.53e-12 |
| `front` | 16 | 39 | 218 | 32.86 | 0.46 | 43.21 | 50.53 | 1.53 | 3.53e-14 |
| `army` | 1 | 2 | 72 | 10.85 | 0.71 | 42.61 | 42.86 | 3.92 | 5.49e-12 |
| `aaron` | 2 | 35 | 172 | 25.93 | 0.51 | 41.50 | 67.52 | 1.75 | 4.33e-19 |
| `sin` | 5 | 17 | 131 | 19.75 | 0.56 | 40.25 | 45.33 | 2.10 | 1.11e-12 |
| `altar` | 7 | 20 | 144 | 21.71 | 0.54 | 40.06 | 44.86 | 1.95 | 1.51e-12 |
| `sons` | 36 | 21 | 214 | 32.26 | 0.45 | 39.29 | 42.06 | 1.45 | 9.17e-12 |
| `five` | 7 | 2 | 88 | 13.26 | 0.64 | 37.68 | 39.77 | 2.77 | 4.13e-11 |
| `a` | 289 | 331 | 1203 | 181.33 | 0.19 | 37.55 | 39.92 | 0.51 | 3.75e-11 |
| `it` | 198 | 275 | 958 | 144.40 | 0.21 | 36.82 | 46.48 | 0.57 | 5.23e-13 |
| `shekels` | 0 | 1 | 54 | 8.14 | 0.74 | 36.82 | 37.83 | 4.73 | 1.47e-10 |
| `wash` | 4 | 0 | 66 | 9.95 | 0.69 | 35.15 | 39.12 | 3.44 | 6.20e-11 |
| `equipment` | 0 | 0 | 44 | 6.63 | 0.76 | 34.87 | 34.87 | 6.03 | 1.05e-09 |
| `eternal` | 0 | 0 | 44 | 6.63 | 0.76 | 34.87 | 34.87 | 6.03 | 1.05e-09 |
| `blood` | 7 | 15 | 119 | 17.94 | 0.54 | 33.55 | 35.76 | 1.96 | 5.93e-10 |
| `eleazar` | 0 | 0 | 41 | 6.18 | 0.76 | 32.49 | 32.49 | 5.93 | 5.13e-09 |
| `one` | 81 | 66 | 376 | 56.68 | 0.31 | 32.45 | 33.44 | 0.91 | 2.73e-09 |
| `an` | 31 | 64 | 271 | 40.85 | 0.36 | 30.44 | 39.13 | 1.06 | 6.20e-11 |
| `burn` | 1 | 2 | 53 | 7.99 | 0.69 | 28.85 | 29.10 | 3.49 | 4.79e-08 |
| `commanded` | 12 | 11 | 111 | 16.73 | 0.51 | 27.90 | 27.93 | 1.80 | 1.03e-07 |
| `cubits` | 1 | 1 | 47 | 7.08 | 0.70 | 27.67 | 27.67 | 3.80 | 1.20e-07 |
| `fire` | 9 | 10 | 100 | 15.07 | 0.53 | 27.46 | 27.51 | 1.92 | 1.33e-07 |
| `four` | 2 | 3 | 58 | 8.74 | 0.65 | 26.98 | 27.13 | 2.96 | 1.69e-07 |
| `columns` | 0 | 0 | 34 | 5.12 | 0.75 | 26.94 | 26.94 | 5.66 | 1.88e-07 |
| `skin` | 1 | 1 | 45 | 6.78 | 0.70 | 26.21 | 26.21 | 3.74 | 3.01e-07 |
| `peace-offering` | 0 | 1 | 40 | 6.03 | 0.72 | 26.16 | 27.16 | 4.31 | 1.66e-07 |
| `donation` | 0 | 0 | 33 | 4.97 | 0.75 | 26.15 | 26.15 | 5.62 | 3.07e-07 |
| `frames` | 0 | 0 | 33 | 4.97 | 0.75 | 26.15 | 26.15 | 5.62 | 3.07e-07 |
| `person` | 1 | 4 | 56 | 8.44 | 0.65 | 25.64 | 27.05 | 2.91 | 1.78e-07 |
| `impurity` | 0 | 0 | 32 | 4.82 | 0.75 | 25.36 | 25.36 | 5.57 | 5.24e-07 |

### P as language, not merely topic

P is the clearest lexical system by far. Three mutually reinforcing layers appear.

1. **Cult / purity / ritual:** `offering`, `priest`, `holy`, `impure`, `atonement`, `tabernacle`, `oil`, `pure`, `altar`, `sin`, `blood`, `wash`.
2. **Classification / genealogy / administration:** `congregation`, `tribe`, `family`, `families`, `Levites`, `counts`, `hundred`, `thousand`, repeated numerals and measurements.
3. **Grammatical and structural texture:** `shall`, `of`, `the`, `its`, `their`, `any`, `for`, `by`, plus spatial/technical words such as `front` and `forward`.

The third layer matters most if the goal is authorship/style rather than subject matter. A priestly law will of course say `priest`; a genealogy will of course say `family`. But there is no topical necessity for **the enormous density of `of`, possessive `its/their`, determiners, numerals, and prescriptive `shall`**. Those features are compatible with long noun phrases, object specifications, classifications, and formulaic instructions—the syntactic feel readers traditionally notice in P.

### Selected ordinary/structural P markers

| word | J | E | P | source rate/10k | source info bits | global bits |
|---|---:|---:|---:|---:|---:|---:|
| `shall` | 56 | 199 | 1736 | 261.67 | 593.20 | 655.59 |
| `of` | 611 | 669 | 3336 | 502.85 | 302.36 | 304.71 |
| `the` | 1324 | 1335 | 5388 | 812.16 | 207.55 | 207.71 |
| `its` | 35 | 46 | 457 | 68.89 | 133.94 | 135.11 |
| `their` | 94 | 56 | 512 | 77.18 | 81.03 | 87.78 |
| `any` | 3 | 7 | 129 | 19.44 | 62.78 | 64.00 |
| `for` | 187 | 172 | 825 | 124.36 | 51.77 | 52.12 |
| `by` | 76 | 63 | 393 | 59.24 | 43.29 | 44.07 |
| `make` | 27 | 29 | 289 | 43.56 | 77.85 | 77.92 |
| `children` | 28 | 65 | 427 | 64.36 | 101.60 | 112.79 |
| `offering` | 3 | 19 | 412 | 62.10 | 228.25 | 237.73 |
| `priest` | 1 | 4 | 244 | 36.78 | 164.24 | 165.65 |
| `holy` | 1 | 2 | 191 | 28.79 | 132.74 | 133.00 |
| `impure` | 0 | 0 | 167 | 25.17 | 132.34 | 132.34 |
| `congregation` | 0 | 0 | 92 | 13.87 | 72.90 | 72.90 |
| `atonement` | 0 | 1 | 93 | 14.02 | 66.95 | 67.96 |
| `tabernacle` | 0 | 0 | 80 | 12.06 | 63.39 | 63.39 |
| `oil` | 0 | 2 | 88 | 13.26 | 58.38 | 60.40 |
| `counts` | 0 | 0 | 71 | 10.70 | 56.26 | 56.26 |
| `meeting` | 0 | 6 | 103 | 15.53 | 55.56 | 61.61 |
| `pure` | 4 | 0 | 93 | 14.02 | 54.62 | 58.59 |
| `hundred` | 6 | 7 | 127 | 19.14 | 54.36 | 54.42 |
| `family` | 3 | 0 | 84 | 12.66 | 51.47 | 54.44 |
| `families` | 4 | 2 | 91 | 13.72 | 47.09 | 47.57 |
| `thousand` | 0 | 4 | 85 | 12.81 | 48.79 | 52.81 |
| `blood` | 7 | 15 | 119 | 17.94 | 33.55 | 35.76 |

---

## J versus E directly

Because J and E are almost exactly the same corpus size (24,404 vs 24,158 tokens), their direct contrast is particularly clean. The table below ignores P when calculating the signed J-vs-E information score. Positive values favor J; negative values favor E.

### Strongest J-over-E contrasts (minimum 10 J+E occurrences)

| word | J | E | P | J-vs-E signed info bits | J-vs-E WoE bits |
|---|---:|---:|---:|---:|---:|
| `she` | 112 | 33 | 71 | 32.23 | 1.74 |
| `father` | 107 | 31 | 29 | 31.39 | 1.76 |
| `abram` | 27 | 0 | 16 | 26.80 | 5.77 |
| `her` | 140 | 57 | 136 | 25.43 | 1.28 |
| `rebekah` | 22 | 0 | 4 | 21.84 | 5.48 |
| `brother` | 63 | 16 | 31 | 21.23 | 1.93 |
| `judah` | 21 | 0 | 13 | 20.85 | 5.41 |
| `lot` | 20 | 0 | 17 | 19.85 | 5.34 |
| `servant` | 41 | 8 | 1 | 17.30 | 2.27 |
| `city` | 33 | 5 | 15 | 16.45 | 2.59 |
| `was` | 297 | 190 | 278 | 16.32 | 0.63 |
| `ark` | 16 | 0 | 41 | 15.88 | 5.03 |
| `earth` | 54 | 16 | 65 | 15.44 | 1.71 |
| `cain` | 15 | 0 | 0 | 14.89 | 4.94 |
| `again` | 15 | 0 | 4 | 14.89 | 4.94 |
| `lord` | 50 | 15 | 5 | 14.09 | 1.69 |
| `camels` | 22 | 2 | 0 | 13.92 | 3.16 |
| `brother's` | 13 | 0 | 7 | 12.91 | 4.74 |
| `garden` | 13 | 0 | 0 | 12.91 | 4.74 |
| `youngest` | 13 | 0 | 0 | 12.91 | 4.74 |
| `daughter` | 30 | 6 | 41 | 12.42 | 2.22 |
| `woman` | 32 | 7 | 51 | 12.34 | 2.10 |
| `down` | 52 | 18 | 11 | 12.18 | 1.49 |
| `sodom` | 12 | 0 | 0 | 11.91 | 4.63 |
| `esau` | 35 | 9 | 17 | 11.65 | 1.89 |
| `and` | 2612 | 2311 | 5074 | 11.18 | 0.18 |
| `human` | 32 | 8 | 33 | 10.95 | 1.92 |
| `noah` | 11 | 0 | 16 | 10.92 | 4.51 |
| `pregnant` | 18 | 2 | 0 | 10.50 | 2.87 |
| `gave` | 45 | 16 | 34 | 10.15 | 1.45 |
| `edom` | 10 | 0 | 8 | 9.93 | 4.38 |
| `ruled` | 10 | 0 | 0 | 9.93 | 4.38 |
| `ground` | 34 | 10 | 8 | 9.80 | 1.70 |
| `son` | 83 | 42 | 177 | 9.59 | 0.96 |
| `his` | 393 | 296 | 717 | 9.19 | 0.40 |

### Strongest E-over-J contrasts (minimum 10 J+E occurrences)

| word | J | E | P | J-vs-E signed info bits | J-vs-E WoE bits |
|---|---:|---:|---:|---:|---:|
| `shall` | 56 | 199 | 1736 | -62.39 | -1.84 |
| `moses` | 48 | 178 | 351 | -58.35 | -1.90 |
| `god` | 54 | 183 | 150 | -54.45 | -1.77 |
| `balaam` | 0 | 45 | 1 | -45.33 | -6.53 |
| `will` | 123 | 261 | 708 | -37.60 | -1.11 |
| `pharaoh` | 24 | 92 | 23 | -31.18 | -1.94 |
| `balak` | 1 | 32 | 0 | -26.76 | -4.45 |
| `aaron` | 2 | 35 | 172 | -26.02 | -3.84 |
| `set` | 14 | 56 | 61 | -19.77 | -1.98 |
| `you` | 358 | 502 | 1138 | -18.54 | -0.51 |
| `burnt` | 0 | 18 | 92 | -18.13 | -5.23 |
| `hail` | 0 | 17 | 0 | -17.12 | -5.14 |
| `people` | 97 | 174 | 87 | -16.57 | -0.86 |
| `seven` | 14 | 49 | 71 | -15.11 | -1.79 |
| `egypt` | 63 | 123 | 71 | -14.66 | -0.98 |
| `ox` | 2 | 22 | 12 | -14.22 | -3.19 |
| `meaning` | 0 | 13 | 0 | -13.10 | -4.77 |
| `ears` | 2 | 20 | 4 | -12.46 | -3.05 |
| `not` | 108 | 176 | 465 | -12.36 | -0.72 |
| `swarm` | 0 | 12 | 6 | -12.09 | -4.66 |
| `cows` | 0 | 12 | 0 | -12.09 | -4.66 |
| `owner` | 0 | 12 | 0 | -12.09 | -4.66 |
| `children` | 28 | 65 | 427 | -11.19 | -1.22 |
| `drive` | 0 | 11 | 0 | -11.08 | -4.54 |
| `pit` | 0 | 11 | 0 | -11.08 | -4.54 |
| `chiefs` | 2 | 18 | 17 | -10.74 | -2.90 |
| `ass` | 5 | 25 | 1 | -10.65 | -2.23 |
| `out` | 69 | 119 | 154 | -10.08 | -0.80 |
| `yesterday` | 0 | 10 | 0 | -10.07 | -4.41 |
| `wood` | 0 | 10 | 38 | -10.07 | -4.41 |
| `joshua` | 0 | 10 | 10 | -10.07 | -4.41 |
| `if` | 51 | 94 | 155 | -9.66 | -0.89 |
| `it` | 198 | 275 | 958 | -9.65 | -0.49 |
| `serve` | 3 | 19 | 2 | -9.48 | -2.49 |
| `offering` | 3 | 19 | 412 | -9.48 | -2.49 |

This direct comparison sharpens the qualitative distinction:

- **J > E:** female/kinship/household and ancestral-story language (`she`, `father`, `her`, `Rebekah`, `brother`, `Judah`, `Lot`, `daughter`, `woman`), plus `servant`, `city`, `earth`, `ground`, `camels`, `down`.
- **E > J:** `Moses`, `God`, `Pharaoh`, `Aaron`, `people`, `Egypt`, along with `will/shall`, `set`, `you`, `not`, `if`, `serve`, `elders`, `ox`, and the dream/plague vocabulary.

Again, some of this is story distribution. The pronouns, auxiliaries, prepositions, deictics, and common verbs are more interesting for style.

---

## How much of this is “style” versus “what the source happens to narrate”?

This is the main interpretive limitation of a unigram study.

### Strong but topic-bound evidence

Names (`Balaam`, `Sodom`, `Rebekah`, etc.), cult objects, plague terms, genealogical labels, and specialized legal nouns may classify passages brilliantly without revealing a stable authorial dialect. They answer: **“What kinds of material are assigned to this source?”**

### More stylistically interesting evidence

High-frequency function words, pronouns, auxiliaries, discourse markers, and ordinary verbs are harder to explain away by subject matter:

- P: `shall`, `of`, `the`, `its`, `their`, `any`, `for`, `by`.
- J: unusually personal pronouns and kinship framing; `was`, `went`, `came`, `down`, `there`; much direct narrative.
- E: `here`, `now`, `this`, `because`, `would`, `if`, `go`, `set`, with strong dialogue and directive language.

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

The assignment is the source with the largest positive source-vs-rest information score. **Do not treat a one-off as strong evidence**: use `source info bits`, `global bits`, total count, and q-value together.

| word | J | E | P | n | source info bits | global bits | source WoE bits | q | FDR<.05 | artifact? |
|---|---:|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|
| `said` | 380 | 329 | 115 | 824 | 181.911 | 493.903 | 1.682 | 4.50e-146 | yes |  |
| `father` | 107 | 31 | 29 | 167 | 102.509 | 114.617 | 2.725 | 7.95e-33 | yes |  |
| `and` | 2612 | 2311 | 5074 | 9997 | 97.922 | 153.605 | 0.432 | 2.48e-44 | yes |  |
| `my` | 224 | 190 | 105 | 519 | 90.332 | 222.320 | 1.503 | 1.02e-64 | yes |  |
| `was` | 297 | 190 | 278 | 765 | 87.871 | 118.450 | 1.246 | 5.92e-34 | yes |  |
| `she` | 112 | 33 | 71 | 216 | 70.382 | 71.320 | 2.002 | 3.56e-20 | yes |  |
| `me` | 198 | 188 | 109 | 495 | 64.255 | 189.647 | 1.314 | 5.00e-55 | yes |  |
| `servant` | 41 | 8 | 1 | 50 | 60.741 | 71.903 | 4.020 | 2.50e-20 | yes |  |
| `lord` | 50 | 15 | 5 | 70 | 58.232 | 72.828 | 3.194 | 1.39e-20 | yes |  |
| `her` | 140 | 57 | 136 | 333 | 52.521 | 53.083 | 1.434 | 6.54e-15 | yes |  |
| `we` | 69 | 33 | 21 | 123 | 51.154 | 71.380 | 2.245 | 3.50e-20 | yes |  |
| `him` | 263 | 190 | 310 | 763 | 51.079 | 72.966 | 0.973 | 1.33e-20 | yes |  |
| `went` | 99 | 73 | 38 | 210 | 50.016 | 103.234 | 1.731 | 1.50e-29 | yes |  |
| `down` | 52 | 18 | 11 | 81 | 49.998 | 61.454 | 2.725 | 2.52e-17 | yes |  |
| `brother` | 63 | 16 | 31 | 110 | 48.693 | 49.582 | 2.313 | 6.54e-14 | yes |  |
| `camels` | 22 | 2 | 0 | 24 | 39.933 | 43.743 | 5.062 | 3.11e-12 | yes |  |
| `i'll` | 87 | 75 | 31 | 193 | 39.328 | 103.704 | 1.611 | 1.18e-29 | yes |  |
| `well` | 45 | 22 | 7 | 74 | 39.090 | 61.022 | 2.518 | 3.34e-17 | yes |  |
| `to` | 878 | 865 | 1563 | 3306 | 38.173 | 105.384 | 0.437 | 3.87e-30 | yes |  |
| `us` | 74 | 64 | 18 | 156 | 37.948 | 105.698 | 1.747 | 3.27e-30 | yes |  |
| `won't` | 53 | 31 | 13 | 97 | 37.226 | 63.589 | 2.159 | 6.20e-18 | yes |  |
| `name` | 68 | 33 | 41 | 142 | 35.668 | 43.539 | 1.772 | 3.47e-12 | yes |  |
| `rebekah` | 22 | 0 | 4 | 26 | 34.449 | 36.241 | 4.214 | 4.31e-10 | yes |  |
| `ground` | 34 | 10 | 8 | 52 | 33.808 | 38.606 | 2.792 | 8.71e-11 | yes |  |
| `came` | 89 | 63 | 59 | 211 | 33.696 | 58.264 | 1.441 | 2.01e-16 | yes |  |
| `cain` | 15 | 0 | 0 | 15 | 33.529 | 33.529 | 6.846 | 2.59e-09 | yes |  |
| `brothers` | 50 | 24 | 20 | 94 | 33.194 | 44.146 | 2.076 | 2.43e-12 | yes |  |
| `jacob` | 68 | 51 | 29 | 148 | 32.254 | 66.843 | 1.661 | 6.77e-19 | yes |  |
| `pregnant` | 18 | 2 | 0 | 20 | 31.543 | 35.354 | 4.779 | 7.71e-10 | yes |  |
| `city` | 33 | 5 | 15 | 53 | 29.975 | 29.997 | 2.601 | 2.69e-08 | yes |  |
| `garden` | 13 | 0 | 0 | 13 | 29.058 | 29.058 | 6.646 | 4.87e-08 | yes |  |
| `youngest` | 13 | 0 | 0 | 13 | 29.058 | 29.058 | 6.646 | 4.87e-08 | yes |  |
| `esau` | 35 | 9 | 17 | 61 | 27.150 | 27.720 | 2.314 | 1.17e-07 | yes |  |
| `sodom` | 12 | 0 | 0 | 12 | 26.823 | 26.823 | 6.535 | 2.02e-07 | yes |  |
| `birth` | 44 | 17 | 26 | 87 | 26.170 | 28.579 | 1.925 | 6.71e-08 | yes |  |
| `his` | 393 | 296 | 717 | 1406 | 25.530 | 27.868 | 0.533 | 1.07e-07 | yes |  |
| `abram` | 27 | 0 | 16 | 43 | 24.915 | 32.083 | 2.629 | 6.66e-09 | yes |  |
| `there` | 91 | 67 | 83 | 241 | 24.598 | 40.678 | 1.176 | 2.28e-11 | yes |  |
| `you're` | 26 | 11 | 4 | 41 | 24.438 | 34.640 | 2.666 | 1.22e-09 | yes |  |
| `he` | 450 | 412 | 798 | 1660 | 23.222 | 46.150 | 0.472 | 6.40e-13 | yes |  |
| `gave` | 45 | 16 | 34 | 95 | 22.998 | 23.497 | 1.742 | 1.76e-06 | yes |  |
| `ruled` | 10 | 0 | 0 | 10 | 22.352 | 22.352 | 6.284 | 3.64e-06 | yes |  |
| `joseph's` | 18 | 6 | 1 | 25 | 21.259 | 28.998 | 3.194 | 5.05e-08 | yes |  |
| `lord's` | 17 | 6 | 0 | 23 | 21.020 | 32.453 | 3.321 | 5.23e-09 | yes |  |
| `told` | 25 | 16 | 1 | 42 | 20.842 | 46.290 | 2.435 | 5.88e-13 | yes |  |
| `called` | 53 | 44 | 27 | 124 | 20.814 | 48.713 | 1.474 | 1.18e-13 | yes |  |
| `again` | 15 | 0 | 4 | 19 | 20.799 | 22.591 | 3.676 | 3.11e-06 | yes |  |
| `sent` | 31 | 20 | 7 | 58 | 20.791 | 39.744 | 2.088 | 4.17e-11 | yes |  |
| `your` | 270 | 258 | 418 | 946 | 20.222 | 50.659 | 0.574 | 3.27e-14 | yes |  |
| `i've` | 45 | 30 | 26 | 101 | 19.740 | 32.757 | 1.580 | 4.30e-09 | yes |  |
| `another` | 16 | 4 | 2 | 22 | 19.233 | 22.241 | 3.236 | 3.88e-06 | yes |  |
| `judah` | 21 | 0 | 13 | 34 | 18.788 | 24.612 | 2.563 | 8.47e-07 | yes |  |
| `abel` | 8 | 0 | 0 | 8 | 17.882 | 17.882 | 5.979 | 6.00e-05 | yes |  |
| `bag` | 8 | 0 | 0 | 8 | 17.882 | 17.882 | 5.979 | 6.00e-05 | yes |  |
| `older` | 8 | 0 | 0 | 8 | 17.882 | 17.882 | 5.979 | 6.00e-05 | yes |  |
| `younger` | 10 | 1 | 0 | 11 | 17.862 | 19.768 | 4.699 | 1.85e-05 | yes |  |
| `tree` | 19 | 5 | 6 | 30 | 17.816 | 19.097 | 2.654 | 2.81e-05 | yes |  |
| `wife` | 49 | 21 | 48 | 118 | 17.750 | 18.096 | 1.403 | 5.31e-05 | yes |  |
| `earth` | 54 | 16 | 65 | 135 | 17.524 | 19.057 | 1.312 | 2.87e-05 | yes |  |
| `canaanite` | 16 | 6 | 2 | 24 | 16.480 | 22.319 | 2.849 | 3.70e-06 | yes |  |
| `had` | 118 | 88 | 164 | 370 | 16.372 | 22.314 | 0.802 | 3.70e-06 | yes |  |
| `saw` | 44 | 40 | 21 | 105 | 16.356 | 45.321 | 1.426 | 1.11e-12 | yes |  |
| `lived` | 21 | 4 | 12 | 37 | 15.940 | 15.957 | 2.274 | 2.01e-04 | yes |  |
| `jar` | 9 | 0 | 1 | 10 | 15.772 | 16.220 | 4.554 | 1.69e-04 | yes |  |
| `spring` | 9 | 0 | 1 | 10 | 15.772 | 16.220 | 4.554 | 1.69e-04 | yes |  |
| `girl` | 9 | 1 | 0 | 10 | 15.772 | 17.677 | 4.554 | 6.82e-05 | yes |  |
| `isaac` | 36 | 22 | 23 | 81 | 15.691 | 22.930 | 1.574 | 2.49e-06 | yes |  |
| `drink` | 22 | 9 | 9 | 40 | 15.664 | 18.845 | 2.174 | 3.25e-05 | yes |  |
| `watered` | 7 | 0 | 0 | 7 | 15.647 | 15.647 | 5.798 | 2.39e-04 | yes |  |
| `draw` | 7 | 0 | 0 | 7 | 15.647 | 15.647 | 5.798 | 2.39e-04 | yes |  |
| `bags` | 7 | 0 | 0 | 7 | 15.647 | 15.647 | 5.798 | 2.39e-04 | yes |  |
| `successful` | 7 | 0 | 0 | 7 | 15.647 | 15.647 | 5.798 | 2.39e-04 | yes |  |
| `our` | 45 | 38 | 27 | 110 | 15.612 | 36.463 | 1.367 | 3.72e-10 | yes |  |
| `flock` | 24 | 13 | 9 | 46 | 15.286 | 22.616 | 2.015 | 3.07e-06 | yes |  |
| `live` | 36 | 12 | 34 | 82 | 15.195 | 15.201 | 1.543 | 3.15e-04 | yes |  |
| `kindness` | 11 | 3 | 0 | 14 | 15.127 | 20.843 | 3.608 | 9.37e-06 | yes |  |
| `you've` | 27 | 26 | 2 | 55 | 15.009 | 55.051 | 1.840 | 1.80e-15 | yes |  |
| `we'll` | 27 | 25 | 3 | 55 | 15.009 | 50.234 | 1.840 | 4.28e-14 | yes |  |
| `else` | 15 | 5 | 3 | 23 | 14.846 | 18.081 | 2.758 | 5.35e-05 | yes |  |
| `also` | 27 | 23 | 6 | 56 | 14.392 | 39.575 | 1.791 | 4.65e-11 | yes |  |
| `ate` | 16 | 8 | 2 | 26 | 14.216 | 23.136 | 2.544 | 2.21e-06 | yes |  |
| `blessed` | 24 | 10 | 14 | 48 | 13.912 | 15.722 | 1.892 | 2.30e-04 | yes |  |
| `man` | 82 | 45 | 119 | 246 | 13.877 | 13.910 | 0.897 | 7.09e-04 | yes |  |
| `don't` | 29 | 24 | 10 | 63 | 13.819 | 34.314 | 1.666 | 1.51e-09 | yes |  |
| `lot` | 20 | 0 | 17 | 37 | 13.736 | 21.352 | 2.120 | 6.70e-06 | yes |  |
| `hamor` | 8 | 1 | 0 | 9 | 13.697 | 15.602 | 4.394 | 2.45e-04 | yes |  |
| `game` | 8 | 0 | 1 | 9 | 13.697 | 14.145 | 4.394 | 6.10e-04 | yes |  |
| `hurried` | 8 | 1 | 0 | 9 | 13.697 | 15.602 | 4.394 | 2.45e-04 | yes |  |
| `presence` | 8 | 0 | 1 | 9 | 13.697 | 14.145 | 4.394 | 6.10e-04 | yes |  |
| `human` | 32 | 8 | 33 | 73 | 13.452 | 14.285 | 1.539 | 5.69e-04 | yes |  |
| `wept` | 11 | 4 | 0 | 15 | 13.416 | 21.037 | 3.245 | 8.23e-06 | yes |  |
| `we're` | 11 | 3 | 1 | 15 | 13.416 | 16.335 | 3.245 | 1.58e-04 | yes |  |
| `birthright` | 6 | 0 | 0 | 6 | 13.411 | 13.411 | 5.592 | 9.40e-04 | yes |  |
| `eden` | 6 | 0 | 0 | 6 | 13.411 | 13.411 | 5.592 | 9.40e-04 | yes |  |
| `shepherds` | 6 | 0 | 0 | 6 | 13.411 | 13.411 | 5.592 | 9.40e-04 | yes |  |
| `can't` | 6 | 0 | 0 | 6 | 13.411 | 13.411 | 5.592 | 9.40e-04 | yes |  |
| `dove` | 6 | 0 | 0 | 6 | 13.411 | 13.411 | 5.592 | 9.40e-04 | yes |  |
| `sheol` | 6 | 0 | 0 | 6 | 13.411 | 13.411 | 5.592 | 9.40e-04 | yes |  |
| `delicacies` | 6 | 0 | 0 | 6 | 13.411 | 13.411 | 5.592 | 9.40e-04 | yes |  |
| `drew` | 6 | 0 | 0 | 6 | 13.411 | 13.411 | 5.592 | 9.40e-04 | yes |  |
| `humankind` | 6 | 0 | 0 | 6 | 13.411 | 13.411 | 5.592 | 9.40e-04 | yes |  |
| `dug` | 9 | 2 | 0 | 11 | 13.282 | 17.092 | 3.817 | 9.80e-05 | yes |  |
| `nahor` | 9 | 0 | 2 | 11 | 13.282 | 14.178 | 3.817 | 6.01e-04 | yes |  |
| `became` | 20 | 7 | 11 | 38 | 12.981 | 13.893 | 2.040 | 7.16e-04 | yes |  |
| `took` | 55 | 48 | 49 | 152 | 12.830 | 29.249 | 1.080 | 4.35e-08 | yes |  |
| `brother's` | 13 | 0 | 7 | 20 | 12.788 | 15.924 | 2.739 | 2.05e-04 | yes |  |
| `know` | 33 | 29 | 16 | 78 | 12.600 | 32.773 | 1.450 | 4.28e-09 | yes |  |
| `he's` | 12 | 6 | 0 | 18 | 12.360 | 23.793 | 2.835 | 1.45e-06 | yes |  |
| `still` | 14 | 7 | 2 | 23 | 12.184 | 19.540 | 2.502 | 2.12e-05 | yes |  |
| `river` | 11 | 5 | 0 | 16 | 11.973 | 21.500 | 2.955 | 6.17e-06 | yes |  |
| `maybe` | 11 | 5 | 0 | 16 | 11.973 | 21.500 | 2.955 | 6.17e-06 | yes |  |
| `negeb` | 7 | 0 | 1 | 8 | 11.643 | 12.091 | 4.213 | 0.0022 | yes |  |
| `looked` | 7 | 1 | 0 | 8 | 11.643 | 13.548 | 4.213 | 8.93e-04 | yes |  |
| `found` | 25 | 18 | 12 | 55 | 11.543 | 22.087 | 1.633 | 4.20e-06 | yes |  |
| `prostitute` | 9 | 0 | 3 | 12 | 11.415 | 12.759 | 3.332 | 0.0014 | yes |  |
| `daughters` | 29 | 14 | 25 | 68 | 11.320 | 12.464 | 1.471 | 0.0017 | yes |  |
| `rachel` | 17 | 12 | 3 | 32 | 11.256 | 24.636 | 2.067 | 8.42e-07 | yes |  |
| `far` | 12 | 6 | 1 | 19 | 11.194 | 18.933 | 2.628 | 3.08e-05 | yes |  |
| `lamech` | 5 | 0 | 0 | 5 | 11.176 | 11.176 | 5.351 | 0.0038 | yes |  |
| `tamar` | 5 | 0 | 0 | 5 | 11.176 | 11.176 | 5.351 | 0.0038 | yes |  |
| `honest` | 5 | 0 | 0 | 5 | 11.176 | 11.176 | 5.351 | 0.0038 | yes |  |
| `escape` | 5 | 0 | 0 | 5 | 11.176 | 11.176 | 5.351 | 0.0038 | yes |  |
| `faithfulness` | 5 | 0 | 0 | 5 | 11.176 | 11.176 | 5.351 | 0.0038 | yes |  |
| `began` | 5 | 0 | 0 | 5 | 11.176 | 11.176 | 5.351 | 0.0038 | yes |  |
| `gomorrah` | 5 | 0 | 0 | 5 | 11.176 | 11.176 | 5.351 | 0.0038 | yes |  |
| `lowered` | 5 | 0 | 0 | 5 | 11.176 | 11.176 | 5.351 | 0.0038 | yes |  |
| `zoar` | 5 | 0 | 0 | 5 | 11.176 | 11.176 | 5.351 | 0.0038 | yes |  |
| `fathered` | 11 | 1 | 5 | 17 | 10.731 | 10.976 | 2.714 | 0.0042 | yes |  |
| `abraham's` | 13 | 6 | 3 | 22 | 10.686 | 15.197 | 2.398 | 3.15e-04 | yes |  |
| `let's` | 13 | 9 | 0 | 22 | 10.686 | 27.834 | 2.398 | 1.09e-07 | yes |  |
| `words` | 17 | 16 | 0 | 33 | 10.532 | 41.019 | 1.976 | 1.82e-11 | yes |  |
| `house` | 63 | 30 | 97 | 190 | 10.423 | 10.876 | 0.887 | 0.0045 | yes |  |
| `laban` | 21 | 19 | 5 | 45 | 10.351 | 31.075 | 1.703 | 1.33e-08 | yes |  |
| `opened` | 10 | 4 | 1 | 15 | 10.300 | 14.760 | 2.824 | 4.22e-04 | yes |  |
| `good` | 27 | 20 | 17 | 64 | 10.227 | 19.127 | 1.444 | 2.77e-05 | yes |  |
| `boy` | 15 | 13 | 0 | 28 | 10.109 | 34.880 | 2.091 | 1.05e-09 | yes |  |
| `alive` | 15 | 7 | 6 | 28 | 10.109 | 13.191 | 2.091 | 0.0011 | yes |  |
| `blessing` | 9 | 2 | 2 | 13 | 9.919 | 10.625 | 2.969 | 0.0052 | yes |  |
| `bethuel` | 8 | 0 | 3 | 11 | 9.616 | 10.960 | 3.171 | 0.0043 | yes |  |
| `goshen` | 8 | 2 | 1 | 11 | 9.616 | 11.120 | 3.171 | 0.0039 | yes |  |
| `birthplace` | 6 | 0 | 1 | 7 | 9.614 | 10.062 | 4.007 | 0.0073 | yes |  |
| `gerar` | 6 | 1 | 0 | 7 | 9.614 | 11.520 | 4.007 | 0.0031 | yes |  |
| `mourning` | 6 | 0 | 1 | 7 | 9.614 | 10.062 | 4.007 | 0.0073 | yes |  |
| `raised` | 14 | 8 | 4 | 26 | 9.538 | 15.553 | 2.106 | 2.52e-04 | yes |  |
| `garment` | 7 | 0 | 2 | 9 | 9.458 | 10.354 | 3.476 | 0.0062 | yes |  |
| `drank` | 7 | 1 | 1 | 9 | 9.458 | 9.811 | 3.476 | 0.0086 | yes |  |
| `loved` | 7 | 2 | 0 | 9 | 9.458 | 13.269 | 3.476 | 0.0010 | yes |  |
| `how` | 17 | 11 | 7 | 35 | 9.220 | 15.962 | 1.811 | 2.01e-04 | yes |  |
| `daughter` | 30 | 6 | 41 | 77 | 8.976 | 12.880 | 1.253 | 0.0013 | yes |  |
| `abiram` | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| `nights` | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| `anguish` | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| `ishmaelites` | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| `articles` | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| `spies` | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| `fodder` | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| `sake` | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| `brown` | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| `grown` | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| `doesn't` | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| `invoked` | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| `timnah` | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| `dathan` | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| `gazed` | 4 | 0 | 0 | 4 | 8.941 | 8.941 | 5.061 | 0.0140 | yes |  |
| `column` | 9 | 5 | 0 | 14 | 8.675 | 18.202 | 2.680 | 4.95e-05 | yes |  |
| `too` | 19 | 15 | 8 | 42 | 8.667 | 19.394 | 1.622 | 2.33e-05 | yes |  |
| `get` | 17 | 14 | 5 | 36 | 8.624 | 21.741 | 1.735 | 5.27e-06 | yes |  |
| `heard` | 23 | 15 | 17 | 55 | 8.500 | 12.787 | 1.424 | 0.0014 | yes |  |
| `before` | 33 | 31 | 25 | 89 | 8.388 | 23.121 | 1.138 | 2.23e-06 | yes |  |
| `ran` | 8 | 2 | 2 | 12 | 8.240 | 8.947 | 2.809 | 0.0140 | yes |  |
| `virtuous` | 8 | 4 | 0 | 12 | 8.240 | 15.862 | 2.809 | 2.12e-04 | yes |  |
| `asked` | 8 | 4 | 0 | 12 | 8.240 | 15.862 | 2.809 | 2.12e-04 | yes |  |
| `many` | 10 | 6 | 1 | 17 | 8.147 | 15.886 | 2.377 | 2.10e-04 | yes |  |
| `we've` | 7 | 1 | 2 | 10 | 7.867 | 7.914 | 2.991 | 0.0251 | yes |  |
| `she's` | 7 | 3 | 0 | 10 | 7.867 | 13.583 | 2.991 | 8.74e-04 | yes |  |
| `sihon` | 5 | 0 | 1 | 6 | 7.621 | 8.068 | 3.766 | 0.0234 | yes |  |
| `sight` | 5 | 0 | 1 | 6 | 7.621 | 8.068 | 3.766 | 0.0234 | yes |  |
| `dinah` | 5 | 0 | 1 | 6 | 7.621 | 8.068 | 3.766 | 0.0234 | yes |  |
| `messengers` | 5 | 1 | 0 | 6 | 7.621 | 9.526 | 3.766 | 0.0101 | yes |  |
| `language` | 5 | 0 | 1 | 6 | 7.621 | 8.068 | 3.766 | 0.0234 | yes |  |
| `shelah` | 6 | 0 | 2 | 8 | 7.610 | 8.506 | 3.270 | 0.0177 | yes |  |
| `whole` | 6 | 1 | 1 | 8 | 7.610 | 7.964 | 3.270 | 0.0249 | yes |  |
| `egyptians` | 6 | 2 | 0 | 8 | 7.610 | 11.421 | 3.270 | 0.0033 | yes |  |
| `mother` | 14 | 4 | 11 | 29 | 7.485 | 7.485 | 1.795 | 0.0325 | yes |  |
| `bless` | 15 | 11 | 6 | 32 | 7.474 | 15.198 | 1.716 | 3.15e-04 | yes |  |
| `edom` | 10 | 0 | 8 | 18 | 7.269 | 10.853 | 2.196 | 0.0045 | yes |  |
| `place` | 52 | 26 | 85 | 163 | 7.226 | 7.675 | 0.805 | 0.0293 | yes |  |
| `fled` | 8 | 4 | 1 | 13 | 7.108 | 11.568 | 2.519 | 0.0030 | yes |  |
| `could` | 8 | 2 | 3 | 13 | 7.108 | 7.408 | 2.519 | 0.0340 | yes |  |
| `little` | 8 | 4 | 1 | 13 | 7.108 | 11.568 | 2.519 | 0.0030 | yes |  |
| `woman` | 32 | 7 | 51 | 90 | 7.001 | 12.369 | 1.044 | 0.0018 | yes |  |
| `bowed` | 12 | 10 | 2 | 24 | 6.956 | 19.106 | 1.891 | 2.80e-05 | yes |  |
| `wine` | 9 | 0 | 7 | 16 | 6.709 | 9.845 | 2.232 | 0.0084 | yes |  |
| `shechem` | 9 | 6 | 1 | 16 | 6.709 | 14.448 | 2.232 | 5.13e-04 | yes |  |
| `ammon` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `lot's` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `nostrils` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `attractive` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `marah` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `eve` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `king's` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `colors` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `mistress` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `nakedness` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `three-year-old` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `lodging` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `warden` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `gray` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `shechem's` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `defiled` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `enoch` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `rain` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `zillah` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `delayed` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `jobab` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `hairy` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `sacred` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `pt` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `completed` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `aroma` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `pledge` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `adullamite` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `amalekite` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `burial` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `bracelets` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `roll` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `spying` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `consent` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `circles` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `nephilim` | 3 | 0 | 0 | 3 | 6.706 | 6.706 | 4.698 | 0.0480 | yes |  |
| `egyptian` | 7 | 2 | 2 | 11 | 6.622 | 7.329 | 2.628 | 0.0358 | yes |  |
| `neck` | 7 | 3 | 1 | 11 | 6.622 | 9.541 | 2.628 | 0.0101 | yes |  |
| `time` | 20 | 14 | 16 | 50 | 6.490 | 10.430 | 1.318 | 0.0059 | yes |  |
| `much` | 11 | 4 | 7 | 22 | 6.376 | 6.732 | 1.891 | 0.0480 | yes |  |
| `face` | 27 | 26 | 22 | 75 | 6.183 | 17.821 | 1.073 | 6.21e-05 | yes |  |
| `grew` | 6 | 2 | 1 | 9 | 6.180 | 7.684 | 2.784 | 0.0292 | yes |  |
| `flocks` | 6 | 1 | 2 | 9 | 6.180 | 6.227 | 2.784 | 0.0630 |  |  |
| `spotted` | 6 | 2 | 1 | 9 | 6.180 | 7.684 | 2.784 | 0.0292 | yes |  |
| `amorite` | 8 | 5 | 1 | 14 | 6.155 | 12.230 | 2.278 | 0.0020 | yes |  |
| `may` | 26 | 23 | 23 | 72 | 6.021 | 14.150 | 1.080 | 6.10e-04 | yes |  |
| `soul` | 9 | 5 | 3 | 17 | 5.915 | 9.151 | 2.052 | 0.0127 | yes |  |
| `road` | 9 | 8 | 0 | 17 | 5.915 | 21.158 | 2.052 | 7.63e-06 | yes |  |
| `days` | 50 | 32 | 80 | 162 | 5.900 | 6.043 | 0.736 | 0.0707 |  |  |
| `shem` | 5 | 0 | 2 | 7 | 5.823 | 6.719 | 3.029 | 0.0480 | yes |  |
| `plain` | 5 | 0 | 2 | 7 | 5.823 | 6.719 | 3.029 | 0.0480 | yes |  |
| `rods` | 5 | 0 | 2 | 7 | 5.823 | 6.719 | 3.029 | 0.0480 | yes |  |
| `waters` | 12 | 4 | 10 | 26 | 5.756 | 5.774 | 1.677 | 0.0835 |  |  |
| `suffering` | 4 | 1 | 0 | 5 | 5.676 | 7.581 | 3.476 | 0.0306 | yes |  |
| `bearing` | 4 | 0 | 1 | 5 | 5.676 | 6.124 | 3.476 | 0.0671 |  |  |
| `recognize` | 4 | 1 | 0 | 5 | 5.676 | 7.581 | 3.476 | 0.0306 | yes |  |
| `few` | 4 | 0 | 1 | 5 | 5.676 | 6.124 | 3.476 | 0.0671 |  |  |
| `kid` | 4 | 1 | 0 | 5 | 5.676 | 7.581 | 3.476 | 0.0306 | yes |  |
| `rose` | 4 | 1 | 0 | 5 | 5.676 | 7.581 | 3.476 | 0.0306 | yes |  |
| `bush` | 4 | 1 | 0 | 5 | 5.676 | 7.581 | 3.476 | 0.0306 | yes |  |
| `spend` | 4 | 1 | 0 | 5 | 5.676 | 7.581 | 3.476 | 0.0306 | yes |  |
| `sarai` | 8 | 0 | 7 | 15 | 5.341 | 8.477 | 2.072 | 0.0180 | yes |  |
| `today` | 13 | 11 | 6 | 30 | 5.299 | 13.024 | 1.517 | 0.0012 | yes |  |
| `find` | 13 | 12 | 5 | 30 | 5.299 | 15.547 | 1.517 | 2.52e-04 | yes |  |
| `forty` | 13 | 1 | 16 | 30 | 5.299 | 8.886 | 1.517 | 0.0144 | yes |  |
| `king` | 13 | 12 | 5 | 30 | 5.299 | 15.547 | 1.517 | 2.52e-04 | yes |  |
| `very` | 25 | 21 | 25 | 71 | 5.273 | 10.738 | 1.025 | 0.0049 | yes |  |
| `isn't` | 9 | 8 | 1 | 18 | 5.217 | 16.379 | 1.891 | 1.53e-04 | yes |  |
| `they` | 200 | 161 | 432 | 793 | 5.198 | 5.243 | 0.328 | 0.1129 |  |  |
| `son's` | 6 | 1 | 3 | 10 | 5.080 | 5.084 | 2.422 | 0.1245 |  |  |
| `knew` | 6 | 2 | 2 | 10 | 5.080 | 5.787 | 2.422 | 0.0829 |  |  |
| `philistines` | 6 | 4 | 0 | 10 | 5.080 | 12.701 | 2.422 | 0.0015 | yes |  |
| `sister` | 14 | 5 | 15 | 34 | 4.950 | 4.971 | 1.392 | 0.1316 |  |  |
| `where` | 19 | 17 | 15 | 51 | 4.909 | 12.111 | 1.154 | 0.0022 | yes |  |
| `pass` | 13 | 6 | 12 | 31 | 4.842 | 5.121 | 1.437 | 0.1218 |  |  |
| `upon` | 7 | 3 | 3 | 13 | 4.769 | 5.829 | 2.098 | 0.0808 |  |  |
| `son` | 83 | 42 | 177 | 302 | 4.765 | 9.653 | 0.498 | 0.0095 | yes |  |
| `those` | 18 | 3 | 27 | 48 | 4.755 | 8.497 | 1.170 | 0.0178 | yes |  |
| `come` | 64 | 53 | 108 | 225 | 4.687 | 6.888 | 0.568 | 0.0465 | yes |  |
| `maid` | 11 | 7 | 7 | 25 | 4.670 | 7.144 | 1.557 | 0.0397 | yes |  |
| `dust` | 8 | 0 | 8 | 16 | 4.637 | 8.221 | 1.891 | 0.0213 | yes |  |
| `coat` | 8 | 0 | 8 | 16 | 4.637 | 8.221 | 1.891 | 0.0213 | yes |  |
| `asses` | 8 | 2 | 6 | 16 | 4.637 | 4.646 | 1.891 | 0.1414 |  |  |
| `call` | 9 | 5 | 5 | 19 | 4.600 | 6.367 | 1.747 | 0.0586 |  |  |
| `yet` | 5 | 3 | 0 | 8 | 4.574 | 10.290 | 2.543 | 0.0063 | yes |  |
| `gift` | 5 | 0 | 3 | 8 | 4.574 | 5.918 | 2.543 | 0.0764 |  |  |
| `household` | 5 | 0 | 3 | 8 | 4.574 | 5.918 | 2.543 | 0.0764 |  |  |
| `stopped` | 5 | 3 | 0 | 8 | 4.574 | 10.290 | 2.543 | 0.0063 | yes |  |
| `lahai-roi` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `care` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `chesed` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `territory` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `undertaken` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `smooth` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `peeled` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `substance` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `bridegroom` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `waited` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `sheaves` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `twins` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `later` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `abounding` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `oaks` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `hirah` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `hazo` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `nimrod` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `tending` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `weren't` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `remnant` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `says` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `sidon` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `leaves` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `tahash` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `sarai's` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `husham` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `annihilate` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `friend` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `pildash` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `euphrates` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `plowing` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `wretchedness` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `present` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `ai` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `rode` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `extended` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `hamor's` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `herded` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `environs` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `joktan` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `expelled` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `kids` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `troughs` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `copulate` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `buz` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `wiped` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `israelites` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `heel` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `shinar` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `compassion` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `rained` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `atad` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `tender` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `maacah` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `slow` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `irad` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `mentioned` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `finds` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `achbor` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `hitched` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `countable` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `tower` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `grow` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `drinking` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `thread` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `pishon` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `nursed` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `widowhood` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `slumber` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `roamer` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `dawn` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `quick` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `disgrace` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `pasture` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `resting` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `superior` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `canaanites` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `mehuya-el` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `pairs` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `loaded` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `desire` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `stew` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `nineveh` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `hunting` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `baal-hanan` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `ripped` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `led` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `hunter` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `swallow` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `calah` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `hadad` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `proportion` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `loves` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `stuff` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `pain` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `week` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `backwards` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `sustain` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `eased` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `samlah` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `follow` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `wells` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `noon` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `tebah` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `virtue` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `rover` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `seal` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `resident` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `struggled` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `limit` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `herders` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `portions` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `eber` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `metusha-el` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `restrained` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `shua` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `mightier` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `reumah` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `traveling` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `hormah` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `sevenfold` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `channels` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `fighting` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `physicians` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `loud` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `good-looking` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `exhausted` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `trusted` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `walking` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `reaches` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `deception` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `sought` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `flame` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `bitumen` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `bore` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `inclination` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `reckoning` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `associated` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `jidlaph` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `greatly` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `cluster` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `gaham` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `rising` | 2 | 0 | 0 | 2 | 4.470 | 4.470 | 4.213 | 0.1414 |  |  |
| `father's` | 26 | 20 | 32 | 78 | 4.400 | 6.860 | 0.905 | 0.0472 | yes |  |
| `great` | 11 | 6 | 9 | 26 | 4.200 | 5.100 | 1.461 | 0.1235 |  |  |
| `milcah` | 6 | 0 | 5 | 11 | 4.199 | 6.439 | 2.132 | 0.0570 |  |  |
| `youth` | 4 | 0 | 2 | 6 | 4.120 | 5.016 | 2.739 | 0.1292 |  |  |
| `she'll` | 4 | 1 | 1 | 6 | 4.120 | 4.473 | 2.739 | 0.1414 |  |  |
| `yaphet` | 4 | 0 | 2 | 6 | 4.120 | 5.016 | 2.739 | 0.1292 |  |  |
| `laban's` | 4 | 2 | 0 | 6 | 4.120 | 7.931 | 2.739 | 0.0250 | yes |  |
| `lying` | 4 | 0 | 2 | 6 | 4.120 | 5.016 | 2.739 | 0.1292 |  |  |
| `tents` | 4 | 0 | 2 | 6 | 4.120 | 5.016 | 2.739 | 0.1292 |  |  |
| `age` | 4 | 2 | 0 | 6 | 4.120 | 7.931 | 2.739 | 0.0250 | yes |  |
| `spent` | 4 | 2 | 0 | 6 | 4.120 | 7.931 | 2.739 | 0.0250 | yes |  |
| `happen` | 4 | 2 | 0 | 6 | 4.120 | 7.931 | 2.739 | 0.0250 | yes |  |
| `indeed` | 4 | 1 | 1 | 6 | 4.120 | 4.473 | 2.739 | 0.1414 |  |  |
| `bilhah` | 4 | 0 | 2 | 6 | 4.120 | 5.016 | 2.739 | 0.1292 |  |  |
| `bury` | 7 | 0 | 7 | 14 | 4.058 | 7.194 | 1.891 | 0.0391 | yes |  |
| `listened` | 9 | 6 | 5 | 20 | 4.050 | 6.789 | 1.616 | 0.0480 | yes |  |
| `east` | 13 | 5 | 15 | 33 | 4.026 | 4.048 | 1.289 | 0.1796 |  |  |
| `feet` | 8 | 2 | 7 | 17 | 4.024 | 4.093 | 1.731 | 0.1796 |  |  |
| `done` | 25 | 21 | 30 | 76 | 3.995 | 7.600 | 0.877 | 0.0305 | yes |  |
| `than` | 14 | 9 | 14 | 37 | 3.811 | 5.022 | 1.195 | 0.1292 |  |  |
| `naked` | 3 | 0 | 1 | 4 | 3.805 | 4.253 | 3.113 | 0.1621 |  |  |
| `prepared` | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| `dreams` | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| `unless` | 3 | 0 | 1 | 4 | 3.805 | 4.253 | 3.113 | 0.1621 |  |  |
| `expanded` | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| `wrong` | 3 | 0 | 1 | 4 | 3.805 | 4.253 | 3.113 | 0.1621 |  |  |
| `though` | 3 | 0 | 1 | 4 | 3.805 | 4.253 | 3.113 | 0.1621 |  |  |
| `harm` | 3 | 0 | 1 | 4 | 3.805 | 4.253 | 3.113 | 0.1621 |  |  |
| `planted` | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| `pitched` | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| `destroying` | 3 | 0 | 1 | 4 | 3.805 | 4.253 | 3.113 | 0.1621 |  |  |
| `ourselves` | 3 | 0 | 1 | 4 | 3.805 | 4.253 | 3.113 | 0.1621 |  |  |
| `valley` | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| `trembled` | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| `divided` | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| `hurry` | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| `hid` | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| `ready` | 3 | 0 | 1 | 4 | 3.805 | 4.253 | 3.113 | 0.1621 |  |  |
| `hated` | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| `concubine` | 3 | 0 | 1 | 4 | 3.805 | 4.253 | 3.113 | 0.1621 |  |  |
| `beautiful` | 3 | 0 | 1 | 4 | 3.805 | 4.253 | 3.113 | 0.1621 |  |  |
| `consoled` | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| `recognized` | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| `door` | 3 | 1 | 0 | 4 | 3.805 | 5.710 | 3.113 | 0.0850 |  |  |
| `noah` | 11 | 0 | 16 | 27 | 3.770 | 10.938 | 1.370 | 0.0043 | yes |  |
| `himself` | 10 | 9 | 5 | 24 | 3.658 | 9.882 | 1.425 | 0.0082 | yes |  |
| `jacob's` | 10 | 5 | 9 | 24 | 3.658 | 4.053 | 1.425 | 0.1796 |  |  |
| `sun` | 5 | 2 | 2 | 9 | 3.634 | 4.341 | 2.181 | 0.1546 |  |  |
| `speckled` | 5 | 4 | 0 | 9 | 3.634 | 11.256 | 2.181 | 0.0037 | yes |  |
| `themselves` | 9 | 8 | 4 | 21 | 3.561 | 9.576 | 1.495 | 0.0099 | yes |  |
| `yourself` | 9 | 8 | 4 | 21 | 3.561 | 9.576 | 1.495 | 0.0099 | yes |  |
| `wives` | 12 | 4 | 15 | 31 | 3.517 | 3.752 | 1.250 | 0.2067 |  |  |
| `sarah` | 12 | 8 | 11 | 31 | 3.517 | 5.032 | 1.250 | 0.1287 |  |  |
| `buy` | 8 | 6 | 4 | 18 | 3.487 | 7.002 | 1.586 | 0.0433 | yes |  |
| `milk` | 6 | 4 | 2 | 12 | 3.478 | 6.486 | 1.891 | 0.0553 |  |  |
| `speaking` | 7 | 2 | 6 | 15 | 3.450 | 3.459 | 1.710 | 0.2494 |  |  |
| `trip` | 4 | 3 | 0 | 7 | 3.078 | 8.794 | 2.254 | 0.0152 | yes |  |
| `wadi` | 4 | 1 | 2 | 7 | 3.078 | 3.124 | 2.254 | 0.2897 |  |  |
| `closed` | 4 | 2 | 1 | 7 | 3.078 | 4.582 | 2.254 | 0.1414 |  |  |
| `perizzite` | 4 | 3 | 0 | 7 | 3.078 | 8.794 | 2.254 | 0.0152 | yes |  |
| `knelt` | 4 | 3 | 0 | 7 | 3.078 | 8.794 | 2.254 | 0.0152 | yes |  |
| `eating` | 4 | 1 | 2 | 7 | 3.078 | 3.124 | 2.254 | 0.2897 |  |  |
| `worked` | 4 | 1 | 2 | 7 | 3.078 | 3.124 | 2.254 | 0.2897 |  |  |
| `prison` | 4 | 3 | 0 | 7 | 3.078 | 8.794 | 2.254 | 0.0152 | yes |  |
| `fact` | 4 | 3 | 0 | 7 | 3.078 | 8.794 | 2.254 | 0.0152 | yes |  |
| `hate` | 4 | 1 | 2 | 7 | 3.078 | 3.124 | 2.254 | 0.2897 |  |  |
| `skies` | 16 | 12 | 19 | 47 | 2.956 | 4.483 | 0.958 | 0.1414 |  |  |
| `killed` | 7 | 4 | 5 | 16 | 2.927 | 3.869 | 1.550 | 0.1913 |  |  |
| `isaac's` | 5 | 3 | 2 | 10 | 2.898 | 4.656 | 1.891 | 0.1414 |  |  |
| `toward` | 12 | 7 | 14 | 33 | 2.849 | 3.175 | 1.109 | 0.2834 |  |  |
| `seed` | 30 | 17 | 55 | 102 | 2.711 | 2.970 | 0.642 | 0.3182 |  |  |
| `finished` | 8 | 3 | 9 | 20 | 2.596 | 2.609 | 1.335 | 0.3223 |  |  |
| `nurse` | 3 | 2 | 0 | 5 | 2.540 | 6.351 | 2.376 | 0.0586 |  |  |
| `scattered` | 3 | 2 | 0 | 5 | 2.540 | 6.351 | 2.376 | 0.0586 |  |  |
| `benjamin's` | 3 | 0 | 2 | 5 | 2.540 | 3.436 | 2.376 | 0.2510 |  |  |
| `havilah` | 3 | 0 | 2 | 5 | 2.540 | 3.436 | 2.376 | 0.2510 |  |  |
| `multiplied` | 3 | 0 | 2 | 5 | 2.540 | 3.436 | 2.376 | 0.2510 |  |  |
| `allow` | 3 | 2 | 0 | 5 | 2.540 | 6.351 | 2.376 | 0.0586 |  |  |
| `prepare` | 3 | 2 | 0 | 5 | 2.540 | 6.351 | 2.376 | 0.0586 |  |  |
| `daughter-in-law` | 3 | 0 | 2 | 5 | 2.540 | 3.436 | 2.376 | 0.2510 |  |  |
| `ham` | 3 | 0 | 2 | 5 | 2.540 | 3.436 | 2.376 | 0.2510 |  |  |
| `feast` | 3 | 2 | 0 | 5 | 2.540 | 6.351 | 2.376 | 0.0586 |  |  |
| `heshbon` | 3 | 0 | 2 | 5 | 2.540 | 3.436 | 2.376 | 0.2510 |  |  |
| `sending` | 3 | 2 | 0 | 5 | 2.540 | 6.351 | 2.376 | 0.0586 |  |  |
| `fought` | 3 | 1 | 1 | 5 | 2.540 | 2.893 | 2.376 | 0.3223 |  |  |
| `left` | 21 | 16 | 31 | 68 | 2.486 | 3.374 | 0.748 | 0.2612 |  |  |
| `leah` | 7 | 6 | 4 | 17 | 2.475 | 5.990 | 1.406 | 0.0729 |  |  |
| `powerful` | 4 | 3 | 1 | 8 | 2.319 | 5.238 | 1.891 | 0.1131 |  |  |
| `h` | 4 | 0 | 4 | 8 | 2.319 | 4.111 | 1.891 | 0.1783 |  | ⚠ |
| `wagons` | 4 | 0 | 4 | 8 | 2.319 | 4.111 | 1.891 | 0.1783 |  |  |
| `stay` | 5 | 3 | 3 | 11 | 2.309 | 3.369 | 1.650 | 0.2619 |  |  |
| `whatever` | 5 | 3 | 3 | 11 | 2.309 | 3.369 | 1.650 | 0.2619 |  |  |
| `cursed` | 5 | 2 | 4 | 11 | 2.309 | 2.402 | 1.650 | 0.3223 |  |  |
| `ad` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `childed` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `bered` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `grows` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `note` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `worker` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `gihon` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `based` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `bowing` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `forgets` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `loving` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `crouches` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `peleth` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `droves` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `gum` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `sad` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `exert` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `bozrah` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `jerah` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `revolving` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `sinite` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `rehovoth-ir` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `desired` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `uzal` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `shadow` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `overturn` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `besides` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `former` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `magnitude` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `diklah` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `rules` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `satisfy` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `precious` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `lahai` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `shield` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `attraction` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `farthest` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `cause` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `plane` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `reward` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `deeds` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `roi` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `el-roi` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `exercising` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `naharaim` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `quiver` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `emptied` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `exist` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `widespread` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `peni-el` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `accad` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `brother-in-law` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `salvation` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `almodad` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `heedlessly` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `precluded` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `daily` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `hamathite` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `blindness` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `cold` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `he'd` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `sons-in-law's` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `unloaded` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `sheleph` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `rib` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `ten-thousands` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `feebler` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `followed` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `forger` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `embalming` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `pains` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `idea` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `soon` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `ben-ammi` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `clings` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `fittest` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `breadth` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `sphinxes` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `mesha` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `eber's` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `feeble` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `girl's` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `cattleman` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `console` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `poplar` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `girgashites` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `stiff-necked` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `matred` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `ruler` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `whenever` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `blowing` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `numb` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `regular` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `moon` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `worse` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `in-sides` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `tubal-cain's` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `iram` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `pipe` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `dislocated` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `she'd` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `naphtuhim` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `preserve` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `longs` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `consoles` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `event` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `merciful` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `country` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `survive` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `boiling` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `tent-dweller` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `sweat` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `pinon` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `hobab` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `visibly` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `circumcisions` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `bulrushes` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `tossed` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `joker` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `masrekah` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `succeed` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `granted` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `chezib` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `promised` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `wondrous` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `building` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `sitnah` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `ashamed` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `threshold` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `perizzites` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `proceeded` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `jubal` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `kad-monites` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `tend` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `lit` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `considered` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `shepherdess` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `figs` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `rehovot` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `warned` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `rule` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `eye-to-eye` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `erech` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `watchman` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `meditate` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `calneh` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `milcah's` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `tricked` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `fter` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `sinful` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `migdal-eder` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `alvah` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `knead` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `removing` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `damascus` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `abimael` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `he-goat` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `pistachios` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `arms` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `desirable` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `sheepshearers` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `everywhere` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `sackcloth` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `mehetabel` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `kush` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `load` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `envied` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `removed` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `summer` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `erom` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `jetheth` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `dirt` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `expand` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `dinhabah` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `nd` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `everyone's` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `breathing` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `egyptian's` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `bathe` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `approach` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `rehoboth` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `room` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `hurting` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `potency` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `elder` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `drinks` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `hat` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `harvested` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `thorn` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `magnified` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `beth` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `confirmed` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `praised` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `penuel` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `enlarge` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `divines` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `whored` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `handsome` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `praise` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `trough` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `pits` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `run` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `pained` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `nearly` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `additional` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `clever` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `winter` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `garden's` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `couple` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `lasha` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `furious` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `hadoram` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `tangled` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `biggest` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `adm` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `finishing` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `jabal` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `babble` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `wearied` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `implement` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `flint` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `divine` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `gaza` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `admh` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `resen` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `hittites` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `follows` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `mibzar` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `balm` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `knowing` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `affront` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `gh` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  | ⚠ |
| `past` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `avith` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `embalm` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `hostility` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `peaceable` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `phicol` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `kills` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `esek` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `certified` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `cainites` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `warn` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `disdained` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `vitality` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `member` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `feelings` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `obal` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `trickster` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `overturned` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `men's` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `caravan` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `taking` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `she-goat` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `joktan's` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `married` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `kindnesses` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `arvadite` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `rephaim` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `carve` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `finest` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `violating` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `arad` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `leaders` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `servant's` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `sodom's` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `nonetheless` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `stripes` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `magdiel` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `builder` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `quieted` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `attracted` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `curds` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `pau` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `covet` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `shot` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `advance` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `asherahs` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `chariotry` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `dream-master` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `understand` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `retrieved` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `casluhim` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `girls` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `deceived` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `prevailed` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `pathrusim` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `heroes` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `simple` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `respected` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `actually` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `trembling` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `brimstone` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `noses` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `elah` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `almonds` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `righteousness` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `lords` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `you'd` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `continually` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `babbled` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `babel` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `endowed` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `pleasure` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `proverbially` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `faced` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `impoverished` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `afterward` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `annoyed` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `dominion` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `earth's` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `amazed` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `anamim` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `driving` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `babylon` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `edrei` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `different` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `grasshoppers` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `despoil` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `regret` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `thistle` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `city-take` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `faltering` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `tubal-cain` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `divined` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `sephar` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `hundredfold` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `caphtorim` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `tigris` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `direct` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `hunted` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `raining` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `suffer` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `hazarmaveth` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `lentil` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `news` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `supply` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `ahuzat` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `grieved` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `finding` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `occupation` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `spy` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `almond` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `lehabim` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `beasts` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `mated` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `exposing` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `surviving` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `content` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `copulated` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `player` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `watering` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `naamah` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `ration` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `regretted` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `heifer` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `uphold` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `really` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `shittim` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `widened` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `pomegranates` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `dawn's` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `arise` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `jahaz` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `admah` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `wrestled` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `clung` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `fitter` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `wrestling` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `bedad` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `zeboim` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `quarreling` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `sweetened` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `loincloths` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `create` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `silver's` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `ou` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `kenizzites` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `cord` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `measures` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `dinah's` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `there'll` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `temani` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `accused` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `practicing` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `renown` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `ludim` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `gir-gashite` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `moreh` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `stealthily` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `seventy-seven` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `dwell` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `mezahab` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `usurped` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `thoughts` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `marry` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `profit` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `slier` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `urged` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `hill` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `fire's` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `arkite` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `ruddy` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `several` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `ophir` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `smeared` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `k` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  | ⚠ |
| `funeral` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `meager` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `atharim` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `tip` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `highway` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `balsam` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `grasped` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `foolhardy` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `kin` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `plagued` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `justify` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `song` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `son-in-law` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `tied` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `assyria` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `flow` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `handle` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `smallest` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `visible` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `nod` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `despised` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `turns` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `plenty` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `peleg` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `surely` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `zemarite` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `relax` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `never` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `jebu-sites` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `widen` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `child's` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `another's` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `acted` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `ribs` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `sons-in-law` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `sure` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `catch` | 1 | 0 | 0 | 1 | 2.235 | 2.235 | 3.476 | 0.3223 |  |  |
| `brought` | 43 | 37 | 79 | 159 | 2.177 | 3.292 | 0.470 | 0.2759 |  |  |
| `men` | 15 | 14 | 18 | 47 | 2.088 | 5.190 | 0.823 | 0.1164 |  |  |
| `swear` | 7 | 6 | 5 | 18 | 2.082 | 4.820 | 1.274 | 0.1414 |  |  |
| `eshcol` | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| `laugh` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `empty-handed` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `listening` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `willing` | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| `freed` | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| `conceal` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `myrrh` | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| `children's` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `attention` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `ours` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `zipporah` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `caused` | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| `window` | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| `chosen` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `chose` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `laughed` | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| `double` | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| `upset` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `hunt` | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| `rebekah's` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `here's` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `feel` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `giants` | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| `happens` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `shepherd` | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| `fool` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `baal` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `arnon` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `justice` | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| `companion` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `she-asses` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `smelled` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `twice` | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| `stronger` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `ever` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `kemuel` | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| `annihilated` | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| `amorites` | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| `changes` | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| `bashan` | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| `fashioned` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `drunk` | 2 | 0 | 1 | 3 | 2.060 | 2.508 | 2.628 | 0.3223 |  |  |
| `knows` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `judges` | 2 | 1 | 0 | 3 | 2.060 | 3.965 | 2.628 | 0.1796 |  |  |
| `destroy` | 6 | 1 | 8 | 15 | 1.947 | 2.907 | 1.344 | 0.3223 |  |  |
| `best` | 5 | 2 | 5 | 12 | 1.829 | 1.838 | 1.444 | 0.4138 |  |  |
| `honey` | 5 | 3 | 4 | 12 | 1.829 | 2.440 | 1.444 | 0.3223 |  |  |
| `things` | 18 | 10 | 32 | 60 | 1.823 | 1.955 | 0.691 | 0.3827 |  |  |
| `long` | 4 | 2 | 3 | 9 | 1.743 | 2.044 | 1.601 | 0.3625 |  |  |
| `saved` | 3 | 2 | 1 | 6 | 1.739 | 3.243 | 1.891 | 0.2834 |  |  |
| `delivered` | 3 | 2 | 1 | 6 | 1.739 | 3.243 | 1.891 | 0.2834 |  |  |
| `kadesh` | 3 | 0 | 3 | 6 | 1.739 | 3.083 | 1.891 | 0.2967 |  |  |
| `power` | 3 | 2 | 1 | 6 | 1.739 | 3.243 | 1.891 | 0.2834 |  |  |
| `touched` | 3 | 1 | 2 | 6 | 1.739 | 1.786 | 1.891 | 0.4260 |  |  |
| `keeping` | 3 | 0 | 3 | 6 | 1.739 | 3.083 | 1.891 | 0.2967 |  |  |
| `mourned` | 3 | 1 | 2 | 6 | 1.739 | 1.786 | 1.891 | 0.4260 |  |  |
| `abram's` | 3 | 0 | 3 | 6 | 1.739 | 3.083 | 1.891 | 0.2967 |  |  |
| `veil` | 3 | 0 | 3 | 6 | 1.739 | 3.083 | 1.891 | 0.2967 |  |  |
| `trees` | 3 | 0 | 3 | 6 | 1.739 | 3.083 | 1.891 | 0.2967 |  |  |
| `no` | 21 | 20 | 32 | 73 | 1.655 | 4.115 | 0.603 | 0.1780 |  |  |
| `appeared` | 8 | 5 | 10 | 23 | 1.610 | 1.843 | 1.024 | 0.4126 |  |  |
| `crime` | 9 | 0 | 18 | 27 | 1.523 | 9.587 | 0.929 | 0.0099 | yes |  |
| `canaan` | 17 | 5 | 36 | 58 | 1.505 | 5.227 | 0.645 | 0.1138 |  |  |
| `oath` | 5 | 1 | 7 | 13 | 1.436 | 2.129 | 1.263 | 0.3447 |  |  |
| `vineyard` | 4 | 3 | 3 | 10 | 1.298 | 2.358 | 1.360 | 0.3223 |  |  |
| `life` | 14 | 4 | 30 | 48 | 1.203 | 4.497 | 0.641 | 0.1414 |  |  |
| `onan` | 3 | 0 | 4 | 7 | 1.187 | 2.979 | 1.528 | 0.3163 |  |  |
| `prisoners` | 3 | 1 | 3 | 7 | 1.187 | 1.191 | 1.528 | 0.5711 |  |  |
| `er` | 3 | 0 | 4 | 7 | 1.187 | 2.979 | 1.528 | 0.3163 |  |  |
| `ring` | 3 | 1 | 3 | 7 | 1.187 | 1.191 | 1.528 | 0.5711 |  |  |
| `completely` | 3 | 2 | 2 | 7 | 1.187 | 1.894 | 1.528 | 0.3989 |  |  |
| `peor` | 3 | 1 | 3 | 7 | 1.187 | 1.191 | 1.528 | 0.5711 |  |  |
| `covered` | 7 | 3 | 11 | 21 | 1.185 | 1.334 | 0.940 | 0.5193 |  |  |
| `fruit` | 7 | 1 | 13 | 21 | 1.185 | 3.717 | 0.940 | 0.2110 |  |  |
| `surrounded` | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| `fallen` | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| `sees` | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| `zilpah` | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| `despoiled` | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| `weights` | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| `dispossess` | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| `bigger` | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| `uz` | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| `rod` | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| `rather` | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| `wasn't` | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| `happened` | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| `months` | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| `lain` | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| `borne` | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| `infertile` | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| `dispersed` | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| `gathering` | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| `furnace` | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| `possessions` | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| `degraded` | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| `wonders` | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| `knowledge` | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| `chariot` | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| `begun` | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| `beginning` | 2 | 0 | 2 | 4 | 1.159 | 2.055 | 1.891 | 0.3599 |  |  |
| `rejected` | 2 | 1 | 1 | 4 | 1.159 | 1.513 | 1.891 | 0.4642 |  |  |
| `curse` | 5 | 4 | 5 | 14 | 1.112 | 2.054 | 1.102 | 0.3599 |  |  |
| `passed` | 5 | 4 | 5 | 14 | 1.112 | 2.054 | 1.102 | 0.3599 |  |  |
| `give` | 45 | 41 | 94 | 180 | 1.055 | 1.710 | 0.317 | 0.4455 |  |  |
| `benjamin` | 7 | 3 | 12 | 22 | 0.961 | 1.224 | 0.844 | 0.5598 |  |  |
| `harvest` | 4 | 1 | 6 | 11 | 0.950 | 1.401 | 1.154 | 0.4999 |  |  |
| `died` | 14 | 10 | 26 | 50 | 0.921 | 0.936 | 0.559 | 0.5969 |  |  |
| `giving` | 5 | 1 | 9 | 15 | 0.846 | 2.094 | 0.958 | 0.3531 |  |  |
| `flood` | 3 | 0 | 5 | 8 | 0.792 | 3.032 | 1.239 | 0.3059 |  |  |
| `quiet` | 3 | 0 | 5 | 8 | 0.792 | 3.032 | 1.239 | 0.3059 |  |  |
| `adah` | 3 | 0 | 5 | 8 | 0.792 | 3.032 | 1.239 | 0.3059 |  |  |
| `created` | 3 | 0 | 5 | 8 | 0.792 | 3.032 | 1.239 | 0.3059 |  |  |
| `wife's` | 3 | 0 | 5 | 8 | 0.792 | 3.032 | 1.239 | 0.3059 |  |  |
| `possess` | 4 | 3 | 5 | 12 | 0.677 | 0.998 | 0.973 | 0.5969 |  |  |
| `reside` | 4 | 0 | 8 | 12 | 0.677 | 4.261 | 0.973 | 0.1621 |  |  |
| `die` | 18 | 17 | 34 | 69 | 0.665 | 1.456 | 0.414 | 0.4823 |  |  |
| `city's` | 2 | 1 | 2 | 5 | 0.649 | 0.696 | 1.405 | 0.6341 |  |  |
| `saul` | 2 | 0 | 3 | 5 | 0.649 | 1.993 | 1.405 | 0.3732 |  |  |
| `destroyed` | 2 | 1 | 2 | 5 | 0.649 | 0.696 | 1.405 | 0.6341 |  |  |
| `dew` | 2 | 1 | 2 | 5 | 0.649 | 0.696 | 1.405 | 0.6341 |  |  |
| `floor` | 2 | 0 | 3 | 5 | 0.649 | 1.993 | 1.405 | 0.3732 |  |  |
| `fortified` | 2 | 1 | 2 | 5 | 0.649 | 0.696 | 1.405 | 0.6341 |  |  |
| `forgive` | 2 | 0 | 3 | 5 | 0.649 | 1.993 | 1.405 | 0.3732 |  |  |
| `even` | 2 | 1 | 2 | 5 | 0.649 | 0.696 | 1.405 | 0.6341 |  |  |
| `captured` | 2 | 0 | 3 | 5 | 0.649 | 1.993 | 1.405 | 0.3732 |  |  |
| `bela` | 2 | 0 | 3 | 5 | 0.649 | 1.993 | 1.405 | 0.3732 |  |  |
| `threshing` | 2 | 0 | 3 | 5 | 0.649 | 1.993 | 1.405 | 0.3732 |  |  |
| `infants` | 6 | 5 | 9 | 20 | 0.608 | 1.003 | 0.733 | 0.5969 |  |  |
| `lie` | 8 | 3 | 17 | 28 | 0.603 | 1.739 | 0.621 | 0.4398 |  |  |
| `break` | 7 | 3 | 14 | 24 | 0.601 | 1.161 | 0.669 | 0.5832 |  |  |
| `paid` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `hadar` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `onyx` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `og` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `pigeon` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `complete` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `arrival` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `wail` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `shoulders` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `leaf` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `oldest` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `reject` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `shoes` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `astonished` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `wore` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `re-bekah` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `fig` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `area` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `sheep's` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `beyond` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `camel` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `scatter` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `trust` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `dispossessed` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `concealed` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `lied` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `weeks` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `cush` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `growth` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `use` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `shur` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `seventeen` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `arpachshad` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `commanding` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `insides` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `beqa` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `touching` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `stands` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `showed` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `belly` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `dipped` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `corpses` | 1 | 0 | 1 | 2 | 0.580 | 1.028 | 1.891 | 0.5969 |  |  |
| `jealous` | 3 | 2 | 4 | 9 | 0.508 | 0.601 | 0.998 | 0.6761 |  |  |
| `exposed` | 3 | 1 | 5 | 9 | 0.508 | 0.753 | 0.998 | 0.6126 |  |  |
| `regarding` | 3 | 2 | 4 | 9 | 0.508 | 0.601 | 0.998 | 0.6761 |  |  |
| `along` | 3 | 1 | 5 | 9 | 0.508 | 0.753 | 0.998 | 0.6126 |  |  |
| `third` | 8 | 6 | 15 | 29 | 0.472 | 0.499 | 0.552 | 0.7217 |  |  |
| `both` | 7 | 3 | 15 | 25 | 0.460 | 1.196 | 0.588 | 0.5698 |  |  |
| `nations` | 7 | 3 | 15 | 25 | 0.460 | 1.196 | 0.588 | 0.5698 |  |  |
| `fell` | 5 | 3 | 9 | 17 | 0.452 | 0.465 | 0.706 | 0.7384 |  |  |
| `ten` | 12 | 8 | 26 | 46 | 0.443 | 0.572 | 0.426 | 0.6891 |  |  |
| `sister's` | 2 | 0 | 4 | 6 | 0.338 | 2.130 | 1.043 | 0.3444 |  |  |
| `noah's` | 2 | 0 | 4 | 6 | 0.338 | 2.130 | 1.043 | 0.3444 |  |  |
| `fresh` | 2 | 1 | 3 | 6 | 0.338 | 0.343 | 1.043 | 0.7999 |  |  |
| `security` | 2 | 1 | 3 | 6 | 0.338 | 0.343 | 1.043 | 0.7999 |  |  |
| `corresponding` | 2 | 1 | 3 | 6 | 0.338 | 0.343 | 1.043 | 0.7999 |  |  |
| `report` | 2 | 1 | 3 | 6 | 0.338 | 0.343 | 1.043 | 0.7999 |  |  |
| `home` | 2 | 1 | 3 | 6 | 0.338 | 0.343 | 1.043 | 0.7999 |  |  |
| `sheaf` | 2 | 0 | 4 | 6 | 0.338 | 2.130 | 1.043 | 0.3444 |  |  |
| `bone` | 2 | 0 | 4 | 6 | 0.338 | 2.130 | 1.043 | 0.3444 |  |  |
| `stayed` | 3 | 1 | 6 | 10 | 0.304 | 0.756 | 0.791 | 0.6118 |  |  |
| `dominate` | 3 | 1 | 6 | 10 | 0.304 | 0.756 | 0.791 | 0.6118 |  |  |
| `something` | 3 | 2 | 5 | 10 | 0.304 | 0.313 | 0.791 | 0.8162 |  |  |
| `thousands` | 4 | 2 | 8 | 14 | 0.302 | 0.477 | 0.668 | 0.7322 |  |  |
| `given` | 15 | 9 | 37 | 61 | 0.285 | 1.205 | 0.306 | 0.5667 |  |  |
| `childless` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `who's` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `chaldees` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `stricken` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `seek` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `demolish` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `asshur` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `teman` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `roof` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `during` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `breath` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `ur` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `fury` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `rescue` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `kenaz` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `whoring` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `weep` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `gotten` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `tented` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `enmity` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `yoke` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `binding` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `cling` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `arm` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `sarah's` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `crushed` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `remaining` | 1 | 0 | 2 | 3 | 0.169 | 1.065 | 1.154 | 0.5969 |  |  |
| `taken` | 7 | 6 | 15 | 28 | 0.164 | 0.191 | 0.371 | 0.8836 |  |  |
| `cease` | 3 | 2 | 6 | 11 | 0.162 | 0.171 | 0.611 | 0.8951 |  |  |
| `appear` | 3 | 2 | 6 | 11 | 0.162 | 0.171 | 0.611 | 0.8951 |  |  |
| `places` | 2 | 1 | 4 | 7 | 0.151 | 0.239 | 0.753 | 0.8555 |  |  |
| `remain` | 2 | 1 | 4 | 7 | 0.151 | 0.239 | 0.753 | 0.8555 |  |  |
| `residents` | 2 | 1 | 4 | 7 | 0.151 | 0.239 | 0.753 | 0.8555 |  |  |
| `mother's` | 4 | 3 | 9 | 16 | 0.094 | 0.107 | 0.417 | 0.9333 |  |  |
| `have` | 54 | 52 | 146 | 252 | 0.004 | 0.018 | 0.026 | 0.9893 |  |  |

### All words assigned to E (1,124 types)

The assignment is the source with the largest positive source-vs-rest information score. **Do not treat a one-off as strong evidence**: use `source info bits`, `global bits`, total count, and q-value together.

| word | J | E | P | n | source info bits | global bits | source WoE bits | q | FDR<.05 | artifact? |
|---|---:|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|
| `people` | 97 | 174 | 87 | 358 | 96.333 | 135.829 | 1.836 | 5.06e-39 | yes |  |
| `god` | 54 | 183 | 150 | 387 | 95.013 | 95.026 | 1.761 | 4.10e-27 | yes |  |
| `pharaoh` | 24 | 92 | 23 | 139 | 94.692 | 103.574 | 2.876 | 1.24e-29 | yes |  |
| `balaam` | 0 | 45 | 1 | 46 | 94.634 | 95.085 | 6.835 | 4.09e-27 | yes |  |
| `balak` | 1 | 32 | 0 | 33 | 65.871 | 67.766 | 6.349 | 3.73e-19 | yes |  |
| `egypt` | 63 | 123 | 71 | 257 | 65.702 | 83.500 | 1.791 | 1.01e-23 | yes |  |
| `up` | 95 | 138 | 112 | 345 | 45.990 | 70.611 | 1.331 | 5.68e-20 | yes |  |
| `here` | 100 | 114 | 60 | 274 | 42.564 | 106.441 | 1.426 | 2.06e-30 | yes |  |
| `joseph` | 52 | 70 | 17 | 139 | 41.991 | 92.621 | 1.933 | 2.09e-26 | yes |  |
| `you'll` | 56 | 72 | 20 | 148 | 39.947 | 91.898 | 1.835 | 3.33e-26 | yes |  |
| `hail` | 0 | 17 | 0 | 17 | 38.248 | 38.248 | 7.040 | 1.11e-10 | yes |  |
| `ass` | 5 | 25 | 1 | 31 | 36.316 | 42.341 | 3.883 | 7.65e-12 | yes |  |
| `i` | 139 | 203 | 272 | 614 | 34.523 | 41.421 | 0.899 | 1.41e-11 | yes |  |
| `dream` | 5 | 23 | 0 | 28 | 34.495 | 43.969 | 4.006 | 2.69e-12 | yes |  |
| `now` | 31 | 43 | 2 | 76 | 32.933 | 81.688 | 2.288 | 3.45e-23 | yes |  |
| `this` | 118 | 145 | 145 | 408 | 32.760 | 60.866 | 1.057 | 3.65e-17 | yes |  |
| `nile` | 4 | 21 | 0 | 25 | 32.751 | 40.330 | 4.167 | 2.88e-11 | yes |  |
| `because` | 124 | 148 | 150 | 422 | 31.838 | 62.352 | 1.027 | 1.41e-17 | yes |  |
| `meaning` | 0 | 13 | 0 | 13 | 29.248 | 29.248 | 6.665 | 4.35e-08 | yes |  |
| `heavy` | 9 | 23 | 0 | 32 | 27.383 | 44.435 | 3.217 | 2.01e-12 | yes |  |
| `hand` | 55 | 95 | 100 | 250 | 27.007 | 30.969 | 1.209 | 1.42e-08 | yes |  |
| `cows` | 0 | 12 | 0 | 12 | 26.998 | 26.998 | 6.554 | 1.82e-07 | yes |  |
| `owner` | 0 | 12 | 0 | 12 | 26.998 | 26.998 | 6.554 | 1.82e-07 | yes |  |
| `ears` | 2 | 20 | 4 | 26 | 26.777 | 26.864 | 3.568 | 1.98e-07 | yes |  |
| `serve` | 3 | 19 | 2 | 24 | 26.731 | 28.464 | 3.736 | 7.22e-08 | yes |  |
| `out` | 69 | 119 | 154 | 342 | 24.848 | 26.150 | 1.010 | 3.07e-07 | yes |  |
| `elders` | 3 | 18 | 2 | 23 | 24.826 | 26.560 | 3.660 | 2.38e-07 | yes |  |
| `drive` | 0 | 11 | 0 | 11 | 24.748 | 24.748 | 6.434 | 7.83e-07 | yes |  |
| `pit` | 0 | 11 | 0 | 11 | 24.748 | 24.748 | 6.434 | 7.83e-07 | yes |  |
| `go` | 109 | 134 | 157 | 400 | 24.078 | 41.835 | 0.927 | 1.06e-11 | yes |  |
| `set` | 14 | 56 | 61 | 131 | 22.526 | 24.535 | 1.493 | 8.80e-07 | yes |  |
| `yesterday` | 0 | 10 | 0 | 10 | 22.499 | 22.499 | 6.302 | 3.30e-06 | yes |  |
| `moses` | 48 | 178 | 351 | 577 | 21.991 | 59.998 | 0.751 | 6.44e-17 | yes |  |
| `would` | 26 | 49 | 36 | 111 | 21.456 | 26.156 | 1.575 | 3.07e-07 | yes |  |
| `servants` | 30 | 38 | 10 | 78 | 21.152 | 50.062 | 1.838 | 4.75e-14 | yes |  |
| `father-in-law` | 3 | 14 | 0 | 17 | 21.091 | 26.775 | 3.961 | 2.08e-07 | yes |  |
| `bad` | 19 | 33 | 12 | 64 | 20.847 | 32.419 | 2.000 | 5.31e-09 | yes |  |
| `jethro` | 0 | 9 | 0 | 9 | 20.249 | 20.249 | 6.158 | 1.34e-05 | yes |  |
| `boys` | 1 | 11 | 0 | 12 | 20.123 | 22.018 | 4.849 | 4.37e-06 | yes |  |
| `angel` | 8 | 18 | 0 | 26 | 20.069 | 35.227 | 3.032 | 8.36e-10 | yes |  |
| `let` | 70 | 74 | 54 | 198 | 19.921 | 54.448 | 1.171 | 2.66e-15 | yes |  |
| `abraham` | 31 | 51 | 39 | 121 | 19.740 | 26.762 | 1.458 | 2.09e-07 | yes |  |
| `they'll` | 12 | 24 | 5 | 41 | 19.652 | 29.790 | 2.396 | 3.09e-08 | yes |  |
| `ox` | 2 | 22 | 12 | 36 | 19.557 | 20.486 | 2.544 | 1.17e-05 | yes |  |
| `gods` | 8 | 19 | 2 | 29 | 19.201 | 28.043 | 2.803 | 9.60e-08 | yes |  |
| `pharaoh's` | 15 | 27 | 8 | 50 | 18.809 | 29.407 | 2.137 | 3.98e-08 | yes |  |
| `eyes` | 48 | 53 | 30 | 131 | 18.266 | 47.793 | 1.358 | 2.18e-13 | yes |  |
| `pray` | 0 | 8 | 0 | 8 | 17.999 | 17.999 | 5.997 | 5.61e-05 | yes |  |
| `pile` | 0 | 8 | 0 | 8 | 17.999 | 17.999 | 5.997 | 5.61e-05 | yes |  |
| `pay` | 8 | 24 | 11 | 43 | 17.887 | 19.359 | 2.240 | 2.38e-05 | yes |  |
| `back` | 52 | 61 | 48 | 161 | 17.177 | 37.509 | 1.203 | 1.82e-10 | yes |  |
| `got` | 17 | 24 | 4 | 45 | 16.292 | 35.558 | 2.099 | 6.75e-10 | yes |  |
| `abimelek` | 7 | 15 | 0 | 22 | 16.279 | 29.542 | 2.957 | 3.65e-08 | yes |  |
| `insect` | 0 | 7 | 0 | 7 | 15.749 | 15.749 | 5.817 | 2.26e-04 | yes |  |
| `purpose` | 0 | 7 | 0 | 7 | 15.749 | 15.749 | 5.817 | 2.26e-04 | yes |  |
| `execrate` | 0 | 7 | 0 | 7 | 15.749 | 15.749 | 5.817 | 2.26e-04 | yes |  |
| `that` | 262 | 294 | 546 | 1102 | 14.428 | 23.154 | 0.457 | 2.20e-06 | yes |  |
| `livestock` | 8 | 19 | 7 | 34 | 14.195 | 17.565 | 2.241 | 7.32e-05 | yes |  |
| `you` | 358 | 502 | 1138 | 1998 | 13.966 | 18.902 | 0.341 | 3.14e-05 | yes |  |
| `whoever` | 0 | 8 | 1 | 9 | 13.810 | 14.262 | 4.412 | 5.69e-04 | yes |  |
| `way` | 18 | 21 | 1 | 40 | 13.789 | 42.694 | 2.051 | 6.11e-12 | yes |  |
| `did` | 44 | 61 | 67 | 172 | 13.677 | 19.785 | 1.053 | 1.83e-05 | yes |  |
| `midwives` | 0 | 6 | 0 | 6 | 13.499 | 13.499 | 5.610 | 9.13e-04 | yes |  |
| `bountifulness` | 0 | 6 | 0 | 6 | 13.499 | 13.499 | 5.610 | 9.13e-04 | yes |  |
| `thunders` | 0 | 6 | 0 | 6 | 13.499 | 13.499 | 5.610 | 9.13e-04 | yes |  |
| `drink-stewards` | 0 | 6 | 0 | 6 | 13.499 | 13.499 | 5.610 | 9.13e-04 | yes |  |
| `dies` | 0 | 6 | 0 | 6 | 13.499 | 13.499 | 5.610 | 9.13e-04 | yes |  |
| `miriam` | 0 | 9 | 2 | 11 | 13.405 | 14.309 | 3.836 | 5.64e-04 | yes |  |
| `beer-sheba` | 3 | 10 | 0 | 13 | 13.389 | 19.073 | 3.495 | 2.85e-05 | yes |  |
| `if` | 51 | 94 | 155 | 300 | 12.539 | 12.890 | 0.784 | 0.0013 | yes |  |
| `swarm` | 0 | 12 | 6 | 18 | 12.512 | 15.224 | 2.853 | 3.12e-04 | yes |  |
| `answered` | 5 | 14 | 4 | 23 | 12.353 | 14.715 | 2.520 | 4.34e-04 | yes |  |
| `seven` | 14 | 49 | 71 | 134 | 12.250 | 15.999 | 1.122 | 1.97e-04 | yes |  |
| `didn't` | 9 | 17 | 5 | 31 | 12.225 | 18.373 | 2.181 | 4.45e-05 | yes |  |
| `people's` | 3 | 15 | 8 | 26 | 11.939 | 11.940 | 2.341 | 0.0024 | yes |  |
| `anger` | 8 | 15 | 3 | 26 | 11.939 | 19.154 | 2.341 | 2.73e-05 | yes |  |
| `what` | 45 | 54 | 54 | 153 | 11.894 | 23.150 | 1.043 | 2.20e-06 | yes |  |
| `stolen` | 1 | 7 | 0 | 8 | 11.741 | 13.636 | 4.232 | 8.47e-04 | yes |  |
| `entire` | 0 | 7 | 1 | 8 | 11.741 | 12.193 | 4.232 | 0.0021 | yes |  |
| `only` | 9 | 16 | 4 | 29 | 11.649 | 18.932 | 2.200 | 3.08e-05 | yes |  |
| `early` | 3 | 9 | 0 | 12 | 11.535 | 17.219 | 3.350 | 9.04e-05 | yes |  |
| `straw` | 2 | 8 | 0 | 10 | 11.461 | 15.250 | 3.675 | 3.08e-04 | yes |  |
| `famine` | 10 | 14 | 0 | 24 | 11.386 | 30.334 | 2.376 | 2.15e-08 | yes |  |
| `ewes` | 0 | 5 | 0 | 5 | 11.249 | 11.249 | 5.369 | 0.0037 | yes |  |
| `balak's` | 0 | 5 | 0 | 5 | 11.249 | 11.249 | 5.369 | 0.0037 | yes |  |
| `master` | 0 | 5 | 0 | 5 | 11.249 | 11.249 | 5.369 | 0.0037 | yes |  |
| `communicated` | 0 | 5 | 0 | 5 | 11.249 | 11.249 | 5.369 | 0.0037 | yes |  |
| `bakers` | 0 | 5 | 0 | 5 | 11.249 | 11.249 | 5.369 | 0.0037 | yes |  |
| `voice` | 18 | 19 | 1 | 38 | 11.217 | 40.122 | 1.910 | 3.30e-11 | yes |  |
| `i'm` | 28 | 30 | 15 | 73 | 10.817 | 30.528 | 1.398 | 1.89e-08 | yes |  |
| `able` | 12 | 18 | 6 | 36 | 10.627 | 19.546 | 1.910 | 2.12e-05 | yes |  |
| `mouth` | 18 | 19 | 2 | 39 | 10.576 | 36.205 | 1.838 | 4.38e-10 | yes |  |
| `it's` | 14 | 19 | 6 | 39 | 10.576 | 22.188 | 1.838 | 3.93e-06 | yes |  |
| `tomorrow` | 2 | 10 | 3 | 15 | 10.427 | 10.717 | 2.843 | 0.0049 | yes |  |
| `tell` | 10 | 15 | 3 | 28 | 10.278 | 20.449 | 2.109 | 1.19e-05 | yes |  |
| `neighbor` | 1 | 9 | 3 | 13 | 10.034 | 10.040 | 2.988 | 0.0074 | yes |  |
| `there's` | 3 | 9 | 1 | 13 | 10.034 | 12.925 | 2.988 | 0.0013 | yes |  |
| `flared` | 2 | 9 | 2 | 13 | 10.034 | 10.728 | 2.988 | 0.0049 | yes |  |
| `pillar` | 1 | 9 | 3 | 13 | 10.034 | 10.040 | 2.988 | 0.0074 | yes |  |
| `chiefs` | 2 | 18 | 17 | 37 | 9.987 | 12.235 | 1.834 | 0.0020 | yes |  |
| `say` | 27 | 39 | 40 | 106 | 9.959 | 14.023 | 1.138 | 6.59e-04 | yes |  |
| `witness` | 0 | 8 | 3 | 11 | 9.722 | 11.077 | 3.190 | 0.0040 | yes |  |
| `hebrews` | 3 | 8 | 0 | 11 | 9.722 | 15.406 | 3.190 | 2.78e-04 | yes |  |
| `why` | 22 | 24 | 10 | 56 | 9.721 | 27.250 | 1.503 | 1.58e-07 | yes |  |
| `bosom` | 1 | 6 | 0 | 7 | 9.698 | 11.593 | 4.025 | 0.0030 | yes |  |
| `rescued` | 1 | 6 | 0 | 7 | 9.698 | 11.593 | 4.025 | 0.0030 | yes |  |
| `continue` | 1 | 6 | 0 | 7 | 9.698 | 11.593 | 4.025 | 0.0030 | yes |  |
| `believe` | 1 | 6 | 0 | 7 | 9.698 | 11.593 | 4.025 | 0.0030 | yes |  |
| `distance` | 2 | 7 | 0 | 9 | 9.552 | 13.342 | 3.495 | 9.82e-04 | yes |  |
| `maids` | 2 | 7 | 0 | 9 | 9.552 | 13.342 | 3.495 | 9.82e-04 | yes |  |
| `locust` | 0 | 7 | 2 | 9 | 9.552 | 10.456 | 3.495 | 0.0058 | yes |  |
| `stood` | 6 | 15 | 8 | 29 | 9.540 | 10.730 | 2.006 | 0.0049 | yes |  |
| `account` | 21 | 21 | 5 | 47 | 9.485 | 33.170 | 1.608 | 3.27e-09 | yes |  |
| `they're` | 3 | 12 | 6 | 21 | 9.373 | 9.504 | 2.306 | 0.0101 | yes |  |
| `against` | 16 | 35 | 43 | 94 | 9.305 | 9.306 | 1.165 | 0.0114 | yes |  |
| `mountain` | 21 | 22 | 8 | 51 | 9.067 | 27.829 | 1.519 | 1.09e-07 | yes |  |
| `throne` | 0 | 4 | 0 | 4 | 8.999 | 8.999 | 5.079 | 0.0138 | yes |  |
| `honor` | 0 | 4 | 0 | 4 | 8.999 | 8.999 | 5.079 | 0.0138 | yes |  |
| `knife` | 0 | 4 | 0 | 4 | 8.999 | 8.999 | 5.079 | 0.0138 | yes |  |
| `boy's` | 0 | 4 | 0 | 4 | 8.999 | 8.999 | 5.079 | 0.0138 | yes |  |
| `zippor` | 0 | 4 | 0 | 4 | 8.999 | 8.999 | 5.079 | 0.0138 | yes |  |
| `liberated` | 0 | 4 | 0 | 4 | 8.999 | 8.999 | 5.079 | 0.0138 | yes |  |
| `maid's` | 0 | 4 | 0 | 4 | 8.999 | 8.999 | 5.079 | 0.0138 | yes |  |
| `gore` | 0 | 4 | 0 | 4 | 8.999 | 8.999 | 5.079 | 0.0138 | yes |  |
| `going` | 15 | 24 | 19 | 58 | 8.824 | 12.172 | 1.416 | 0.0021 | yes |  |
| `land` | 122 | 131 | 218 | 471 | 8.797 | 18.290 | 0.539 | 4.69e-05 | yes |  |
| `cried` | 3 | 9 | 2 | 14 | 8.787 | 10.521 | 2.698 | 0.0056 | yes |  |
| `officers` | 2 | 8 | 2 | 12 | 8.341 | 9.035 | 2.827 | 0.0137 | yes |  |
| `he'll` | 15 | 18 | 7 | 40 | 8.278 | 20.009 | 1.628 | 1.58e-05 | yes |  |
| `favor` | 12 | 14 | 2 | 28 | 8.265 | 23.622 | 1.910 | 1.62e-06 | yes |  |
| `amalek` | 1 | 7 | 2 | 10 | 7.958 | 8.001 | 3.009 | 0.0243 | yes |  |
| `wind` | 2 | 7 | 1 | 10 | 7.958 | 9.444 | 3.009 | 0.0105 | yes |  |
| `coming` | 14 | 19 | 11 | 44 | 7.852 | 14.610 | 1.523 | 4.64e-04 | yes |  |
| `eye` | 3 | 9 | 3 | 15 | 7.728 | 8.767 | 2.457 | 0.0154 | yes |  |
| `turned` | 10 | 17 | 11 | 38 | 7.703 | 10.655 | 1.613 | 0.0051 | yes |  |
| `frogs` | 0 | 6 | 2 | 8 | 7.690 | 8.594 | 3.288 | 0.0167 | yes |  |
| `changed` | 1 | 6 | 1 | 8 | 7.690 | 8.037 | 3.288 | 0.0238 | yes |  |
| `none` | 1 | 6 | 1 | 8 | 7.690 | 8.037 | 3.288 | 0.0238 | yes |  |
| `guards` | 1 | 5 | 0 | 6 | 7.690 | 9.584 | 3.784 | 0.0099 | yes |  |
| `written` | 0 | 5 | 1 | 6 | 7.690 | 8.142 | 3.784 | 0.0224 | yes |  |
| `refuse` | 0 | 5 | 1 | 6 | 7.690 | 8.142 | 3.784 | 0.0224 | yes |  |
| `prayed` | 1 | 5 | 0 | 6 | 7.690 | 9.584 | 3.784 | 0.0099 | yes |  |
| `standing` | 11 | 14 | 4 | 29 | 7.631 | 17.731 | 1.814 | 6.59e-05 | yes |  |
| `israel's` | 4 | 15 | 13 | 32 | 7.627 | 7.700 | 1.735 | 0.0290 | yes |  |
| `see` | 30 | 40 | 49 | 119 | 7.288 | 10.602 | 0.937 | 0.0053 | yes |  |
| `judge` | 3 | 8 | 2 | 13 | 7.205 | 8.939 | 2.538 | 0.0140 | yes |  |
| `sat` | 3 | 8 | 2 | 13 | 7.205 | 8.939 | 2.538 | 0.0140 | yes |  |
| `struck` | 6 | 16 | 14 | 36 | 7.129 | 7.199 | 1.597 | 0.0390 | yes |  |
| `watch` | 11 | 15 | 7 | 33 | 7.074 | 13.726 | 1.655 | 7.98e-04 | yes |  |
| `hard-necked` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `impose` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `scorched` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `bottle` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `drink-steward` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `harnessed` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `dispute` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `trouble` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `hazeroth` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `continued` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `looking` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `lazy` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `thief` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `mercy` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `burden` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `teraphim` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `arranged` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `scrawny` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `horeb` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `stole` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `lightning` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `singing` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `subtract` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `bend` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `wouldn't` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `dreamed` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `attendant` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `sacrificing` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `jewelry` | 0 | 3 | 0 | 3 | 6.750 | 6.750 | 4.717 | 0.0480 | yes |  |
| `ahead` | 4 | 7 | 0 | 11 | 6.709 | 14.288 | 2.647 | 5.69e-04 | yes |  |
| `held` | 4 | 10 | 5 | 19 | 6.601 | 7.520 | 2.054 | 0.0318 | yes |  |
| `speak` | 12 | 35 | 57 | 104 | 6.408 | 8.910 | 0.941 | 0.0142 | yes |  |
| `night` | 19 | 20 | 12 | 51 | 6.278 | 17.851 | 1.290 | 6.11e-05 | yes |  |
| `like` | 36 | 43 | 56 | 135 | 6.199 | 10.877 | 0.822 | 0.0045 | yes |  |
| `joshua` | 0 | 10 | 10 | 20 | 5.904 | 10.423 | 1.910 | 0.0059 | yes |  |
| `place's` | 2 | 5 | 0 | 7 | 5.888 | 9.678 | 3.047 | 0.0093 | yes |  |
| `remember` | 0 | 5 | 2 | 7 | 5.888 | 6.792 | 3.047 | 0.0480 | yes |  |
| `bricks` | 1 | 5 | 1 | 7 | 5.888 | 6.235 | 3.047 | 0.0627 |  |  |
| `tooth` | 0 | 5 | 2 | 7 | 5.888 | 6.792 | 3.047 | 0.0480 | yes |  |
| `offense` | 2 | 5 | 0 | 7 | 5.888 | 9.678 | 3.047 | 0.0093 | yes |  |
| `send` | 11 | 12 | 3 | 26 | 5.877 | 17.580 | 1.696 | 7.27e-05 | yes |  |
| `houses` | 2 | 12 | 12 | 26 | 5.877 | 6.806 | 1.696 | 0.0480 | yes |  |
| `afraid` | 10 | 11 | 2 | 23 | 5.866 | 17.917 | 1.789 | 5.91e-05 | yes |  |
| `sheep` | 21 | 25 | 24 | 70 | 5.750 | 11.529 | 1.075 | 0.0031 | yes |  |
| `day's` | 0 | 4 | 1 | 5 | 5.730 | 6.182 | 3.494 | 0.0647 |  |  |
| `balaam's` | 0 | 4 | 1 | 5 | 5.730 | 6.182 | 3.494 | 0.0647 |  |  |
| `foreign` | 1 | 4 | 0 | 5 | 5.730 | 7.625 | 3.494 | 0.0300 | yes |  |
| `taskmasters` | 1 | 4 | 0 | 5 | 5.730 | 7.625 | 3.494 | 0.0300 | yes |  |
| `scroll` | 0 | 4 | 1 | 5 | 5.730 | 6.182 | 3.494 | 0.0647 |  |  |
| `flare` | 1 | 4 | 0 | 5 | 5.730 | 7.625 | 3.494 | 0.0300 | yes |  |
| `dying` | 1 | 4 | 0 | 5 | 5.730 | 7.625 | 3.494 | 0.0300 | yes |  |
| `fight` | 1 | 4 | 0 | 5 | 5.730 | 7.625 | 3.494 | 0.0300 | yes |  |
| `bereaved` | 1 | 4 | 0 | 5 | 5.730 | 7.625 | 3.494 | 0.0300 | yes |  |
| `felt` | 1 | 4 | 0 | 5 | 5.730 | 7.625 | 3.494 | 0.0300 | yes |  |
| `following` | 1 | 4 | 0 | 5 | 5.730 | 7.625 | 3.494 | 0.0300 | yes |  |
| `nation` | 3 | 8 | 4 | 15 | 5.431 | 6.026 | 2.090 | 0.0714 |  |  |
| `haven't` | 8 | 9 | 1 | 18 | 5.313 | 16.394 | 1.910 | 1.52e-04 | yes |  |
| `moab` | 7 | 11 | 6 | 24 | 5.296 | 8.326 | 1.678 | 0.0199 | yes |  |
| `hear` | 2 | 6 | 2 | 10 | 5.152 | 5.845 | 2.440 | 0.0800 |  |  |
| `look` | 3 | 6 | 1 | 10 | 5.152 | 8.043 | 2.440 | 0.0238 | yes |  |
| `known` | 6 | 12 | 10 | 28 | 4.860 | 5.477 | 1.509 | 0.0969 |  |  |
| `staff` | 2 | 12 | 14 | 28 | 4.860 | 6.279 | 1.509 | 0.0610 |  |  |
| `together` | 0 | 7 | 6 | 13 | 4.848 | 7.559 | 2.116 | 0.0310 | yes |  |
| `cry` | 4 | 7 | 2 | 13 | 4.848 | 7.821 | 2.116 | 0.0267 | yes |  |
| `bow` | 5 | 7 | 1 | 13 | 4.848 | 10.873 | 2.116 | 0.0045 | yes |  |
| `seen` | 11 | 11 | 3 | 25 | 4.776 | 16.479 | 1.575 | 1.44e-04 | yes |  |
| `offered` | 2 | 5 | 1 | 8 | 4.635 | 6.122 | 2.562 | 0.0671 |  |  |
| `generation` | 2 | 5 | 1 | 8 | 4.635 | 6.122 | 2.562 | 0.0671 |  |  |
| `about` | 16 | 18 | 15 | 49 | 4.572 | 10.689 | 1.142 | 0.0050 | yes |  |
| `increased` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `abused` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `nor` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `beaten` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `beneath` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `produced` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `fat-fleshed` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `sukkot` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `snow` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `drum` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `feeding` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `medad` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `ear` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `ephrat` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `quota` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `apparel` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `eldad` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `innocence` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `heaps` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `mo-riah` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `belongings` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `piled` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `station` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `oppress` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `theft` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `disgust` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `bad-looking` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `straying` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `tongue` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `prophesied` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `keturah` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `shattered` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `sacrificed` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `abimelek's` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `hanged` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `seized` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `dealt` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `fields` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `distress` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `matters` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `difficulty` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `sickness` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `vein` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `baker` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `goring` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `shower` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `hilltop` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `fiery` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `withhold` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `grace` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `help` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `whomever` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `knees` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `sunset` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `horses` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `phichol` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `fence` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `drawn` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `houseful` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `headrest` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `jokshan` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `flock's` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `empty` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `cushite` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `advise` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `dough` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `injured` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `bribery` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `tens` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `memory` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `hattaavah` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `potiphera` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `stalk` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `beautiful-looking` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `weaned` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `writing` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `testing` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `kibroth` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `longing` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `baskets` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `fifties` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `predominate` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `heed` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `flax` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `dream's` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `dog` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `thin-fleshed` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `dothan` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `tendon` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `adversary` | 0 | 2 | 0 | 2 | 4.500 | 4.500 | 4.231 | 0.1414 |  |  |
| `sword` | 7 | 12 | 10 | 29 | 4.412 | 5.578 | 1.424 | 0.0927 |  |  |
| `snake` | 5 | 6 | 0 | 11 | 4.267 | 13.741 | 2.151 | 7.93e-04 | yes |  |
| `tablets` | 2 | 6 | 3 | 11 | 4.267 | 4.558 | 2.151 | 0.1414 |  |  |
| `signs` | 2 | 6 | 3 | 11 | 4.267 | 4.558 | 2.151 | 0.1414 |  |  |
| `calf` | 2 | 6 | 3 | 11 | 4.267 | 4.558 | 2.151 | 0.1414 |  |  |
| `egypt's` | 6 | 10 | 7 | 23 | 4.208 | 5.796 | 1.547 | 0.0825 |  |  |
| `slaves` | 1 | 4 | 1 | 6 | 4.171 | 4.517 | 2.758 | 0.1414 |  |  |
| `neighbor's` | 0 | 4 | 2 | 6 | 4.171 | 5.075 | 2.758 | 0.1250 |  |  |
| `please` | 2 | 4 | 0 | 6 | 4.171 | 7.960 | 2.758 | 0.0249 | yes |  |
| `aren't` | 2 | 4 | 0 | 6 | 4.171 | 7.960 | 2.758 | 0.0249 | yes |  |
| `numerous` | 0 | 4 | 2 | 6 | 4.171 | 5.075 | 2.758 | 0.1250 |  |  |
| `degradation` | 2 | 4 | 0 | 6 | 4.171 | 7.960 | 2.758 | 0.0249 | yes |  |
| `swore` | 8 | 9 | 3 | 20 | 4.139 | 11.354 | 1.634 | 0.0035 | yes |  |
| `sound` | 4 | 8 | 5 | 17 | 4.106 | 5.025 | 1.749 | 0.1292 |  |  |
| `whom` | 20 | 29 | 43 | 92 | 3.981 | 4.507 | 0.804 | 0.1414 |  |  |
| `leprous` | 0 | 3 | 1 | 4 | 3.845 | 4.297 | 3.132 | 0.1585 |  |  |
| `rest` | 1 | 3 | 0 | 4 | 3.845 | 5.740 | 3.132 | 0.0846 |  |  |
| `bank` | 1 | 3 | 0 | 4 | 3.845 | 5.740 | 3.132 | 0.0846 |  |  |
| `answer` | 1 | 3 | 0 | 4 | 3.845 | 5.740 | 3.132 | 0.0846 |  |  |
| `letting` | 1 | 3 | 0 | 4 | 3.845 | 5.740 | 3.132 | 0.0846 |  |  |
| `bones` | 1 | 3 | 0 | 4 | 3.845 | 5.740 | 3.132 | 0.0846 |  |  |
| `sow` | 0 | 3 | 1 | 4 | 3.845 | 4.297 | 3.132 | 0.1585 |  |  |
| `met` | 1 | 3 | 0 | 4 | 3.845 | 5.740 | 3.132 | 0.0846 |  |  |
| `oak` | 1 | 3 | 0 | 4 | 3.845 | 5.740 | 3.132 | 0.0846 |  |  |
| `driven` | 0 | 3 | 1 | 4 | 3.845 | 4.297 | 3.132 | 0.1585 |  |  |
| `crossed` | 1 | 3 | 0 | 4 | 3.845 | 5.740 | 3.132 | 0.0846 |  |  |
| `stoned` | 1 | 3 | 0 | 4 | 3.845 | 5.740 | 3.132 | 0.0846 |  |  |
| `growing` | 0 | 3 | 1 | 4 | 3.845 | 4.297 | 3.132 | 0.1585 |  |  |
| `such` | 1 | 3 | 0 | 4 | 3.845 | 5.740 | 3.132 | 0.0846 |  |  |
| `thought` | 1 | 3 | 0 | 4 | 3.845 | 5.740 | 3.132 | 0.0846 |  |  |
| `kill` | 13 | 13 | 8 | 34 | 3.770 | 11.883 | 1.238 | 0.0025 | yes |  |
| `strong` | 9 | 10 | 5 | 24 | 3.749 | 9.897 | 1.444 | 0.0081 | yes |  |
| `they've` | 4 | 5 | 0 | 9 | 3.692 | 11.271 | 2.199 | 0.0037 | yes |  |
| `items` | 0 | 5 | 4 | 9 | 3.692 | 5.499 | 2.199 | 0.0955 |  |  |
| `thin` | 0 | 5 | 4 | 9 | 3.692 | 5.499 | 2.199 | 0.0955 |  |  |
| `one's` | 4 | 5 | 0 | 9 | 3.692 | 11.271 | 2.199 | 0.0037 | yes |  |
| `built` | 8 | 9 | 4 | 21 | 3.645 | 9.591 | 1.514 | 0.0099 | yes |  |
| `threw` | 2 | 6 | 4 | 12 | 3.542 | 3.630 | 1.910 | 0.2230 |  |  |
| `matter` | 1 | 6 | 5 | 12 | 3.542 | 3.796 | 1.910 | 0.2008 |  |  |
| `beth-el` | 5 | 6 | 1 | 12 | 3.542 | 9.568 | 1.910 | 0.0099 | yes |  |
| `everything` | 12 | 24 | 39 | 75 | 3.535 | 3.752 | 0.838 | 0.2067 |  |  |
| `festival` | 5 | 7 | 3 | 15 | 3.521 | 6.715 | 1.729 | 0.0480 | yes |  |
| `big` | 15 | 15 | 13 | 43 | 3.162 | 9.561 | 1.031 | 0.0100 | yes |  |
| `drove` | 2 | 4 | 1 | 7 | 3.124 | 4.611 | 2.272 | 0.1414 |  |  |
| `sitting` | 2 | 4 | 1 | 7 | 3.124 | 4.611 | 2.272 | 0.1414 |  |  |
| `offspring` | 1 | 4 | 2 | 7 | 3.124 | 3.168 | 2.272 | 0.2834 |  |  |
| `refused` | 3 | 4 | 0 | 7 | 3.124 | 8.809 | 2.272 | 0.0152 | yes |  |
| `seeing` | 2 | 4 | 1 | 7 | 3.124 | 4.611 | 2.272 | 0.1414 |  |  |
| `ephraim's` | 0 | 4 | 3 | 7 | 3.124 | 4.480 | 2.272 | 0.1414 |  |  |
| `altars` | 1 | 4 | 2 | 7 | 3.124 | 3.168 | 2.272 | 0.2834 |  |  |
| `streaked` | 3 | 4 | 0 | 7 | 3.124 | 8.809 | 2.272 | 0.0152 | yes |  |
| `hasn't` | 2 | 4 | 1 | 7 | 3.124 | 4.611 | 2.272 | 0.1414 |  |  |
| `bulls` | 0 | 4 | 3 | 7 | 3.124 | 4.480 | 2.272 | 0.1414 |  |  |
| `gone` | 4 | 8 | 7 | 19 | 3.088 | 3.428 | 1.474 | 0.2519 |  |  |
| `strike` | 10 | 10 | 6 | 26 | 2.955 | 9.342 | 1.258 | 0.0112 | yes |  |
| `forever` | 3 | 5 | 2 | 10 | 2.952 | 4.685 | 1.910 | 0.1414 |  |  |
| `leavened` | 1 | 5 | 4 | 10 | 2.952 | 3.045 | 1.910 | 0.3042 |  |  |
| `since` | 5 | 5 | 0 | 10 | 2.952 | 12.425 | 1.910 | 0.0018 | yes |  |
| `cup` | 5 | 5 | 0 | 10 | 2.952 | 12.425 | 1.910 | 0.0018 | yes |  |
| `kissed` | 5 | 5 | 0 | 10 | 2.952 | 12.425 | 1.910 | 0.0018 | yes |  |
| `sell` | 2 | 5 | 3 | 10 | 2.952 | 3.242 | 1.910 | 0.2834 |  |  |
| `slave` | 1 | 5 | 4 | 10 | 2.952 | 3.045 | 1.910 | 0.3042 |  |  |
| `child` | 3 | 5 | 2 | 10 | 2.952 | 4.685 | 1.910 | 0.1414 |  |  |
| `hivite` | 4 | 5 | 1 | 10 | 2.952 | 7.373 | 1.910 | 0.0348 | yes |  |
| `edge` | 3 | 6 | 4 | 13 | 2.938 | 3.534 | 1.703 | 0.2375 |  |  |
| `behind` | 5 | 6 | 2 | 13 | 2.938 | 7.274 | 1.703 | 0.0371 | yes |  |
| `listen` | 8 | 15 | 21 | 44 | 2.893 | 2.898 | 0.981 | 0.3223 |  |  |
| `more` | 12 | 13 | 12 | 37 | 2.816 | 6.975 | 1.050 | 0.0441 | yes |  |
| `should` | 5 | 9 | 9 | 23 | 2.806 | 3.183 | 1.300 | 0.2834 |  |  |
| `fleeing` | 2 | 3 | 0 | 5 | 2.576 | 6.365 | 2.395 | 0.0586 |  |  |
| `epidemic` | 1 | 3 | 1 | 5 | 2.576 | 2.922 | 2.395 | 0.3223 |  |  |
| `weak` | 1 | 3 | 1 | 5 | 2.576 | 2.922 | 2.395 | 0.3223 |  |  |
| `alone` | 1 | 3 | 1 | 5 | 2.576 | 2.922 | 2.395 | 0.3223 |  |  |
| `what's` | 1 | 3 | 1 | 5 | 2.576 | 2.922 | 2.395 | 0.3223 |  |  |
| `garments` | 2 | 3 | 0 | 5 | 2.576 | 6.365 | 2.395 | 0.0586 |  |  |
| `provide` | 2 | 3 | 0 | 5 | 2.576 | 6.365 | 2.395 | 0.0586 |  |  |
| `nothing` | 2 | 3 | 0 | 5 | 2.576 | 6.365 | 2.395 | 0.0586 |  |  |
| `woke` | 2 | 3 | 0 | 5 | 2.576 | 6.365 | 2.395 | 0.0586 |  |  |
| `feed` | 2 | 3 | 0 | 5 | 2.576 | 6.365 | 2.395 | 0.0586 |  |  |
| `feared` | 2 | 3 | 0 | 5 | 2.576 | 6.365 | 2.395 | 0.0586 |  |  |
| `innocent` | 2 | 3 | 0 | 5 | 2.576 | 6.365 | 2.395 | 0.0586 |  |  |
| `wipe` | 2 | 3 | 0 | 5 | 2.576 | 6.365 | 2.395 | 0.0586 |  |  |
| `young` | 2 | 3 | 0 | 5 | 2.576 | 6.365 | 2.395 | 0.0586 |  |  |
| `nose` | 2 | 3 | 0 | 5 | 2.576 | 6.365 | 2.395 | 0.0586 |  |  |
| `three` | 16 | 23 | 37 | 76 | 2.574 | 2.780 | 0.723 | 0.3223 |  |  |
| `that's` | 4 | 7 | 6 | 17 | 2.538 | 3.119 | 1.424 | 0.2906 |  |  |
| `word` | 7 | 14 | 21 | 42 | 2.464 | 2.502 | 0.935 | 0.3223 |  |  |
| `man's` | 3 | 6 | 5 | 14 | 2.430 | 2.738 | 1.523 | 0.3223 |  |  |
| `gathered` | 6 | 12 | 17 | 35 | 2.367 | 2.372 | 0.999 | 0.3223 |  |  |
| `ask` | 3 | 4 | 1 | 8 | 2.362 | 5.252 | 1.909 | 0.1123 |  |  |
| `jebusite` | 4 | 4 | 0 | 8 | 2.362 | 9.940 | 1.909 | 0.0079 | yes |  |
| `fish` | 0 | 4 | 4 | 8 | 2.362 | 4.169 | 1.909 | 0.1717 |  |  |
| `hebrew` | 4 | 4 | 0 | 8 | 2.362 | 9.940 | 1.909 | 0.0079 | yes |  |
| `case` | 5 | 5 | 1 | 11 | 2.358 | 8.383 | 1.669 | 0.0191 | yes |  |
| `chief` | 13 | 16 | 21 | 50 | 2.356 | 3.849 | 0.846 | 0.1938 |  |  |
| `treachery` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `communicate` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `delaying` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `thirst` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `read` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `spelt` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `flashes` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `despise` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `second-in-command` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `started` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `adversaries` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `appease` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `direction` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `humble` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `opponent` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `stairs` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `visions` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `songs` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `structure` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `longed` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `person's` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `dismal` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `nimbus` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `massah` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `espouse` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `olam` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `enigmas` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `conform` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `exhaustion` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `stacked` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `merchants` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `onions` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `descended` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `hornet` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `camel's` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `posterity` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `dances` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `lingered` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `odor` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `surroundings` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `grumblers` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `doorpost` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `saddle` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `reminder` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `penalized` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `mute` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `sapphire` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `perform` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `ashurim` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `goods` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `homers` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `relent` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `wheel` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `bad-figured` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `thrust` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `original` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `healer` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `medanites` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `divinations` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `laughter` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `highest` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `lick` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `shepherded` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `testified` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `garlics` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `recalling` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `opponents` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `sustained` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `work-companies` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `safe` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `crops` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `harvests` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `father-in-law's` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `graze` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `late` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `blaspheme` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `happiness` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `prophesying` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `blazed` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `outer` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `shuah` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `might` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `heal` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `weeping` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `medan` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `bold` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `pethor` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `looks` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `clusters` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `pierce` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `foreigners` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `graves` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `leummim` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `undermine` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `precipitous` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `supported` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `forgot` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `ladder` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `creamy` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `distinction` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `survived` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `nile's` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `greeting` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `armed` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `tore` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `vineyards` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `prophets` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `pathway` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `latter` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `dissuaded` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `gal` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `teeth` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `zaphenathpaneah` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `lend` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `olives` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `reaching` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `divested` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `means` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `cleanness` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `regularly` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `beast` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `humbled` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `emptying` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `behalf` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `revealed` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `well-being` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `orphan` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `judged` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `hit` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `widows` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `forgotten` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `thirsted` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `relented` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `tells` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `chain` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `criticized` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `unrecognizable` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `hired` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `tones` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `miss` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `foods` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `moment` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `change` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `ford` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `humiliated` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `angered` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `snakes` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `implored` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `oh` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `dreaming` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `rise` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `prodding` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `prestigious` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `responded` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `five-out` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `toyed` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `itself` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `shepherding` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `huzoth` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `ridden` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `essence` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `puah` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `interpreter` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `victory` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `neither` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `enlighten` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `coffin` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `rameses` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `meets` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `absence` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `founding` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `shrubs` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `rushed` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `zophim` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `protect` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `prophetess` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `plotted` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `full-fledged` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `memorial` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `jeshimon` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `commandment` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `deborah` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `witch` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `grazed` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `pithom` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `dancing` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `permit` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `plot` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `awe` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `stubble` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `obliterated` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `master's` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `virgins` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `mahanaim` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `moab's` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `toy` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `asks` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `wrung` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `chewed` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `loss` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `riding` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `orphans` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `creditor` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `gal-ed` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `stylus` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `stewardship` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `tamarisk` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `strayed` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `stick` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `oppression` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `foolish` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `heaviness` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `taberah` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `pisgah` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `viewpoint` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `shouting` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `forget` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `bribe` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `believed` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `obliterate` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `section` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `fistfuls` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `recurrence` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `bowman` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `eldaah` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `assigned` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `graced` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `joshua's` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `hardened` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `rephidim` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `midian's` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `betrayal` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `flashing` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `defeat` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `weigh` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `offend` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `hates` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `melons` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `spawn` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `blooming` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `bottom` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `commemorate` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `buying` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `conciliated` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `bud` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `storage` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `subsided` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `clarity` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `compensate` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `shackled` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `sea's` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `beautiful-figured` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `drums` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `indigent` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `bethlehem` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `expect` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `commanders` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `hungered` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `smoking` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `eagles` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `mills` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `suckling` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `afterwards` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `ben-oni` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `pace` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `shdta` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `hire` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `hygiene` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `thunder` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `yards` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `conspired` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `fearful` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `accustomed` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `lets` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `pounded` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `transported` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `bundle` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `vindicate` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `telling` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `ice` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `falls` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `soul's` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `devastated` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `envision` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `revulsion` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `quails` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `birthday` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `requirement` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `blaze` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `bow-shot` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `terrified` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `qesita` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `justified` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `lighter` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `firstborn's` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `knock` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `evidence` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `cleft` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `denigration` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `meanings` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `stashed` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `showing` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `overseers` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `foolishly` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `fallow` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `awl` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `sacks` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `hurrying` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `implicate` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `licks` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `asking` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `jether` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `forceful` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `blossom` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `dig` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `bunch` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `join` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `letushim` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `previous` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `standard` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `abida` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `mill` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `showered` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `zimran` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `showering` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `steals` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `leek` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `lent` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `helping` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `malevolent` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `envisioned` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `hitting` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `ox's` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `sick` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `scrawny-fleshed` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `defeated` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `seize` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `weary` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `perhaps` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `cucumbers` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `pilgrimages` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `rebel` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `pull` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `shiphrah` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `narrow` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `epher` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `deceive` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `rejoiced` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `betrothed` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `bundles` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `commemorated` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `yh's` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `bitten` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `ygar` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `ishbak` | 0 | 1 | 0 | 1 | 2.250 | 2.250 | 3.494 | 0.3223 |  |  |
| `turn` | 8 | 11 | 13 | 32 | 2.192 | 3.091 | 1.007 | 0.2959 |  |  |
| `them` | 143 | 188 | 467 | 798 | 2.165 | 4.907 | 0.215 | 0.1372 |  |  |
| `firstborn` | 15 | 19 | 29 | 63 | 2.087 | 2.883 | 0.719 | 0.3223 |  |  |
| `field` | 24 | 26 | 41 | 91 | 2.086 | 4.333 | 0.604 | 0.1554 |  |  |
| `manasseh's` | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| `seashore` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `asenath` | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| `doorposts` | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| `hurt` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `house's` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `bit` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `vision` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `males` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `treat` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `she-goats` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `brick` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `provisions` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `dedan` | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| `taste` | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| `wound` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `heart's` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `labor` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `midwife` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `slave's` | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| `pillars` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `sleep` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `pole` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `nursing` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `prophet` | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| `bride-price` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `further` | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| `lintel` | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| `watchful` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `without` | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| `lies` | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| `delay` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `trap` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `vine` | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| `worthy` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `lead` | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| `start` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `fed` | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| `state` | 0 | 2 | 1 | 3 | 2.085 | 2.537 | 2.646 | 0.3223 |  |  |
| `embraced` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `stop` | 1 | 2 | 0 | 3 | 2.085 | 3.980 | 2.646 | 0.1796 |  |  |
| `at` | 78 | 79 | 159 | 316 | 2.079 | 5.098 | 0.331 | 0.1235 |  |  |
| `into` | 17 | 22 | 36 | 75 | 2.070 | 2.574 | 0.660 | 0.3223 |  |  |
| `finish` | 1 | 6 | 8 | 15 | 2.000 | 2.980 | 1.362 | 0.3163 |  |  |
| `show` | 3 | 6 | 6 | 15 | 2.000 | 2.131 | 1.362 | 0.3444 |  |  |
| `morning` | 12 | 20 | 36 | 68 | 1.912 | 1.976 | 0.667 | 0.3776 |  |  |
| `vegetation` | 2 | 5 | 5 | 12 | 1.875 | 1.882 | 1.462 | 0.4021 |  |  |
| `do` | 48 | 65 | 145 | 258 | 1.863 | 2.157 | 0.347 | 0.3389 |  |  |
| `sinned` | 3 | 7 | 9 | 19 | 1.796 | 1.812 | 1.173 | 0.4202 |  |  |
| `doing` | 4 | 7 | 8 | 19 | 1.796 | 1.970 | 1.173 | 0.3788 |  |  |
| `lift` | 1 | 4 | 4 | 9 | 1.782 | 1.875 | 1.620 | 0.4038 |  |  |
| `el` | 0 | 4 | 5 | 9 | 1.782 | 4.042 | 1.620 | 0.1796 |  |  |
| `pressed` | 2 | 4 | 3 | 9 | 1.782 | 2.073 | 1.620 | 0.3573 |  |  |
| `rock` | 0 | 4 | 5 | 9 | 1.782 | 4.042 | 1.620 | 0.1796 |  |  |
| `placed` | 4 | 4 | 1 | 9 | 1.782 | 6.203 | 1.620 | 0.0639 |  |  |
| `degrade` | 0 | 4 | 5 | 9 | 1.782 | 4.042 | 1.620 | 0.1796 |  |  |
| `getting` | 3 | 3 | 0 | 6 | 1.771 | 7.455 | 1.909 | 0.0330 | yes |  |
| `regard` | 0 | 3 | 3 | 6 | 1.771 | 3.127 | 1.909 | 0.2897 |  |  |
| `tested` | 3 | 3 | 0 | 6 | 1.771 | 7.455 | 1.909 | 0.0330 | yes |  |
| `required` | 0 | 3 | 3 | 6 | 1.771 | 3.127 | 1.909 | 0.2897 |  |  |
| `horn` | 1 | 3 | 2 | 6 | 1.771 | 1.815 | 1.909 | 0.4201 |  |  |
| `instruct` | 0 | 3 | 3 | 6 | 1.771 | 3.127 | 1.909 | 0.2897 |  |  |
| `burdens` | 1 | 3 | 2 | 6 | 1.771 | 1.815 | 1.909 | 0.4201 |  |  |
| `camped` | 1 | 3 | 2 | 6 | 1.771 | 1.815 | 1.909 | 0.4201 |  |  |
| `strength` | 3 | 3 | 0 | 6 | 1.771 | 7.455 | 1.909 | 0.0330 | yes |  |
| `sand` | 2 | 3 | 1 | 6 | 1.771 | 3.258 | 1.909 | 0.2822 |  |  |
| `camp` | 8 | 27 | 63 | 98 | 1.696 | 9.260 | 0.531 | 0.0118 | yes |  |
| `yours` | 1 | 8 | 14 | 23 | 1.668 | 4.589 | 1.043 | 0.1414 |  |  |
| `top` | 5 | 6 | 5 | 16 | 1.633 | 3.367 | 1.218 | 0.2622 |  |  |
| `foot` | 3 | 6 | 7 | 16 | 1.633 | 1.668 | 1.218 | 0.4455 |  |  |
| `enemies` | 2 | 7 | 11 | 20 | 1.494 | 2.203 | 1.062 | 0.3294 |  |  |
| `can` | 3 | 5 | 5 | 13 | 1.477 | 1.786 | 1.281 | 0.4260 |  |  |
| `gather` | 2 | 5 | 6 | 13 | 1.477 | 1.488 | 1.281 | 0.4719 |  |  |
| `cross` | 0 | 5 | 8 | 13 | 1.477 | 5.093 | 1.281 | 0.1238 |  |  |
| `spoken` | 6 | 12 | 21 | 39 | 1.463 | 1.688 | 0.772 | 0.4455 |  |  |
| `spirit` | 4 | 8 | 12 | 24 | 1.408 | 1.429 | 0.953 | 0.4910 |  |  |
| `other` | 5 | 8 | 11 | 24 | 1.408 | 1.516 | 0.953 | 0.4642 |  |  |
| `from` | 215 | 227 | 552 | 994 | 1.390 | 1.752 | 0.156 | 0.4360 |  |  |
| `flowing` | 4 | 4 | 2 | 10 | 1.333 | 4.306 | 1.379 | 0.1579 |  |  |
| `moved` | 2 | 4 | 4 | 10 | 1.333 | 1.420 | 1.379 | 0.4938 |  |  |
| `throw` | 2 | 4 | 4 | 10 | 1.333 | 1.420 | 1.379 | 0.4938 |  |  |
| `womb` | 5 | 6 | 6 | 17 | 1.322 | 2.572 | 1.086 | 0.3223 |  |  |
| `wilderness` | 9 | 19 | 40 | 68 | 1.317 | 2.731 | 0.566 | 0.3223 |  |  |
| `oxen` | 10 | 12 | 18 | 40 | 1.281 | 2.035 | 0.721 | 0.3645 |  |  |
| `traveled` | 7 | 7 | 7 | 21 | 1.232 | 3.658 | 0.958 | 0.2189 |  |  |
| `manna` | 1 | 3 | 3 | 7 | 1.215 | 1.220 | 1.547 | 0.5610 |  |  |
| `collect` | 0 | 3 | 4 | 7 | 1.215 | 3.023 | 1.547 | 0.3074 |  |  |
| `wicked` | 3 | 3 | 1 | 7 | 1.215 | 4.106 | 1.547 | 0.1784 |  |  |
| `journey` | 2 | 3 | 2 | 7 | 1.215 | 1.908 | 1.547 | 0.3951 |  |  |
| `hur` | 0 | 3 | 4 | 7 | 1.215 | 3.023 | 1.547 | 0.3074 |  |  |
| `loose` | 0 | 3 | 4 | 7 | 1.215 | 3.023 | 1.547 | 0.3074 |  |  |
| `stars` | 3 | 3 | 1 | 7 | 1.215 | 4.106 | 1.547 | 0.1784 |  |  |
| `love` | 2 | 3 | 2 | 7 | 1.215 | 1.908 | 1.547 | 0.3951 |  |  |
| `quarrel` | 3 | 3 | 1 | 7 | 1.215 | 4.106 | 1.547 | 0.1784 |  |  |
| `angels` | 2 | 2 | 0 | 4 | 1.181 | 4.970 | 1.909 | 0.1316 |  |  |
| `bound` | 2 | 2 | 0 | 4 | 1.181 | 4.970 | 1.909 | 0.1316 |  |  |
| `avenged` | 2 | 2 | 0 | 4 | 1.181 | 4.970 | 1.909 | 0.1316 |  |  |
| `steal` | 1 | 2 | 1 | 4 | 1.181 | 1.527 | 1.909 | 0.4616 |  |  |
| `households` | 1 | 2 | 1 | 4 | 1.181 | 1.527 | 1.909 | 0.4616 |  |  |
| `heat` | 2 | 2 | 0 | 4 | 1.181 | 4.970 | 1.909 | 0.1316 |  |  |
| `grave` | 0 | 2 | 2 | 4 | 1.181 | 2.085 | 1.909 | 0.3545 |  |  |
| `abib` | 2 | 2 | 0 | 4 | 1.181 | 4.970 | 1.909 | 0.1316 |  |  |
| `barley` | 0 | 2 | 2 | 4 | 1.181 | 2.085 | 1.909 | 0.3545 |  |  |
| `terror` | 1 | 2 | 1 | 4 | 1.181 | 1.527 | 1.909 | 0.4616 |  |  |
| `sack` | 1 | 2 | 1 | 4 | 1.181 | 1.527 | 1.909 | 0.4616 |  |  |
| `hadn't` | 2 | 2 | 0 | 4 | 1.181 | 4.970 | 1.909 | 0.1316 |  |  |
| `swallowed` | 1 | 2 | 1 | 4 | 1.181 | 1.527 | 1.909 | 0.4616 |  |  |
| `commander` | 2 | 2 | 0 | 4 | 1.181 | 4.970 | 1.909 | 0.1316 |  |  |
| `tonight` | 2 | 2 | 0 | 4 | 1.181 | 4.970 | 1.909 | 0.1316 |  |  |
| `wealth` | 1 | 2 | 1 | 4 | 1.181 | 1.527 | 1.909 | 0.4616 |  |  |
| `reeds` | 2 | 2 | 0 | 4 | 1.181 | 4.970 | 1.909 | 0.1316 |  |  |
| `rachel's` | 0 | 2 | 2 | 4 | 1.181 | 2.085 | 1.909 | 0.3545 |  |  |
| `causing` | 0 | 2 | 2 | 4 | 1.181 | 2.085 | 1.909 | 0.3545 |  |  |
| `crying` | 2 | 2 | 0 | 4 | 1.181 | 4.970 | 1.909 | 0.1316 |  |  |
| `resided` | 0 | 2 | 2 | 4 | 1.181 | 2.085 | 1.909 | 0.3545 |  |  |
| `striking` | 1 | 2 | 1 | 4 | 1.181 | 1.527 | 1.909 | 0.4616 |  |  |
| `rested` | 1 | 2 | 1 | 4 | 1.181 | 1.527 | 1.909 | 0.4616 |  |  |
| `flaring` | 1 | 2 | 1 | 4 | 1.181 | 1.527 | 1.909 | 0.4616 |  |  |
| `speaks` | 1 | 2 | 1 | 4 | 1.181 | 1.527 | 1.909 | 0.4616 |  |  |
| `in` | 346 | 397 | 1040 | 1783 | 1.177 | 3.098 | 0.109 | 0.2946 |  |  |
| `sign` | 1 | 5 | 8 | 14 | 1.150 | 2.131 | 1.121 | 0.3444 |  |  |
| `times` | 5 | 12 | 24 | 41 | 1.115 | 2.202 | 0.671 | 0.3296 |  |  |
| `next` | 1 | 6 | 11 | 18 | 1.056 | 2.956 | 0.966 | 0.3210 |  |  |
| `were` | 75 | 86 | 204 | 365 | 0.992 | 0.992 | 0.218 | 0.5969 |  |  |
| `hagar` | 3 | 4 | 4 | 11 | 0.981 | 1.576 | 1.172 | 0.4480 |  |  |
| `money` | 1 | 8 | 17 | 26 | 0.975 | 4.981 | 0.788 | 0.1316 |  |  |
| `away` | 11 | 11 | 16 | 38 | 0.957 | 2.701 | 0.652 | 0.3223 |  |  |
| `been` | 12 | 16 | 31 | 59 | 0.894 | 0.910 | 0.511 | 0.5969 |  |  |
| `sacrifices` | 2 | 5 | 8 | 15 | 0.880 | 1.066 | 0.977 | 0.5969 |  |  |
| `darkness` | 1 | 3 | 4 | 8 | 0.817 | 0.909 | 1.257 | 0.5969 |  |  |
| `mountains` | 3 | 3 | 2 | 8 | 0.817 | 2.550 | 1.257 | 0.3223 |  |  |
| `reached` | 1 | 3 | 4 | 8 | 0.817 | 0.909 | 1.257 | 0.5969 |  |  |
| `shoulder` | 2 | 3 | 3 | 8 | 0.817 | 1.107 | 1.257 | 0.5969 |  |  |
| `belong` | 2 | 3 | 3 | 8 | 0.817 | 1.107 | 1.257 | 0.5969 |  |  |
| `wise` | 0 | 4 | 8 | 12 | 0.704 | 4.319 | 0.992 | 0.1566 |  |  |
| `paran` | 0 | 2 | 3 | 5 | 0.667 | 2.022 | 1.424 | 0.3666 |  |  |
| `raise` | 1 | 2 | 2 | 5 | 0.667 | 0.710 | 1.424 | 0.6285 |  |  |
| `gracious` | 2 | 2 | 1 | 5 | 0.667 | 2.153 | 1.424 | 0.3398 |  |  |
| `aramean` | 0 | 2 | 3 | 5 | 0.667 | 2.022 | 1.424 | 0.3666 |  |  |
| `mass` | 1 | 2 | 2 | 5 | 0.667 | 0.710 | 1.424 | 0.6285 |  |  |
| `setting` | 0 | 2 | 3 | 5 | 0.667 | 2.022 | 1.424 | 0.3666 |  |  |
| `move` | 0 | 2 | 3 | 5 | 0.667 | 2.022 | 1.424 | 0.3666 |  |  |
| `instructions` | 1 | 2 | 2 | 5 | 0.667 | 0.710 | 1.424 | 0.6285 |  |  |
| `molten` | 1 | 2 | 2 | 5 | 0.667 | 0.710 | 1.424 | 0.6285 |  |  |
| `short` | 1 | 2 | 2 | 5 | 0.667 | 0.710 | 1.424 | 0.6285 |  |  |
| `corrupted` | 0 | 2 | 3 | 5 | 0.667 | 2.022 | 1.424 | 0.3666 |  |  |
| `caught` | 1 | 2 | 2 | 5 | 0.667 | 0.710 | 1.424 | 0.6285 |  |  |
| `blind` | 0 | 2 | 3 | 5 | 0.667 | 2.022 | 1.424 | 0.3666 |  |  |
| `kingdom` | 1 | 2 | 2 | 5 | 0.667 | 0.710 | 1.424 | 0.6285 |  |  |
| `build` | 1 | 2 | 2 | 5 | 0.667 | 0.710 | 1.424 | 0.6285 |  |  |
| `leah's` | 2 | 2 | 1 | 5 | 0.667 | 2.153 | 1.424 | 0.3398 |  |  |
| `wherever` | 1 | 2 | 2 | 5 | 0.667 | 0.710 | 1.424 | 0.6285 |  |  |
| `manner` | 0 | 2 | 3 | 5 | 0.667 | 2.022 | 1.424 | 0.3666 |  |  |
| `hard` | 1 | 2 | 2 | 5 | 0.667 | 0.710 | 1.424 | 0.6285 |  |  |
| `most` | 0 | 2 | 3 | 5 | 0.667 | 2.022 | 1.424 | 0.3666 |  |  |
| `hittite` | 3 | 5 | 8 | 16 | 0.658 | 0.659 | 0.845 | 0.6501 |  |  |
| `war` | 1 | 5 | 10 | 16 | 0.658 | 2.238 | 0.845 | 0.3223 |  |  |
| `women` | 3 | 5 | 8 | 16 | 0.658 | 0.659 | 0.845 | 0.6501 |  |  |
| `stone` | 6 | 8 | 14 | 28 | 0.642 | 0.711 | 0.639 | 0.6285 |  |  |
| `roam` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `faithful` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `alongside` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `bdellium` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `sets` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `attended` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `nahor's` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `deliver` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `false` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `invoke` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `holding` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `herds` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `blew` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `gershom` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `test` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `official` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `implements` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `sinning` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `shear` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `he-asses` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `killing` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `risen` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `sang` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `halt` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `slept` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `scheme` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `shatter` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `divination` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `falsely` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `conveyed` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `coriander` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `dark` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `face-to-face` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `destroyer` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `fulfill` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `containers` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `remains` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `searched` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `suddenly` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `enemy` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `deaf` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `quail` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `testify` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `save` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `lyre` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `kiss` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `walked` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `man-asseh` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `perished` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `pointed` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `sagging` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `restrain` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `staying` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `picked` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `spit` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `awesome` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `second's` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `thorns` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `jabbok` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `stink` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `shaved` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `embalmed` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `potiphar` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `conceive` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `ass's` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `daytime` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `elevating` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `fooling` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `myself` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `wrapped` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `deposit` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `refreshed` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `descend` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `deal` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `odious` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `prisoner` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `heavens` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `alien's` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `truth` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `designate` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `amorite's` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `booths` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `kneel` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `fruits` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `worn` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `served` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `seeking` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `happy` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `pot` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `eliezer` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `increase` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `enemy's` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `treasure` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `passing` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `tumult` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `honored` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `hide` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `tenting` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `hardship` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `inscribed` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `mixture` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `fourteen` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `future` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `pulled` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `choose` | 0 | 1 | 1 | 2 | 0.590 | 1.042 | 1.909 | 0.5969 |  |  |
| `plagues` | 1 | 1 | 0 | 2 | 0.590 | 2.485 | 1.909 | 0.3223 |  |  |
| `thing` | 25 | 31 | 72 | 128 | 0.548 | 0.593 | 0.280 | 0.6796 |  |  |
| `free` | 3 | 3 | 3 | 9 | 0.528 | 1.568 | 1.016 | 0.4504 |  |  |
| `strikes` | 0 | 3 | 6 | 9 | 0.528 | 3.240 | 1.016 | 0.2834 |  |  |
| `reach` | 0 | 3 | 6 | 9 | 0.528 | 3.240 | 1.016 | 0.2834 |  |  |
| `herd` | 1 | 3 | 5 | 9 | 0.528 | 0.782 | 1.016 | 0.6009 |  |  |
| `food` | 8 | 8 | 13 | 29 | 0.507 | 1.407 | 0.571 | 0.4983 |  |  |
| `bread` | 17 | 24 | 57 | 98 | 0.492 | 0.924 | 0.305 | 0.5969 |  |  |
| `order` | 3 | 4 | 6 | 13 | 0.488 | 0.619 | 0.831 | 0.6682 |  |  |
| `own` | 4 | 4 | 5 | 13 | 0.488 | 1.406 | 0.831 | 0.4983 |  |  |
| `fear` | 4 | 6 | 11 | 21 | 0.481 | 0.482 | 0.656 | 0.7300 |  |  |
| `between` | 12 | 18 | 43 | 73 | 0.402 | 0.945 | 0.325 | 0.5969 |  |  |
| `consumed` | 1 | 2 | 3 | 6 | 0.352 | 0.357 | 1.061 | 0.7931 |  |  |
| `greater` | 2 | 2 | 2 | 6 | 0.352 | 1.045 | 1.061 | 0.5969 |  |  |
| `baked` | 1 | 2 | 3 | 6 | 0.352 | 0.357 | 1.061 | 0.7931 |  |  |
| `understanding` | 1 | 2 | 3 | 6 | 0.352 | 0.357 | 1.061 | 0.7931 |  |  |
| `hundreds` | 0 | 2 | 4 | 6 | 0.352 | 2.160 | 1.061 | 0.3385 |  |  |
| `collected` | 0 | 2 | 4 | 6 | 0.352 | 2.160 | 1.061 | 0.3385 |  |  |
| `quarreled` | 2 | 2 | 2 | 6 | 0.352 | 1.045 | 1.061 | 0.5969 |  |  |
| `healed` | 0 | 2 | 4 | 6 | 0.352 | 2.160 | 1.061 | 0.3385 |  |  |
| `onto` | 1 | 2 | 3 | 6 | 0.352 | 0.357 | 1.061 | 0.7931 |  |  |
| `poor` | 0 | 2 | 4 | 6 | 0.352 | 2.160 | 1.061 | 0.3385 |  |  |
| `sold` | 5 | 6 | 11 | 22 | 0.350 | 0.458 | 0.565 | 0.7415 |  |  |
| `gate` | 5 | 6 | 11 | 22 | 0.350 | 0.458 | 0.565 | 0.7415 |  |  |
| `sit` | 1 | 3 | 6 | 10 | 0.320 | 0.785 | 0.810 | 0.6000 |  |  |
| `cloud` | 9 | 9 | 18 | 36 | 0.237 | 0.630 | 0.376 | 0.6633 |  |  |
| `torn` | 3 | 4 | 8 | 15 | 0.196 | 0.196 | 0.556 | 0.8809 |  |  |
| `flee` | 4 | 4 | 7 | 15 | 0.196 | 0.536 | 0.556 | 0.7067 |  |  |
| `just` | 5 | 7 | 16 | 28 | 0.184 | 0.259 | 0.390 | 0.8445 |  |  |
| `quickly` | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| `levite` | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| `luz` | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| `plants` | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| `better` | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| `either` | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| `fulfillment` | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| `interest` | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| `kiriath` | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| `last` | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| `cooked` | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| `spreading` | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| `write` | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| `simeon's` | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| `curses` | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| `pursue` | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| `mortar` | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| `inherit` | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| `disgusted` | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| `counting` | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| `putting` | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| `least` | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| `sheba` | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| `breaking` | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| `devastation` | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| `hang` | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| `wheat` | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| `depart` | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| `walk` | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| `lost` | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| `beor` | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| `serving` | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| `uncovered` | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| `halted` | 0 | 1 | 2 | 3 | 0.176 | 1.080 | 1.172 | 0.5969 |  |  |
| `wrote` | 1 | 1 | 1 | 3 | 0.176 | 0.523 | 1.172 | 0.7105 |  |  |
| `carried` | 3 | 3 | 5 | 11 | 0.175 | 0.483 | 0.629 | 0.7295 |  |  |
| `bought` | 1 | 3 | 7 | 11 | 0.175 | 0.884 | 0.629 | 0.5969 |  |  |
| `anymore` | 2 | 3 | 6 | 11 | 0.175 | 0.186 | 0.629 | 0.8865 |  |  |
| `hold` | 2 | 3 | 6 | 11 | 0.175 | 0.186 | 0.629 | 0.8865 |  |  |
| `small` | 3 | 3 | 5 | 11 | 0.175 | 0.483 | 0.629 | 0.7295 |  |  |
| `grapes` | 2 | 2 | 3 | 7 | 0.160 | 0.451 | 0.772 | 0.7447 |  |  |
| `remembered` | 1 | 2 | 4 | 7 | 0.160 | 0.253 | 0.772 | 0.8475 |  |  |
| `dried` | 1 | 2 | 4 | 7 | 0.160 | 0.253 | 0.772 | 0.8475 |  |  |
| `woman's` | 2 | 2 | 3 | 7 | 0.160 | 0.451 | 0.772 | 0.7447 |  |  |
| `dry` | 1 | 2 | 4 | 7 | 0.160 | 0.253 | 0.772 | 0.8475 |  |  |
| `heart` | 11 | 13 | 31 | 55 | 0.158 | 0.166 | 0.255 | 0.8980 |  |  |
| `within` | 5 | 5 | 10 | 20 | 0.132 | 0.350 | 0.415 | 0.7969 |  |  |
| `peace` | 4 | 5 | 11 | 20 | 0.132 | 0.132 | 0.415 | 0.9180 |  |  |
| `hands` | 9 | 11 | 27 | 47 | 0.113 | 0.161 | 0.243 | 0.9011 |  |  |
| `ones` | 3 | 4 | 9 | 16 | 0.105 | 0.121 | 0.435 | 0.9243 |  |  |
| `midian` | 4 | 4 | 8 | 16 | 0.105 | 0.280 | 0.435 | 0.8330 |  |  |
| `kept` | 3 | 4 | 9 | 16 | 0.105 | 0.121 | 0.435 | 0.9243 |  |  |
| `under` | 11 | 13 | 33 | 57 | 0.077 | 0.136 | 0.189 | 0.9157 |  |  |
| `mine` | 4 | 4 | 9 | 17 | 0.045 | 0.115 | 0.324 | 0.9283 |  |  |
| `inside` | 6 | 7 | 18 | 31 | 0.032 | 0.064 | 0.202 | 0.9586 |  |  |
| `pursued` | 1 | 1 | 2 | 4 | 0.026 | 0.070 | 0.687 | 0.9549 |  |  |
| `offer` | 1 | 1 | 2 | 4 | 0.026 | 0.070 | 0.687 | 0.9549 |  |  |
| `dressed` | 1 | 1 | 2 | 4 | 0.026 | 0.070 | 0.687 | 0.9549 |  |  |
| `virgin` | 1 | 1 | 2 | 4 | 0.026 | 0.070 | 0.687 | 0.9549 |  |  |
| `field's` | 1 | 1 | 2 | 4 | 0.026 | 0.070 | 0.687 | 0.9549 |  |  |
| `widow` | 1 | 1 | 2 | 4 | 0.026 | 0.070 | 0.687 | 0.9549 |  |  |
| `practice` | 1 | 1 | 2 | 4 | 0.026 | 0.070 | 0.687 | 0.9549 |  |  |
| `pitch` | 1 | 1 | 2 | 4 | 0.026 | 0.070 | 0.687 | 0.9549 |  |  |
| `apart` | 1 | 1 | 2 | 4 | 0.026 | 0.070 | 0.687 | 0.9549 |  |  |
| `designated` | 1 | 1 | 2 | 4 | 0.026 | 0.070 | 0.687 | 0.9549 |  |  |
| `celebrate` | 1 | 1 | 2 | 4 | 0.026 | 0.070 | 0.687 | 0.9549 |  |  |
| `red` | 3 | 3 | 7 | 13 | 0.023 | 0.058 | 0.324 | 0.9622 |  |  |
| `offensive` | 2 | 2 | 5 | 9 | 0.006 | 0.013 | 0.324 | 0.9922 |  |  |
| `but` | 18 | 18 | 49 | 85 | 0.001 | 0.001 | 0.042 | 0.9994 |  |  |

### All words assigned to P (1,980 types)

The assignment is the source with the largest positive source-vs-rest information score. **Do not treat a one-off as strong evidence**: use `source info bits`, `global bits`, total count, and q-value together.

| word | J | E | P | n | source info bits | global bits | source WoE bits | q | FDR<.05 | artifact? |
|---|---:|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|
| `shall` | 56 | 199 | 1736 | 1991 | 593.203 | 655.593 | 2.345 | 1.91e-194 | yes |  |
| `of` | 611 | 669 | 3336 | 4616 | 302.364 | 304.708 | 0.967 | 2.69e-89 | yes |  |
| `offering` | 3 | 19 | 412 | 434 | 228.251 | 237.727 | 3.755 | 2.94e-69 | yes |  |
| `the` | 1324 | 1335 | 5388 | 8047 | 207.550 | 207.712 | 0.610 | 2.13e-60 | yes |  |
| `n` | 3 | 0 | 250 | 253 | 178.340 | 181.318 | 5.717 | 1.41e-52 | yes | ⚠ |
| `priest` | 1 | 4 | 244 | 249 | 164.236 | 165.648 | 5.029 | 6.52e-48 | yes |  |
| `its` | 35 | 46 | 457 | 538 | 133.944 | 135.106 | 2.046 | 7.65e-39 | yes |  |
| `holy` | 1 | 2 | 191 | 194 | 132.743 | 132.996 | 5.328 | 3.05e-38 | yes |  |
| `impure` | 0 | 0 | 167 | 167 | 132.337 | 132.337 | 7.942 | 4.47e-38 | yes |  |
| `l` | 0 | 0 | 165 | 165 | 130.752 | 130.752 | 7.924 | 1.25e-37 | yes | ⚠ |
| `children` | 28 | 65 | 427 | 520 | 101.601 | 112.791 | 1.749 | 2.66e-32 | yes |  |
| `forward` | 0 | 0 | 108 | 108 | 85.583 | 85.583 | 7.314 | 2.47e-24 | yes |  |
| `their` | 94 | 56 | 512 | 662 | 81.034 | 87.779 | 1.324 | 5.59e-25 | yes |  |
| `make` | 27 | 29 | 289 | 345 | 77.855 | 77.922 | 1.912 | 4.42e-22 | yes |  |
| `e` | 4 | 0 | 124 | 128 | 77.552 | 81.523 | 4.343 | 3.75e-23 | yes | ⚠ |
| `congregation` | 0 | 0 | 92 | 92 | 72.904 | 72.904 | 7.083 | 1.35e-20 | yes |  |
| `d` | 0 | 1 | 99 | 100 | 71.614 | 72.622 | 5.604 | 1.56e-20 | yes | ⚠ |
| `tribe` | 0 | 0 | 88 | 88 | 69.734 | 69.734 | 7.019 | 9.96e-20 | yes |  |
| `r` | 2 | 0 | 101 | 103 | 68.291 | 70.276 | 4.895 | 7.00e-20 | yes | ⚠ |
| `atonement` | 0 | 1 | 93 | 94 | 66.949 | 67.957 | 5.514 | 3.34e-19 | yes |  |
| `tabernacle` | 0 | 0 | 80 | 80 | 63.395 | 63.395 | 6.883 | 6.96e-18 | yes |  |
| `any` | 3 | 7 | 129 | 139 | 62.784 | 64.001 | 3.177 | 4.76e-18 | yes |  |
| `ho` | 0 | 0 | 74 | 74 | 58.640 | 58.640 | 6.771 | 1.60e-16 | yes | ⚠ |
| `y` | 0 | 0 | 74 | 74 | 58.640 | 58.640 | 6.771 | 1.60e-16 | yes | ⚠ |
| `oil` | 0 | 2 | 88 | 90 | 58.383 | 60.397 | 4.697 | 4.97e-17 | yes |  |
| `counts` | 0 | 0 | 71 | 71 | 56.263 | 56.263 | 6.711 | 7.90e-16 | yes |  |
| `meeting` | 0 | 6 | 103 | 109 | 55.563 | 61.607 | 3.545 | 2.31e-17 | yes |  |
| `pure` | 4 | 0 | 93 | 97 | 54.617 | 58.588 | 3.929 | 1.63e-16 | yes |  |
| `hundred` | 6 | 7 | 127 | 140 | 54.361 | 54.424 | 2.792 | 2.66e-15 | yes |  |
| `for` | 187 | 172 | 825 | 1184 | 51.775 | 52.124 | 0.757 | 1.23e-14 | yes |  |
| `family` | 3 | 0 | 84 | 87 | 51.466 | 54.444 | 4.145 | 2.66e-15 | yes |  |
| `levites` | 0 | 0 | 64 | 64 | 50.716 | 50.716 | 6.563 | 3.19e-14 | yes |  |
| `thousand` | 0 | 4 | 85 | 89 | 48.785 | 52.814 | 3.800 | 7.76e-15 | yes |  |
| `families` | 4 | 2 | 91 | 97 | 47.094 | 47.570 | 3.367 | 2.51e-13 | yes |  |
| `work` | 12 | 6 | 131 | 149 | 46.955 | 48.383 | 2.382 | 1.47e-13 | yes |  |
| `affliction` | 0 | 0 | 59 | 59 | 46.754 | 46.754 | 6.446 | 4.37e-13 | yes |  |
| `s` | 2 | 13 | 119 | 134 | 45.168 | 51.751 | 2.499 | 1.58e-14 | yes | ⚠ |
| `o` | 0 | 0 | 55 | 55 | 43.584 | 43.584 | 6.346 | 3.40e-12 | yes | ⚠ |
| `bases` | 0 | 0 | 55 | 55 | 43.584 | 43.584 | 6.346 | 3.40e-12 | yes |  |
| `by` | 76 | 63 | 393 | 532 | 43.286 | 44.072 | 1.050 | 2.53e-12 | yes |  |
| `front` | 16 | 39 | 218 | 273 | 43.206 | 50.531 | 1.530 | 3.53e-14 | yes |  |
| `army` | 1 | 2 | 72 | 75 | 42.611 | 42.863 | 3.924 | 5.49e-12 | yes |  |
| `aaron` | 2 | 35 | 172 | 209 | 41.502 | 67.519 | 1.754 | 4.33e-19 | yes |  |
| `te` | 0 | 0 | 52 | 52 | 41.207 | 41.207 | 6.265 | 1.61e-11 | yes | ⚠ |
| `sin` | 5 | 17 | 131 | 153 | 40.250 | 45.327 | 2.099 | 1.11e-12 | yes |  |
| `altar` | 7 | 20 | 144 | 171 | 40.057 | 44.861 | 1.946 | 1.51e-12 | yes |  |
| `sons` | 36 | 21 | 214 | 271 | 39.291 | 42.064 | 1.452 | 9.17e-12 | yes |  |
| `aa` | 0 | 0 | 49 | 49 | 38.829 | 38.829 | 6.180 | 7.53e-11 | yes | ⚠ |
| `five` | 7 | 2 | 88 | 97 | 37.685 | 39.771 | 2.771 | 4.13e-11 | yes |  |
| `a` | 289 | 331 | 1203 | 1823 | 37.550 | 39.923 | 0.514 | 3.75e-11 | yes |  |
| `it` | 198 | 275 | 958 | 1431 | 36.824 | 46.478 | 0.574 | 5.23e-13 | yes |  |
| `shekels` | 0 | 1 | 54 | 55 | 36.823 | 37.830 | 4.734 | 1.47e-10 | yes |  |
| `wash` | 4 | 0 | 66 | 70 | 35.151 | 39.122 | 3.437 | 6.20e-11 | yes |  |
| `eternal` | 0 | 0 | 44 | 44 | 34.867 | 34.867 | 6.027 | 1.05e-09 | yes |  |
| `equipment` | 0 | 0 | 44 | 44 | 34.867 | 34.867 | 6.027 | 1.05e-09 | yes |  |
| `blood` | 7 | 15 | 119 | 141 | 33.549 | 35.756 | 1.961 | 5.93e-10 | yes |  |
| `t` | 6 | 0 | 71 | 77 | 33.317 | 39.274 | 3.011 | 5.68e-11 | yes | ⚠ |
| `eleazar` | 0 | 0 | 41 | 41 | 32.490 | 32.490 | 5.926 | 5.13e-09 | yes |  |
| `one` | 81 | 66 | 376 | 523 | 32.446 | 33.445 | 0.906 | 2.73e-09 | yes |  |
| `li` | 0 | 0 | 39 | 39 | 30.905 | 30.905 | 5.855 | 1.47e-08 | yes | ⚠ |
| `an` | 31 | 64 | 271 | 366 | 30.443 | 39.129 | 1.060 | 6.20e-11 | yes |  |
| `ti` | 0 | 0 | 37 | 37 | 29.320 | 29.320 | 5.780 | 4.20e-08 | yes | ⚠ |
| `burn` | 1 | 2 | 53 | 56 | 28.849 | 29.102 | 3.485 | 4.79e-08 | yes |  |
| `commanded` | 12 | 11 | 111 | 134 | 27.905 | 27.929 | 1.798 | 1.03e-07 | yes |  |
| `cubits` | 1 | 1 | 47 | 49 | 27.674 | 27.674 | 3.799 | 1.20e-07 | yes |  |
| `fire` | 9 | 10 | 100 | 119 | 27.464 | 27.510 | 1.917 | 1.33e-07 | yes |  |
| `four` | 2 | 3 | 58 | 63 | 26.978 | 27.130 | 2.962 | 1.69e-07 | yes |  |
| `columns` | 0 | 0 | 34 | 34 | 26.943 | 26.943 | 5.659 | 1.88e-07 | yes |  |
| `skin` | 1 | 1 | 45 | 47 | 26.212 | 26.212 | 3.737 | 3.01e-07 | yes |  |
| `peace-offering` | 0 | 1 | 40 | 41 | 26.157 | 27.165 | 4.306 | 1.66e-07 | yes |  |
| `donation` | 0 | 0 | 33 | 33 | 26.150 | 26.150 | 5.617 | 3.07e-07 | yes |  |
| `frames` | 0 | 0 | 33 | 33 | 26.150 | 26.150 | 5.617 | 3.07e-07 | yes |  |
| `person` | 1 | 4 | 56 | 61 | 25.636 | 27.048 | 2.912 | 1.78e-07 | yes |  |
| `impurity` | 0 | 0 | 32 | 32 | 25.358 | 25.358 | 5.573 | 5.24e-07 | yes |  |
| `legacy` | 1 | 2 | 47 | 50 | 24.600 | 24.852 | 3.313 | 7.36e-07 | yes |  |
| `poles` | 0 | 0 | 31 | 31 | 24.565 | 24.565 | 5.528 | 8.66e-07 | yes |  |
| `pho` | 0 | 0 | 31 | 31 | 24.565 | 24.565 | 5.528 | 8.66e-07 | yes |  |
| `burnt` | 0 | 18 | 92 | 110 | 24.546 | 42.678 | 1.873 | 6.11e-12 | yes |  |
| `chieftain` | 1 | 1 | 42 | 44 | 24.030 | 24.030 | 3.638 | 1.24e-06 | yes |  |
| `side` | 0 | 7 | 60 | 67 | 23.881 | 30.932 | 2.563 | 1.45e-08 | yes |  |
| `testimony` | 0 | 0 | 29 | 29 | 22.981 | 22.981 | 5.433 | 2.42e-06 | yes |  |
| `incense` | 0 | 0 | 29 | 29 | 22.981 | 22.981 | 5.433 | 2.42e-06 | yes |  |
| `leprosy` | 0 | 0 | 29 | 29 | 22.981 | 22.981 | 5.433 | 2.42e-06 | yes |  |
| `be` | 141 | 184 | 647 | 972 | 22.947 | 27.383 | 0.547 | 1.45e-07 | yes |  |
| `guilt` | 1 | 0 | 35 | 36 | 22.385 | 23.378 | 4.115 | 1.90e-06 | yes |  |
| `blu` | 0 | 0 | 28 | 28 | 22.188 | 22.188 | 5.383 | 3.93e-06 | yes | ⚠ |
| `elevation` | 0 | 0 | 28 | 28 | 22.188 | 22.188 | 5.383 | 3.93e-06 | yes |  |
| `ri` | 0 | 0 | 28 | 28 | 22.188 | 22.188 | 5.383 | 3.93e-06 | yes |  |
| `leather` | 0 | 0 | 28 | 28 | 22.188 | 22.188 | 5.383 | 3.93e-06 | yes |  |
| `israel` | 52 | 72 | 300 | 424 | 22.132 | 24.617 | 0.824 | 8.47e-07 | yes |  |
| `fifty` | 4 | 0 | 47 | 51 | 21.987 | 25.957 | 2.951 | 3.48e-07 | yes |  |
| `clothes` | 11 | 2 | 74 | 87 | 21.862 | 26.745 | 2.015 | 2.10e-07 | yes |  |
| `on` | 147 | 187 | 655 | 989 | 21.583 | 25.345 | 0.525 | 5.26e-07 | yes |  |
| `gs` | 0 | 0 | 27 | 27 | 21.396 | 21.396 | 5.332 | 6.55e-06 | yes | ⚠ |
| `emission` | 0 | 0 | 27 | 27 | 21.396 | 21.396 | 5.332 | 6.55e-06 | yes |  |
| `mixed` | 0 | 0 | 27 | 27 | 21.396 | 21.396 | 5.332 | 6.55e-06 | yes |  |
| `bronze` | 1 | 2 | 42 | 45 | 21.109 | 21.361 | 3.153 | 6.68e-06 | yes |  |
| `names` | 5 | 0 | 49 | 54 | 21.008 | 25.972 | 2.721 | 3.46e-07 | yes |  |
| `sabbath` | 0 | 0 | 26 | 26 | 20.603 | 20.603 | 5.278 | 1.08e-05 | yes |  |
| `courtyard's` | 0 | 0 | 26 | 26 | 20.603 | 20.603 | 5.278 | 1.08e-05 | yes |  |
| `unblemished` | 0 | 0 | 26 | 26 | 20.603 | 20.603 | 5.278 | 1.08e-05 | yes |  |
| `acacia` | 0 | 0 | 26 | 26 | 20.603 | 20.603 | 5.278 | 1.08e-05 | yes |  |
| `dais` | 0 | 0 | 26 | 26 | 20.603 | 20.603 | 5.278 | 1.08e-05 | yes |  |
| `two` | 28 | 43 | 196 | 267 | 20.446 | 22.860 | 1.011 | 2.60e-06 | yes |  |
| `nudity` | 0 | 1 | 32 | 33 | 20.135 | 21.143 | 3.988 | 7.68e-06 | yes |  |
| `year` | 4 | 8 | 67 | 79 | 19.452 | 20.462 | 1.984 | 1.18e-05 | yes |  |
| `flour` | 1 | 0 | 31 | 32 | 19.388 | 20.381 | 3.943 | 1.24e-05 | yes |  |
| `fine` | 1 | 0 | 31 | 32 | 19.388 | 20.381 | 3.943 | 1.24e-05 | yes |  |
| `flesh` | 7 | 3 | 61 | 71 | 19.126 | 20.284 | 2.101 | 1.32e-05 | yes |  |
| `ram` | 1 | 4 | 46 | 51 | 19.064 | 20.477 | 2.630 | 1.17e-05 | yes |  |
| `g` | 0 | 0 | 24 | 24 | 19.018 | 19.018 | 5.165 | 2.92e-05 | yes | ⚠ |
| `pavilion` | 0 | 0 | 24 | 24 | 19.018 | 19.018 | 5.165 | 2.92e-05 | yes |  |
| `month` | 3 | 5 | 54 | 62 | 18.335 | 18.715 | 2.232 | 3.55e-05 | yes |  |
| `curtains` | 0 | 0 | 23 | 23 | 18.226 | 18.226 | 5.105 | 4.89e-05 | yes |  |
| `bull` | 0 | 4 | 41 | 45 | 17.986 | 22.015 | 2.756 | 4.37e-06 | yes |  |
| `years` | 12 | 21 | 113 | 146 | 17.979 | 19.839 | 1.312 | 1.77e-05 | yes |  |
| `evening` | 5 | 2 | 50 | 57 | 17.689 | 18.625 | 2.302 | 3.76e-05 | yes |  |
| `tent` | 12 | 31 | 133 | 176 | 17.645 | 24.054 | 1.169 | 1.22e-06 | yes |  |
| `menorah` | 0 | 0 | 22 | 22 | 17.434 | 17.434 | 5.042 | 7.84e-05 | yes |  |
| `tpla` | 0 | 0 | 22 | 22 | 17.434 | 17.434 | 5.042 | 7.84e-05 | yes | ⚠ |
| `connected` | 0 | 0 | 22 | 22 | 17.434 | 17.434 | 5.042 | 7.84e-05 | yes |  |
| `holies` | 0 | 0 | 22 | 22 | 17.434 | 17.434 | 5.042 | 7.84e-05 | yes |  |
| `ca` | 0 | 0 | 22 | 22 | 17.434 | 17.434 | 5.042 | 7.84e-05 | yes |  |
| `shekel` | 0 | 0 | 22 | 22 | 17.434 | 17.434 | 5.042 | 7.84e-05 | yes |  |
| `bre` | 0 | 0 | 22 | 22 | 17.434 | 17.434 | 5.042 | 7.84e-05 | yes |  |
| `curtain` | 0 | 0 | 21 | 21 | 16.641 | 16.641 | 4.977 | 1.30e-04 | yes |  |
| `pu` | 0 | 0 | 21 | 21 | 16.641 | 16.641 | 4.977 | 1.30e-04 | yes | ⚠ |
| `table` | 0 | 0 | 21 | 21 | 16.641 | 16.641 | 4.977 | 1.30e-04 | yes |  |
| `jubilee` | 0 | 0 | 21 | 21 | 16.641 | 16.641 | 4.977 | 1.30e-04 | yes |  |
| `identify` | 0 | 0 | 21 | 21 | 16.641 | 16.641 | 4.977 | 1.30e-04 | yes |  |
| `ple` | 0 | 0 | 21 | 21 | 16.641 | 16.641 | 4.977 | 1.30e-04 | yes |  |
| `woven` | 0 | 0 | 21 | 21 | 16.641 | 16.641 | 4.977 | 1.30e-04 | yes |  |
| `appraisal` | 0 | 0 | 21 | 21 | 16.641 | 16.641 | 4.977 | 1.30e-04 | yes |  |
| `will` | 123 | 261 | 708 | 1092 | 16.574 | 54.177 | 0.436 | 3.11e-15 | yes |  |
| `or` | 39 | 48 | 213 | 300 | 16.272 | 17.012 | 0.839 | 1.03e-04 | yes |  |
| `old` | 19 | 4 | 87 | 110 | 16.148 | 23.708 | 1.448 | 1.53e-06 | yes |  |
| `le` | 0 | 0 | 20 | 20 | 15.849 | 15.849 | 4.908 | 2.13e-04 | yes | ⚠ |
| `chieftains` | 0 | 0 | 20 | 20 | 15.849 | 15.849 | 4.908 | 2.13e-04 | yes |  |
| `second` | 2 | 5 | 46 | 53 | 15.305 | 16.285 | 2.183 | 1.63e-04 | yes |  |
| `seventh` | 1 | 4 | 40 | 45 | 15.263 | 16.676 | 2.431 | 1.30e-04 | yes |  |
| `carcass` | 0 | 0 | 19 | 19 | 15.056 | 15.056 | 4.836 | 3.45e-04 | yes |  |
| `expose` | 0 | 0 | 19 | 19 | 15.056 | 15.056 | 4.836 | 3.45e-04 | yes |  |
| `item` | 0 | 0 | 19 | 19 | 15.056 | 15.056 | 4.836 | 3.45e-04 | yes |  |
| `thirty` | 2 | 2 | 36 | 40 | 14.738 | 14.738 | 2.570 | 4.28e-04 | yes |  |
| `fat` | 5 | 5 | 53 | 63 | 14.655 | 14.655 | 1.900 | 4.51e-04 | yes |  |
| `animals` | 5 | 1 | 42 | 48 | 14.646 | 16.717 | 2.260 | 1.26e-04 | yes |  |
| `smoke` | 5 | 0 | 39 | 44 | 14.643 | 19.606 | 2.395 | 2.04e-05 | yes |  |
| `law` | 0 | 5 | 39 | 44 | 14.643 | 19.680 | 2.395 | 1.96e-05 | yes |  |
| `is` | 134 | 138 | 517 | 789 | 14.453 | 14.529 | 0.478 | 4.89e-04 | yes |  |
| `kind` | 3 | 0 | 32 | 35 | 14.315 | 17.294 | 2.766 | 8.61e-05 | yes |  |
| `ce` | 0 | 0 | 18 | 18 | 14.264 | 14.264 | 4.760 | 5.69e-04 | yes | ⚠ |
| `gad` | 0 | 0 | 18 | 18 | 14.264 | 14.264 | 4.760 | 5.69e-04 | yes |  |
| `lambs` | 0 | 0 | 18 | 18 | 14.264 | 14.264 | 4.760 | 5.69e-04 | yes |  |
| `se` | 0 | 0 | 18 | 18 | 14.264 | 14.264 | 4.760 | 5.69e-04 | yes | ⚠ |
| `persons` | 0 | 0 | 18 | 18 | 14.264 | 14.264 | 4.760 | 5.69e-04 | yes |  |
| `horns` | 0 | 0 | 18 | 18 | 14.264 | 14.264 | 4.760 | 5.69e-04 | yes |  |
| `generations` | 4 | 0 | 35 | 39 | 14.100 | 18.070 | 2.530 | 5.37e-05 | yes |  |
| `sprinkle` | 0 | 0 | 17 | 17 | 13.471 | 13.471 | 4.680 | 9.22e-04 | yes |  |
| `records` | 0 | 0 | 17 | 17 | 13.471 | 13.471 | 4.680 | 9.22e-04 | yes |  |
| `innards` | 0 | 0 | 17 | 17 | 13.471 | 13.471 | 4.680 | 9.22e-04 | yes |  |
| `finger` | 0 | 0 | 17 | 17 | 13.471 | 13.471 | 4.680 | 9.22e-04 | yes |  |
| `width` | 1 | 0 | 23 | 24 | 13.471 | 14.464 | 3.520 | 5.09e-04 | yes |  |
| `aaron's` | 0 | 1 | 23 | 24 | 13.471 | 14.479 | 3.520 | 5.05e-04 | yes |  |
| `full` | 2 | 2 | 33 | 37 | 12.836 | 12.836 | 2.447 | 0.0014 | yes |  |
| `cover` | 1 | 3 | 33 | 37 | 12.836 | 13.605 | 2.447 | 8.63e-04 | yes |  |
| `length` | 1 | 0 | 22 | 23 | 12.742 | 13.734 | 3.457 | 7.95e-04 | yes |  |
| `kidneys` | 0 | 0 | 16 | 16 | 12.679 | 12.679 | 4.595 | 0.0015 | yes |  |
| `korah` | 0 | 0 | 16 | 16 | 12.679 | 12.679 | 4.595 | 0.0015 | yes |  |
| `head` | 2 | 12 | 59 | 73 | 12.671 | 18.461 | 1.588 | 4.20e-05 | yes |  |
| `six` | 2 | 6 | 44 | 52 | 12.599 | 14.139 | 1.939 | 6.12e-04 | yes |  |
| `lamb` | 2 | 1 | 29 | 32 | 12.345 | 12.582 | 2.626 | 0.0016 | yes |  |
| `heads` | 1 | 1 | 25 | 27 | 12.010 | 12.010 | 2.901 | 0.0023 | yes |  |
| `charge` | 2 | 0 | 25 | 27 | 12.010 | 13.996 | 2.901 | 6.70e-04 | yes |  |
| `frame` | 0 | 0 | 15 | 15 | 11.887 | 11.887 | 4.504 | 0.0025 | yes |  |
| `d's` | 0 | 0 | 15 | 15 | 11.887 | 11.887 | 4.504 | 0.0025 | yes |  |
| `bars` | 0 | 0 | 15 | 15 | 11.887 | 11.887 | 4.504 | 0.0025 | yes |  |
| `eats` | 0 | 0 | 15 | 15 | 11.887 | 11.887 | 4.504 | 0.0025 | yes |  |
| `lamps` | 0 | 0 | 15 | 15 | 11.887 | 11.887 | 4.504 | 0.0025 | yes |  |
| `priest's` | 0 | 0 | 15 | 15 | 11.887 | 11.887 | 4.504 | 0.0025 | yes |  |
| `hangings` | 0 | 0 | 15 | 15 | 11.887 | 11.887 | 4.504 | 0.0025 | yes |  |
| `plate` | 0 | 0 | 15 | 15 | 11.887 | 11.887 | 4.504 | 0.0025 | yes |  |
| `dan` | 0 | 0 | 14 | 14 | 11.094 | 11.094 | 4.408 | 0.0039 | yes |  |
| `kohath` | 0 | 0 | 14 | 14 | 11.094 | 11.094 | 4.408 | 0.0039 | yes |  |
| `ends` | 0 | 0 | 14 | 14 | 11.094 | 11.094 | 4.408 | 0.0039 | yes |  |
| `desecrate` | 0 | 0 | 14 | 14 | 11.094 | 11.094 | 4.408 | 0.0039 | yes |  |
| `plated` | 0 | 0 | 14 | 14 | 11.094 | 11.094 | 4.408 | 0.0039 | yes |  |
| `tabernacle's` | 0 | 0 | 14 | 14 | 11.094 | 11.094 | 4.408 | 0.0039 | yes |  |
| `fragrances` | 0 | 0 | 14 | 14 | 11.094 | 11.094 | 4.408 | 0.0039 | yes |  |
| `cherubs` | 0 | 0 | 14 | 14 | 11.094 | 11.094 | 4.408 | 0.0039 | yes |  |
| `pan` | 0 | 0 | 14 | 14 | 11.094 | 11.094 | 4.408 | 0.0039 | yes |  |
| `hair` | 3 | 0 | 27 | 30 | 11.053 | 14.032 | 2.524 | 6.57e-04 | yes |  |
| `being` | 4 | 4 | 41 | 49 | 10.969 | 10.969 | 1.838 | 0.0043 | yes |  |
| `possession` | 9 | 0 | 43 | 52 | 10.693 | 19.628 | 1.746 | 2.02e-05 | yes |  |
| `basin` | 0 | 2 | 23 | 25 | 10.657 | 12.671 | 2.783 | 0.0015 | yes |  |
| `covering` | 1 | 1 | 23 | 25 | 10.657 | 10.657 | 2.783 | 0.0051 | yes |  |
| `linen` | 0 | 1 | 19 | 20 | 10.571 | 11.578 | 3.251 | 0.0030 | yes |  |
| `counted` | 1 | 0 | 19 | 20 | 10.571 | 11.564 | 3.251 | 0.0030 | yes |  |
| `who` | 85 | 74 | 313 | 472 | 10.511 | 10.983 | 0.527 | 0.0042 | yes |  |
| `male` | 9 | 1 | 45 | 55 | 10.463 | 15.714 | 1.666 | 2.31e-04 | yes |  |
| `everyone` | 5 | 8 | 52 | 65 | 10.434 | 10.960 | 1.510 | 0.0043 | yes |  |
| `goat` | 5 | 0 | 32 | 37 | 10.430 | 15.394 | 2.113 | 2.79e-04 | yes |  |
| `half` | 2 | 3 | 32 | 37 | 10.430 | 10.583 | 2.113 | 0.0054 | yes |  |
| `ng` | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes | ⚠ |
| `scab` | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| `anointing` | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| `hooks` | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| `intercourse` | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| `nazirite` | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| `merari` | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| `tenth` | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| `per` | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| `murderer` | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| `altar's` | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| `row` | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| `dish` | 0 | 0 | 13 | 13 | 10.302 | 10.302 | 4.305 | 0.0063 | yes |  |
| `cattle` | 4 | 3 | 37 | 44 | 10.204 | 10.300 | 1.872 | 0.0063 | yes |  |
| `smell` | 1 | 1 | 22 | 24 | 9.987 | 9.987 | 2.720 | 0.0077 | yes |  |
| `bring` | 28 | 37 | 151 | 216 | 9.819 | 10.788 | 0.761 | 0.0047 | yes |  |
| `spread` | 0 | 3 | 25 | 28 | 9.784 | 12.806 | 2.415 | 0.0014 | yes |  |
| `twenty` | 5 | 6 | 46 | 57 | 9.783 | 9.856 | 1.566 | 0.0083 | yes |  |
| `ithamar` | 0 | 0 | 12 | 12 | 9.509 | 9.509 | 4.194 | 0.0101 | yes |  |
| `legs` | 0 | 0 | 12 | 12 | 9.509 | 9.509 | 4.194 | 0.0101 | yes |  |
| `shut` | 0 | 0 | 12 | 12 | 9.509 | 9.509 | 4.194 | 0.0101 | yes |  |
| `hammered` | 0 | 0 | 12 | 12 | 9.509 | 9.509 | 4.194 | 0.0101 | yes |  |
| `bright` | 0 | 0 | 12 | 12 | 9.509 | 9.509 | 4.194 | 0.0101 | yes |  |
| `function` | 0 | 0 | 12 | 12 | 9.509 | 9.509 | 4.194 | 0.0101 | yes |  |
| `loops` | 0 | 0 | 12 | 12 | 9.509 | 9.509 | 4.194 | 0.0101 | yes |  |
| `attain` | 0 | 0 | 12 | 12 | 9.509 | 9.509 | 4.194 | 0.0101 | yes |  |
| `blue` | 0 | 0 | 12 | 12 | 9.509 | 9.509 | 4.194 | 0.0101 | yes |  |
| `gershon` | 0 | 0 | 12 | 12 | 9.509 | 9.509 | 4.194 | 0.0101 | yes |  |
| `swarming` | 0 | 0 | 12 | 12 | 9.509 | 9.509 | 4.194 | 0.0101 | yes |  |
| `pleasant` | 2 | 0 | 21 | 23 | 9.323 | 11.308 | 2.655 | 0.0036 | yes |  |
| `add` | 1 | 1 | 21 | 23 | 9.323 | 9.323 | 2.655 | 0.0113 | yes |  |
| `cut` | 4 | 5 | 40 | 49 | 9.166 | 9.254 | 1.642 | 0.0118 | yes |  |
| `instruction` | 1 | 2 | 24 | 27 | 9.158 | 9.411 | 2.358 | 0.0108 | yes |  |
| `purified` | 0 | 1 | 17 | 18 | 9.142 | 10.149 | 3.095 | 0.0069 | yes |  |
| `anointed` | 0 | 1 | 17 | 18 | 9.142 | 10.149 | 3.095 | 0.0069 | yes |  |
| `asher` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `expiation` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `fabric` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `assembly` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `group` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `ornament` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `naphtali` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `liver` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `sabbaths` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `ephron` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `breast` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `ordination` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `elevate` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `bull's` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `detestable` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `issachar` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `anoint` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `courtyard` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `cu` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `always` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `height` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `fling` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `bald` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `bi` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `container` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `refuge` | 0 | 0 | 11 | 11 | 8.717 | 8.717 | 4.074 | 0.0154 | yes |  |
| `around` | 7 | 11 | 59 | 77 | 8.711 | 9.387 | 1.236 | 0.0109 | yes |  |
| `all` | 137 | 133 | 477 | 747 | 8.398 | 8.417 | 0.372 | 0.0187 | yes |  |
| `above` | 2 | 0 | 19 | 21 | 8.013 | 9.999 | 2.514 | 0.0076 | yes |  |
| `touches` | 2 | 0 | 19 | 21 | 8.013 | 9.999 | 2.514 | 0.0076 | yes |  |
| `fire-holders` | 0 | 0 | 10 | 10 | 7.924 | 7.924 | 3.942 | 0.0250 | yes |  |
| `pegs` | 0 | 0 | 10 | 10 | 7.924 | 7.924 | 3.942 | 0.0250 | yes |  |
| `citizen` | 0 | 0 | 10 | 10 | 7.924 | 7.924 | 3.942 | 0.0250 | yes |  |
| `outsider` | 0 | 0 | 10 | 10 | 7.924 | 7.924 | 3.942 | 0.0250 | yes |  |
| `minister` | 0 | 0 | 10 | 10 | 7.924 | 7.924 | 3.942 | 0.0250 | yes |  |
| `zebulun` | 0 | 0 | 10 | 10 | 7.924 | 7.924 | 3.942 | 0.0250 | yes |  |
| `ke` | 0 | 0 | 10 | 10 | 7.924 | 7.924 | 3.942 | 0.0250 | yes | ⚠ |
| `cubit` | 0 | 0 | 10 | 10 | 7.924 | 7.924 | 3.942 | 0.0250 | yes |  |
| `clasps` | 0 | 0 | 10 | 10 | 7.924 | 7.924 | 3.942 | 0.0250 | yes |  |
| `flag` | 0 | 0 | 10 | 10 | 7.924 | 7.924 | 3.942 | 0.0250 | yes |  |
| `base` | 0 | 0 | 10 | 10 | 7.924 | 7.924 | 3.942 | 0.0250 | yes |  |
| `slaughter` | 1 | 4 | 27 | 32 | 7.600 | 9.012 | 1.872 | 0.0138 | yes |  |
| `entrance` | 8 | 9 | 54 | 71 | 7.533 | 7.583 | 1.189 | 0.0306 | yes |  |
| `rams` | 0 | 4 | 24 | 28 | 7.422 | 11.451 | 1.995 | 0.0033 | yes |  |
| `branches` | 0 | 2 | 18 | 20 | 7.369 | 9.384 | 2.438 | 0.0109 | yes |  |
| `through` | 18 | 9 | 73 | 100 | 7.250 | 9.390 | 0.969 | 0.0109 | yes |  |
| `vows` | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| `armies` | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| `evenings` | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| `flesh's` | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| `anah` | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| `paddan` | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| `woof` | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| `pigeons` | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| `space` | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| `corners` | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| `visitor` | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| `shave` | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| `lobe` | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| `crown` | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| `ceasing` | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| `equipped` | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| `spot` | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| `warp` | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| `turtledoves` | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| `frankincense` | 0 | 0 | 9 | 9 | 7.132 | 7.132 | 3.798 | 0.0397 | yes |  |
| `wood` | 0 | 10 | 38 | 48 | 7.100 | 17.173 | 1.425 | 9.30e-05 | yes |  |
| `part` | 1 | 0 | 14 | 15 | 7.036 | 8.029 | 2.823 | 0.0239 | yes |  |
| `burned` | 1 | 3 | 23 | 27 | 6.856 | 7.626 | 1.935 | 0.0300 | yes |  |
| `spoke` | 22 | 25 | 108 | 155 | 6.776 | 6.937 | 0.743 | 0.0451 | yes |  |
| `husband` | 0 | 2 | 17 | 19 | 6.733 | 8.747 | 2.358 | 0.0154 | yes |  |
| `every` | 29 | 28 | 125 | 182 | 6.658 | 6.664 | 0.677 | 0.0491 | yes |  |
| `redemption` | 0 | 1 | 13 | 14 | 6.347 | 7.354 | 2.720 | 0.0352 | yes |  |
| `designer's` | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| `rim` | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| `blow` | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| `boil` | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| `swelling` | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| `sale` | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| `cups` | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| `designed` | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| `dre` | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  | ⚠ |
| `expired` | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| `priesthood` | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| `lighting` | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| `theirs` | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| `wisdom` | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| `earlobe` | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| `shoulder-pieces` | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| `arrange` | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| `purification` | 0 | 0 | 8 | 8 | 6.339 | 6.339 | 3.638 | 0.0586 |  |  |
| `white` | 3 | 1 | 22 | 26 | 6.300 | 7.040 | 1.872 | 0.0422 | yes |  |
| `service` | 0 | 3 | 19 | 22 | 6.142 | 9.164 | 2.028 | 0.0126 | yes |  |
| `living` | 6 | 1 | 29 | 36 | 6.094 | 8.916 | 1.526 | 0.0142 | yes |  |
| `day` | 36 | 47 | 165 | 248 | 5.812 | 6.949 | 0.538 | 0.0448 | yes |  |
| `skins` | 1 | 0 | 12 | 13 | 5.666 | 6.658 | 2.609 | 0.0492 | yes |  |
| `sides` | 0 | 1 | 12 | 13 | 5.666 | 6.673 | 2.609 | 0.0489 | yes |  |
| `heth` | 1 | 0 | 12 | 13 | 5.666 | 6.658 | 2.609 | 0.0492 | yes |  |
| `poured` | 0 | 1 | 12 | 13 | 5.666 | 6.673 | 2.609 | 0.0489 | yes |  |
| `guilty` | 0 | 1 | 12 | 13 | 5.666 | 6.673 | 2.609 | 0.0489 | yes |  |
| `sins` | 0 | 1 | 12 | 13 | 5.666 | 6.673 | 2.609 | 0.0489 | yes |  |
| `among` | 29 | 23 | 112 | 164 | 5.572 | 6.030 | 0.650 | 0.0713 |  |  |
| `does` | 1 | 2 | 18 | 21 | 5.566 | 5.819 | 1.952 | 0.0813 |  |  |
| `creep` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `settings` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `ornaments` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `clear` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `deeper` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `toe` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `forehead` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `representative` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `establish` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `restriction` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `makes` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `housings` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `jephunneh` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `measure` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `thumb` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `flung` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `resides` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `construction` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `libation` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `cud` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `jericho` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `pans` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `ammihud` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `israelite` | 0 | 0 | 7 | 7 | 5.547 | 5.547 | 3.457 | 0.0927 |  |  |
| `stones` | 1 | 5 | 25 | 31 | 5.292 | 7.421 | 1.522 | 0.0337 | yes |  |
| `cities` | 8 | 5 | 40 | 53 | 5.253 | 5.736 | 1.135 | 0.0847 |  |  |
| `some` | 18 | 7 | 63 | 88 | 5.222 | 8.755 | 0.867 | 0.0154 | yes |  |
| `twelve` | 2 | 2 | 20 | 24 | 5.218 | 5.218 | 1.738 | 0.1144 |  |  |
| `these` | 37 | 32 | 139 | 208 | 5.212 | 5.439 | 0.556 | 0.0994 |  |  |
| `then` | 34 | 31 | 132 | 197 | 5.135 | 5.215 | 0.567 | 0.1146 |  |  |
| `become` | 18 | 10 | 68 | 96 | 5.073 | 6.687 | 0.816 | 0.0486 | yes |  |
| `community` | 2 | 1 | 17 | 20 | 5.002 | 5.240 | 1.872 | 0.1130 |  |  |
| `plague` | 0 | 1 | 11 | 12 | 4.994 | 6.001 | 2.489 | 0.0725 |  |  |
| `ishmael` | 1 | 0 | 11 | 12 | 4.994 | 5.986 | 2.489 | 0.0731 |  |  |
| `eighth` | 0 | 1 | 11 | 12 | 4.994 | 6.001 | 2.489 | 0.0725 |  |  |
| `alien` | 1 | 4 | 22 | 27 | 4.981 | 6.394 | 1.583 | 0.0586 |  |  |
| `which` | 24 | 23 | 101 | 148 | 4.981 | 4.990 | 0.646 | 0.1315 |  |  |
| `bringing` | 1 | 1 | 14 | 16 | 4.882 | 4.882 | 2.086 | 0.1393 |  |  |
| `tribes` | 0 | 2 | 14 | 16 | 4.882 | 6.897 | 2.086 | 0.0463 | yes |  |
| `goats` | 2 | 0 | 14 | 16 | 4.882 | 6.868 | 2.086 | 0.0471 | yes |  |
| `portion` | 1 | 1 | 14 | 16 | 4.882 | 4.882 | 2.086 | 0.1393 |  |  |
| `judgments` | 0 | 2 | 14 | 16 | 4.882 | 6.897 | 2.086 | 0.0463 | yes |  |
| `offerings` | 0 | 6 | 24 | 30 | 4.816 | 10.860 | 1.465 | 0.0045 | yes |  |
| `anyone` | 5 | 1 | 24 | 30 | 4.816 | 6.887 | 1.465 | 0.0465 | yes |  |
| `smaller` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `plains` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `sa` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  | ⚠ |
| `tax` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `complaints` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `zibeon` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `avenger` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `covers` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `contribution` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `clay` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `almond-shaped` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `amminadab` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `rear` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `spoil` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `brings` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `creature` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `beings` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `purple` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `legacies` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `congregation's` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `spilled` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `ministering` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `fire-holder` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `lower` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `cedarwood` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `nahshon` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `batter` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `zin` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `signet` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `uncircumcised` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `skirts` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `sixteen` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `lips` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `machpelah` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `fourteenth` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `commemoration` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `vital` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `surrounding` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `coats` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `basemath` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `projections` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `employee` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `cursing` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `eliasaph` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `eliphaz` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `ne` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `embroiderer's` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `bezalel` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `mind` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `reddish` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `yx` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `dyed` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `fats` | 0 | 0 | 6 | 6 | 4.755 | 4.755 | 3.250 | 0.1414 |  |  |
| `made` | 37 | 39 | 148 | 224 | 4.707 | 4.761 | 0.508 | 0.1414 |  |  |
| `eaten` | 1 | 6 | 26 | 33 | 4.699 | 7.594 | 1.371 | 0.0306 | yes |  |
| `sacrifice` | 4 | 13 | 46 | 63 | 4.577 | 8.262 | 0.960 | 0.0208 | yes |  |
| `number` | 6 | 3 | 30 | 39 | 4.561 | 5.275 | 1.233 | 0.1107 |  |  |
| `count` | 3 | 0 | 16 | 19 | 4.451 | 7.429 | 1.787 | 0.0336 | yes |  |
| `priests` | 2 | 4 | 23 | 29 | 4.351 | 4.856 | 1.404 | 0.1414 |  |  |
| `humans` | 0 | 1 | 10 | 11 | 4.332 | 5.340 | 2.357 | 0.1061 |  |  |
| `forgiven` | 1 | 0 | 10 | 11 | 4.332 | 5.325 | 2.357 | 0.1070 |  |  |
| `cave` | 1 | 0 | 10 | 11 | 4.332 | 5.325 | 2.357 | 0.1070 |  |  |
| `domestic` | 2 | 0 | 13 | 15 | 4.289 | 6.274 | 1.983 | 0.0611 |  |  |
| `south` | 2 | 0 | 13 | 15 | 4.289 | 6.274 | 1.983 | 0.0611 |  |  |
| `not` | 108 | 176 | 465 | 749 | 4.226 | 16.588 | 0.262 | 1.34e-04 | yes |  |
| `unleavened` | 3 | 5 | 27 | 35 | 4.193 | 4.572 | 1.244 | 0.1414 |  |  |
| `female` | 4 | 0 | 18 | 22 | 4.185 | 8.156 | 1.590 | 0.0222 | yes |  |
| `fathers` | 9 | 13 | 54 | 76 | 4.156 | 4.713 | 0.827 | 0.1414 |  |  |
| `extent` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `robe's` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `dung` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `zuar` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `trumpets` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `tops` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `harshness` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `flower` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `amount` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `zelophehad's` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `devoted` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `units` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `lice` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `elizur` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `leper` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `dress` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `talents` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `hin` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `blasting` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `hezron` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `uzziel` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `seventy-five` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `walls` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `shedeur` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `ochran` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `molech` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `ahira` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `pomegranate` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `image` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `continual` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `rash` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `kohathite` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `opening` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `whore` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `glo` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  | ⚠ |
| `sanctify` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `elishama` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `meet` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `jealousy` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `ammishadday` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `zurishadday` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `hor` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `sister-piece` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `loins` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `libations` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `helon` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `creatures` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `enan` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `responsibility` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `corner` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `reuben's` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `menorah's` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `ahiezer` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `log` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `nethanel` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `defiance` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `string` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `amram` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `appraise` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `oholiab` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `pagiel` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `gamaliel` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `gideoni` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `acceptable` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `abidan` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `de` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `pedahzur` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `purchased` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `acceptance` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `thirty-two` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `size` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `shelumiel` | 0 | 0 | 5 | 5 | 3.962 | 3.962 | 3.009 | 0.1796 |  |  |
| `vow` | 1 | 2 | 15 | 18 | 3.914 | 4.166 | 1.697 | 0.1719 |  |  |
| `am` | 12 | 22 | 74 | 108 | 3.832 | 6.059 | 0.661 | 0.0700 |  |  |
| `bear` | 1 | 7 | 26 | 34 | 3.781 | 7.477 | 1.191 | 0.0327 | yes |  |
| `scarlet` | 2 | 0 | 12 | 14 | 3.711 | 5.696 | 1.872 | 0.0857 |  |  |
| `yhwh's` | 22 | 20 | 87 | 129 | 3.693 | 3.748 | 0.592 | 0.2069 |  |  |
| `command` | 2 | 2 | 17 | 21 | 3.690 | 3.690 | 1.510 | 0.2147 |  |  |
| `touch` | 2 | 2 | 17 | 21 | 3.690 | 3.690 | 1.510 | 0.2147 |  |  |
| `mistake` | 1 | 0 | 9 | 10 | 3.684 | 4.677 | 2.213 | 0.1414 |  |  |
| `carrying` | 1 | 0 | 9 | 10 | 3.684 | 4.677 | 2.213 | 0.1414 |  |  |
| `parts` | 0 | 1 | 9 | 10 | 3.684 | 4.692 | 2.213 | 0.1414 |  |  |
| `first` | 11 | 12 | 54 | 77 | 3.633 | 3.672 | 0.764 | 0.2172 |  |  |
| `ark` | 16 | 0 | 41 | 57 | 3.555 | 19.439 | 0.881 | 2.27e-05 | yes |  |
| `stand` | 3 | 12 | 39 | 54 | 3.513 | 7.750 | 0.900 | 0.0280 | yes |  |
| `manasseh` | 0 | 6 | 21 | 27 | 3.463 | 9.507 | 1.276 | 0.0101 | yes |  |
| `gold` | 10 | 10 | 48 | 68 | 3.457 | 3.457 | 0.793 | 0.2495 |  |  |
| `grain` | 12 | 16 | 62 | 90 | 3.421 | 3.864 | 0.683 | 0.1918 |  |  |
| `weight` | 3 | 0 | 14 | 17 | 3.393 | 6.371 | 1.601 | 0.0586 |  |  |
| `light` | 2 | 1 | 14 | 17 | 3.393 | 3.631 | 1.601 | 0.2229 |  |  |
| `commandments` | 2 | 1 | 14 | 17 | 3.393 | 3.631 | 1.601 | 0.2229 |  |  |
| `end` | 3 | 5 | 25 | 33 | 3.382 | 3.762 | 1.135 | 0.2055 |  |  |
| `outside` | 11 | 5 | 40 | 56 | 3.243 | 4.863 | 0.846 | 0.1411 |  |  |
| `are` | 55 | 46 | 179 | 280 | 3.224 | 3.740 | 0.373 | 0.2078 |  |  |
| `cherub` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `residences` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `donate` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `regurgitates` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `dan's` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `flowers` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `ishmael's` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `chains` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `ceased` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `beard` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `belted` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `owl` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `spirits` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `charms` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `wafer` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `astray` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `rope` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `izhar` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `elon` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `gerah` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `wool` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `reap` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `basis` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `swarms` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `cutting` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `human's` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `chase` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `thanks` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `ash` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `perversion` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `head's` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `ark's` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `developed` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `zohar` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `azazel` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `gra` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `gme` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  | ⚠ |
| `dishes` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `scouted` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `thirty-seven` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `seas` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `cake` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `bake` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `donated` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `eighty` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `low` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `ram's` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `atone` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `dedication` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `unfitting` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `gershonite` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `dishon` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `th` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `omer` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `creeps` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `scales` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `commemorative` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `completion` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `panel` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `phinehas` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `po` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `ju` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `lizard` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `na` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `ropes` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `homeborn` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `flying` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `plating` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `jealousies` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `aside` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `inscriptions` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `grate` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `hats` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `ephod` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `kinds` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `deuel` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `wafers` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `connect` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `manslayer` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `goat's` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `trade` | 0 | 0 | 4 | 4 | 3.170 | 3.170 | 2.720 | 0.2834 |  |  |
| `homes` | 1 | 1 | 11 | 13 | 3.150 | 3.150 | 1.752 | 0.2866 |  |  |
| `produce` | 1 | 1 | 11 | 13 | 3.150 | 3.150 | 1.752 | 0.2866 |  |  |
| `esau's` | 2 | 0 | 11 | 13 | 3.150 | 5.135 | 1.752 | 0.1207 |  |  |
| `sinai` | 5 | 0 | 18 | 23 | 3.103 | 8.066 | 1.300 | 0.0234 | yes |  |
| `as` | 87 | 65 | 256 | 408 | 3.063 | 5.210 | 0.301 | 0.1148 |  |  |
| `according` | 8 | 10 | 43 | 61 | 3.053 | 3.229 | 0.784 | 0.2834 |  |  |
| `tithe` | 0 | 1 | 8 | 9 | 3.053 | 4.060 | 2.053 | 0.1796 |  |  |
| `wear` | 0 | 1 | 8 | 9 | 3.053 | 4.060 | 2.053 | 0.1796 |  |  |
| `ashes` | 1 | 0 | 8 | 9 | 3.053 | 4.045 | 2.053 | 0.1796 |  |  |
| `relative` | 0 | 1 | 8 | 9 | 3.053 | 4.060 | 2.053 | 0.1796 |  |  |
| `fellow` | 0 | 1 | 8 | 9 | 3.053 | 4.060 | 2.053 | 0.1796 |  |  |
| `appearance` | 0 | 3 | 13 | 16 | 2.890 | 5.912 | 1.498 | 0.0767 |  |  |
| `fruitful` | 1 | 2 | 13 | 16 | 2.890 | 3.142 | 1.498 | 0.2876 |  |  |
| `passover` | 1 | 2 | 13 | 16 | 2.890 | 3.142 | 1.498 | 0.2876 |  |  |
| `travel` | 1 | 2 | 13 | 16 | 2.890 | 3.142 | 1.498 | 0.2876 |  |  |
| `put` | 37 | 48 | 151 | 236 | 2.766 | 3.878 | 0.376 | 0.1903 |  |  |
| `laws` | 1 | 3 | 15 | 19 | 2.749 | 3.519 | 1.334 | 0.2398 |  |  |
| `observe` | 1 | 6 | 21 | 28 | 2.623 | 5.518 | 1.070 | 0.0944 |  |  |
| `redeemed` | 0 | 2 | 10 | 12 | 2.609 | 4.624 | 1.620 | 0.1414 |  |  |
| `basket` | 0 | 2 | 10 | 12 | 2.609 | 4.624 | 1.620 | 0.1414 |  |  |
| `committed` | 0 | 2 | 10 | 12 | 2.609 | 4.624 | 1.620 | 0.1414 |  |  |
| `hyssop` | 0 | 1 | 7 | 8 | 2.441 | 3.448 | 1.872 | 0.2499 |  |  |
| `sixty` | 1 | 0 | 7 | 8 | 2.441 | 3.434 | 1.872 | 0.2510 |  |  |
| `pour` | 0 | 1 | 7 | 8 | 2.441 | 3.448 | 1.872 | 0.2499 |  |  |
| `act` | 0 | 1 | 7 | 8 | 2.441 | 3.448 | 1.872 | 0.2499 |  |  |
| `hoof` | 0 | 1 | 7 | 8 | 2.441 | 3.448 | 1.872 | 0.2499 |  |  |
| `m` | 1 | 0 | 7 | 8 | 2.441 | 3.434 | 1.872 | 0.2510 |  | ⚠ |
| `assembled` | 0 | 1 | 7 | 8 | 2.441 | 3.448 | 1.872 | 0.2499 |  |  |
| `cast` | 0 | 1 | 7 | 8 | 2.441 | 3.448 | 1.872 | 0.2499 |  |  |
| `camping` | 0 | 1 | 7 | 8 | 2.441 | 3.448 | 1.872 | 0.2499 |  |  |
| `burning` | 1 | 0 | 7 | 8 | 2.441 | 3.434 | 1.872 | 0.2510 |  |  |
| `faces` | 0 | 3 | 12 | 15 | 2.408 | 5.430 | 1.387 | 0.0998 |  |  |
| `fifth` | 0 | 3 | 12 | 15 | 2.408 | 5.430 | 1.387 | 0.0998 |  |  |
| `meat` | 1 | 10 | 28 | 39 | 2.385 | 8.617 | 0.860 | 0.0164 | yes |  |
| `until` | 22 | 19 | 79 | 120 | 2.377 | 2.515 | 0.488 | 0.3223 |  |  |
| `levi's` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `pallu` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `crimes` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `shaft` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `banded` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `ninth` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `jamin` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `rage` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `settled` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `concentration` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `jars` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `flags` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `assemble` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `doubled` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `restricted` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `gifts` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `assemblies` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `complain` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `spots` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `talent` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `yellow` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `proclaim` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `sash` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `uri` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `shovels` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `idols` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `conceptions` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `restrictions` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `ahisamach` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `zelophehad` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `jeush` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `produces` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `naaman` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `network` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `source` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `bird's` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `gives` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `deep` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `beriah` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `limb` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `thus` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `functioning` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `tirzah` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `scorn` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `carmi` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `asher's` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `husband's` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `hoglah` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `purify` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `breastplate` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `hearts` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `confess` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `seeds` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `terah` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `daughter's` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `oven` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `watching` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `glorified` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `slaughters` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `twenty-two` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `forks` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `commit` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `inspired` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `ointment-maker` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `ezer` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `presented` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `extend` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `imnah` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `griddle` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `black` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `fifty-three` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `remainder` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `northern` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `redeemer` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `malignant` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `harvest's` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `evaluation` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `weaver's` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `hooves` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `exodus` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `lights` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `jalam` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `rows` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `cannot` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `once` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `headdress` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `twisted` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `distributed` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `fins` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `purchase` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `hepher` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `horites` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `pursuing` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `nebaioth` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `western` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `suet` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `two-tenths` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `community's` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `design` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `southern` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `masses` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `jachin` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `becomes` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `revenge` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `dishan` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `lotan` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `exchange` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `tent's` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `juxtaposition` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `larger` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `eastward` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `fringe` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `tongs` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `mahlah` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `mate` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `fifty-seven` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `rinsed` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `shobal` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `transformed` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `bells` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `corpse` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `rainbow` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `beside` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `crop` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `mark` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `gershonites` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `foreigner` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `impurities` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `cow` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `aunt` | 0 | 0 | 3 | 3 | 2.377 | 2.377 | 2.357 | 0.3223 |  |  |
| `water` | 37 | 19 | 103 | 159 | 2.375 | 6.493 | 0.424 | 0.0551 |  |  |
| `fill` | 1 | 3 | 14 | 18 | 2.309 | 3.078 | 1.238 | 0.2976 |  |  |
| `clothing` | 0 | 5 | 16 | 21 | 2.263 | 7.299 | 1.135 | 0.0365 | yes |  |
| `making` | 5 | 1 | 18 | 24 | 2.248 | 4.319 | 1.059 | 0.1566 |  |  |
| `has` | 40 | 62 | 173 | 275 | 2.203 | 5.816 | 0.310 | 0.0814 |  |  |
| `creeping` | 2 | 0 | 9 | 11 | 2.093 | 4.078 | 1.476 | 0.1796 |  |  |
| `bitter` | 2 | 0 | 9 | 11 | 2.093 | 4.078 | 1.476 | 0.1796 |  |  |
| `enough` | 1 | 1 | 9 | 11 | 2.093 | 2.093 | 1.476 | 0.3532 |  |  |
| `wild` | 3 | 0 | 11 | 14 | 1.950 | 4.928 | 1.266 | 0.1353 |  |  |
| `rings` | 0 | 3 | 11 | 14 | 1.950 | 4.972 | 1.266 | 0.1316 |  |  |
| `injury` | 1 | 2 | 11 | 14 | 1.950 | 2.203 | 1.266 | 0.3294 |  |  |
| `slaughtered` | 2 | 1 | 11 | 14 | 1.950 | 2.188 | 1.266 | 0.3326 |  |  |
| `each` | 16 | 29 | 83 | 128 | 1.948 | 4.791 | 0.426 | 0.1414 |  |  |
| `fall` | 3 | 1 | 13 | 17 | 1.891 | 2.631 | 1.135 | 0.3223 |  |  |
| `he-goats` | 1 | 3 | 13 | 17 | 1.891 | 2.660 | 1.135 | 0.3223 |  |  |
| `bird` | 4 | 0 | 13 | 17 | 1.891 | 5.861 | 1.135 | 0.0792 |  |  |
| `birds` | 4 | 2 | 17 | 23 | 1.881 | 2.357 | 0.979 | 0.3223 |  |  |
| `jordan` | 6 | 0 | 17 | 23 | 1.881 | 7.838 | 0.979 | 0.0265 | yes |  |
| `take` | 48 | 38 | 146 | 232 | 1.875 | 2.644 | 0.311 | 0.3223 |  |  |
| `aholibamah` | 1 | 0 | 6 | 7 | 1.855 | 2.848 | 1.665 | 0.3223 |  |  |
| `cords` | 1 | 0 | 6 | 7 | 1.855 | 2.848 | 1.665 | 0.3223 |  |  |
| `sixth` | 1 | 0 | 6 | 7 | 1.855 | 2.848 | 1.665 | 0.3223 |  |  |
| `price` | 1 | 0 | 6 | 7 | 1.855 | 2.848 | 1.665 | 0.3223 |  |  |
| `dip` | 0 | 1 | 6 | 7 | 1.855 | 2.863 | 1.665 | 0.3223 |  |  |
| `square` | 1 | 0 | 6 | 7 | 1.855 | 2.848 | 1.665 | 0.3223 |  |  |
| `share` | 0 | 1 | 6 | 7 | 1.855 | 2.863 | 1.665 | 0.3223 |  |  |
| `someone` | 0 | 1 | 6 | 7 | 1.855 | 2.863 | 1.665 | 0.3223 |  |  |
| `tomb` | 1 | 0 | 6 | 7 | 1.855 | 2.848 | 1.665 | 0.3223 |  |  |
| `breach` | 1 | 0 | 6 | 7 | 1.855 | 2.848 | 1.665 | 0.3223 |  |  |
| `bands` | 0 | 1 | 6 | 7 | 1.855 | 2.863 | 1.665 | 0.3223 |  |  |
| `scout` | 1 | 0 | 6 | 7 | 1.855 | 2.848 | 1.665 | 0.3223 |  |  |
| `machir` | 0 | 1 | 6 | 7 | 1.855 | 2.863 | 1.665 | 0.3223 |  |  |
| `horsemen` | 1 | 0 | 6 | 7 | 1.855 | 2.848 | 1.665 | 0.3223 |  |  |
| `branch` | 1 | 0 | 6 | 7 | 1.855 | 2.848 | 1.665 | 0.3223 |  |  |
| `close` | 6 | 6 | 28 | 40 | 1.847 | 1.847 | 0.739 | 0.4115 |  |  |
| `keep` | 6 | 3 | 22 | 31 | 1.673 | 2.387 | 0.794 | 0.3223 |  |  |
| `eat` | 31 | 23 | 95 | 149 | 1.622 | 2.423 | 0.360 | 0.3223 |  |  |
| `reuben` | 3 | 5 | 20 | 28 | 1.622 | 2.001 | 0.820 | 0.3719 |  |  |
| `wall` | 0 | 2 | 8 | 10 | 1.605 | 3.620 | 1.316 | 0.2240 |  |  |
| `spill` | 0 | 2 | 8 | 10 | 1.605 | 3.620 | 1.316 | 0.2240 |  |  |
| `property` | 0 | 2 | 8 | 10 | 1.605 | 3.620 | 1.316 | 0.2240 |  |  |
| `eight` | 2 | 0 | 8 | 10 | 1.605 | 3.591 | 1.316 | 0.2285 |  |  |
| `right` | 7 | 9 | 34 | 50 | 1.604 | 1.800 | 0.614 | 0.4230 |  |  |
| `malchiel` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `gad's` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `keeps` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `year-old` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `herbs` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `loaf` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `drained` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `hamath` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `mushi` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `guni` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `whichever` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `worth` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `sered` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `scraped` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `wronged` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `pieces` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `hamul` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `regulation` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `streams` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `jezer` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `parched` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `jahleel` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `cozbi` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `ledge` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `connection` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `timna` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `sir` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `repugnant` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `including` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `omar` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `prune` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `spun` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `di` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  | ⚠ |
| `purity` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `violence` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `zerahites` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `kohath's` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `scheming` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `swell` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `thirty-five` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `broke` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `elzaphan` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `chance` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `ys` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  | ⚠ |
| `lifetime` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `animal's` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `gatam` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `parallel` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `sixty-one` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `aberration` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `suffice` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `net` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `baal-zephon` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `adjacent` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `discipline` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `hollow` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `breasts` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `ard` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `re` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  | ⚠ |
| `integrated` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `sag` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `nine` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `arose` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `zepho` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `express` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `yields` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `azmon` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `nahath` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `fifty-nine` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `groats` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `jochebed` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `devastate` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `reubenites` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `handfuls` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `injustice` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `develop` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `shimei` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `pools` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `seventeenth` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `regurgitate` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `tola` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `holiness` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `vomit` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `scar` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `shuni` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `hawk` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `mo` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  | ⚠ |
| `scabbed` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `sprinkled` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `razor` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `inspect` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `twenty-eight` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `mahli` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `omer-ful` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `aligned` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `ashbel` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `firstling` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `becher` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `divorc` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `hairless` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `hori` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `amen` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `engravings` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `winepress` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `sidewalls` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `yl` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  | ⚠ |
| `pollute` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `kadesh-barnea` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `layer` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `shuthelah` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `ataroth` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `ointment` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `jas` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `profanes` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `closest` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `pe` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  | ⚠ |
| `thirty-three` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `doubles` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `winged` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `entirely` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `untrimmed` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `drawers` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `falsehood` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `mail` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `gleaning` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `serpent` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `choice` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `buys` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `sworn` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `prominent` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `detest` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `sits` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `pushed` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `afflict` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `accept` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `fifty-four` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `fifteenth` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `twenty-four` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `wooden` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `amram's` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `inward` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `korahites` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `seventy-three` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `nebo` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `villages` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `pi-hahiroth` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `horse` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `sixty-two` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `hazar-enan` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `arba` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `ewe-lamb` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `ra` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  | ⚠ |
| `donations` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `object` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `adultery` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `shammah` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `shem's` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `b` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  | ⚠ |
| `embroiderer` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `rebelled` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `dibon` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `vain` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `burns` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `appearing` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `ninety` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `attend` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `jahzeel` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `twos` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `appendage` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `collecting` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `vinegar` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `designer` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `subdued` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `shuhamites` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `midianites` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `frame's` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `z` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  | ⚠ |
| `decontaminate` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `seventy-four` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `areli` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `greenish` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `aromatic` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `vintage` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `pots` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `arrangement` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `canals` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `shorts` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `jaci` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `ru` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `fountains` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `hezronites` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `mountings` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `faith` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `elizaphan` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `forty-six` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `encampments` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `cow's` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `forty-one` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `libni` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `handbreadth` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `uncle` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `sores` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `traded` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `scurvied` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `wring` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `issachar's` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `blast` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `one-year-olds` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `developing` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `kohathites` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `detached` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `ham's` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `menstruation` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `residing` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `simeonites` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `uncle's` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `ohad` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `serah` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `pa` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `lamp` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `slain` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `cleared` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `shepham` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `affliction's` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `shillem` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `ghosts` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `nobah` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `eri` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `fences` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `elongated` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `washing` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `fellow's` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `urim` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `ga` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `merarite` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `offenses` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `permanently` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `hoshea` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `naphtali's` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `ruin` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `rub` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `rivers` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `beam` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `leftover` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `menstrual` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `mishael` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `observed` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `apertures` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `jemuel` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `accounts` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `divorced` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `fire-roasted` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `boards` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `elealeh` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `visitors` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `inscribe` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `contributions` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `diminish` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `shimron` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `strengthened` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `eagle` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `seventy-two` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `ishvi` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `serpents` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `consecrates` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `zur` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `quantities` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `acquaintances` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `carved` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `bar` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `sixty-four` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `raven` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `vomited` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `languages` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `vulture` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `thirty-six` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `battered` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `boiled` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `zebulun's` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `northward` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `spatter` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `pphi` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `instant` | 0 | 0 | 2 | 2 | 1.585 | 1.585 | 1.872 | 0.4455 |  |  |
| `lay` | 5 | 2 | 18 | 25 | 1.575 | 2.512 | 0.853 | 0.3223 |  |  |
| `so` | 41 | 48 | 148 | 237 | 1.573 | 2.023 | 0.281 | 0.3666 |  |  |
| `seventy` | 1 | 5 | 16 | 22 | 1.536 | 3.666 | 0.894 | 0.2180 |  |  |
| `aram` | 3 | 0 | 10 | 13 | 1.520 | 4.499 | 1.135 | 0.1414 |  |  |
| `nun` | 0 | 3 | 10 | 13 | 1.520 | 4.542 | 1.135 | 0.1414 |  |  |
| `washed` | 3 | 0 | 10 | 13 | 1.520 | 4.499 | 1.135 | 0.1414 |  |  |
| `herself` | 3 | 0 | 10 | 13 | 1.520 | 4.499 | 1.135 | 0.1414 |  |  |
| `comes` | 2 | 3 | 14 | 19 | 1.509 | 1.661 | 0.949 | 0.4455 |  |  |
| `yourselves` | 1 | 3 | 12 | 16 | 1.499 | 2.268 | 1.024 | 0.3223 |  |  |
| `death` | 8 | 9 | 35 | 52 | 1.447 | 1.497 | 0.571 | 0.4691 |  |  |
| `covenant` | 9 | 7 | 33 | 49 | 1.375 | 1.542 | 0.572 | 0.4585 |  |  |
| `consecrated` | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| `desecrated` | 0 | 1 | 5 | 6 | 1.305 | 2.312 | 1.424 | 0.3223 |  |  |
| `acquired` | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| `laid` | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| `fifteen` | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| `tail` | 0 | 1 | 5 | 6 | 1.305 | 2.312 | 1.424 | 0.3223 |  |  |
| `addition` | 0 | 1 | 5 | 6 | 1.305 | 2.312 | 1.424 | 0.3223 |  |  |
| `separate` | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| `subtracted` | 0 | 1 | 5 | 6 | 1.305 | 2.312 | 1.424 | 0.3223 |  |  |
| `carcasses` | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| `established` | 0 | 1 | 5 | 6 | 1.305 | 2.312 | 1.424 | 0.3223 |  |  |
| `prey` | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| `facing` | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| `hidden` | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| `broken` | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| `robe` | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| `leaven` | 0 | 1 | 5 | 6 | 1.305 | 2.312 | 1.424 | 0.3223 |  |  |
| `ephah` | 0 | 1 | 5 | 6 | 1.305 | 2.312 | 1.424 | 0.3223 |  |  |
| `shadday` | 0 | 1 | 5 | 6 | 1.305 | 2.312 | 1.424 | 0.3223 |  |  |
| `travels` | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| `kings` | 1 | 0 | 5 | 6 | 1.305 | 2.297 | 1.424 | 0.3223 |  |  |
| `wings` | 0 | 1 | 5 | 6 | 1.305 | 2.312 | 1.424 | 0.3223 |  |  |
| `accepted` | 0 | 1 | 5 | 6 | 1.305 | 2.312 | 1.424 | 0.3223 |  |  |
| `redeem` | 3 | 4 | 17 | 24 | 1.268 | 1.379 | 0.772 | 0.5053 |  |  |
| `off` | 8 | 12 | 39 | 59 | 1.249 | 1.859 | 0.496 | 0.4081 |  |  |
| `appointed` | 3 | 3 | 15 | 21 | 1.216 | 1.216 | 0.804 | 0.5624 |  |  |
| `mount` | 5 | 1 | 15 | 21 | 1.216 | 3.287 | 0.804 | 0.2767 |  |  |
| `silver` | 20 | 16 | 64 | 100 | 1.179 | 1.471 | 0.372 | 0.4773 |  |  |
| `simeon` | 3 | 2 | 13 | 18 | 1.171 | 1.309 | 0.845 | 0.5284 |  |  |
| `circumcised` | 5 | 0 | 13 | 18 | 1.171 | 6.135 | 0.845 | 0.0668 |  |  |
| `abihu` | 0 | 2 | 7 | 9 | 1.154 | 3.169 | 1.135 | 0.2834 |  |  |
| `caleb` | 2 | 0 | 7 | 9 | 1.154 | 3.140 | 1.135 | 0.2878 |  |  |
| `magicians` | 0 | 2 | 7 | 9 | 1.154 | 3.169 | 1.135 | 0.2834 |  |  |
| `hebron` | 1 | 1 | 7 | 9 | 1.154 | 1.154 | 1.135 | 0.5853 |  |  |
| `nadab` | 0 | 2 | 7 | 9 | 1.154 | 3.169 | 1.135 | 0.2834 |  |  |
| `open` | 1 | 1 | 7 | 9 | 1.154 | 1.154 | 1.135 | 0.5853 |  |  |
| `north` | 2 | 0 | 7 | 9 | 1.154 | 3.140 | 1.135 | 0.2878 |  |  |
| `carry` | 5 | 4 | 20 | 29 | 1.118 | 1.191 | 0.660 | 0.5711 |  |  |
| `whose` | 8 | 0 | 18 | 26 | 1.051 | 8.993 | 0.672 | 0.0139 | yes |  |
| `ephraim` | 0 | 5 | 12 | 17 | 0.864 | 5.901 | 0.734 | 0.0772 |  |  |
| `gilead` | 1 | 3 | 10 | 14 | 0.811 | 1.580 | 0.772 | 0.4468 |  |  |
| `shed` | 1 | 0 | 4 | 5 | 0.803 | 1.795 | 1.135 | 0.4236 |  |  |
| `statutory` | 0 | 1 | 4 | 5 | 0.803 | 1.810 | 1.135 | 0.4202 |  |  |
| `salt` | 1 | 0 | 4 | 5 | 0.803 | 1.795 | 1.135 | 0.4236 |  |  |
| `forty-five` | 1 | 0 | 4 | 5 | 0.803 | 1.795 | 1.135 | 0.4236 |  |  |
| `body` | 0 | 1 | 4 | 5 | 0.803 | 1.810 | 1.135 | 0.4202 |  |  |
| `distinguished` | 0 | 1 | 4 | 5 | 0.803 | 1.810 | 1.135 | 0.4202 |  |  |
| `carries` | 0 | 1 | 4 | 5 | 0.803 | 1.810 | 1.135 | 0.4202 |  |  |
| `basins` | 0 | 1 | 4 | 5 | 0.803 | 1.810 | 1.135 | 0.4202 |  |  |
| `separation` | 1 | 0 | 4 | 5 | 0.803 | 1.795 | 1.135 | 0.4236 |  |  |
| `new` | 0 | 1 | 4 | 5 | 0.803 | 1.810 | 1.135 | 0.4202 |  |  |
| `therefore` | 1 | 0 | 4 | 5 | 0.803 | 1.795 | 1.135 | 0.4236 |  |  |
| `elevated` | 0 | 1 | 4 | 5 | 0.803 | 1.810 | 1.135 | 0.4202 |  |  |
| `span` | 0 | 1 | 4 | 5 | 0.803 | 1.810 | 1.135 | 0.4202 |  |  |
| `born` | 6 | 2 | 17 | 25 | 0.802 | 2.283 | 0.592 | 0.3223 |  |  |
| `seed's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `starvation` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `havvoth-jair` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `mounted` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `compound` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `receded` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ejecting` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `crossing` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `mirrors` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `sha` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  | ⚠ |
| `haste` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `morning's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `estimate` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `faraway` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `inter-course` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `hupham` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `generate` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `togarmah` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `abarim` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `arod` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `harvesting` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ararat` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `powder` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `shelomith` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `leg` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `mushites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `spear` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `galbanum` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `hemdan` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `afflicts` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `point` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `relatives` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `elonites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `bukki` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `sibmah` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `subdue` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `inherits` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `towns` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `migdol` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `patterned` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `leaks` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `coated` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `secular` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `hazar-addar` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `brass` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `rival` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `quantity` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `mizzah` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `profaned` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `coals` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `moons` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `murdered` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `bat` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `circumcise` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `alert` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `nemuelites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `naamites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `oneself` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `paws` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `beams` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `foe` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `belt` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `tithes` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `beeri` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `salted` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `stumbling` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `arelites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `elam` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `figures` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `jaminites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `testicles` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `meshech` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `wonder` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `bruised` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `vophsi` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `aroer` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `el-isha` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `zoan` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `lots` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `tree's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `hanging` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `murder` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `wagon` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `shine` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `abiasaph` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `double-fold` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `requiring` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `offshoot` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `rock-badger` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `principal` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `tetter` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `farther` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `elidad` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `teemed` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `atnez` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `eighty-six` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `freedom` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `likeness` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ghost` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `desecrating` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `extracted` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `frustration` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `threads` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `rains` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ain` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `zebulunites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `punites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `expiate` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `eleventh` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `afflicting` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `gether` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `liberty` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `stories` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `grieving` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `mouths` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `he-lambs` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `haggites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `exploited` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `geuel` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `failed` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `inhabitants` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `adbeel` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `gomer's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `decreased` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `hemam` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `deposited` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `rekem` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `substantial` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `kenath` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `pallu's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `grieve` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `shemidaites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `selling` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `fistful` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `asriel` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `sown` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `chooses` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `tolaites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `inaccessible` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `bereave` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `desolation` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `izharite` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `southward` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `conveyance` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `fifty-one` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `scoured` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `one-year-old` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `becherites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `employee's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `mahlite` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `raamah` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `zedad` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `gathers` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `oznites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `shuham` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `fire-holder-full` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `zuriel` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `handiwork` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `multiplying` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `mouse` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `muddled` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `lael` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `gaddiel` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `beard's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `head-opening` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `madai` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `heberites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `indicates` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `requiting` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `tarshish` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `divide` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `dodanim` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `seredites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `adulterer` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `poti-phera` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `fifty-two` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `final` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `streaks` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `granddaughters` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `tin` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `partial` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ebal` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `widow's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `hot` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `acquaintance` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `palluites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `occasion` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `sithri` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `menstruating` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `merarites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `accumulated` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `rooms` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `jetur` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `fastened` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `pick` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `overthrowing` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `warriors` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `wide` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `stove` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `heron` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `hatred` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `rich` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `tahanites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `gershon's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `baal-meon` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `sashes` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `voices` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `convocation` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `souls` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `cassia` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `elderly` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `trim` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `gomer` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `merari's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `virginity` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `extending` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `walled` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `shame` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `pronouncement` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `strip` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `uncles` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `jair` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `kenizzite` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `jointed` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `kedmah` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `daughter-in-law's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `uzzielite` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `elkanah` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `sixty-five` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `machirites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `pride` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `judith` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `stork` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `tended` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `eranites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ephron's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `thirteen` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `forty-three` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `thighs` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `rehob` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `wages` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `gadites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `compensation` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `forth` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `fly` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `beth-nimrah` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `magog` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `sheets` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `sebam` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `libnite` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `burners` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `strengthen` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `perezites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `consumption` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `coerced` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ardites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `beth-haran` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `cripple` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `akrabim` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `jogli` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `beriites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `abominable` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `eliphaz's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `desolated` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `hare` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `perish` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `helek` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `crimson` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `overs` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `mustache` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `samuel` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ishvah` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `hunchback` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `tubal` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `recorded` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `pronouncing` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `leavening` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `islands` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `column's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `satyrs` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `clouds` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `obstructed` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `zimri` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `beriah's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `gileadites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `twenty-nine` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `measured` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `repute` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ishvites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `worms` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `gaddi` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `horite` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `adulteress` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `silent` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `cutter` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `footing` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `amramite` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `dread` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `gecko` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `regulate` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `supervise` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `weaver` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `announcement` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ashkenaz` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `mishma` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `hebronites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `zichri` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `groaned` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `melted` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `jogbehah` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `engraver` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `jahzeelites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `elisheba` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `twenty-first` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `slashed` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `floodwaters` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `puts` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `reba` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `tema` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `piece` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `desires` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `plates` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `evi` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `shephupham` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `shemida` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ammiel` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `raamah's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `tu` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  | ⚠ |
| `outstretched` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `hovering` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `aged` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `igal` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `shammua` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `nemuel` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `stumble` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `concentrated` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `atroth-shophan` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `belaites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `spice` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `mash` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ziphion` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `gunites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `restricting` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `outsider's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `inheritance` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `chronic` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `paltiel` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `sanctuary` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `outward` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `arodi` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `shaphat` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `determined` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `shunites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `sanctified` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `eighty-three` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `mibsam` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `eshban` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `riblah` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `tattoo` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `meant` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `array` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `cush's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `mahalath` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `cost` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `devote` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `revolt` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `faintness` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `reparation` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `text` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `hepherites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `hushim` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `attends` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `dumah` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `liquid` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `roads` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `lud` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `consume` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `rate` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `abihail` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `hamulites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `scab's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `shuthelahites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `talmai` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `shiphtan` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `customs` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `pound` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `loosen` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `male's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `exhausting` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `bitterness` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `twenty-three` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `haggai` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `puvah` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `hung` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `machi` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `hul` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `zaavan` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `robbery` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `worm` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `purifying` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `attached` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ascent` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `michael` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `zephonites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `oven-baked` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `alerted` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `belongs` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `malchielites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `conspiracies` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `avenger's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `eran` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `sheds` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `disperse` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `job` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `desecrates` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `burying` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `heber` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `mushite` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `bottoms` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `takes` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ziphron` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `dispossesses` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `sore` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `libnites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `homer` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `defile` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `loosed` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `grasshopper` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `pattern` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `stank` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `intercede` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `flaw` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `vowed` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `extract` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `earrings` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `shechemites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `nahbi` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `raphu` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `aram's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `clothed` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `sorcerers` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `yawan` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `sethur` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `aran` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `nazirite's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `producing` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `reckoned` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `iscah` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `protection` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `rob` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `feathers` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `strengthening` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `border's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `slander` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `current` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `riphath` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `perez's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `functioned` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `assembling` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `tremendous` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `slipping` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `twenty-seventh` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `position` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `harden` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ride` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `jashub` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `exceeded` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `shuphamites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `soothsaying` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `mizzeh` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `shillemites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `cheran` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `shortage` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `helekites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `shelanites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `clans` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `raw` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `scaly` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `mi` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `gopher` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `sowing` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `inscription` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `witnesses` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `inquired` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `flings` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `huphamites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `alvan` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `leap` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `erites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `frost` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `sabtah` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ehi` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `iezer` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `stacte` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `mounting` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `demolished` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `asrielites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `levy` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `toil` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `retribution` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `formless` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `year-by-year` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `calling` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `elohim` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `weave` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `consistently` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `flay` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `jachinites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `huppim` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `orders` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `rip` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `assir` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `gera` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `seeding` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `twelfth` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `overthrow` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `onam` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `pelican` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `yawan's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `unsheathe` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `expressly` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `cricket` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `first-born` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `respect` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `puwah` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `spotting` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `figured` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `parnach` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `deterioration` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `earring` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `dropped` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `cormorant` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `hanniel` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `shepho` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `pedahel` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `grapevine` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `akan` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ahiram` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `mountaintop` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `expire` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `settlements` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `flight` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `forty-eight` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `susi` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `twentieth` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `nighthawk` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `wise-hearted` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `seba` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `remove` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ashbelites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `fewer` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `mahlites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `brooches` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `cinnamon` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `palti` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `juice` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `model` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `lotan's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `fragrance` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `kittim` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `rosh` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `expiated` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `moaning` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `arodites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `eyebrows` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `growths` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `block` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ninety-nine` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `naphish` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `engraver's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `twenty-five` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `establishing` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `nepheg` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `fowl` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `tributes` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `exploit` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `creating` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `shouted` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `consuming` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `chameleon` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `eastern` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `tall` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `coating` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `seagull` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `one-tenth` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `nimrah` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `horn-blasting` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `gemalli` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `seventy-six` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `duration` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `criticize` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `mutilated` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `vineyard's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `grate's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `beon` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `determine` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `sabteca` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `stomach` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `shimeite` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `hoopoe` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `measurement` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `rat` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `complaining` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `armlet` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `yielded` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `foil` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `disciplined` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `massa` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `dibri` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `sixty-six` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `returns` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `individual` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `yaphet's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `tummim` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `shapeless` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `bracelet` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `staffs` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `fever` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `sacrificial` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `haggi` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `moves` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `enslaving` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `casting` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `enclosure` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ripe` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `grandson` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `azzan` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `kiriathaim` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `dwarf` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `sodi` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `onycha` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `three-tenths` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ozni` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `kedar` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `sticks` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `chew` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `hanochites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ephod's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `jashubites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `scouting` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ahihud` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ezbon` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `pig` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `manahath` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `carmites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `salu` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ajah` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `yarn` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `backbone` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `commands` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `zaccur` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `tahan` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `roving` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `appears` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `rebels` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `kite` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `grandsons` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `putiel` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `attach` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `flows` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `muppim` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `receding` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `turtledove` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `reed` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `eminence` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `jahleelites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `jezerites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ahiramites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `loaves` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `atoning` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `robbed` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `chiefdoms` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `korah's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `chislon` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `bilhan` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `iezerites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `merchant's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `zephon` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `hever` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `hundredth` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `sprinkles` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `foreigner's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `tombs` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `shimronites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `excluded` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `lacking` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `conceived` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `scraping` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `hebronite` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `images` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `weighed` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `swarmed` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `kinneret` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `prostitution` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `cistern` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `senior` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ithran` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `tiras` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `shelomi` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `saulites` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `murderer's` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `falcon` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `forty-two` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `forty-nine` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `sheshai` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `ahiman` | 0 | 0 | 1 | 1 | 0.792 | 0.792 | 1.135 | 0.5969 |  |  |
| `fourth` | 3 | 0 | 8 | 11 | 0.768 | 3.746 | 0.830 | 0.2069 |  |  |
| `lands` | 2 | 1 | 8 | 11 | 0.768 | 1.006 | 0.830 | 0.5969 |  |  |
| `whether` | 2 | 1 | 8 | 11 | 0.768 | 1.006 | 0.830 | 0.5969 |  |  |
| `haran` | 3 | 0 | 8 | 11 | 0.768 | 3.746 | 0.830 | 0.2069 |  |  |
| `camps` | 3 | 0 | 8 | 11 | 0.768 | 3.746 | 0.830 | 0.2069 |  |  |
| `bed` | 1 | 2 | 8 | 11 | 0.768 | 1.021 | 0.830 | 0.5969 |  |  |
| `mamre` | 2 | 0 | 6 | 8 | 0.749 | 2.735 | 0.928 | 0.3223 |  |  |
| `same` | 2 | 0 | 6 | 8 | 0.749 | 2.735 | 0.928 | 0.3223 |  |  |
| `foreskin` | 2 | 0 | 6 | 8 | 0.749 | 2.735 | 0.928 | 0.3223 |  |  |
| `aliens` | 0 | 2 | 6 | 8 | 0.749 | 2.764 | 0.928 | 0.3223 |  |  |
| `high` | 1 | 1 | 6 | 8 | 0.749 | 0.749 | 0.928 | 0.6138 |  |  |
| `eliab` | 2 | 0 | 6 | 8 | 0.749 | 2.735 | 0.928 | 0.3223 |  |  |
| `dim` | 2 | 0 | 6 | 8 | 0.749 | 2.735 | 0.928 | 0.3223 |  |  |
| `goes` | 2 | 0 | 6 | 8 | 0.749 | 2.735 | 0.928 | 0.3223 |  |  |
| `reuel` | 2 | 0 | 6 | 8 | 0.749 | 2.735 | 0.928 | 0.3223 |  |  |
| `lives` | 2 | 0 | 6 | 8 | 0.749 | 2.735 | 0.928 | 0.3223 |  |  |
| `near` | 1 | 1 | 6 | 8 | 0.749 | 0.749 | 0.928 | 0.6138 |  |  |
| `levi` | 5 | 2 | 15 | 22 | 0.732 | 1.668 | 0.597 | 0.4455 |  |  |
| `except` | 3 | 4 | 15 | 22 | 0.732 | 0.842 | 0.597 | 0.5969 |  |  |
| `consecrate` | 3 | 2 | 11 | 16 | 0.593 | 0.731 | 0.614 | 0.6215 |  |  |
| `anything` | 4 | 4 | 16 | 24 | 0.580 | 0.580 | 0.507 | 0.6854 |  |  |
| `buried` | 1 | 3 | 9 | 13 | 0.526 | 1.295 | 0.628 | 0.5333 |  |  |
| `west` | 3 | 1 | 9 | 13 | 0.526 | 1.266 | 0.628 | 0.5439 |  |  |
| `while` | 3 | 1 | 9 | 13 | 0.526 | 1.266 | 0.628 | 0.5439 |  |  |
| `animal` | 12 | 13 | 42 | 67 | 0.491 | 0.528 | 0.287 | 0.7102 |  |  |
| `distinguish` | 0 | 3 | 7 | 10 | 0.462 | 3.484 | 0.650 | 0.2453 |  |  |
| `land's` | 1 | 2 | 7 | 10 | 0.462 | 0.714 | 0.650 | 0.6284 |  |  |
| `below` | 0 | 3 | 7 | 10 | 0.462 | 3.484 | 0.650 | 0.2453 |  |  |
| `cakes` | 1 | 2 | 7 | 10 | 0.462 | 0.714 | 0.650 | 0.6284 |  |  |
| `judgment` | 0 | 3 | 7 | 10 | 0.462 | 3.484 | 0.650 | 0.2453 |  |  |
| `dead` | 3 | 8 | 20 | 31 | 0.429 | 2.167 | 0.384 | 0.3374 |  |  |
| `zerah` | 2 | 0 | 5 | 7 | 0.405 | 2.391 | 0.687 | 0.3223 |  |  |
| `having` | 1 | 1 | 5 | 7 | 0.405 | 0.405 | 0.687 | 0.7680 |  |  |
| `figure` | 2 | 0 | 5 | 7 | 0.405 | 2.391 | 0.687 | 0.3223 |  |  |
| `judah's` | 2 | 0 | 5 | 7 | 0.405 | 2.391 | 0.687 | 0.3223 |  |  |
| `spices` | 1 | 0 | 3 | 4 | 0.375 | 1.367 | 0.772 | 0.5077 |  |  |
| `borders` | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| `ransom` | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| `beer` | 1 | 0 | 3 | 4 | 0.375 | 1.367 | 0.772 | 0.5077 |  |  |
| `hanoch` | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| `iron` | 1 | 0 | 3 | 4 | 0.375 | 1.367 | 0.772 | 0.5077 |  |  |
| `persecute` | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| `perez` | 1 | 0 | 3 | 4 | 0.375 | 1.367 | 0.772 | 0.5077 |  |  |
| `jazer` | 1 | 0 | 3 | 4 | 0.375 | 1.367 | 0.772 | 0.5077 |  |  |
| `plant` | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| `tear` | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| `task` | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| `large` | 1 | 0 | 3 | 4 | 0.375 | 1.367 | 0.772 | 0.5077 |  |  |
| `used` | 1 | 0 | 3 | 4 | 0.375 | 1.367 | 0.772 | 0.5077 |  |  |
| `bowls` | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| `added` | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| `fist` | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| `passes` | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| `meribah` | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| `hears` | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| `hips` | 1 | 0 | 3 | 4 | 0.375 | 1.367 | 0.772 | 0.5077 |  |  |
| `u` | 1 | 0 | 3 | 4 | 0.375 | 1.367 | 0.772 | 0.5077 |  | ⚠ |
| `olive` | 1 | 0 | 3 | 4 | 0.375 | 1.367 | 0.772 | 0.5077 |  |  |
| `separated` | 1 | 0 | 3 | 4 | 0.375 | 1.367 | 0.772 | 0.5077 |  |  |
| `form` | 0 | 1 | 3 | 4 | 0.375 | 1.382 | 0.772 | 0.5045 |  |  |
| `when` | 50 | 48 | 147 | 245 | 0.373 | 0.390 | 0.133 | 0.7764 |  |  |
| `glory` | 3 | 2 | 10 | 15 | 0.363 | 0.501 | 0.483 | 0.7212 |  |  |
| `leave` | 4 | 3 | 13 | 20 | 0.318 | 0.414 | 0.398 | 0.7636 |  |  |
| `filled` | 4 | 3 | 13 | 20 | 0.318 | 0.414 | 0.398 | 0.7636 |  |  |
| `thigh` | 6 | 3 | 16 | 25 | 0.295 | 1.008 | 0.346 | 0.5969 |  |  |
| `split` | 2 | 2 | 8 | 12 | 0.290 | 0.290 | 0.468 | 0.8273 |  |  |
| `yhwh` | 213 | 209 | 600 | 1022 | 0.286 | 0.292 | 0.058 | 0.8265 |  |  |
| `sea` | 7 | 6 | 22 | 35 | 0.275 | 0.323 | 0.287 | 0.8106 |  |  |
| `border` | 8 | 7 | 25 | 40 | 0.271 | 0.313 | 0.268 | 0.8162 |  |  |
| `with` | 162 | 167 | 469 | 798 | 0.253 | 0.351 | 0.061 | 0.7966 |  |  |
| `after` | 27 | 21 | 73 | 121 | 0.242 | 0.742 | 0.150 | 0.6170 |  |  |
| `opposite` | 3 | 5 | 14 | 22 | 0.230 | 0.609 | 0.320 | 0.6725 |  |  |
| `multiply` | 4 | 3 | 12 | 19 | 0.167 | 0.264 | 0.287 | 0.8422 |  |  |
| `saying` | 54 | 51 | 152 | 257 | 0.151 | 0.193 | 0.082 | 0.8827 |  |  |
| `eleven` | 1 | 1 | 4 | 6 | 0.145 | 0.145 | 0.398 | 0.9101 |  |  |
| `appoint` | 1 | 1 | 4 | 6 | 0.145 | 0.145 | 0.398 | 0.9101 |  |  |
| `complained` | 1 | 1 | 4 | 6 | 0.145 | 0.145 | 0.398 | 0.9101 |  |  |
| `cook` | 1 | 1 | 4 | 6 | 0.145 | 0.145 | 0.398 | 0.9101 |  |  |
| `over` | 49 | 49 | 139 | 237 | 0.059 | 0.060 | 0.052 | 0.9608 |  |  |
| `middle` | 1 | 2 | 5 | 8 | 0.054 | 0.307 | 0.202 | 0.8189 |  |  |
| `shown` | 1 | 2 | 5 | 8 | 0.054 | 0.307 | 0.202 | 0.8189 |  |  |
| `chariots` | 2 | 1 | 5 | 8 | 0.054 | 0.292 | 0.202 | 0.8265 |  |  |
| `seir` | 1 | 2 | 5 | 8 | 0.054 | 0.307 | 0.202 | 0.8189 |  |  |
| `lifted` | 2 | 1 | 5 | 8 | 0.054 | 0.292 | 0.202 | 0.8265 |  |  |
| `firstfruits` | 2 | 1 | 5 | 8 | 0.054 | 0.292 | 0.202 | 0.8265 |  |  |
| `peoples` | 2 | 1 | 5 | 8 | 0.054 | 0.292 | 0.202 | 0.8265 |  |  |
| `angry` | 2 | 2 | 6 | 10 | 0.015 | 0.015 | 0.080 | 0.9906 |  |  |
| `midianite` | 1 | 1 | 3 | 5 | 0.008 | 0.008 | 0.035 | 0.9949 |  |  |
| `inquire` | 1 | 1 | 3 | 5 | 0.008 | 0.008 | 0.035 | 0.9949 |  |  |
| `across` | 1 | 1 | 3 | 5 | 0.008 | 0.008 | 0.035 | 0.9949 |  |  |

---

## Machine-readable companion

The companion CSV/JSON contain every word and all calculated fields, including normalized rates, expected counts, shares, smoothed enrichment, source-vs-rest WoE, source-specific signed information, all pairwise J/E/P WoE and signed-information contrasts, global surprise bits, G², p-value, BH q-value, and artifact/reliability flags.

The JSON additionally embeds the corpus totals, formulas, metric definitions, caveats, and corpus-level statistics used in this report.
