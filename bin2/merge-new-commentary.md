#!/usr/bin/env bash

lord --verbose << "EOF"

eng/ is the current default english translation, as markdown.

com/ is the current default english translation, as markdown, with any commentary I happen to have written while out walking away from my laptop.

Whenever you find a bit of commentary in com/ that isn't in eng/, I want you to:

1. Find the corresponding book, chapter, and verse in:

`[01][0-9]*/*.tex`

2. Add the commentary for each such verse in com/ to the lualatex files there. The .tex files. Don't change anything in eng/.

3. Be idempotent: If you find a verse already has the same commentary or similar commentary in the .tex file that corresponds to a verse in some file in com/, then do nothing for that verse.

4. Remember to change any markdown-isms you find in the com/ commentary into equivalent latex-isms when you move the commentary from com/ to the .tex files. ESPECIALLY: If you see a table in the markdown, use \Table{...} as defined in master.tex to make it into a table, and search through `01-genesis/*.tex` and `08-samuel/*.tex` for other examples of how to make a table fit on the page. The file `01-genesis/20.tex` has one, for example.

5. EDIT: DON'T DO DUMB SHIT! I want the book and its code to be simple.
   Don't add \par\smallskip for idiotic reasons to the tex. I want a simple update of the commentary *in the tex files* using the commentary in com/.

6. You should only be editing the following this time around:

    01-genesis/36.tex

7. Whenever you find a Friedman footnote in the com/ directory, move it to the tex files, but leave it commented out.

8. Whenever I've already put latex-isms in the .md files, don't escape them even more when you add them to the tex. The latex-isms in the .md (when you see them) are the latex I want in the .tex files. I wrote the .md stuff on my phone where I don't have a latex compiler, so those latex-isms (e.g., \footnote{...} and \aC{...} etc.) are my attempt to signal what the .tex should be when you move it.

Do all that now.

EOF
