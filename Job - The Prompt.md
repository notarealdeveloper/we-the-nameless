
# AGENTS.md

## Job First-Principles Decipherment Prompt

Your task is to **reverse engineer the requested chapter of Job from first principles**.

Treat Job not merely as difficult Biblical Hebrew, but as a deliberately multilingual, archaizing, script-sensitive ANE poetic text whose transmitted Masoretic form may preserve the underlying poem only imperfectly.

The goal is to recover the **simplest, strongest, most obviously parallel poetic reading** that can plausibly underlie the surviving consonantal evidence.

Assume as a working axiom:

> **Every poetic verse in Job originally has strong, intelligible parallelism. If the current translation does not exhibit convincing parallelism, the decoding is not finished.**

Assume further that the author may intentionally exploit obscure cognates, foreign Semitic vocabulary, mixed-language morphology, unusual spelling, ambiguous word boundaries, and visually confusable graphemes as part of the literary genre.

Do not stop when a reading is merely grammatical or possible. **Iterate until the verse clicks.**

The desired reaction to a successful reconstruction is:

> **Of course those two cola belong together.**

---

## Core Decipherment Model

### 1. Begin from the full Masoretic text

For every verse, reproduce the **entire Masoretic Hebrew exactly and completely**.

**Never omit, skip, silently discard, or fail to account for any Masoretic Hebrew letters in the verse tables.**

The Masoretic Hebrew must always remain visible as the transmitted evidence.

However:

> Treat the Masoretic consonants as **weak, noisy, and sometimes untrustworthy evidence**, not as inviolable ground truth.

The vowels, accents, punctuation, traditional word boundaries, grammatical parsing, and lexical assignments have an even lower prior.

A reconstruction may conclude that a surviving letter represents:

- a mater lectionis,
    
- secondary spelling normalization,
    
- dialect adaptation,
    
- scribal corruption,
    
- graphical confusion,
    
- partial translation,
    
- foreign-language morphology,
    
- or deliberate orthographic play.
    

But the report must always show **what Masoretic material is being explained**.

---

## 2. Strip the verse down

For each verse provide:

**Masoretic:** the full vocalized Masoretic text.

**Raw:** all consonants concatenated without vowels, cantillation, punctuation, maqqef-based assumptions, or spaces.

**Lossy:** a deliberately simplified Semitic ASCII search representation.

Use approximately:

|Hebrew class|Lossy symbol|
|---|---|
|‎ש / ס|`s`|
|‎ח / ה|`h`|
|‎ע|`3`|
|‎א|`'`|
|‎צ|`S`|
|‎ט|`T`|
|‎ק|`q`|

Do **not** delete letters in the lossy form.

“Lossy” means their evidentiary value is weakened, especially:

- matres lectionis,
    
- weak consonants,
    
- spelling updates,
    
- dialect-specific consonants,
    
- letters plausibly affected by graphical confusion.
    

Imagine that the surviving stream is an imperfect witness to an earlier poetic text.

---

## 3. Treat the stream as an unknown ANE Semitic inscription

Temporarily forget that the text is supposed to be Hebrew.

Approach it as though it had just been excavated and its language, segmentation, and dialect were unknown.

Do not privilege Biblical Hebrew in advance.

Search comparatively across:

- Ugaritic
    
- Aramaic
    
- Imperial Aramaic
    
- Syriac
    
- Phoenician
    
- Canaanite
    
- Akkadian
    
- Arabic as comparative evidence
    
- Old South Arabian where useful
    
- other relevant Northwest Semitic dialects
    

Reduce words mentally to root-like consonantal structures.

Prioritize **ordinary attested meanings in another Semitic language** over rare or strained Hebrew meanings invented only to rescue the traditional parsing.

Allow hybrids such as:

- an Aramaic lexical stem with Hebrew morphology,
    
- a Ugaritic-like root with a Hebrew prefix or suffix,
    
- an Akkadian semantic value under a Northwest Semitic consonantal form,
    
- an Aramaic particle embedded in otherwise Hebrew syntax,
    
- a foreign lexeme subsequently normalized toward Hebrew spelling.
    

Do not require the verse to belong consistently to one language.

---

## Parallelism Is the Main Error-Correcting Code

Treat strong poetic parallelism as the highest-level decoding constraint.

For every verse, explicitly identify what the two or more cola **ought to be doing with each other**.

Test structures such as:

- synonym // synonym
    
- antonym // antonym
    
- action // corresponding action
    
- cause // effect
    
- action // consequence
    
- object // corresponding object
    
- body part // corresponding action
    
- agent // action
    
- image // matching image
    
- concrete object // concrete object
    
- A:B :: C:D
    
- repeated lexical field
    
- escalation
    
- reversal
    
- chiastic inversion
    
- premise // conclusion
    
- question // matching question
    

If the resulting relationship is weak, awkward, or merely thematic, **continue decoding**.

Do not explain away missing parallelism as “irregular poetry” until all reasonable low-cost alternatives have been exhausted.

---

## Iterative Reconstruction Algorithm

For **every verse**, run this loop.

### Pass 1: Conventional consonants, new vocalization

Keep the consonants.

Discard the Masoretic vowels.

Test alternative vocalizations and ordinary polysemy.

Ask whether one familiar consonantal root has simply been assigned the wrong Hebrew meaning.

---

### Pass 2: New word boundaries

Discard inherited segmentation.

Test:

- one MT word → two earlier words,
    
- two MT words → one earlier word,
    
- prefix reassigned to previous or following word,
    
- suffix reassigned,
    
- a consonant moved across the traditional boundary,
    
- particles hidden inside a larger MT word,
    
- defective spelling that disguises a common root.
    

Resegmentation is extremely cheap and should be tried aggressively.

---

### Pass 3: Comparative Semitic lexical assignment

For each difficult consonantal cluster, search for the most natural cognates across ANE Semitic languages.

In the comparative table use concise labels such as:

- `DYN (Arm/Uga) “legal case”`
    
- `SPQ (Arm/Heb) “strike, clap”`
    
- `NḤT (Arm/Syr) “descend”`
    
- `ŠD (NW Sem.) “breast”`
    
- `KPR (Akk/NW Sem.) “cover/ransom”`
    

If multiple candidates are genuinely useful, include them.

Do not artificially choose Hebrew when another Semitic language yields a simpler and more parallel line.

---

## Grapheme Confusion Is a Core Reconstruction Tool

If the verse still does not exhibit strong parallelism, explicitly test paleographic corruption.

Do **not** limit the search to similarities in modern square Hebrew.

Ask:

> Could this consonant derive from a visually similar letter in Paleo-Hebrew, Phoenician-like writing, Imperial Aramaic, Jewish Aramaic, transitional Aramaic, or the later square script?

Especially test:

### Very high-priority confusions

- **Paleo-Hebrew Resh ↔ Paleo-Hebrew Dalet**
    
- **Aramaic Resh ↔ Aramaic Dalet**
    
- **Paleo-Hebrew Waw ↔ Aramaic Resh**
    
- **Paleo-Hebrew Waw ↔ Aramaic Dalet**
    

Operationally:

- `R ↔ D`
    
- `W ↔ R`
    
- `W ↔ D`
    

These should be tested early whenever they turn an obscure root into a common Semitic word that improves the parallelism.

### High-value additional confusions

- **Aramaic Kaph ↔ Aramaic Beth**
    
    - test `K ↔ B`
        
- **Aramaic Ayin ↔ Aramaic Yodh**
    
    - test `ʿ ↔ Y`
        

### Secondary but plausible

- **Paleo-Hebrew Resh ↔ Paleo-Hebrew Beth**
    
    - test `R ↔ B`
        

Also consider other historically plausible similarities when the script evidence warrants them.

A proposed graphical corruption becomes especially attractive when **one letter swap causes several neighboring words to collapse into a coherent semantic field**.

For example, a reconstruction producing something like:

> strike // hand  
> eye // see  
> heat // fire  
> hunger // food

is much stronger than an emendation that merely creates one possible dictionary word.

---

## Language-Stage Corruption

If necessary, allow the text to have passed through more than one linguistic or scribal stage.

Possible mechanisms include:

- lexical borrowing,
    
- dialect substitution,
    
- calquing,
    
- mistranslation,
    
- partial translation,
    
- phonological adaptation,
    
- Hebrew grammatical affixes attached to a foreign Semitic stem,
    
- replacement of one Semitic cognate with another,
    
- word redivision after a language change,
    
- spelling normalization,
    
- corruption during script transition,
    
- deliberate multilingual wordplay by the author.
    

Do not assume such mechanisms gratuitously.

But do not reject them merely because the resulting form is “not normal Hebrew.”

In Job, **“not normal Hebrew” is part of the evidence**.

---

## Reconstruction Cost Function

The objective is:

> **Maximum obvious parallelism for minimum reconstruction cost.**

Prefer, roughly in this order:

|Reconstruction move|Cost|
|---|---|
|Different vocalization|very low|
|Different word boundary|very low|
|Different ordinary sense of same root|very low|
|Common cognate sense from another Semitic language|low|
|Aramaic/Ugaritic/etc. stem with Hebrew morphology|low|
|Mater or weak-letter reinterpretation|low|
|One strongly motivated grapheme confusion|medium|
|One plausible language-stage corruption|medium|
|One graphically weaker consonantal change|medium-high|
|Two independent strong-consonant changes|high|
|Multiple unrelated emendations|very high|
|Unattested root invented for the verse|extremely high|

Do not mechanically prefer zero emendation if the resulting poetry is bad.

A single well-motivated graphical substitution that yields **perfect parallelism** may be far preferable to a zero-change interpretation requiring several bizarre lexical senses and syntactic evasions.

---

## Stopping Rule

For every difficult verse, generate alternatives and iterate.

Do **not** stop because:

- a lexicon permits the MT sense,
    
- a modern translation has produced grammatical English,
    
- an emendation has precedent,
    
- or one possible interpretation can be defended.
    

Stop only when you have identified the **lowest-cost reconstruction that produces very strong, immediately recognizable poetic parallelism**.

If no reconstruction reaches that level, say so explicitly and retain the best candidates.

If several candidates work, rank them.

A particularly strong reconstruction should satisfy several constraints simultaneously:

1. common or well-attested lexical senses,
    
2. economical segmentation,
    
3. plausible morphology,
    
4. obvious parallelism,
    
5. strong relation to neighboring verses,
    
6. strong relation to the speaker's argument,
    
7. plausible paleographic mechanism where needed,
    
8. minimal number of independent assumptions.
    

---

## Top-Down Context Comes After Bottom-Up Reconstruction

Only after the lexical and paleographic pass should you use:

- the immediately surrounding verses,
    
- the paragraph or speech,
    
- the chapter structure,
    
- the speaker's personality,
    
- recurring themes in Job,
    
- human motivations,
    
- legal, social, bodily, natural, or theological imagery.
    

Use these as **constraints**, not excuses.

The context should help choose between viable bottom-up readings.

Do not use context to manufacture a lexical meaning unsupported by the consonants or comparative Semitic evidence.

---

## Required Output Format

Match the structure and style of the supplied **Job: First-Principles Reconstruction** report.

Use only headings at `##`, `###`, `####`, or deeper levels. Never use a single `#` heading.

### Opening sections

Produce:

## Job [passage]: First-Principles Reconstruction

### Purpose

State that the passage is being treated as a decipherment problem and that the controlling question is which reconstruction best explains consonantal evidence, parallelism, context, and comparative Semitic data.

### Why Job [passage]

Briefly explain why this passage is difficult and why it is a useful test case.

If appropriate, include a small ranking table placing it among other notoriously difficult Job passages.

### Method

Summarize the reconstruction algorithm.

### Lossy transliteration conventions

Provide the convention table.

### Paleographic confusion map

Provide a compact table of the most relevant graphical confusions and their priority.

### Evaluation scale

Explain that contextual-fit scores evaluate poetic/discourse coherence, not historical probability.

### Working passage structure

Give a short table showing the likely discourse function of each verse or subsection.

---

# Verse-by-Verse Analysis

For **every verse**, use exactly this structure.

### Job X:Y

**Masoretic:** [FULL Masoretic verse]

**Raw:** [FULL consonantal stream without spaces]

**Lossy:** `[FULL lossy stream]`

The **Masoretic, Raw, and Lossy lines must each represent the entire verse. Never omit any part of the transmitted Hebrew.**

#### Standard MT-Oriented Partitioning

Create a table:

|Hebrew unit|Lossy|Standard construal|Standard English|
|---|---|---|---|

Every portion of the Masoretic verse must appear somewhere in this table.

Do **not** omit particles simply because they are boring.

Do not omit a difficult word because the reconstruction later changes its boundary.

The point of this table is to make the inherited parse completely auditable.

---

#### Bottom-Up Comparative Partitioning

Create a table:

|Hebrew / candidate|Lossy|Comparative evidence|Best English|
|---|---|---|---|

Again:

> **Every Masoretic consonant must be visibly accounted for.**

If the preferred reading changes a boundary, show it explicitly:

LTR example: `MT unit → proposed segmentation`

If a consonant is graphically emended, show it explicitly:

`R → D, Paleo-Hebrew confusion`

If a word is interpreted through another language, name the language:

`DYN (Arm/Uga)`

If Hebrew morphology appears attached to a foreign stem, say so.

If one Masoretic letter is treated as secondary spelling or a mater, state that explicitly rather than silently ignoring it.

---

#### Standard English Translation

Give a fresh, fairly literal English rendering of the normal MT-oriented interpretation.

Do not quote a copyrighted translation at length.

---

#### Our English Translation

Give the best reconstructed translation.

It should be readable but still close enough to the proposed lexical reconstruction to show the recovered parallelism.

---

#### Recovered Parallelism

For difficult or substantially reconstructed verses, add a compact table such as:

|Colon A|Colon B|
|---|---|
|blow|hand|
|wrath|El|
|strike|bend|

or:

|A|B|C|D|
|---|---|---|---|
|drought|steals|snow-water|—|
|Sheol|steals|sinners|—|

Explain in one or two sentences why this structure is compelling.

For verses where the MT is already obviously parallel, this section may simply state that no additional reconstruction is required.

---

#### Reconstruction Cost

Give a compact list or table showing what the reading required, for example:

|Move|Cost|
|---|---|
|Re-vocalize DYN as “legal case”|low|
|Re-segment BLYLW → BLY LW|very low|
|R → D by Paleo/Aramaic confusion|medium|

Do not hide the cost of the reconstruction.

---

#### Contextual Fit

Use:

|Metric|Rating|Reason|
|---|---|---|
|Standard contextual fit|X/10|...|
|Our contextual fit|X/10|...|
|Improvement|+X.X|...|

The score should emphasize **parallelism plus discourse coherence**.

A standard reading that is grammatically possible but poetically incoherent should score poorly.

---

**Philological confidence:** very high / high / medium-high / medium / low-to-medium / low.

Keep confidence separate from contextual-fit score.

A reconstruction can have:

- very high contextual payoff,
    
- but only medium philological confidence.
    

Say so.

---

#### Analysis

Explain:

- which consonantal cluster was decisive,
    
- which alternative segmentations were tested,
    
- which comparative roots matter,
    
- whether a grapheme swap was necessary,
    
- why the resulting parallelism is stronger,
    
- how the verse fits its neighbors.
    

Do not over-explain routine words.

Concentrate analysis on the **key that unlocks the verse**.

---

## Passage-Level or Chapter-Level Synthesis

Use whichever label fits the scope.

### Recovered Argument

Rewrite the whole reconstructed passage continuously in fluid English.

The aim is to show whether the formerly obscure verses now form a coherent discourse.

### Principal Departures from the Standard Reading

Use:

|Verse|Standard construal|Bottom-up proposal|Payoff|Confidence|
|---|---|---|---|---|

Include only meaningful departures.

### Overall Contextual-Fit Result

Calculate:

- mean standard contextual fit,
    
- mean bottom-up contextual fit,
    
- mean improvement.
    

Treat this as bookkeeping rather than proof.

### Confidence Summary

Group conclusions by confidence level.

### Recovered Poetic Architecture

Where useful, show larger structures such as:

- A / B / C / C′ / B′ / A′
    
- lexical chains,
    
- repeated roots,
    
- recurring images,
    
- question-response sequences,
    
- spatial oppositions,
    
- legal terminology,
    
- body imagery,
    
- death/light/darkness structures.
    

### Corruption-Mechanism Summary

For passages requiring reconstruction, summarize which mechanisms actually did useful work:

- re-vocalization,
    
- resegmentation,
    
- Aramaism,
    
- Ugaritic cognate,
    
- Akkadian semantic cognate,
    
- Hebrew morphology on foreign stem,
    
- `R ↔ D`,
    
- `W ↔ R/D`,
    
- `K ↔ B`,
    
- `ʿ ↔ Y`,
    
- `R ↔ B`,
    
- weak-letter reinterpretation,
    
- other script-specific confusion.
    

Note if the same corruption mechanism explains multiple verses. Repeated success by one mechanism should raise its prior elsewhere in Job.

### Future Expansion Template

Recommend further work such as:

1. full dictionary citations,
    
2. Septuagint,
    
3. Peshitta,
    
4. Targum,
    
5. Vulgate,
    
6. DSS evidence where extant,
    
7. paleographic exemplars,
    
8. alternative defective spellings,
    
9. exhaustive segmentation search,
    
10. scored reconstruction alternatives.
    

### Textual and Comparative Sources Already Used

List major primary texts, dictionaries, comparative resources, and textual witnesses actually used.

---

## Critical Rules

1. **Never omit any Masoretic Hebrew from the verse-level evidence tables.**
    
2. **Never treat Masoretic word boundaries as sacred.**
    
3. **Never treat Masoretic vowels as primary evidence.**
    
4. **Never assume an obscure word must be Hebrew.**
    
5. **Allow Aramaisms and other ANE Semitic roots with Hebrew grammatical attachments.**
    
6. **Actively test defective spellings.**
    
7. **Actively test new word boundaries.**
    
8. **Actively test paleographic confusions in Paleo-Hebrew, Aramaic, transitional Aramaic, and square Hebrew.**
    
9. **Assume strong poetic parallelism exists and use it as the main error-correcting code.**
    
10. **Prefer one elegant corruption that repairs an entire couplet over several strained dictionary meanings that preserve MT unchanged.**
    
11. **Do not maximize novelty; minimize total reconstruction cost.**
    
12. **Do not stop until the verse has been iterated toward the strongest obvious parallelism available.**
    
13. **Treat “this is strange Hebrew” as a reason to investigate, not as an explanation.**
    
14. **Assume the author may be doing this deliberately as part of Job's poetic technique.**
    
15. **For each verse, look for the simple hidden key that makes the verse collapse into intelligible poetry.**
    

The governing heuristic is:

> **The transmitted text is evidence. Parallelism is the checksum. Comparative Semitic is the dictionary. Paleography is the error model. Find the cheapest reconstruction that makes the poetry click.**