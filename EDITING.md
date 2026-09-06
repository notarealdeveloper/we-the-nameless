
Resume editing in Gen 25.

---

Agents: Do all the items below except the ones marked as MANUAL. If there are no MANUAL ones, do them all.

## Stuff to review manually

Automate Later: Remove manual line breaks in the eng and HEB.

Catch R up on Gen 44-48.

Gen 22:21-24. Have red add one liner comments about the names.

Gen 22. Find a way to remove the duplicate copy.

Gen 24:66. Do a playful censorship thing.

## Stuff to do now

ATTENTION! EBOOK PROBLEMS TO FIX!

The TeX macro in 01-genesis/16.tex Verse 1 isn't rendering in the ebook. This is odd, because it's \eRJE{}, and RJE is rendering in the ebook just fine (e.g., in Genesis 22)

Genesis 17:1. In the ebook, the i in Putting an \`i' appears as a backtick and not as a proper unicode type quote. In the main pdf book build, it looks fine. Fix this in the ebook, for all latex quotes of this form.

Genesis 17:6. In the ebook, things like "c\eR{hildren }o\eR{h my oh }me " are getting rendered as "c\eR{hildren}o\eR{h my oh}me " (note the missing spaces at the end of the redactor block.) Fix this in the ebook, for all such examples in all source profiles. The behavior of whitespace in the ebook is _almost_ exactly following TeX's behavior, so don't change much about the behavior of whitespace in the ebook. Just try to fix examples like that, which will usually occur inside commentary blocks where the redactor interleaves his text with the pre-existing commentary in order to censor or somewhat hide some word in the original text.

Genesis 17:7. Another example of the `{\pussyc}` macro not rendering in the ebook.