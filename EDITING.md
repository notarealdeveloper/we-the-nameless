
Resume editing in Gen 25.

---

Agents: Do all the items below except the ones marked as MANUAL. If there are no MANUAL ones, do them all.

## Stuff to review manually

Catch R up on Gen 44-48.

Automate Later: Remove manual line breaks in the english (\\eP{}, \\eJ{}, \\eR{}) and hebrew (\\hP{}, \\hJ{}, \\hR{}) blocks (not the commentary blocks) that sometimes occur early on, primarily in the early chapters of `[01][0-9]-*/*.tex` like `01-genesis/0[123].tex` and maybe `01-genesis/0[456].tex`

Gen 22:21-24. Have red add one liner comments about the names.

Gen 24:66. Do a playful censorship thing.

Whenever R (as opposed to RJE) deletes a character in the source material, we get the blue \redacted{} box. RJE, on the other hand, just deletes it.

In Gen 2:4 to 2:8, find one pair of A-Ts to delete so that you can get to 12 and then it breaks in the middle of 13 cuz obviously.

Gen 2:20. Change commentary line to "However, the human had something else in mind mate wise."

## Stuff to do now

Gen 1:2. Delete the W* and T* lines. Just keep the A* and the O* ones, and the J* one. Add a ... before the J* line and make sure to keep it at the bottom below the other two.

Gen 1:3. Delete all 3 footnotes, and replace each with two newline characters so LaTeX will put a paragraph break there. Make sure the two newlines / paragraph break ends up in the ebook, because in the version of the ebook I currently have, the footnotes somehow caused 1:3's commentary to be all in one paragraph, while 1:4 correctly displays as three one-line paragraphs in the ebook and in the LaTeX. So there's a general problem (footnotes should be removed in 1:3) and a ebook specific problem (ebook not doing paragraph breaks in a way that's faithful to the original TeX source.)

Gen 1:5. Be faithful to the multi level indentation in the TeX when creating the ebook. Also change "Now suddenly there’s a dead body, cuz obviously." to "Now for some reason there's a dead body."

Gen 1:9. Turn the \\\\ newlines into paragraphs by deleting the \\\\ and just adding and empty line between each pair of lines in the TeX.

Gen 1:14. This is good, stop doubting it, but you need to fix the syntax and semantics error before the opening of the final parentheses. It used to say "So Yang's associated with things like this" and then open the parentheses and then when they finally close it resumes where it left off and says "and naturally, sort of by process of elimination, the sun." Fix that by somehow adding parentheses or doing some very minor rewordings near the end, perhaps manually or in an automated way if we think we can do it. Also make sure moon is fg color (black, or white in dark mode) and ri/sun is blue and the/speech is red in the final chinese characters at the end of the footnote.

Gen 2:6-7. The "God" in "YHWH God" should be removed from both the English and the Hebrew.

Gen 32:26. In the ebook, the final footnote has literal html in it in and around the word watteqa.

