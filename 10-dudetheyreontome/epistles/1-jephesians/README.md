Epistles occupy numbered book directories such as `1-jephesians` under
`10-dudetheyreontome`. The directory name supplies the printed title:
`1-jephesians` becomes “1 Jephesians”. Add future books as `2-jephesians`, etc.
Full and subset entrypoints discover numbered directories and their chapter
files automatically, excluding `N-on-the-lamb` and `N-exile-*` directories.

Use `01.tex`, `02.tex`, etc., each beginning with its editorial-policy comment
and `\Chapter{1}`, `\Chapter{2}`, etc. Use `\Sentence{original}{English}{commentary}`
without a number; numbering restarts at each chapter. English manuscripts live
at matching paths under `../eng/` (for example `eng/1-jephesians/01.md`).

Ezra, Nehemiah, and Esther always retain `\Verse` and fixed source numbering.
