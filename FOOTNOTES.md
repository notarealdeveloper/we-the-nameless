# Footnote revision prompt

Apply the replacements requested below to the specified `.tex` files.

- Each entry identifies one footnote by file and verse, and includes its original
  `REF: ` text and current replacement text. The text blocks contain footnote
  contents, without the surrounding `\fC{...}` command.
- Only use text inside a `CHANGE TO:` fenced block as a requested replacement.
  If that block is empty or contains only whitespace, leave that footnote unchanged.
  If every `CHANGE TO:` block is empty, make no changes at all.
- For each nonempty `CHANGE TO:` block, replace only that entry's active footnote
  contents with the supplied text, preserving any LaTeX commands. Do not paraphrase
  or otherwise rewrite the supplied wording.
- Preserve the complete commented-out original `\fC` block, including its `REF: `
  prefix. Keep it immediately above the active footnote, fully commented out.
- Preserve indentation, the existing footnote macro, and TeX whitespace behavior.
  Use `%` where necessary so formatting introduces no meaningful whitespace,
  particularly between adjacent footnotes or between prose and a footnote.
- Treat repeated text at different verses as separate entries; update only entries
  with a nonempty `CHANGE TO:` block. If an entry cannot be matched unambiguously,
  report that entry instead of guessing.
- Leave unrelated text and this review file unchanged. Do not build the book.

## 1. `01-genesis/31.tex` — verse 53

OLD FOOTNOTE:

```tex
REF: ``God'' and ``gods'' are both \heb{אלהים}, so exactly
how many gods Laban means here is unclear.
```

CURRENT FOOTNOTE:

```tex
The Hebrew \heb{אלהים} can mean either ``God'' or ``gods,'' leaving Laban's intended
number unclear.
```

CHANGE TO:

```tex
\aB{Laban's either talking about ``God'' singular or ``gods'' plural here, we can't tell.}
```

## 2. `01-genesis/38.tex` — verse 1

OLD FOOTNOTE:

```tex
REF: Judah. The eponymous ancestor of the Jews, Judah is the most prominent
of the brothers in the Joseph stories, and here he is the only one of
Jacob’s sons besides Joseph to have a separate story about him. Some say
that the word means “to be thankful.” Its derivation is unknown.
Footnote 38:1. Judah went down. The next chapter begins with “Joseph had
been brought down.” The contrast is blatant (even more so in the Hebrew)
between Judah’s independence and Joseph’s weakness: Judah went down, and
Joseph was brought down.
```

CURRENT FOOTNOTE:

```tex
Judah, namesake of the Jews, leads the brothers in the Joseph narrative and alone
besides Joseph gets his own story. His name's origin is uncertain, though some connect
it to thankfulness. Judah “went down” freely; Joseph “was brought down” (39:1),
emphasizing their contrasting freedom and powerlessness.
```

CHANGE TO:

```tex
Judah's the only one of the kids besides Joseph to have a whole story about him.
```

## 3. `01-genesis/41.tex` — verse 40

OLD FOOTNOTE:

```tex
REF: conform. The verb here, which usually means “to kiss,”
is a problem for all translators. It may reflect a scribal
problem or an idiom that is no longer familiar to us.
\aB{
	\footnotesize Or the magic stick is making him say it.
}
```

CURRENT FOOTNOTE:

```tex
“Conform” translates a verb normally meaning “kiss”; the wording may be corrupt or
preserve an unfamiliar idiom. \aB{\footnotesize Or the magic stick is making him say
it.}
```

CHANGE TO:

```tex
The verb here means “to kiss.” We don't know why he's saying that.%
\fB{Maybe the magic stick is making him say it.}

```

## 4. `01-genesis/44.tex` — verse 1

OLD FOOTNOTE:

```tex
REF: each man’s silver. The first time, when ten brothers come to Egypt,
Joseph imprisons Simeon, and he has their silver placed back in their
nine sacks. The second time, when they return with Benjamin, Joseph
releases Simeon, and he has their silver placed back in their eleven
sacks. The total number of portions of silver returned is twenty,
corresponding to the price that was paid for Joseph (37:28). It is yet
another case of a hidden link between acts of deception and their
payback in later events.
```

CURRENT FOOTNOTE:

```tex
Joseph returns silver in nine sacks on the first visit and eleven on the second: twenty
portions, echoing his sale price (37:28). The hidden numerical link connects the
brothers' deception with its later repayment.
```

CHANGE TO:

```tex
\aB{Count how many silver. There's a thing.}
```

## 5. `01-genesis/47.tex` — verse 3

OLD FOOTNOTE:

```tex
REF: Your servants are shepherds. Joseph had just told them not to answer
Pharaoh that they are shepherds (46:33–34), yet they go ahead and say
it! Some might surmise that this seeming contradiction is the result of
the combination of two sources into one story. But that is not correct.
This has nothing to do with the sources that are identified in critical
biblical scholarship. This is one continuous passage (all from the
source known in scholarship as J). The difficulty in the brothers’ words
must therefore be understood as being a part of the story itself. The
brothers simply do not follow Joseph’s instructions. He has told them to
say that they are cowherds, not shepherds, because Egyptians disdain
shepherds; but they are not willing to misrepresent themselves in this
way. Are they right? On one hand, Pharaoh does permit them to settle and
offers them the best of Egypt’s land. But, on the other hand, Pharaoh
stops speaking directly to them. He switches to speaking about them in
the third person to Joseph. And he offers to have some of them serve as
officers over his cattle even though they have just said they are
shepherds, not cattlemen.
```

CURRENT FOOTNOTE:

```tex
The brothers call themselves shepherds despite Joseph's advice to say cattlemen
(46:33–34). This tension occurs within J, rather than between sources: they refuse to
disguise their occupation. Pharaoh grants them good land, but then addresses Joseph
instead and offers them work managing cattle anyway.
```

CHANGE TO:

```tex
```

(Just remove this footnote.)

## 6. `01-genesis/47.tex` — verse 5

OLD FOOTNOTE:

```tex
REF: This section, 47:5–12, comes in the middle of a J text. But Jacob says here that he is 130 years old and that Abraham and Isaac lived longer, while in J YHWH has decreed that no human will live more than 120 years. It is in P that ages are given and that Abraham and Isaac live longer. Moreover, this section has other characteristics of P: The phrases “the days of the years” and “the years of your life” occur only in P. The terms “residences” and “possession” occur only in P. The phrase “as he commanded” occurs fifty-three other times in Genesis–Numbers, and fifty-two are in P. And it is in P that the people live in Rameses. Nonetheless, we should recognize that it is possible that the Redactor combined some material from J or E with P to form this section. The reference to Goshen (v. 6) may be in conflict with the reference to Rameses, and P never mentions Goshen elsewhere. The words “Let them live in Goshen” may have originally read “they lived in Goshen,” which would look the same in the consonantal text. And Goshen is what the brothers requested in the J text (v. 4). Further, this matter is complicated by the fact that the Septuagint text is different, which may be related to the recurrence of the words “let them live in the land of Goshen” in vv. 4 and 6.
```

CURRENT FOOTNOTE:

```tex
Genesis 47:5–12 interrupts J with P's characteristic ages and vocabulary: Jacob is 130,
beyond J's 120-year limit, and the passage uses P's language of residences, possession,
and commands, as well as Rameses. Goshen may indicate material from J or E added by the
Redactor. The consonantal Hebrew permits either “let them live” or “they lived” in
Goshen, and the Septuagint's differing text further complicates the passage.
```

CHANGE TO:

```tex
REF: This section, 47:5–12, comes in the middle of a J text. But Jacob says here that he is 130 years old and that Abraham and Isaac lived longer, while in J YHWH has decreed that no human will live more than 120 years. It is in P that ages are given and that Abraham and Isaac live longer. Moreover, this section has other characteristics of P: The phrases “the days of the years” and “the years of your life” occur only in P. The terms “residences” and “possession” occur only in P. The phrase “as he commanded” occurs fifty-three other times in Genesis–Numbers, and fifty-two are in P. And it is in P that the people live in Rameses. Nonetheless, we should recognize that it is possible that the Redactor combined some material from J or E with P to form this section. The reference to Goshen (v. 6) may be in conflict with the reference to Rameses, and P never mentions Goshen elsewhere. The words “Let them live in Goshen” may have originally read “they lived in Goshen,” which would look the same in the consonantal text. And Goshen is what the brothers requested in the J text (v. 4). Further, this matter is complicated by the fact that the Septuagint text is different, which may be related to the recurrence of the words “let them live in the land of Goshen” in vv. 4 and 6.

```

## 7. `01-genesis/48.tex` — verse 4

OLD FOOTNOTE:

```tex
REF: I’m making you fruitful and multiplying you, and I’ll make you …
But God did not say, “I’ll make you fruitful…” God said, “Be fruitful …”
(35:11). Why does Jacob tell Joseph that God promised to do it when God
actually told him to do it? Perhaps it is because Jacob has only one
more son (Benjamin) after God tells him this, and so the becoming
fruitful must refer to the births of his grandchildren and
great-grandchildren. Jacob would not see this as in his power but rather
as God’s doing, and so he understands God’s words not as a command but
as a promise and a blessing.
```

CURRENT FOOTNOTE:

```tex
Jacob recalls God's command to “be fruitful” (35:11) as a promise to make him fruitful.
Since only Benjamin was born afterward, he may understand the words as a blessing
fulfilled through grandchildren and later descendants, whose births he credits to God.
```

CHANGE TO:

```tex

```

Remove the footnote. Keep the commented out REF one.

## 8. `01-genesis/48.tex` — verse 7

OLD FOOTNOTE:

```tex
REF: Verse 7 fits uncomfortably in its context, connecting neither to the preceding nor to the following verses. And it merges elements of two sources: It refers to Paddan Aram, which is characteristic of P, but it says “there was still a span of land to come to Ephrath,” and it refers to Rachel’s being buried on the Ephrath road, which comes from E (Gen 35:16–20). It therefore appears to be an addition that the Redactor made to the text. Perhaps its function was to separate the two conflicting passages about Ephraim and Manasseh that precede and follow it. See the next note. Alternatively, this verse might after all be P, because it fits with the next P passage (49:29–33). As a unit these two passages could be saying: “As for me: Rachel died and was buried on the road, but when I die I want to be buried back in my ancestral tomb with the other patriarchs and matriarchs.” It is therefore uncertain whether v. 7 is P or R.
```

CURRENT FOOTNOTE:

```tex
Verse 7 interrupts the surrounding narrative and combines P's Paddan Aram with E's
account of Rachel's burial near Ephrath (35:16–20). The Redactor may have inserted it to
separate conflicting accounts of Ephraim and Manasseh. Alternatively, it may belong to
P, contrasting Rachel's roadside grave with Jacob's request for the ancestral tomb
(49:29–33). Its attribution remains uncertain.
```

CHANGE TO: Keep the REF footnote, uncommented.

```tex
REF: This section, 47:5–12, comes in the middle of a J text. But Jacob says here that he is 130 years old and that Abraham and Isaac lived longer, while in J YHWH has decreed that no human will live more than 120 years. It is in P that ages are given and that Abraham and Isaac live longer. Moreover, this section has other characteristics of P: The phrases “the days of the years” and “the years of your life” occur only in P. The terms “residences” and “possession” occur only in P. The phrase “as he commanded” occurs fifty-three other times in Genesis–Numbers, and fifty-two are in P. And it is in P that the people live in Rameses. Nonetheless, we should recognize that it is possible that the Redactor combined some material from J or E with P to form this section. The reference to Goshen (v. 6) may be in conflict with the reference to Rameses, and P never mentions Goshen elsewhere. The words “Let them live in Goshen” may have originally read “they lived in Goshen,” which would look the same in the consonantal text. And Goshen is what the brothers requested in the J text (v. 4). Further, this matter is complicated by the fact that the Septuagint text is different, which may be related to the recurrence of the words “let them live in the land of Goshen” in vv. 4 and 6.
```

## 9. `01-genesis/48.tex` — verse 8

OLD FOOTNOTE:

```tex
REF: In v. 5 Jacob promotes Ephraim and Manasseh to full status, equal to his own sons. But now in v. 8 he looks at them and asks, “Who are these?”! The former verse is P, and the contradiction developed when this verse was placed in the middle of the E passage about Ephraim and Manasseh.
```

CURRENT FOOTNOTE:

```tex
In P's verse 5, Jacob adopts Ephraim and Manasseh as his own sons; in E's verse 8, he
asks who they are. Combining the two accounts creates the contradiction.
```

CHANGE TO: Keep the REF: footnote, uncommented.

```tex

```

## 10. `01-genesis/48.tex` — verse 10

OLD FOOTNOTE:

```tex
REF: Israel’s eyes were heavy from old age. The analogy to his father is
obvious. When Isaac had been old, on his deathbed, unable to see, Jacob
had come and appropriated his brother Esau’s blessing. Now Jacob himself
is old, on his deathbed, unable to see, and he favors the younger son,
Ephraim, in his blessing.
```

CURRENT FOOTNOTE:

```tex
Jacob once exploited his aged, blind father's condition to take Esau's blessing. Now
aged and blind himself, he again favors the younger son, blessing Ephraim over his older
brother.
```

CHANGE TO:

```tex
Jacob always pulls a fast one in these death bed blessing things, even his own.
```

## 11. `01-genesis/48.tex` — verse 22

OLD FOOTNOTE:

```tex
REF: one shoulder over your brothers. This expression appears to refer to
Joseph’s getting two tribes while each of his brothers gets only one.
But it also puns on the word for shoulder, Hebrew š kem (Shechem).
Shechem is the name of the city that will one day be the capital of the
kingdom of Israel, and it is located in one of the Joseph tribes
(Manasseh).
```

CURRENT FOOTNOTE:

```tex
Joseph's extra “shoulder” apparently means his two tribes, compared with one for each
brother. The Hebrew also puns on Shechem, a city in Manasseh's territory that later
becomes Israel's capital.
```

CHANGE TO: The following, as a \fC{} footnote. Make sure the {d,tr} displays properly in the TeX, since { and } are special in TeX.

```tex
Shechem means shoulder. It's also the future capital of the Northern kingdom of Israel, and the past capital of dirty {d,tr}icks.
```

## 12. `01-genesis/49.tex` — verse 20

OLD FOOTNOTE:

```tex
REF: Asher. The MT says “from Asher,” but that is a scribal mistake. The
Hebrew letter mem (meaning “from”) has been displaced from the end of
the preceding word, ‘qbm (where it means “their” heel).
```

CURRENT FOOTNOTE:

```tex
The MT's “from Asher” appears to misplace the letter mem: it belongs at the end of the
preceding word, where it makes “heel” into “their heel.”
```

CHANGE TO: Keep the REF footnote, uncommented. Delete the current one.

```tex

```

## 13. `01-genesis/50.tex` — verse 21

OLD FOOTNOTE:

```tex
REF: he spoke on their heart. We have seen that each act of deception since
Jacob led to another deception that came as a recompense. Thus
deceptions and hurts within a family can go on in a perpetual cycle. In
order to bring it to an end, one member of the family who is entitled to
retribution must stop the cycle and forgive instead. That is what Joseph
does here. This beautiful end of the story of deceptions and
retributions completes an intricately embroidered narrative. Many
interpreters have treated the Joseph cycle as if it were a separate
entity, referring to it as a “novella.” Insofar as that term connotes an
independent work, it is misleading, cutting off what is an integral part
of this connected narrative. Symbols, ironies, and relationships of
characters and events are lost when one performs this surgery and
separates the Joseph cycle from the rest of the story.
```

CURRENT FOOTNOTE:

```tex
Joseph breaks the family's recurring cycle of deception and retaliation by forgiving
when he could take revenge. This ending ties his story to Jacob's; treating the Joseph
narrative as an independent novella obscures their shared symbols, ironies, and
relationships.
```

CHANGE TO: No changes.

```tex

```

## 14. `02-exodus/01.tex` — verse 11

OLD FOOTNOTE:

```tex
REF: work-companies. The Hebrew term, missîm, refers not to individually
owned household slaves but to a policy of forced labor imposed on an
entire community (a corvée). The Israelites build whole cities, and they
all live in a particular region of Egypt (Goshen), separate from the
Egyptian population (Exod 8:18; 9:26). Centuries later, King Solomon
imposes missîm on Israel, requiring, in addition to monetary taxes, a
period of labor on national projects. This so infuriates the Israelites
that they stone to death the king’s minister of missîm (1 Kings 5:27–28;
12:18). Israelites will bear taxation, but the requirement of forced
labor implies control over people’s bodies by the government. This is
appalling to a people whose recollection of having been slaves is a
central doctrine to their understanding of themselves and their history.
```

CURRENT FOOTNOTE:

```tex
The Hebrew missîm means compulsory labor imposed on a community, rather than private
household slavery. Israel builds cities while living apart in Goshen (8:18; 9:26).
Solomon later imposes similar labor, and Israelites eventually kill the official
responsible (1 Kings 5:27–28; 12:18). Such state control over their bodies clashes with
a national identity grounded in escape from slavery.
```

CHANGE TO: No changes.

```tex

```

## 15. `02-exodus/01.tex` — verse 16

OLD FOOTNOTE:

```tex
REF: the two stones. This is often understood to mean some sort of birthing
stool made of two stones, but the more natural understanding here in the
context of identifying boys is that the two stones refer to the
testicles.
```

CURRENT FOOTNOTE:

```tex
“The two stones” is often taken as a birthing stool, but the context of identifying male
babies suggests testicles.
```

CHANGE TO: Keep the REF footnote, uncommented.

```tex

```

## 16. `02-exodus/01.tex` — verse 19

OLD FOOTNOTE:

```tex
REF: they’re animals! The vowels inserted in the Masoretic Text would make
this an adjective (“they’re lively”), but that form of the word does not
occur anywhere else in the Bible. I think that it is more likely that
the midwives are meant to be speaking in this negative way about the
Israelite women in order to hide their own violation of the king’s
order.
```

CURRENT FOOTNOTE:

```tex
The Masoretic vowels yield “they're lively,” an adjective otherwise unattested in the
Bible. “They're animals” may instead be the midwives' disparaging cover story for
disobeying Pharaoh.
```

CHANGE TO: Keep the REF footnote, uncommented.

```tex

```

###############
No more changes after this.
###############

## 17. `02-exodus/14.tex` — verse 21

OLD FOOTNOTE:

```tex
REF: In the J Red Sea story, the Hebrew uses the same term for dry ground (ḥārābâ) that is used in the J flood story (Gen 7:22). Meanwhile, in the P Red Sea story, the Hebrew uses the same term for dry ground (yabbāšâ) that is used in the P flood (and creation) story (Gen 1:9,10; 8:14).
```

CURRENT FOOTNOTE:

```tex
Each source repeats its own word for dry ground across the sea and flood stories: J uses
ḥārābâ (Gen 7:22), while P uses yabbāšâ, also found in its creation account (Gen 1:9–10;
8:14).
```

CHANGE TO:

```tex

```

## 18. `02-exodus/15.tex` — verse 26

OLD FOOTNOTE:

```tex
REF: Exod 15:26 has more phrases that sound Deuteronomistic than any other passage in Genesis through Numbers. Still, it is uncertain and may be E, which has other similarities to Deuteronomistic language. (See the note on Exod 12:24.)
```

CURRENT FOOTNOTE:

```tex
Exodus 15:26 has an unusually strong concentration of Deuteronomistic phrasing for
Genesis–Numbers. Its source remains uncertain: E also shares such language and may be
responsible here (see the note on Exod 12:24).
```

CHANGE TO:

```tex

```

## 19. `02-exodus/34.tex` — verse 1

OLD FOOTNOTE:

```tex
REF: The tablets in E are shattered. Now comes the J account of the tablets. In the combined JE text, it would be awkward to picture God just commanding Moses to make some tablets, as if there were no history to this matter, so RJE adds the explanation that these are a replacement for the earlier tablets that were shattered. In E the tablets that are shattered are never said to be replaced. This suggests that, according to E, the ark that is housed in the Temple in Judah to the south either contains broken tablets or no tablets at all. As in other places, the northern Israel source E has clashing religious symbols from those of the southern kingdom of Judah. See the Collection of Evidence, pp. 19, 21.
```

CURRENT FOOTNOTE:

```tex
E's tablets are shattered and never explicitly replaced. The JE editor presents J's
tablets as replacements to connect the accounts. E may therefore imply that Judah's
Temple ark holds broken tablets or none, reflecting tensions between northern Israel's
religious symbols and those of Judah.
```

CHANGE TO:

```tex

```

## 20. `02-exodus/34.tex` — verse 6

OLD FOOTNOTE:

```tex
REF: This famous formula in J emphasizes the merciful over the just side of God: mercy, grace, kindness. As noted in the Collection of Evidence (p. 12), P never uses these words or several other words relating to mercy. P rather emphasizes the just side of God. This is an important example of the pervasive way in which the Bible became more than the sum of its parts when the Redactor combined the sources. J (and E and D) emphasized the merciful side of God; P emphasized the just side. The final version of the united Torah now brings the two sides together in a new balance, conveying a picture of God who is torn between His justice and His mercy—which has been a central element of the conception of God in Judaism and Christianity ever since.
```

CURRENT FOOTNOTE:

```tex
J emphasizes God's mercy, grace, and kindness, while P avoids this vocabulary and
stresses justice. Combining these sources brings both emphases into one portrayal of
God, whose tension between justice and mercy becomes central to Jewish and Christian
understandings.
```

CHANGE TO:

```tex

```

## 21. `02-exodus/34.tex` — verse 27

OLD FOOTNOTE:

```tex
REF: This famous formula in J emphasizes the merciful over the just side of God: mercy, grace, kindness. As noted in the Collection of Evidence (p. 12), P never uses these words or several other words relating to mercy. P rather emphasizes the just side of God. This is an important example of the pervasive way in which the Bible became more than the sum of its parts when the Redactor combined the sources. J (and E and D) emphasized the merciful side of God; P emphasized the just side. The final version of the united Torah now brings the two sides together in a new balance, conveying a picture of God who is torn between His justice and His mercy—which has been a central element of the conception of God in Judaism and Christianity ever since.
```

CURRENT FOOTNOTE:

```tex
J emphasizes God's mercy, grace, and kindness, while P avoids this vocabulary and
stresses justice. Combining these sources brings both emphases into one portrayal of
God, whose tension between justice and mercy becomes central to Jewish and Christian
understandings.
```

CHANGE TO:

```tex

```
