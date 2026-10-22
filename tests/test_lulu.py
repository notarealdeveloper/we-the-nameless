"""Lulu checks with synthetic PDFs only; never build the book."""
import contextlib
import importlib.machinery
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bin'))
from lulu_cover_geometry import geometry
from kdp_fixtures import pdf
from kdp_pdf_lib import inspect
from print_publish_config import profiles

loader = importlib.machinery.SourceFileLoader('lulu_publishing', str(ROOT / 'bin/print_publish.py'))
spec = importlib.util.spec_from_loader(loader.name, loader)
publishing = importlib.util.module_from_spec(spec)
loader.exec_module(publishing)


class LuluTests(unittest.TestCase):
    def test_published_600_page_dimensions(self):
        soft = geometry(600, 7, 10, 'premium-color')
        hard = geometry(600, 7, 10, 'premium-color', 'hardcover')
        self.assertAlmostEqual(soft['spine'], 600/444 + .06)
        self.assertAlmostEqual(soft['width'], 15.66135135135)
        self.assertEqual(soft['height'], 10.25)
        self.assertEqual(hard['spine'], 1.625)
        self.assertEqual((hard['width'], hard['height']), (17.375, 11.75))
        self.assertEqual(geometry(582, 7, 10, 'premium-color', 'hardcover')['spine'], 1.5625)
        self.assertEqual(geometry(584, 7, 10, 'premium-color', 'hardcover')['spine'], 1.625)
        for count in (22, 801, 600.5):
            with self.assertRaises(ValueError):
                geometry(count, 7, 10, 'premium-color', 'hardcover')
        large = geometry(600, 8.25, 11, 'premium-color', 'hardcover')
        self.assertEqual(large['spine'], hard['spine'])
        self.assertEqual((large['width'], large['height']), (19.875, 12.75))

    def test_make_routes_without_building(self):
        for binding in ('paperback', 'hardcover'):
            result = subprocess.check_output(['make', '-n', 'genesis-lulu-' + binding], cwd=ROOT, text=True)
            self.assertIn('--make-target "genesis-lulu-' + binding + '"', result)

    def test_optional_vectorization_on_synthetic_pdfs(self):
        with tempfile.TemporaryDirectory(prefix='lulu-test-') as temp:
            root = Path(temp)
            pipeline = publishing.Pipeline('fixture', root/'build', root/'pub', profiles('lulu', 'simple'), 'lulu')
            pipeline.environment = {}
            for artifact in pipeline.artifacts:
                pdf(pipeline.pdf_path(artifact, 'original'))
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                pipeline.vectorize({'variant': 'soft'})
            for artifact in pipeline.artifacts:
                final = pipeline.pdf_path(artifact, 'vectorized')
                report = inspect(final)
                self.assertEqual(report['pages'], 1)
                self.assertEqual(report['page_geometry'][0]['MediaBox'], [0, 0, 504, 720])
                self.assertEqual(report['font_count'], 0)
                self.assertEqual(report['images'], [])


if __name__ == '__main__':
    unittest.main()
