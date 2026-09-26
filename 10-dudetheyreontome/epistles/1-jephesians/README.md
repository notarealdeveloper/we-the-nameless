Epistles occupy numbered book directories such as `1-jephesians` under
`10-dudetheyreontome/epistles`. The directory name supplies the printed title:
`1-jephesians` becomes “1 Jephesians”. Add future books as `2-jephesians`, etc.
Full and subset entrypoints discover numbered directories and their chapter
files automatically within that collection.

Use `01.tex`, `02.tex`, etc., each beginning with its editorial-policy comment
and `\Chapter{1}`, `\Chapter{2}`, etc. Use `\Sentence{original}{English}{commentary}`
without a number; numbering restarts at each chapter. English manuscripts live
at matching paths under `10-dudetheyreontome/eng/epistles/`
(for example `10-dudetheyreontome/eng/epistles/1-jephesians/01.md`).

Ezra, Nehemiah, and Esther always retain `\Verse` and fixed source numbering.
