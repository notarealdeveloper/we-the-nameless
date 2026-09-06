
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
- [x] In the ebook/ the E source is currently Right to Left BUT it's rendering Down to Up! If there are two lines of E, the beginning of E's paleo Hebrew is currently the BOTTOM RIGHT! Fix that in the ebook, globally, and write a test in the ebook directory that somehow assesses this.
- [x] RJE is backwards: currently rendering left to right.
- [x] J is usually left to right, but there's insane examples like Gen 22:21 where it starts on the top left, goes to the top right for ONE LETTER, then picks up on the second character of the top left. This should just always be RTL. Fix the ebook globally and add a test for J, E, and RJE. P and R are currently rendering right to left, as intended.
- [x] The Paleo source profile in Gen 49 is also rendering left to right in the ebook, fix that.

Look at the pictures below _with your eyes_ and compare each verse to the standard masoretic Hebrew to see what I mean and to see what things you need to fix in the ebook.

1. J is left to right and the sequencing with other sources is wrong in the ebook.

![[ebook-bugs-1.jpg]]

2. E is bottom right to top left.

![[ebook-bugs-2.jpg]]

3. Paleo is left to right.

![[ebook-bugs-3.jpg]]

4. This one is just insane.

![[ebook-bugs-4.jpg]]

Also rename the above images to ebook-bugs-${n}.jpg for n in 1 to 4, both in the cwd and in this file. [DONE]

Gen 25:23.
- [x] Remove manual line breaks in the eng and HEB.
- [x] Delete the red commentary, and massively condense blue.
- [x] Also the image of the map is missing in the Kindle version, fix that in ebook/
