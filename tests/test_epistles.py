"""Exercise full/subset epistle discovery without compiling any book."""
import importlib.machinery
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("epistle_subset", str(ROOT / "bin/book-subset"))
spec = importlib.util.spec_from_loader(loader.name, loader)
subset = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = subset
loader.exec_module(subset)
DIRECTORY = "10-dudetheyreontome"


class EpistlesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        directory = self.root / DIRECTORY
        directory.mkdir(parents=True)
        (directory / "80-1-jephesians").mkdir()
        shutil.copyfile(ROOT / DIRECTORY / "80-1-jephesians/01.tex", directory / "80-1-jephesians/01.tex")
        for name in ("81-2-jephesians", "82-1-gal"):
            (directory / name).mkdir()
            (directory / name / "01.tex").write_text(
                "\\Chapter{1}\n\\Sentence{\\hX{}}{\\eX{}}{First chapter.}\n"
                "\\Chapter{2}\n\\Sentence{\\hX{}}{\\eX{}}{Second chapter.}\n"
            )
        (directory / "81-2-jephesians/02.tex").write_text(
            "\\Chapter{3}\n\\Sentence{\\hX{}}{\\eX{}}{Third chapter.}\n"
        )
        (directory / "79-not-an-epistle").mkdir()
        (directory / "79-not-an-epistle/01.tex").write_text("Ignored.")
        (directory / "83-empty-book").mkdir()
        (directory / "README.md").write_text("Not a book.")
        (directory / "ignored.tex").mkdir()
        self.body = (
            "\\Book{Dudetheyreontome}\n"
            f"\\IncludeEpistles{{{DIRECTORY}}}\n"
        )

    def test_lua_and_subset_discover_same_books_and_destinations(self):
        with patch.object(subset, "ROOT", self.root):
            items = subset.parse_master_books(self.body)[0]["items"]
        titles = [value for kind, value in items if kind == "epistle"]
        self.assertEqual(titles, ["1 Jephesians", "2 Jephesians", "1 Gal"])
        script = self.root / "check.lua"
        script.write_text(
            f'local e = dofile("{ROOT}/bin/epistles.lua")\n'
            'tex = {sprint = function(s) print(s) end}\n'
            f'e.contents("{DIRECTORY}")\n'
            f'e.include("{DIRECTORY}")\n'
        )
        result = subprocess.run(
            ["texlua", str(script)], cwd=self.root, check=True, text=True, capture_output=True
        )
        expected = [rf"\EpistleContentsEntry{{{title}}}" for title in titles]
        for kind, value in items:
            if kind == "epistle":
                expected.append(rf"\clearpage\EpistleBook{{{value}}}")
            elif kind == "include":
                expected.append(rf"\input{{{value}}}")
        self.assertEqual(result.stdout.splitlines(), expected)

    def test_subset_entrypoint_and_navigation_include_future_books(self):
        target = subset.Target("dudetheyreontome", "Dudetheyreontome", "test")
        with patch.object(subset, "ROOT", self.root):
            books = subset.parse_master_books(self.body)
            book = books[0]
            book["generated"], book["chapters"] = {}, {}
            for kind, value in book["items"]:
                if kind == "include":
                    generated, count, chapter = subset.copy_or_filter_chapter(
                        value, target, self.root / "output/chapters"
                    )
                    self.assertGreater(count, 0)
                    book["generated"][value] = generated
                    book["chapters"][value] = chapter
            entrypoint = subset.write_entrypoint(
                target, r"\begin{document}", books, self.root / "output"
            ).read_text()
        self.assertEqual(entrypoint.count(r"\EpistlesHeading"), 1)
        for title in ("1 Gal", "1 Jephesians", "2 Jephesians"):
            self.assertIn(rf"\EpistleContentsEntry{{{title}}}", entrypoint)
            self.assertIn(rf"\clearpage\EpistleBook{{{title}}}", entrypoint)
        self.assertIn(r"\EpistlesContents%", entrypoint)
        self.assertNotIn(r"\BookPart{Epistles}", entrypoint)
        future = (self.root / "output/chapters" / DIRECTORY / "81-2-jephesians/01.tex").read_text()
        self.assertIn(r"\Chapter{2}", future)

        # A filtered-out book must not leave a dangling link or heading.
        book["generated"].pop(f"{DIRECTORY}/82-1-gal/01")
        filtered = subset.write_entrypoint(
            target, r"\begin{document}", books, self.root / "output"
        ).read_text()
        self.assertNotIn("1 Gal", filtered)
        self.assertEqual(filtered.count(r"\EpistlesHeading"), 1)

    def test_editorial_comments_and_mixed_blocks_survive_subset_parsing(self):
        source = self.root / "mixed.tex"
        text = (
            "% Always use \\Verse here; \\Sentence elsewhere.\n"
            "\\Chapter{1}\n"
            "\\Verse{7}{original}{English}{Fixed source number.}\n"
            "% source: 2 Esdras 14:22\n"
            "\\Sentence{original}{English}{A {nested} comment.}\n"
            "\\Chapter{2}\n"
            "\\Sentence{}{}{Next chapter.}\n"
        )
        source.write_text(text)
        target = subset.Target("dudetheyreontome", "Dudetheyreontome", "test")
        result, count, chapter = subset.transform_chapter(
            source, target, f"{DIRECTORY}/80-1-jephesians/01"
        )
        self.assertEqual(result, text)
        self.assertEqual(count, 3)
        self.assertEqual(chapter, "1")


if __name__ == "__main__":
    unittest.main()
