"""Check aux-directory preparation without compiling the book."""
import importlib.machinery
import importlib.util
import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
loader = importlib.machinery.SourceFileLoader("parallel_build", str(ROOT / "bin/parallel-build"))
spec = importlib.util.spec_from_loader(loader.name, loader)
parallel = importlib.util.module_from_spec(spec)
loader.exec_module(parallel)


class BuildPrepareTests(unittest.TestCase):
    def assert_history_dirs(self, output):
        for directory in (
            "on-the-lamb",
            "exile/esther",
            "exile/ezra",
            "exile/nehemiah",
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
        self.assertIn("10-dudetheyreontome/on-the-lamb/opening", book["includes"])
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            parallel.prepare_build_dirs(book, output)
            self.assert_history_dirs(output)

    def test_parallel_cli_can_finish_without_opening_a_viewer(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            with patch.object(sys, 'argv', ['parallel-build', '--plain', '--no-open', '--passes', '1']), \
                 patch.object(parallel, 'BUILD', work), \
                 patch.object(parallel, 'CONFIG_SIGNATURE', work/'config.json'), \
                 patch.object(parallel, 'MERGED_PDF', work/'master.pdf'), \
                 patch.object(parallel, 'read_document_parts', return_value=('', '', [])), \
                 patch.object(parallel, 'warm_tex_cache'), \
                 patch.object(parallel, 'prepare_worker_tex_caches'), \
                 patch.object(parallel, 'run_plain', return_value=0), \
                 patch.object(parallel, 'merge_pdfs', return_value=0), \
                 patch.object(parallel, 'open_pdf') as viewer, \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(parallel.main(), 0)
            viewer.assert_not_called()


if __name__ == "__main__":
    unittest.main()
