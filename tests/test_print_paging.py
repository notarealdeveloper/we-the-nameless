"""Exercise production layout macros with tiny synthetic pages, never the book."""
from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MASTER = (ROOT / "master.tex").read_text()
LAYOUT = MASTER.split("% BEGIN print-page layout", 1)[1].split(
    "% END print-page layout", 1)[0]
BOOK_CONTENTS = MASTER.split(r"\newcommand{\BookChapterLinkArray}", 1)[1].split(
    r"\newcommand{\BookExtraLinkText}", 1)[0]


@unittest.skipUnless(shutil.which("pdflatex"), "pdflatex unavailable")
class PrintPagingTests(unittest.TestCase):
    def render(self, contents_pages=1, cover=False, mode="book", fancy=True):
        centered = mode in ("tech", "even")
        geometry = "inner=.625in,outer=.625in" if centered else "inner=.8in,outer=.45in"
        preamble = (
            r"\documentclass{book}\usepackage[paperwidth=7in,paperheight=10in,twoside,"
            + geometry + r"]{geometry}"
            + r"\newif\ifConfigOutputModeTech"
            + (r"\ConfigOutputModeTechtrue" if mode == "tech" else "")
            + r"\newif\ifConfigKDPOn"
            + LAYOUT
            + r"\newif\ifIndividualBookTitlePageStyleFancy"
            + (r"\IndividualBookTitlePageStyleFancytrue" if fancy else "")
            + r"\newcommand{\BookExtraLinkArray}[1]{}"
            + r"\newcommand{\FancyBookChapterLinkArray}[1]{\ContentsFixture}"
            + r"\newcommand{\PlainBookChapterLinkArray}[1]{\ContentsFixture}"
            + r"\newcommand{\BookChapterLinkArray}" + BOOK_CONTENTS
            + r"\newcommand{\ContentsFixture}{"
            + r"\Mark{individual}"
            + (r"\clearpage\Mark{continued}" * (contents_pages - 1)) + "}"
            + r"""
\newcount\PhysicalPage
\AddToHook{shipout/before}{\global\advance\PhysicalPage by 1}
\newcommand{\Mark}[1]{%
  \typeout{PAGING #1 physical=\the\numexpr\PhysicalPage+1\relax,
    logical=\arabic{page}, odd=\the\oddsidemargin,
    even=\the\evensidemargin, width=\the\textwidth}%
  \noindent #1\par
}
\begin{document}\frontmatter\pagenumbering{gobble}\pagestyle{empty}
"""
        )
        body = r"\Mark{cover}" if cover else ""
        body += r"""
\WeClearToRightPage\WeFrontMatterGeometry\Mark{title}\restoregeometry
\WeClearToLeftPage\Mark{alphabet1}
\WeClearToRightPage\Mark{alphabet2}
\WeClearToRightPage\WeFrontMatterGeometry\Mark{series}
"""
        body += r"\clearpage\Mark{seriescontinued}" * (contents_pages - 1)
        body += r"""
\restoregeometry
\WeClearToLeftPage\Mark{source1}
\WeClearToRightPage\Mark{source2}
\WeClearToLeftPage\Mark{source3}
\WeClearToRightPage\Mark{source4}
\WeClearToLeftPage\Mark{notice1}
\WeClearToRightPage\Mark{notice2}
\WeClearToRightPage\mainmatter
\WeClearToRightPage\BookChapterLinkArray{fixture}\Mark{content}
\clearpage\Mark{nextcontent}\end{document}
"""
        with tempfile.TemporaryDirectory(prefix="print-paging-") as temp:
            source = Path(temp) / "fixture.tex"
            source.write_text(preamble + body)
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", source.name],
                cwd=temp, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout[-4000:])
            log = (Path(temp) / "fixture.log").read_text().replace("\n", "")
        matches = re.findall(
            r"PAGING (\w+) physical=(\d+),\s*logical=(\d+), odd=([\d.-]+)pt,\s*"
            r"even=([\d.-]+)pt, width=([\d.-]+)pt", log)
        self.assertTrue(matches, log)
        return {name: tuple(map(float, values)) for name, *values in matches}

    def test_print_sides_and_binding_margins_survive_contents_growth(self):
        sides = dict(title=1, alphabet1=0, alphabet2=1, series=1,
                     source1=0, source2=1, source3=0, source4=1,
                     notice1=0, notice2=1, individual=1, content=0, nextcontent=1)
        for count in (1, 2, 3):
            for cover in (False, True):
                for fancy in (False, True):
                    with self.subTest(pages=count, cover=cover, fancy=fancy):
                        pages = self.render(count, cover, fancy=fancy)
                        for name, side in sides.items():
                            physical, logical, odd, even, width = pages[name]
                            self.assertEqual(physical % 2, side, name)
                            self.assertEqual(logical % 2, side, name)
                            # Actual physical left/right edges, in TeX points.
                            left = 72.27 + (odd if side else even)
                            right = 7 * 72.27 - left - width
                            self.assertGreater(left if side else right,
                                               right if side else left, name)
                        if count == 1 and not cover:
                            self.assertEqual(pages["title"][0], 1)
                            self.assertEqual(pages["series"][0], 5)
                            self.assertEqual(pages["individual"][0], 13)
                            self.assertEqual(pages["content"][0], 14)

    def test_centered_modes_keep_equal_margins(self):
        for mode in ("tech", "even"):
            with self.subTest(mode=mode):
                for values in self.render(mode=mode).values():
                    self.assertAlmostEqual(values[2], values[3], places=3)

    @unittest.skipUnless(shutil.which("lualatex") and shutil.which("pdfinfo")
                         and shutil.which("pdftotext"), "LuaLaTeX or Poppler unavailable")
    def test_kdp_finishes_even_physical_pages(self):
        # Exercise the production hook with real TeX output, including page
        # counter resets and a float that ships only at the final clearpage.
        cache = self.enterContext(tempfile.TemporaryDirectory(prefix="kdp-tex-cache-"))
        for kdp in (False, True):
            for count in (1, 2, 3, 4):
                for deferred in (False, True):
                    with self.subTest(kdp=kdp, pages=count, deferred=deferred):
                        source = (
                            r"\documentclass{book}\usepackage{geometry}"
                            r"\newif\ifConfigOutputModeTech\newif\ifConfigKDPOn"
                            + (r"\ConfigKDPOntrue" if kdp else "") + LAYOUT
                            + r"\begin{document}"
                            + r"\noindent Content\clearpage" * (count - 1)
                            + r"\setcounter{page}{1}\noindent Final content"
                            + (r"\begin{figure}[p]\centering Deferred figure\end{figure}"
                               if deferred else "")
                            + r"\end{document}"
                        )
                        with tempfile.TemporaryDirectory(prefix="kdp-paging-") as temp:
                            path = Path(temp) / "fixture.tex"
                            path.write_text(source)
                            result = subprocess.run(
                                ["lualatex", "-interaction=nonstopmode", "-halt-on-error", path.name],
                                cwd=temp, capture_output=True, text=True,
                                env={**os.environ, 'TEXMFVAR': cache, 'TEXMFCACHE': cache})
                            self.assertEqual(result.returncode, 0, result.stdout[-4000:])
                            output = path.with_suffix(".pdf")
                            info = subprocess.check_output(["pdfinfo", str(output)], text=True)
                            actual = int(re.search(r"Pages:\s+(\d+)", info)[1])
                            unpadded = count + int(deferred)
                            expected = unpadded + (unpadded % 2 if kdp else 0)
                            self.assertEqual(actual, expected)
                            if expected > unpadded:
                                last = subprocess.check_output(
                                    ["pdftotext", "-f", str(actual), "-l", str(actual),
                                     str(output), "-"], text=True)
                                self.assertEqual(last.strip(), "")


if __name__ == "__main__":
    unittest.main()
