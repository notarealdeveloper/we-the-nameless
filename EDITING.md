
---
## Stuff to do later

Catch R up on Gen 44-48.

Whenever a redactor pun is deleting anything, use \eRJE{...}. Otherwise, use \eR{...}.

## Stuff to review manually

Gen 16:12.

Gen 17:7

Gen 17:10. The come outside and look at the stars part is good, the rest could use some polish.

## Stuff to do now

Agents: Do all the items below except the ones marked as manual.

1. Make a directory that's all symlinks to the tex files but replacing .tex with .md so I can edit them on obsidian from my phone. Call it ed.

2. Add macros for \aAX, \aBX, \aCX, and footnotes \fAX, \fBX, \fCX, which will be compiled away to nothing if a config option called redactor is set to the value censored as opposed to uncensored.

3. Fix all the things below, by editing the files in `[01][0-9]-*/*.tex`

1 Samuel 25:3. Nabal is Laban backwards. Mention this in a footnote.

Gen 11:3. Fix the footnote with the brick image in it by making it either a float or not a footnote or making the brick smaller, just make sure the text all stays together on the page somehow with the brick.

Gen 14:9. Replace the ugly --- with a Unicode dash, it's rendering wrong.

Gen 15:13. Move the footnote on He to the end of the line.

Gen 15:18. Change the }um to }ome

Gen 16:4. Replace reaction with \eRJE{to}.

Gen 16:13. "Then is says" should be "Now the text says"

Gen 16:13. "Then she says" should be "Now she says"

Gen 16:13. "Here's some of their choices" should be wrapped in \aC{} along with the numbered list that follows, and the \redacted{ass} \eR,{posterior} should be changed to \eRJE{posterior}. The \aC{} wrapping everything should continue until right after the "Let’s try to put all that behind us." line.

Gen 16:15. looking at her story when she told him (i.e., sed the/her)

Gen 16:16. Remove footnote. Change text to: Like c'mon, he's eighty. And six. He's doing his best.

Gen 17:1. Change the line saying "Ninety nine" etc to say instead "Ninety years old. And nine." And change All of a sudden to And all of a sudden 

Gen 17:1. In the footnote, wrap YHWH in \eRed{}.

Gen 17:4. Lots of kids, the whole thing should say Lots of kids, the whole deal.

Gen 17:4. I made her come back should say "I maid her come back."

Gen 17:5. Put this definition somewhere nearby where he renames Abe as a footnote on one of the lines where he says "forever and ever." \fC{Ever. (\heb{אבר}; noun). limb, organ, (colloquial) penis.} You can fix up the definition structure's punctuation and syntax to make it more like dictionaries do.

Gen 17:6. Have YHWH say "MLK will come out of you Abe, MLK'im, a lot." near the part where he's saying kings will come out of you.

Gen. 17:6. Make this c\eR{hildren}o\eR{h my oh }me b--- Abe, I'll spread it everywhere. 

Gen 17:10. Latex quotes \`\`'' aren't rendering right inside of \eR{}. Fix that in all the redactor sources: R, RJE, Red, and Reblacktor.

Gen 17:11. Make definition more brief by removing the "In this context / in that context" part, keep the beginning but, and the etymology at the end, and have YHWH say "We're covenant." at the end of the verse.

Gen 17:14. Remove the begin midrash and end midrash markers but keep the lines of midrash between them unchanged.

Gen 17:15. Add a bit where YHWH says "Her name's not \paleo{שרי} Abe that's too similar to my name, if I'm \paleo{שדי} she can't be \paleo{שרי}, people will get confused Abe so she's \paleo{שרה} now Abe. So that's you now Abe, Abr--- hm, \heb{אברחם} that's a hot name right Abe so now you're \heb{אבר}hm and Sera now that's your names b--- Abe baby so go tell Sera and cut the crap and get to work and go get Sera and spread the Zera why are you laughing stop that.

Gen 17:15. Add this table:

```latex
\[
\Table{l l l l l}{
	\textbf{Old name} &
	\textbf{New name} &
	\textbf{Passage} &
	\textbf{Renamer} &
	\textbf{Source}
}{
	Abram (\hJ{אברם}) &
	Abraham (\hJ{אברהם}) &
	Gen 17:5 &
	El Shaddai / God &
	P
	\\

	Sarai (\hJ{שרי}) &
	Sarah (\hJ{שרה}) &
	Gen 17:15 &
	El Shaddai / God &
	P
	\\

	Jacob (\hJ{יעקב}) &
	Israel (\hJ{ישראל}) &
	Gen 32:29 &
	Divine wrestler &
	J/E
	\\

	Jacob (\hJ{יעקב}) &
	Israel (\hJ{ישראל}) &
	Gen 35:10 &
	El Shaddai / God &
	P
	\\

}
\]
```
Gen 17:1. Turn the footnote into \aC{}.

Gen 17:2. Add a line below the current commentary saying \aC{This is the first appearance of God in which he refers to himself as El Shaddai.}


```latex
\Table{l l l p{8.2cm}}{
	\textbf{Verse} &
	\textbf{Name} &
	\textbf{Speaker} &
	\textbf{What Shaddai is doing / what is being discussed}
}{
	Gen 17:1--21 &
	El Shaddai &
	God &
	Introduces himself to Abram as El Shaddai. Immediately promises to
	\textbf{multiply} him exceedingly; changes Abram's name to Abraham;
	makes him father of many nations; promises \textbf{kings} from him;
	establishes the covenant with his \textbf{seed}; institutes
	\textbf{circumcision}; changes Sarai's name to Sarah; \textbf{blesses
	her fertility}; and promises that she will bear Isaac.
	\\

	Gen 28:3--4 &
	El Shaddai &
	Isaac &
	``May El Shaddai bless you, make you \textbf{fruitful}, and
	\textbf{multiply} you, so that you become an assembly of peoples.''
	Then gives Jacob the blessing of Abraham and possession of the land.
	\\

	Gen 35:11--12 &
	El Shaddai &
	God &
	``I am El Shaddai: \textbf{Be fruitful and multiply}.'' A nation and
	an assembly of nations will come from Jacob, and \textbf{kings will
	come from his loins}. God promises the land to his \textbf{seed}.
	\\

	Gen 43:14 &
	El Shaddai &
	Jacob &
	As Benjamin is sent to Egypt, Jacob asks El Shaddai to give his sons
	mercy before Joseph so that Benjamin and Simeon will return. The
	immediate subject is therefore the preservation of Jacob's
	\textbf{sons/family}: ``If I am bereaved, I am bereaved.''
	\\

	Gen 48:3--4 &
	El Shaddai &
	Jacob &
	Jacob tells Joseph that El Shaddai appeared to him at Luz and
	\textbf{blessed} him, saying: ``I will make you \textbf{fruitful}
	and \textbf{multiply} you; I will make you an assembly of peoples.''
	The promise continues to Jacob's \textbf{seed}. Jacob then adopts
	Joseph's sons Ephraim and Manasseh.
	\\

	Gen 49:25 &
	Shaddai &
	Jacob &
	Shaddai \textbf{blesses} Joseph with ``blessings of heaven above,
	blessings of the deep lying below, blessings of the
	\textbf{breasts and womb}'' (\hJ{שדים ורחם}). The most explicit
	fertility context of all.
	\\

	Exod 6:3 &
	El Shaddai &
	God &
	God tells Moses: ``I appeared to Abraham, Isaac, and Jacob as
	El Shaddai.'' He recalls the patriarchal covenant, their
	\textbf{descendants}, and the promised land, and now announces the
	next stage of that covenant under the name YHWH.
	\\

	Num 24:4 &
	Shaddai &
	Balaam &
	Balaam introduces his oracle as one who ``sees the vision of
	Shaddai.'' What he then sees is Israel flourishing: beautiful tents,
	\textbf{seed beside abundant waters}, a king greater than Agag, and
	a kingdom exalted.
	\\

	Num 24:16 &
	Shaddai &
	Balaam &
	Again Balaam ``sees the vision of Shaddai.'' The oracle concerns
	Israel's future power: a \textbf{star comes from Jacob}, a scepter
	rises from Israel, and Israel's descendants defeat neighboring
	nations.
}
```