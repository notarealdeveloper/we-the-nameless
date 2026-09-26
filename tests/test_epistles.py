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
DIRECTORY = "10-dudetheyreontome/epistles"


class EpistlesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        directory = self.root / DIRECTORY
        directory.mkdir(parents=True)
        shutil.copyfile(ROOT / DIRECTORY / "1-jephesians.tex", directory / "1-jephesians.tex")
        for name in ("2-jephesians", "1-gal"):
            (directory / f"{name}.tex").write_text(
                "\\Chapter{1}\n\\Verse{1}{\\hX{}}{\\eX{}}{First chapter.}\n"
                "\\Chapter{2}\n\\Verse{1}{\\hX{}}{\\eX{}}{Second chapter.}\n"
            )
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
        self.assertEqual(titles, ["1 Gal", "1 Jephesians", "2 Jephesians"])
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
        future = (self.root / "output/chapters" / DIRECTORY / "2-jephesians.tex").read_text()
        self.assertIn(r"\Chapter{2}", future)

        # A filtered-out book must not leave a dangling link or heading.
        book["generated"].pop(f"{DIRECTORY}/1-gal")
        filtered = subset.write_entrypoint(
            target, r"\begin{document}", books, self.root / "output"
        ).read_text()
        self.assertNotIn("1 Gal", filtered)
        self.assertEqual(filtered.count(r"\EpistlesHeading"), 1)


if __name__ == "__main__":
    unittest.main()
