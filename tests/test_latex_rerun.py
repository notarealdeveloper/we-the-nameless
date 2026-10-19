"""Exercise reference convergence without compiling a book."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class LatexRerunTests(unittest.TestCase):
    def run_compiler(self, warnings, exit_code=0):
        with tempfile.TemporaryDirectory() as temp:
            log = Path(temp) / "book.log"
            counter = Path(temp) / "passes"
            compiler = Path(temp) / "compiler.py"
            compiler.write_text(
                "from pathlib import Path\n"
                f"counter = Path({str(counter)!r})\n"
                "n = int(counter.read_text()) if counter.exists() else 0\n"
                "counter.write_text(str(n + 1))\n"
                f"warnings = {warnings!r}\n"
                f"Path({str(log)!r}).write_text(warnings[min(n, len(warnings) - 1)])\n"
                f"raise SystemExit({exit_code})\n"
            )
            result = subprocess.run(
                [sys.executable, str(ROOT / "bin/latex-rerun.py"), str(log),
                 sys.executable, str(compiler)],
                capture_output=True, text=True,
            )
            return result, int(counter.read_text())

    def test_reruns_until_references_and_page_numbers_settle(self):
        result, passes = self.run_compiler([
            "LaTeX Warning: There were undefined references.",
            "LaTeX Warning: Label(s) may have changed. Rerun to get\n cross-references right.",
            "Output written on book.pdf.",
        ])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(passes, 3)

    def test_clean_log_needs_only_one_pass(self):
        result, passes = self.run_compiler(["Output written on book.pdf."])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(passes, 1)

    def test_persistent_undefined_references_fail(self):
        result, passes = self.run_compiler(["There were undefined references."])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(passes, 5)
        self.assertIn("did not settle", result.stderr)

    def test_compiler_failure_stops_immediately(self):
        result, passes = self.run_compiler(["There were undefined references."], 7)
        self.assertEqual(result.returncode, 7)
        self.assertEqual(passes, 1)


if __name__ == "__main__":
    unittest.main()
