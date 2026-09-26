"""Check aux-directory preparation without compiling the book."""
import importlib.machinery
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
loader = importlib.machinery.SourceFileLoader("parallel_build", str(ROOT / "bin/parallel-build"))
spec = importlib.util.spec_from_loader(loader.name, loader)
parallel = importlib.util.module_from_spec(spec)
loader.exec_module(parallel)


class BuildPrepareTests(unittest.TestCase):
    def assert_history_dirs(self, output):
        for directory in (
            "dudetheyreontome",
            "exile/esther/additions",
            "exile/nehemiah/additions",
            "sects-acts/nhs",
        ):
            self.assertTrue((output / "10-dudetheyreontome" / directory).is_dir(), directory)

    def test_regular_build_prepares_nested_history(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "output"
            subprocess.run(
                ["make", "build-prepare", f"BUILD={output}"],
                cwd=ROOT, check=True, capture_output=True, text=True,
            )
            self.assert_history_dirs(output)
            self.assertTrue((output / "01-genesis").is_dir())

    def test_parallel_build_prepares_nested_history(self):
        _, _, books = parallel.read_document_parts()
        book = next(book for book in books if book["title"] == "Dudetheyreontome")
        self.assertIn("10-dudetheyreontome/dudetheyreontome/01", book["includes"])
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            parallel.prepare_build_dirs(book, output)
            self.assert_history_dirs(output)


if __name__ == "__main__":
    unittest.main()
