# Job as a decipherment problem: a first-principles attack on its hardest Hebrew

## What the experiment is actually testing

There is a serious philological idea inside the proposed method. In fact, one striking part of it has a direct scholarly precedent: Driver and Grayʾs *International Critical Commentary* explicitly distinguished the ordinary unvocalized Hebrew from a further-reduced representation consisting of the traditional consonants **without regard to the present word divisions and with vowel-consonants removed**. In other words, a century ago they were already doing a controlled version of the proposed “dig up the consonants and resegment them” experiment. citeturn21view0

Job is an unusually appropriate book on which to do this. Edward Greenstein observes that its poetic language has a greater density of strange and foreign-looking words and a greater diversity of forms than any other biblical book; he argues, however, that much of the foreignness is deliberate poetic technique rather than evidence that Job is simply a bad translation from Aramaic, Arabic, Edomite, or some lost source language. The poem even juxtaposes conspicuously Aramaic-looking forms with ordinary Hebrew equivalents, suggesting conscious linguistic play. citeturn19search0turn19search11turn19search23 Marvin Pope likewise treats the Masoretic Hebrew as the primary witness while acknowledging that many passages are corrupt or obscure and sometimes require emendation; he also warns that the ancient Greek Job is sufficiently free and paraphrastic that it cannot simply be reverse-engineered mechanically into an earlier Hebrew text. citeturn4view0

So I would modify the proposed algorithm in exactly one important way: **make it radically permissive during candidate generation, but brutally conservative during candidate selection.** James Barrʾs classic critique of comparative Semitic philology is highly relevant here: once one permits an unusual Hebrew form to acquire whatever meaning a remotely similar Arabic, Akkadian, Ugaritic, or Aramaic word happens to have, it becomes dangerously easy to manufacture new vocabulary rather than recover it. Barrʾs expanded *Comparative Philology and the Text of the Old Testament* includes essays specifically on Job and on the limitations of etymology as a lexicographical tool. citeturn19search3turn19search13

That gives us the following hierarchy:

**Best reading:** same consonants, different pointing or syntactic analysis.

**Next best:** same consonants, different word division or recognition of a foreign/archaic lexical item.

**Next:** an independently plausible Semitic cognate with regular meaning and excellent poetic/contextual fit.

**Next:** a small orthographic disturbance involving matres or a well-attested scribal confusion.

**Last resort:** multiple consonantal alterations, language-hopping, or conjectural restoration.

Parallelism then really does function as something like an error-correcting code—but not a perfect one. It constrains the *semantic class* of the missing or obscure item much better than it identifies an exact lexeme.

One further caveat is important. There is no scholarly publication that ranks “the 100 objectively hardest verses in the Bible.” The ranking below is therefore a **working candidate ranking**, not a claimed consensus. It weights explicit judgments such as “hard,” “uncertain,” “very difficult,” “corrupt,” and “obscure” in major commentaries; rare vocabulary; disagreement among ancient versions; conjectural emendation; unstable word division; and breakdown of local parallelism. That makes a Job-only top 100 defensible as an experimental corpus, especially given Jobʾs exceptional lexical density, but not mathematically provable as the Bible-wide top 100. citeturn19search11turn4view0

## The lossy alphabet, edit hierarchy, and error-correction rules

For the experiment I use the Westminster Leningrad Codex text as represented by the Open Scriptures Hebrew Bible. OSHB explicitly identifies its Hebrew base as the WLC and uses Masoretic versification. citeturn25view0 Pointing, accents, spaces, maqaf, and punctuation disappear in the lossy string.

The ASCII mapping is:

ʿא=ʾ  ב=b  ג=g  ד=d  ה/ח=h  ו=w  ז=z  ט=T  י=y  כ=k  ל=l  מ=m  נ=n  ס/ש=s  ע=\ʿ  פ=p  צ=S  ק=q  ר=r  ת=tʿ

Final forms are normalized to their medial equivalents. Thus ʿשׁʿ, ʿשׂʿ, and ʿסʿ all become ʿsʿ; ʿהʿ and ʿחʿ both become ʿhʿ. I **retain** aleph and ayin as ʿʾʿ and ʿʿ ʿ ʿʿ and retain emphatics as ʿT/S/qʿ, because collapsing those as well destroys too much comparative information.

Crucially, ʿש/ס → sʿ and ʿה/ח → hʿ are **search normalizations**, not assertions that these letters were graphically interchangeable. Paleography and phonology are separate layers.

The grapheme-confusion map I would use is:

| Edit class | Candidate operation | Prior |
|---|---|---:|
| Pointing | Change vowels, stem identification, construct/absolute analysis | Very high |
| Segmentation | Move a word boundary in the continuous consonants | Very high |
| Matres | Treat ʿו/י/ה/אʿ as orthographically secondary where linguistically plausible | High–medium |
| Graphic | ʿד ↔ רʿ | High when the relevant script supports it |
| Graphic | ʿו ↔ יʿ | High in many Jewish/Aramaic book hands |
| Graphic | other look-alikes | Hand- and period-specific only |
| Phonological search | ʿש/סʿ, ʿה/חʿ, related sibilant/guttural classes | Candidate generation only |
| Addition/omission | one short mater or suffixal letter | Medium–low |
| Multiple edits | several substitutions plus resegmentation | Very low |

Confusion of dalet and resh is a standard textual-critical phenomenon and is possible in more than one historical Hebrew script tradition; waw and yod are also especially prone to visual confusion. But one should not make a universal “Hebrew letters that look alike” chart and apply it backward indiscriminately: Israelites first wrote in Old/Paleo-Hebrew, while Aramaic-derived script became increasingly dominant in the Second Temple period, and the shape relations among letters therefore changed over time. citeturn20search5turn20search7turn20search13

That point matters for the proposal to consider a confusion that exists “only in Aramaic.” **Yes—but only if we can plausibly place the corruption after transmission into an Aramaic-derived book hand.** A pair that resembles one another in medieval square Hebrew but not in Paleo-Hebrew should receive a lower prior for an early corruption. Conversely, later corruption may quite legitimately reflect the Aramaic-derived script.

My selection function is therefore conceptually:

> **reading quality ≈ consonantal fit + poetic parallelism + local discourse fit + speaker fit + regular comparative-Semitic support + versional support − textual edit cost − semantic special pleading**

No numerical scores are pretending to be probabilities here. The purpose is to prevent exactly the failure mode a maximally “lossy” procedure would otherwise create: with enough interchangeable letters, languages, roots, and implicit particles, *every* string eventually says whatever the interpreter wants.

Ancient versions are used as independent witnesses, not dictators. Pope specifically regards the Syriac as potentially useful where Hebrew is obscure, while stressing that the Greek can paraphrase rather freely. citeturn4view0

## The working top hundred

The top tier is not arbitrary. Pope explicitly calls Job 24:18–20 and 24:22–25 corrupt and obscure; translation literature notes that the end of Job 24 has generated unusually conjectural renderings and speaker-reassignment proposals. Driver and Gray call 6:14 “hard and uncertain,” 36:19 “very difficult,” 36:33 “again a very difficult verse,” describe Job 38ʾs astronomical terminology as highly uncertain, and say MT Job 41:1–3—English 41:9–11—has generated many conjectures. Translation commentary on Job 39:13 goes so far as to say that practically nothing in its first colon is entirely secure. citeturn4view0turn21view1turn21view3turn22view0turn22view1turn22view3turn23search29

The tags are **L** = lexical identification, **G** = grammar/segmentation, **T** = textual disturbance/emendation, **V** = versional divergence, **P** = parallelism/discourse, and **I** = identification of an animal, astronomical object, natural phenomenon, or technical referent. Ranks after roughly the first twenty should be regarded as tiers rather than falsely precise measurements.

| Rank | MT verse | Tags | Main reason it makes the corpus |
|---:|---|---|---|
| 1 | 24:18 | T/G/P/V | abrupt retribution language; syntax and discourse |
| 2 | 24:19 | T/G/P/V | elliptical parallelism; relation to v.18 |
| 3 | 24:20 | T/G/P/V | shifting imagery and awkward subject |
| 4 | 24:22 | T/G/P/V | implicit divine subject; unstable syntax |
| 5 | 24:23 | T/G/P/V | pronoun/reference ambiguity |
| 6 | 24:24 | T/L/G/P | several compressed/rare verbal expressions |
| 7 | 24:25 | T/G/P | conclusion depends on reconstruction of section |
| 8 | 36:33 | L/G/P/V | thunder/friend/cattle/rising-storm puzzle |
| 9 | 38:36 | L/I/P/V | ʿטחותʿ and ʿשכויʿ; radically different semantic worlds |
| 10 | 39:13 | L/I/G/V | bird identification and syntax profoundly disputed |
| 11 | 41:1 MT / Eng 41:9 | G/P/V | abrupt Leviathan-to-God transition begins |
| 12 | 41:2 MT / Eng 41:10 | G/P/V | creature/divine referent transition |
| 13 | 41:3 MT / Eng 41:11 | G/P/V | apparently intrusive divine ownership claim |
| 14 | 41:4 MT / Eng 41:12 | L/G/P | ketiv/qere plus obscure anatomical wording |
| 15 | 6:14 | G/P/V | relation of the two cola is unusually difficult |
| 16 | 36:19 | L/G/P | ʿשועךʿ, ʿיערךʿ, and ʿבצרʿ permit competing analyses |
| 17 | 11:12 | L/G/P/V | apparently nonsensical human/wild-ass proverb |
| 18 | 10:22 | L/P/V | darkness, “orders,” and paradoxical shining |
| 19 | 16:20 | L/G/V | mediator/mockery ambiguity |
| 20 | 30:11 | L/G/P | cord/bowstring and abrupt subject switch |
| 21 | 6:10 | L/V | exceptionally rare verb in “exult/recoil” clause |
| 22 | 6:7 | L/G/V | difficult food/sickness metaphor |
| 23 | 6:16 | L | unusual torrent terminology |
| 24 | 6:17 | L/G | rare verb describing vanishing wadis |
| 25 | 9:24 | G/P/V | broken sequence and “if not he, who?” |
| 26 | 9:35 | G/V | cryptic final clause |
| 27 | 9:23 | L/P | rare noun in “scourge” saying |
| 28 | 9:12 | L | rare/unattested verbal usage |
| 29 | 10:8 | G/V | syntactically difficult divine-making/destroying line |
| 30 | 10:15 | G/V | compressed conditional lament |
| 31 | 10:17 | L/G/V | “witnesses/hostilities/changes and host” |
| 32 | 10:20 | G/T | awkward transmitted sequence |
| 33 | 17:6 | L/V | ʿתפתʿ and uncertain social image |
| 34 | 17:7 | L/V | rare “forms/members/thoughts” expression |
| 35 | 17:16 | L/G | descent to Sheol/dust syntactic compression |
| 36 | 29:18 | L/I/V | sand versus phoenix tradition |
| 37 | 30:18 | T/G/V | garment/neck imagery with textual instability |
| 38 | 30:22 | L/G | unusual dissolution/resource terminology |
| 39 | 36:16 | G/P | dense Elihu syntax and metaphor |
| 40 | 36:18 | G/P | wrath/ransom/enticement ambiguities |
| 41 | 37:4 | G/V | problematic verbal object after divine thunder |
| 42 | 38:10 | G/V | “break/prescribe a boundary” difficulty |
| 43 | 38:31 | L/I/V | Pleiades binding/cluster terminology |
| 44 | 38:32 | L/I | Mazzaroth and astronomical identities |
| 45 | 38:33 | G/I | “ordinances” and dominion of heavens |
| 46 | 39:19 | L/I | ʿרעמהʿ: mane, trembling, thunder? |
| 47 | 39:21 | L/G | valley/strength and pawing imagery |
| 48 | 39:23 | L | unusual quiver-rattling verb |
| 49 | 39:24 | L/G | “swallows the earth” and trumpet syntax |
| 50 | 39:25 | L/G | battle scent, captainsʾ thunder, shout |
| 51 | 40:17 | L/I | Behemothʾs tail/cedar and sinews |
| 52 | 40:19 | L/G | “first of Godʾs ways” and weapon clause |
| 53 | 40:24 | G/I/V | capture by eyes/nose/snares |
| 54 | 40:25 MT / Eng 41:1 | L/I | Leviathan fishing terminology |
| 55 | 40:26 MT / Eng 41:2 | L/I | rope/reed/hook terminology |
| 56 | 40:30 MT / Eng 41:6 | L/G | traders/partners bargaining over monster |
| 57 | 40:31 MT / Eng 41:7 | L/G | harpoons and fishing spears |
| 58 | 40:32 MT / Eng 41:8 | G | compressed warning about battle |
| 59 | 41:5 MT / Eng 41:13 | L/I | garment/double bridle anatomy |
| 60 | 41:7 MT / Eng 41:15 | L/G/I | channels/shields/scales |
| 61 | 41:17 MT / Eng 41:25 | L/G | mighty/gods terrified; unusual reflexive |
| 62 | 41:18 MT / Eng 41:26 | L/G | weapons vocabulary and syntax |
| 63 | 41:22 MT / Eng 41:30 | L/I | potsherds/threshing-sledge underside |
| 64 | 41:24 MT / Eng 41:32 | L/G/I | sea becoming “gray-haired” |
| 65 | 41:26 MT / Eng 41:34 | L/I | “sons of pride” identification |
| 66 | 3:8 | L/I | Leviathan-rousing professional cursers |
| 67 | 4:18 | L/V | obscure term in accusation against angels |
| 68 | 5:5 | L/G | thorn/hungry/snare wording |
| 69 | 5:7 | L/I | “sons of Resheph” / sparks / supernatural imagery |
| 70 | 6:3 | L | difficult verb describing Jobʾs speech |
| 71 | 6:4 | L/G | divine terrors “arraying” themselves |
| 72 | 6:6 | L/I/V | uncertain tasteless food |
| 73 | 6:13 | G/T | interrogative/textual instability |
| 74 | 6:18 | L/G | caravans/torrents “twisting” into waste |
| 75 | 6:21 | L/V | rare terror term |
| 76 | 6:25 | L/G | difficult “forcible/pleasant words” expression |
| 77 | 7:5 | L/I | skin/scab/dust pathology |
| 78 | 7:15 | L/G | strangling/death clause |
| 79 | 8:19 | G/T/V | difficult plant-path line |
| 80 | 9:5 | L/G | mountains removed “without knowing” |
| 81 | 9:8 | L/I | treading sea waves/back |
| 82 | 9:9 | L/I | constellation names |
| 83 | 9:13 | L/I | helpers of Rahab |
| 84 | 9:22 | G/V | “it is all one” and versional issue |
| 85 | 9:26 | L/I | reed/papyrus boats or swift craft |
| 86 | 12:5 | G/P | obscure proverb about contempt and stumbling |
| 87 | 13:15 | G/V | famous ʿלו/לאʿ interpretive problem |
| 88 | 15:29 | L/V | rare possession/produce terminology |
| 89 | 19:17 | L/G | breath/wife and “sons of my body” |
| 90 | 19:25 | G/L/V | redeemer/witness/afterward syntax |
| 91 | 19:26 | G/L/V | skin destruction and seeing God |
| 92 | 19:27 | G/L/V | pronouns and “kidneys consumed” |
| 93 | 20:23 | G/T | difficult sequence around filling the belly |
| 94 | 20:26 | L/I | hidden darkness/fire imagery |
| 95 | 24:1 | G/T | times “hidden/stored” from Shaddai |
| 96 | 26:5 | L/I | Rephaim writhing beneath waters |
| 97 | 26:13 | L/I | fleeing/crooked serpent constellation/myth |
| 98 | 28:4 | G/L | mining shaft/forgotten foot imagery |
| 99 | 33:9 | L/V | unusual ʿחףʿ “clean/pure” |
| 100 | 38:24 | L/G/I | division of light/east wind |

NETʾs textual notes independently flag a striking number of these same places: Job 6 contains several unusual or unique items and repeatedly difficult cola; Job 9:24 and 9:35 are particularly syntactically troublesome; Job 10:22 contains a unique ʿסדרʿ-form; and Job 17 contains rare vocabulary whose ancient renderings diverge. citeturn10view0turn9search4turn11view2turn1search10

The ranking also tells us something important before doing any reconstruction: the hardest passages are not uniformly “corrupt Hebrew.” There are at least four different pathologies hiding under the single label *obscure*: lost lexical knowledge, hypercompressed poetry, deliberate foreignizing diction, and actual textual disturbance.

## The forensic reconstruction of the hardest twenty

All Hebrew below follows the WLC/OSHB consonantal text; the displayed Hebrew is vocalized for readability, while the ASCII column ignores the Masoretic vowels and divisions. citeturn25view0 ʿUgaʿ = Ugaritic, ʿAkkʿ = Akkadian, ʿArmʿ = Aramaic, ʿSyrʿ = Syriac, ʿPhoʿ = Phoenician, and ʿArbʿ = Arabic. Arabic is not being treated as an ANE witness; where it appears, it is a later comparative-Semitic control used because the older commentaries themselves sometimes make the comparison. A question mark means “search candidate,” not “secure etymology.”

**The Job 24 disaster zone**

Pope singles out 24:18–20 and 22–25 as corrupt and obscure. The deeper problem is obvious from discourse: Job 24 begins by protesting that divine judicial “times” are not visible and then catalogs predators, exploiters, murderers, adulterers, and impoverished victims. Suddenly vv.18–20 sound as though the wicked are promptly cursed and carried to Sheol—the very conventional retribution thesis Job has spent the speech disputing. This has led translators and commentators to insert something like “you say” or otherwise detach/reassign the lines. citeturn4view0turn23search12turn23search28

That is exactly where the userʾs “speaker personality + parallelism” test pays off. Before altering a consonant, try repairing the **discourse frame**.

| Ref.      | Hebrew original                                                                      | Lossy Semitic ASCII                         | Comparative radical candidates                                              | Literal English from the consonants                                                                                                  | Fluid / interpretive reconstruction                                                                                                     |
| --------- | ------------------------------------------------------------------------------------ | ------------------------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| **24:18** | קַל־הוּא עַל־פְּנֵי־מַיִם תְּקֻלַּל חֶלְקָתָם בָּאָרֶץ לֹא־יִפְנֶה דֶּרֶךְ כְּרָמִים | ʿqlhwʾ\ʿlpnymymtqllhlqtmbʾrSlʾypnhdrkkrmymʿ | ʿQLLʿ (Akk?/NWS: light, slight); ʿHLQʿ (Uga?/NWS: divide, share)            | “Light/swift is he upon the face of the waters; cursed is their portion in the land; he does not turn toward the road of vineyards.” | **[You claim:] “He is swept off like something light on water; his estate is cursed; he never returns to the vineyards.”**              |
| **24:19** | צִיָּה גַם־חֹם יִגְזְלוּ מֵימֵי־שֶׁלֶג שְׁאוֹל חָטָאוּ                               | ʿSyhgmhmygzlwmymyslgsʾwlhTʾwʿ               | ʿHMMʿ (Uga?/NWS: heat); ʿSLGʿ (Akk?/Arm: snow)                              | “Drought, also heat, steal snow-waters; Sheol—those who sinned.”                                                                     | **“As drought and heat steal the snowmelt, [you say] Sheol steals away the sinner.”**                                                   |
| **24:20** | יִשְׁכָּחֵהוּ רֶחֶם מְתָקוֹ רִמָּה לֹא־יִזָּכֵר וַתִּשָּׁבֵר כָּעֵץ עַוְלָה          | ʿyskhhwrhmmtqwrmhlʾyzkrwtsbrk\ʿS\ʿwlhʿ      | ʿRHMʿ (Uga?: womb/compassion); ʿRMMʿ (Akk?: worm/maggot)                    | “A womb forgets him; a worm finds him sweet; he is no longer remembered; injustice is broken like a tree.”                           | **“The womb forgets him, the worm feasts on him, his memory disappears, and—so the old doctrine says—the evildoer snaps like a tree.”** |
| **24:22** | וּמָשַׁךְ אַבִּירִים בְּכֹחוֹ יָקוּם וְלֹא־יַאֲמִין בַּחַיִּין                       | ʿwmskʾbyrymbkhwyqwmwlʾyʾmynbhyynʿ           | ʿMSKʿ (Arm/NWS: draw, extend); ʿHYYʿ (Uga/Arm: life)                        | “But he draws/prolongs mighty ones by his power; one rises and does not trust in life.”                                              | **“But [in reality] God keeps the powerful going by his power: a man gets back on his feet even when his life seemed lost.”**           |
| **24:23** | יִתֶּן־לוֹ לָבֶטַח וְיִשָּׁעֵן וְעֵינֵיהוּ עַל־דַּרְכֵיהֶם                           | ʿytnlwlbThwys\ʿnw\ʿynyhw\ʿldrkyhmʿ          | ʿBTHʿ (Arm/NWS: security/trust); ʿSʿNʿ (Arm?: lean/support)                 | “He gives him [something] for security, and he leans; and his eyes are on their ways.”                                               | **“God gives him security to lean on—and keeps his eyes upon their paths.”**                                                            |
| **24:24** | רוֹמּוּ מְּעַט וְאֵינֶנּוּ וְהֻמְּכוּ יִקָּפְצוּן וּכְרֹאשׁ שִׁבֹּלֶת יִמָּלוּ       | ʿrwmwm\ʿTwʾynnwwhmkwyqpSwnwkrʾssbltymlwʿ    | ʿRWMʿ (Uga/Arm: rise); ʿQPSʿ (Arm?: close/gather); ʿMLLʿ (NWS: cut/wither?) | “They are raised a little, and he/it is gone; they are brought low, gathered up; like the head of an ear of grain they are cut off.” | **“They rise for a little while and then are gone; they sink and are gathered like everyone else, cut down like the tops of grain.”**   |
| **24:25** | וְאִם־לֹא אֵפוֹ מִי יַכְזִיבֵנִי וְיָשֵׂם לְאַל מִלָּתִי                             | ʿwʾmlʾʾpwmyykzybnywysmlʾlmltyʿ              | ʿKZBʿ (Uga/Arm: lie/fail); ʿMLL/MILLAʿ (Arm: word/speech)                   | “And if not, then who will make me a liar and reduce my word to nothing?”                                                            | **“And if that is not how things are, who can prove me false and reduce my argument to nothing?”**                                      |

The important reconstruction is not a spectacular dalet-to-resh emendation. It is the insertion of a **speech/discourse operator that poetry can leave implicit**:

> **[You say:]** wicked men are swept away, cursed, forgotten, swallowed by Sheol.  
> **[But look:]** God actually sustains powerful men, gives them security, and watches their paths. Eventually they die—but so does everybody.  
> **Prove me wrong.**

Verse 21, which Pope notably does **not** include among the specifically corrupt lines, supplies the wicked target between those portions: the man mistreats the barren woman and does no good to the widow. On this reading v.22ʾs implicit subject naturally becomes God. The result fits Jobʾs personality and argument extraordinarily well without changing a single consonant.

I would assign this reconstruction **medium-high confidence**. An optative reading—“May the wicked be swept away; may Sheol take him”—is the best alternative and likewise repairs the discourse with almost no textual cost. But the implicit-quotation solution explains the unambiguously indicative feel of v.18 more naturally and has precedent in modern translation practice. citeturn23search12turn23search28

**Storm, weather, and animals**

| Ref. | Hebrew original | Lossy Semitic ASCII | Comparative radical candidates | Literal English from the consonants | Fluid / interpretive reconstruction |
|---|---|---|---|---|---|
| **36:33** | יַגִּיד עָלָיו רֵעוֹ מִקְנֶה אַף עַל־עוֹלֶה | ʿygyd\ʿlywr\ʿwmqnhʾp\ʿl\ʿwlhʿ | ʿQNYʿ (Uga: acquire/possess); ʿʿLYʿ (Uga/NWS: rise); ʿRʿʿ = crash/shout candidate | “His crashing/shout tells concerning him; livestock too, concerning what rises.” | **“His thunder announces his approach; even the livestock sense the storm rising.”** |
| **38:36** | מִי־שָׁת בַּטֻּחוֹת חָכְמָה אוֹ מִי־נָתַן לַשֶּׂכְוִי בִינָה | ʿmystbThwthkmhʾwmyntnlskwybynhʿ | ʿSKY/SKWʿ (Arm: look/watch); ʿTWHʿ (NWS: coat/cover); possible non-Semitic animal/weather term | “Who put wisdom in the *ṭuḥôt*, or who gave understanding to the *śekwî*?” | **Probable weather reading: “Who gave the weather-sign creature its wisdom, or gave the watcher-bird understanding?”** More concretely: **“Who gave the ibis its weather-wisdom, or the rooster its understanding?”** |
| **39:13** | כְּנַף־רְנָנִים נֶעֱלָסָה אִם־אֶבְרָה חֲסִידָה וְנֹצָה | ʿknprnnymn\ʿlshʾmʾbrhhsydhwnShʿ | ʿKNPʿ (Uga/NWS: wing); ʿRNNʿ (Uga?/NWS: cry/rejoice); ʿʾBRʿ (Uga?/NWS: pinion/wing) | “The wing of the crying/rejoicing ones exults; is it the pinion of a stork, and plumage?” | **“The noisy desert bird beats its wings joyfully—but are those a storkʾs pinions and plumage?”** Species deliberately left open. |

Job 36:33 is a beautiful test case because radical emendation turns out to be unnecessary. Driver and Gray call it “again a very difficult verse,” noting the awkwardness of both “noise” and the cattle, while modern translations vary substantially. But the immediate context is lightning and then thunder; Job 37:2 immediately tells the listener to attend to Godʾs roaring voice. Once the line is read as primitive storm observation—**thunder announces the storm, and cattle react before it arrives**—both cola lock together. citeturn22view0turn23search13turn23search5

That is exactly the sort of result the proposed algorithm should reward: **zero consonantal edits, strong parallelism, perfect local context, ordinary human observation**. My confidence in “His thunder announces his approach; even the cattle sense the rising storm” is high.

Job 38:36 is much tougher. Driver and Gray report that the old “inward parts / mind” interpretation derives ʿטחותʿ from something covered or coated and the second noun from an Aramaic watch/look root; they also note attempts to make the first colon refer to clouds or other natural phenomena, and say the parallel term is, if anything, still more uncertain. citeturn22view2 Some translation traditions instead identify an ibis and a rooster, with the birds functioning as natural weather/time forecasters; translation commentary notes support for “rooster” in ancient interpretive tradition and observes the relevance of Egyptian lore about such animals. citeturn23search24turn18search0

Here the “parallelism as error correction” argument is powerful. The sequence is:

**v.34** clouds and water  
**v.35** lightning  
**v.36** ??? wisdom / ??? understanding  
**v.37** counting clouds / heavenly waterskins  
**v.38** rain changing the ground

That context puts a substantial prior on a **meteorological** interpretation rather than an abrupt excursus on the human psyche. I therefore prefer a weather-sign reading. But the exact zoological identifications are not recoverable from the consonants with high confidence. The honest reconstruction is therefore:

> **“Who endowed the weather-signs with wisdom, or gave the watcher understanding?”**

“Ibis / rooster” is a plausible concretization, not something the algorithm can prove. This is one place where the information-theoretic analogy reaches its limit: parallelism reconstructs the *semantic field* better than the nouns themselves.

Job 39:13 produces an even more interesting result. Modern readers routinely encounter “ostrich,” but the underlying ʿרנניםʿ is not simply the normal Hebrew word for ostrich. Translation commentary stresses the exceptional uncertainty of the line. Arthur Walker-Jones has argued at length that the traditional ostrich identification is wrong and proposes a sandgrouse-type bird, noting that several features of vv.13–18 can fit sandgrouse behavior. citeturn23search29turn18search9turn23search7

The lossy procedure says: **stop trying to identify the species too early.**

ʿKNP RNNYM NʿLSHʿ gives us something like:

> **wing + noisy/crying/rejoicing creatures + exult/flap**

and the second colon contrasts its wing with the ʿʾBRH ... WNṢHʿ, pinion and plumage, of the ʿHSYDHʿ, the stork.

So a pre-dictionary translation is:

> **“The wing of the crying bird beats joyfully—but is it a storkʾs pinion and plumage?”**

That is, in my judgment, better philology than putting **ostrich** into the lexical layer. The larger passage can then decide whether the animal is ostrich, sandgrouse, or another desert bird. The consonants do not.

**The notorious Leviathan transition**

The Hebrew and common English verse numbering diverge here: MT 41:1 corresponds to English 41:9. Driver and Gray explicitly label MT 41:1–3 as English 41:9–11 and note that the passage has generated numerous conjectures. citeturn22view3 The WLC/Mechon-Mamre text confirms the sequence. citeturn24view9

| Ref. | Hebrew original | Lossy Semitic ASCII | Comparative radical candidates | Literal English from the consonants | Fluid / interpretive reconstruction |
|---|---|---|---|---|---|
| **41:1 MT / Eng 41:9** | הֵן־תֹּחַלְתּוֹ נִכְזָבָה הֲגַם אֶל־מַרְאָיו יֻטָּל | ʿhnthltwnkzbhhgmʾlmrʾywyTlʿ | ʿKZBʿ (Uga?/Arm: fail/lie) | “Look, his hope is disappointed; even at his appearances/sight is [one] cast down?” | **“Look—any hope of taking him is delusion; at the mere sight of him a man collapses.”** |
| **41:2 MT / Eng 41:10** | לֹא־אַכְזָר כִּי יְעוּרֶנּוּ וּמִי הוּא לְפָנַי יִתְיַצָּב | ʿlʾʾkzrkyy\ʿwrnwwmyhwʾlpnyytySbʿ | ʿYṢBʿ (Uga?/NWS: stand); ʿʿWRʿ (Arm?/NWS: rouse) | “No fierce one [exists] who would rouse him; and who is he who can stand before me?” | **“No one is fierce enough to rouse Leviathan—so who, then, can stand against me?”** |
| **41:3 MT / Eng 41:11** | מִי הִקְדִּימַנִי וַאֲשַׁלֵּם תַּחַת כָּל־הַשָּׁמַיִם לִי־הוּא | ʿmyhqdymnywʾslmthtklhsmymlyhwʾʿ | ʿQDMʿ (Uga/Akk: front, precede); ʿŠLMʿ (Uga/Akk: completeness/payment semantic family) | “Who has preceded me, that I should repay? Under all the heavens it is mine.” | **“Who has ever put me in his debt, so that I owe him repayment? Everything under heaven is mine.”** |
| **41:4 MT / Eng 41:12** | כתיב: לֹא־אַחֲרִישׁ בַּדָּיו וּדְבַר־גְּבוּרוֹת וְחִין עֶרְכּוֹ; קרי begins לוֹ | ʿlʾʾhrysbdywwdbrgbwrwtwhyn\ʿrkwʿ | ʿGBRʿ (Uga/NWS: strength); ʿʿRKʿ (Arm/Uga?: arrange/set); ʿBDʿ (NWS: member/branch?) | Ketiv: “I will not be silent about his parts, the matter of mighty deeds, and the grace of his arrangement.” | **“I will not pass over his limbs, his tremendous strength, or the elegance of his construction.”** |

The Masoretic tradition itself preserves difficulty in 41:4: OSHB marks ʿלאʿ as the ketiv and ʿלוʿ as the qere. fileciteturn0file1 Mechon-Mamre likewise displays the two traditions. citeturn24view9 For the excavation experiment, the **ketiv consonants deserve first place** because that is the written layer we are pretending to discover.

There is an extraordinarily tempting emendation in 41:2: change ʿלפניʿ, “before me,” to ʿלפניוʿ, “before him.” That would produce perfect creature-to-creature parallelism:

> Who dares rouse **him**?  
> Who can stand before **him**?

It requires merely adding a final waw, exactly the sort of weak mater/suffix letter the proposed procedure tells us not to fetishize.

And I would nevertheless **reject it**.

Why? Because the transmitted reading makes excellent rhetorical sense. God deliberately reasons from Leviathan to himself:

> You cannot provoke **that creature**.  
> Therefore who can stand before **me**, its maker?

The next verse then generalizes the claim: nobody has put God in debt because everything under heaven belongs to him. What initially looks like a corrupt pronoun becomes a carefully constructed rhetorical turn. The surrounding speaker identity is the error-correcting information.

That is a major methodological result: **parallelism alone would make us emend the text incorrectly; discourse structure rescues the MT.**

Pope entertained much more radical reconstructions in this region, including mythological possibilities, while Driver and Gray survey numerous conjectures. citeturn22view3turn4view3 On the present bottom-up method, however, MT 41:1–4 mostly survives. Verse 4 has unusual vocabulary and a ketiv/qere complication, but once ʿבדיוʿ is allowed its anatomical “members/limbs” sense and ʿערכוʿ is understood as arrangement/build, the progression into the detailed anatomy of Leviathan in vv.5ff is exactly right.

**Six dialogue lines where syntax matters more than corruption**

| Ref. | Hebrew original | Lossy Semitic ASCII | Comparative radical candidates | Literal English from the consonants | Fluid / interpretive reconstruction |
|---|---|---|---|---|---|
| **6:14** | לַמָּס מֵרֵעֵהוּ חָסֶד וְיִרְאַת שַׁדַּי יַעֲזוֹב | ʿlmsmr\ʿhwhsdwyrʾtsdyy\ʿzwbʿ | ʿMSSʿ (comparative match uncertain); ʿHSDʿ (NWS loyalty/faithfulness semantic field) | “For the melting/despairing one—from his friend—loyalty; and the fear of Shaddai he abandons.” | **“A man whose courage is melting deserves loyalty from his friend—even when his fear of Shaddai is giving way.”** |
| **36:19** | הֲיַעֲרֹךְ שׁוּעֲךָ לֹא בְצָר וְכֹל מַאֲמַצֵּי־כֹחַ | ʿhy\ʿrksw\ʿklʾbSrwklmʾmSykhʿ | ʿʿRKʿ (NWS/Arm: arrange, assess); ʿWSʿʿ (Arb, comparative: breadth/ample means) | “Will your *šûaʿ* be equal/arrayed—not in distress—and all exertions of strength?” | **Best tentative sense: “Can your wealth/resources keep you out of straits—or all your strongest exertions?”** |
| **11:12** | וְאִישׁ נָבוּב יִלָּבֵב וְעַיִר פֶּרֶא אָדָם יִוָּלֵד | ʿwʾysnbwbylbbw\ʿyrprʾʾdmywldʿ | ʿLBBʿ (Uga ʿlbʿ; Akk ʿlibbuʿ: heart/mind); ʿNBBʿ (Arm?/Syr?: hollow) | “A hollow man gets a heart, and a wild-ass colt is born a human.” | **“An empty-headed man will acquire sense when a wild donkey is born human.”** In other words: never. |
| **10:22** | אֶרֶץ עֵיפָתָה כְּמוֹ אֹפֶל צַלְמָוֶת וְלֹא סְדָרִים וַתֹּפַע כְּמוֹ־אֹפֶל | ʿʾrS\ʿypthkmwʾplSlmwtwlʾsdrymwtp\ʿkmwʾplʿ | ʿSDRʿ (Arm: arrange/order); ʿSDRʿ (Arb, Driverʾs semantic comparison); ʿYPʿʿ (NWS: shine/appear) | “A land of gloom like darkness, death-shadow and no orders; and it shines like darkness.” | **“A land black as night—death-shadow without order, where even the gleam is darkness.”** |
| **16:20** | מְלִיצַי רֵעָי אֶל־אֱלוֹהַּ דָּלְפָה עֵינִי | ʿmlySyr\ʿyʾlʾlwhdlph\ʿynyʿ | ʿLṢ/MLṢʿ (Arm/Syr? mocking/interpreting semantic possibilities); ʿDLPʿ (Arm/Syr?: drip) | “My mockers/interpreters—my friends; toward God my eye drips.” | **“My own friends have become my mockers; my eyes pour themselves out to God.”** |
| **30:11** | כִּי־יִתְרִי פִתַּח וַיְעַנֵּנִי וְרֶסֶן מִפָּנַי שִׁלֵּחוּ | ʿkyytrypthwy\ʿnnywrsnmpnyslhwʿ | ʿWTRʿ (Arb, comparative: bowstring); ʿRSNʿ (NWS/Arm?: bridle/restraint) | “For my cord he loosened and humbled me; and restraint before me they cast away.” | **“He has unstrung me and humbled me; therefore they cast off every restraint in my presence.”** |

Driver and Gray call 6:14 “hard and uncertain” and survey radically different grammatical solutions. citeturn21view1 But the surrounding argument gives a remarkably strong semantic constraint: Jobʾs point in chapter 6 is that his companions have failed him like seasonal streams. The natural first colon is therefore **a claim about what a collapsing sufferer is owed by a friend**. The apparent theological shock of the second colon—“he abandons fear of Shaddai”—is precisely what makes the line powerful.

I therefore think the missing English connective is concessive:

> **Even if** his fear of Shaddai is collapsing.

No Hebrew consonant needs changing. The poet has omitted the logical connective because the semantic relation is recoverable. The common tendency to “repair” Job into saying that anyone who withholds friendship has abandoned fear of God is morally attractive, but it costs more textually. The speakerʾs emotional argument strongly favors:

> **A despairing man is owed ḥesed by his friend even at the edge of apostasy.**

That is, in my judgment, one of the experimentʾs strongest gains.

Job 36:19 genuinely resists us. Driver and Gray themselves label it “very difficult” and discuss whether ʿשועʿ means riches/resources or a cry for help, explicitly comparing an Arabic breadth/ample-means root in defense of the wealth interpretation. citeturn21view3 Here the algorithm does **not** produce a miraculous solution. Parallelism wants two ineffective forms of human power:

> your ʿשועʿ  
> all exertions of strength

That makes **wealth/resources** slightly better than “cry,” because resources and muscular effort form a clean pair. Hence:

> **“Can your resources keep you out of straits—or all your strongest exertions?”**

But this remains low-to-medium confidence. This is exactly the place to resist the temptation to announce a new Akkadian cognate and pretend the problem has vanished.

Job 11:12, by contrast, collapses almost completely once parallelism is treated pragmatically instead of grammatically. Driver and Gray speak of the competing interpretations of this notoriously difficult verse. citeturn15view2 The raw semantics are:

> hollow man → gets a heart  
> wild-ass foal → is born a human

That is not defective prose. It is an **impossibility proverb**:

> **An empty-headed man will become wise when a wild donkey gives birth to a human.**

The second colon is the error-correcting key to the first. ʿילבבʿ need not be made exotic; “acquire a heart/mind” is the result that the impossible second event tells us will never happen. This is probably Zophar at his most sarcastic.

Job 10:22 is similarly better if we resist fixing it. NETʾs notes call attention to the exceptional ʿסדרʿ vocabulary and report comparative attempts to explain it. citeturn2search33 But the ending ʿותפע כמו אפלʿ—roughly, “it shines/gleams like darkness”—may be intentionally paradoxical. Job is describing a land beyond ordinary perceptual distinctions. The best reconstruction is therefore not to normalize the paradox away:

> **“death-shadow without order, where even the light is dark.”**

That sounds odd because Job intends the underworld to sound odd.

Job 16:20 works the same way. Instead of hunting for another noun behind ʿמליציʿ, read the apposition rhetorically:

> **“My mockers—my friends.”**

The phrase is bitter precisely because ʿרעיʿ, “my friends,” identifies the mockers. Then the second colon—Jobʾs eye dripping toward God—fits perfectly. Pope regards the surrounding transmitted text as damaged enough that no single emendation has commanded assent, which is reason to prefer a zero-edit reading wherever one is semantically adequate. citeturn4view2

Job 30:11 is especially revealing. Driver and Gray compare Arabic *watar*, “bowstring,” in explaining the cord imagery, and commentators recognize the abrupt movement from a singular agent to plural tormentors. citeturn15view2turn4view0 But Jobʾs situation supplies the missing causal relation:

> **God** unstrung/humbled me → **therefore the mob** threw off restraint.

Hence:

> **“He has unstrung me and humbled me; therefore they cast off every restraint before me.”**

Again, no consonant swap is required. The “corruption” is largely the difference between explicit English syntax and brutally compressed Hebrew poetry.

## Where the method beats, matches, or loses to conventional readings

The first major conclusion is somewhat paradoxical: **the proposed radical method works best when it teaches us not to emend radically.**

Driver and Grayʾs own textual apparatus effectively validates the first step—strip vocalization, distrust inherited division when necessary, compare the naked consonants—but the strongest solutions above usually arise *before* the d/r swaps and speculative foreign lexemes come into play. citeturn21view0

The results fall into four classes.

| Passage | What looked broken | What actually repairs it | Verdict |
|---|---|---|---|
| Job 24:18–25 | apparently pro-retribution material in Jobʾs anti-retribution speech | implicit quotation/ironic conventional doctrine; then contrast with reality | **Discourse repair is much better than wholesale consonantal reconstruction** |
| Job 36:33 | thunder + cattle + “rising” looks incoherent | storm behavior and immediate weather context | **MT essentially wins** |
| Job 38:36 | two nouns whose referents are deeply uncertain | parallelism recovers “paired possessors of weather intelligence,” but not exact identities | **Method narrows semantic field but cannot uniquely decode nouns** |
| Job 39:13 | “ostrich” and syntax seem unstable | translate the lexical layer species-neutrally as a noisy/rejoicing desert bird | **Improvement over premature zoological identification** |
| Job 41:1–4 MT | abrupt switch from Leviathan to God | deliberate *a fortiori* rhetoric: if you cannot face the creature, who can face its maker? | **MT beats tempting emendation** |
| Job 6:14 | grammatical relation between friendship and abandoning fear | implicit concessive: friendship is owed *even if* faith is failing | **Strong contextual improvement** |
| Job 36:19 | almost every key item has alternatives | parallelism favors resources + strength, but does not eliminate ambiguity | **Unresolved; do not overclaim** |
| Job 11:12 | apparently absurd sentence | impossible-condition sarcasm | **Very strong recovery from parallelism** |
| Job 10:22 | “light like darkness” appears contradictory | contradiction is deliberate underworld imagery | **MT essentially wins** |
| Job 16:20 | “interpreters/mockers—friends” | appositional insult | **Pointing/semantic repair, no consonantal repair** |
| Job 30:11 | singular “he” suddenly becomes plural “they” | causal shift: God disables Job, mob exploits him | **Pragmatic repair** |

The second result is that **speaker personality is unusually powerful in Job**. Greensteinʾs analysis of Jobʾs learned, foreignizing poetic language supports exactly this sort of reading: strange diction is often artistic rather than accidental. citeturn19search0turn19search11 Job, Zophar, Elihu, and the divine speaker are not interchangeable producers of generic Hebrew aphorisms.

That gives us very strong constraints:

Job regularly turns conventional wisdom against itself. Therefore an apparently orthodox retribution formula inside Jobʾs protest deserves testing as quotation, sarcasm, or wish before being assigned to a misplaced source.

Zophar is capable of sharp derision. Therefore Job 11:12ʾs human/wild-ass absurdity is more likely an insulting impossibility proverb than textual wreckage.

Elihuʾs final speech is dominated by the storm into which Godʾs appearance emerges. Therefore Job 36:33ʾs thunder, livestock, and “rising” naturally belong to storm phenomenology.

Godʾs speeches use chains of rhetorical questions and arguments from inaccessible creatures to inaccessible divine governance. Therefore the “before **me**” of MT 41:2 need not be changed to “before **him**.”

The third result concerns cognates. Comparative Semitic is most persuasive when **several constraints converge independently**. Job 30:11 is a good example: a cognate meaning “bowstring” helps because a cord fits the Hebrew consonants, the local metaphor of disabling Job, and the following social humiliation. Job 38:36 is the opposite: a remotely comparable root can generate “mind,” “watcher,” “rooster,” cloud phenomena, and more. Once the cognates point in several directions, the comparative evidence stops being decisive. Driver and Grayʾs history of proposed interpretations there illustrates the problem vividly. citeturn22view2

The fourth result concerns paleographic emendation. The experiment should retain d/r, w/y, matres, and script-specific confusions as a **second-stage rescue mechanism**, but none of the very hardest twenty above actually demands a d/r swap for its best reading. That is significant. The freedom to make those swaps is useful for generating hypotheses, yet a candidate requiring one should lose to a zero-edit reading with equally good semantics. Documented scribal confusions are real, but their existence is not evidence that a particular confusing verse contains one. citeturn20search5turn20search7

Job 41:2 is the perfect negative control. Adding a single waw to make ʿלפניʿ → ʿלפניוʿ creates prettier local parallelism. A naive “parallelism = error-correction code” algorithm would therefore make the edit. But the larger rhetorical context says not to. **Error correction must operate hierarchically: colon → verse → paragraph → speaker → book.**

That suggests a more rigorous version of the proposed algorithm:

> **First strip the Masoretic interpretation, not the consonants.**  
> Recover the consonants, possible divisions, and radical families.  
> Let parallelism propose a semantic slot.  
> Let immediate context constrain that slot.  
> Let speaker identity and argument constrain it again.  
> Only then consult comparative Semitic.  
> Use ancient witnesses as independent checks.  
> Only after those fail should paleographic substitution become active.  
> A reconstructed reading must explain why the transmitted reading arose.

That last condition is essential. A good conjecture is not merely a better sentence. It should offer some account of how *this* Hebrew string could have resulted from *that* earlier reading.

## Bottom-line reconstruction

The first-principles exercise produces a more interesting result than “Job is secretly garbled Akkadian/Aramaic.”

There really is reason to loosen the Masoretic vowels and divisions aggressively. Driver and Gray themselves formalized almost exactly that operation, and Jobʾs extraordinary foreignizing vocabulary makes cross-Semitic comparison indispensable. citeturn21view0turn19search11 There is also real textual damage in the book: Pope is explicit that some passages remain corrupt or obscure, with Job 24:18–20, 22–25 among the most conspicuous. citeturn4view0

But after running the proposed approach from the bottom up, the most productive principle is:

> **Treat the consonants as firmer than the grammar, the grammar as firmer than the vowels, and discourse as firmer than the dictionary gloss.**

For the present top twenty, my provisional reconstructed readings are therefore:

| Verse | Best present reconstruction |
|---|---|
| **24:18** | **[You say:] “He is swept away like something light on water; his estate is cursed; he never returns to the vineyards.”** |
| **24:19** | **“As drought and heat steal snowmelt, [you say] Sheol steals the sinner.”** |
| **24:20** | **“The womb forgets him, the worm feeds on him, his memory vanishes, and the evildoer is broken like a tree.”** |
| **24:22** | **“But in reality God sustains the powerful by his power; a man rises again even when life seemed insecure.”** |
| **24:23** | **“God gives him security to lean on and keeps his eyes on his paths.”** |
| **24:24** | **“They rise for a little while, then are gone; they sink with everyone else and are cut like the heads of grain.”** |
| **24:25** | **“If that isnʾt so, who can prove me false and reduce my argument to nothing?”** |
| **36:33** | **“His thunder announces his approach; even the livestock sense the storm rising.”** |
| **38:36** | **“Who endowed the weather-sign creature with wisdom, or gave the watcher understanding?”** Possibly ibis/rooster; exact nouns remain uncertain. |
| **39:13** | **“The noisy desert bird beats its wings joyfully—but are those a storkʾs pinions and plumage?”** Do not insert “ostrich” into the lexical layer. |
| **41:1 MT** | **“Any hope of taking him is delusion; at the mere sight of him a man collapses.”** |
| **41:2 MT** | **“No one is fierce enough to rouse him—so who can stand against me?”** Keep ʿלפניʿ, not conjectural ʿלפניוʿ. |
| **41:3 MT** | **“Who has ever put me in his debt, so that I should repay him? Everything under heaven is mine.”** |
| **41:4 MT** | **“I will not pass over his limbs, his tremendous strength, or the elegance of his construction.”** Ketiv/qere remains noteworthy. |
| **6:14** | **“A man whose courage is melting deserves loyalty from his friend—even when his fear of Shaddai is giving way.”** |
| **36:19** | **“Can your resources keep you out of straits—or all your strongest exertions?”** Low-to-medium confidence. |
| **11:12** | **“An empty-headed man will acquire sense when a wild donkey is born human.”** |
| **10:22** | **“A land black as night—death-shadow without order, where even the gleam is darkness.”** |
| **16:20** | **“My own friends are my mockers; my eyes pour themselves out to God.”** |
| **30:11** | **“He has unstrung me and humbled me; therefore they cast off every restraint in my presence.”** |

The most consequential tentative new synthesis is **Job 24**. Instead of assuming that vv.18–25 are simply a hopeless jumble, the chapter can be read as an argument with an implicit change of discourse level:

> The friendsʾ doctrine says the criminal is swiftly cursed, forgotten, and swallowed by Sheol.  
> Job points to experience: **God gives powerful criminals security.**  
> They eventually disappear, yes—but merely as everyone disappears.  
> That is not the special moral judgment the friends promised.  
> **“Prove me wrong.”**

That makes Job 24 considerably more coherent without changing its consonantal text.

The second strongest gain is **Job 6:14**. Parallelism plus Jobʾs personality strongly favors a radical ethical assertion rather than an orthodox correction of Job:

> **The point of loyal friendship is precisely that it remains when the suffererʾs faith is disintegrating.**

The third is **Job 11:12**, where the supposedly bizarre grammar becomes transparent once the second colon is allowed to decode the first:

> **A hollow man will acquire a mind when a wild donkey is born human.**

The fourth is methodological: **the hardest text does not necessarily require the most radical reconstruction.** Job 36:33, 10:22, 30:11, and most of MT 41:1–4 become substantially clearer once their semantic and discourse structure is recovered, while their consonants remain almost completely untouched. That outcome is consistent with Greensteinʾs larger account of Job as a poet deliberately exploiting foreignness, rare vocabulary, ambiguity, and linguistic innovation rather than merely transmitting a defective translation. citeturn19search0turn19search11

So the working first principle for the rest of the hundred is not “assume MT is right,” but neither is it “assume something underneath MT is garbled.” It is:

> **Assume there was once a maximally intelligible poem. Strip away later interpretive commitments, use parallelism and discourse to reconstruct its semantic architecture, let the Semitic languages compete for the lexical slots, and charge every consonantal alteration a real evidentiary cost.**

That preserves the genuinely powerful part of the “unknown Semitic inscription” thought experiment while preventing its enormous freedom from manufacturing the answer in advance.