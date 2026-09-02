
---

## Stuff to do later

- [ ] Catch R up on Gen 44-48.

---

## Stuff to do now

- Unfuck the frontmatter in light/book mode. Note: This may be the fault of the parallel build, not the book or light config modes. However, it doesn't happen in dark/mobile mode (again, not sure which is responsible, but probably mobile, since color shouldn't change anything unless something dumb is happening, which it is.)

---

## Stuff already done (probably)

master.tex: Alphabet history page. Row 9 is fucked up. Put it in the right order by looking at the ascii or whatever codes that that font uses, and use that to properly order the letters.

Gen 2:4b. Make the \heb{} primitive strip niqqud, and add a \hebniq{} primitive that keeps them.

Gen 2:6-7. Delete the redactor \eR{God} and \hR{אלהים} in this one, it distracts from the point.

Gen 2 and 3: Make the backgrounds for the highlighted words less milky. The blue should be more like \eR{...} redactor blue, the red should be more like \eReblackor{...} red, and the black should be a similar level of color/non-milkiness: It should be light grey (darker than the bg) in light mode and dark grey (lighter than the bg) in dark mode. Achieve this by using the latex ! color mixing primitive.

Gen 3:1. Remove the 2nd God from Redactor blue in the Hebrew.

Gen 3:3. The God here is in quotes, remove the Redactor blue highlight in the eng and the heb.

Gen 3:5. Unhighlight the Hebrew word for God both times, the word God in this verse shouldn't be in Redactor blue.

Gen 3:10. English section. Make the naked / clever fraction be closer together vertically like it used to be, something changed it.

Gen 4:17. Make footnote shorter.

Gen 6:4. Remove the nephilim highlights from the English.

Gen 6:13. everything on earth should say everybody.

Gen 7:1. add "and" before "the death of Moses."

Gen 7:14. "They" shouldn't be multiplied by "by their kind."

Gen 9:5. Kill the footnote. It's dumb.

Gen 10:5. Has some Hebrew that needs to be wrapped in \heb{...}.

Gen 10:8. Put a comma after the word scholar and before "boring"

Gen 10:10. Item 5 has an extraneous colon after the 5 and before Shinar.

Gen 10:11. Move the commas inside the quotes.

Gen 10:15. Wrap the unwrapped Hebrew text in \heb{...}. And put a dot under the H in the footnote.

Gen 10:25. The word small has a single quote on the left side, make it a double quote.

Gen 11:1. Need a "the" in "the" whole world as one nation.

Gen 21:12. 'sending should be `sending.

Genesis 23:2. Mention Joshua here in the commentary block. Say:
- \aC{This is one of the only _stories_ that P has but J and E don't.\fC{Others include the priestly inauguration and Nadab and Abihu (Lev 8--10), the blasphemer (Lev 24:10--23), the Sabbath stick-gatherer (Num 15:32--36), Korah's rebellion (Num 16--17), and the daughters of Zelophehad (Num 27; 36).} Machpelah is in Hebron, and Hebron was an Aaronid priestly city (Josh 21:13).}

Gen 41:45. Footnote. that's YHWH should be that YHWH.