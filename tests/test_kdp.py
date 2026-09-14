"""Publishing checks use synthetic PDFs only; never invoke a book build."""
import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bin'))
from kdp_pdf_lib import inspect, validate
from kdp_fixtures import pdf


def module(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec); loader.exec_module(mod)
    return mod


publishing = module('publishing', ROOT / 'bin/kdp-publish')
visual = module('visual', ROOT / 'bin/kdp-visual-compare')


class PublishingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='kdp-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_make_completion_and_resolution(self):
        query = subprocess.run(['make', '-qp'], cwd=ROOT, text=True, capture_output=True)
        self.assertIn(query.returncode, (0, 1))
        database = query.stdout
        names = subprocess.check_output(['bin/book-subset', '--make-targets'], cwd=ROOT, text=True).split()
        chapters = subprocess.check_output(['bin/book-subset', '--make-chapter-targets'], cwd=ROOT, text=True).split()
        for name in names + chapters:
            for suffix in ('kdp', 'kdp-build', 'kdp-vectorize', 'kdp-check'):
                self.assertIn('\n' + name + '-' + suffix + ':', database)
        for alias in ('genesis', '1-genesis', '01-genesis'):
            self.assertEqual(subprocess.check_output(['bin/book-subset', '--output-name', alias], cwd=ROOT, text=True).strip(), '01-genesis')
        for target in ('genesis-kdp-build', 'J-kdp-vectorize', 'P-kdp-check', 'genesis-1-kdp'):
            dry = subprocess.check_output(['make', '-n', target], cwd=ROOT, text=True)
            self.assertIn('bin/kdp-publish', dry)
            self.assertNotIn('lualatex', dry)

    def test_stale_and_damaged_manifest(self):
        file = self.root / 'interior.pdf'; pdf(file)
        record = dict(config={'trim': '7x10'}, sources={'master.tex': 'one'}, tools={'gs': 'one'},
            files={str(file): {'sha256': publishing.digest(file)}})
        publishing.assert_current(record, record['config'], record['sources'], record['tools'])
        for args in [({'trim': '6x9'}, record['sources'], record['tools']),
                     (record['config'], {'master.tex': 'two'}, record['tools']),
                     (record['config'], record['sources'], {'gs': 'two'})]:
            with self.assertRaisesRegex(RuntimeError, 'stale manifest'):
                publishing.assert_current(record, *args)
        file.write_bytes(b'damaged')
        with self.assertRaisesRegex(RuntimeError, 'damaged'):
            publishing.assert_current(record, record['config'], record['sources'], record['tools'])

    def test_failure_keeps_command_and_full_log(self):
        pipeline = publishing.Pipeline('fixture', self.root)
        with contextlib.redirect_stdout(io.StringIO()) as terminal:
            with self.assertRaises(subprocess.CalledProcessError) as failure:
                pipeline.run('2/6 interior', 'LuaLaTeX pass 2',
                    [sys.executable, '-c', 'import sys; print("complete diagnostic"); sys.exit(7)'], self.root / 'candidate.pdf')
        self.assertEqual(failure.exception.returncode, 7)
        self.assertIn('complete diagnostic', pipeline.log.read_text())
        self.assertIn('[KDP fixture 2/6 interior] START', terminal.getvalue())
        self.assertNotIn('PASS', terminal.getvalue())
        self.assertEqual(pipeline.candidate, self.root / 'candidate.pdf')

    def test_cli_reports_exact_failed_stage(self):
        # Inject a failed metadata probe: no PDF build or repository artifacts.
        def failed_versions(): raise RuntimeError('fixture tool unavailable')
        with patch.object(sys, 'argv', ['kdp-publish', 'genesis', 'check']), \
             patch.object(publishing, 'ROOT', self.root), \
             patch.object(publishing.subprocess, 'check_output', side_effect=lambda cmd, **kw: '1\n' if cmd[0] == 'git' else 'fixture\n'), \
             patch.object(publishing, 'sources', return_value={}), \
             patch.object(publishing, 'versions', failed_versions), \
             contextlib.redirect_stdout(io.StringIO()) as terminal:
            try: self.assertEqual(publishing.main(), 1)
            finally: os.chdir(ROOT)
        output = terminal.getvalue()
        for text in ('0/6 setup', 'FAIL', 'exit 1', 'candidate:', 'log:', 'reports:'):
            self.assertIn(text, output)

    def test_configuration_rejected_before_build(self):
        for options in [('--trim', '6x9'), ('--bleed', 'bleed'), ('--paper', 'cream')]:
            p = subprocess.run(['bin/kdp-publish', 'genesis', 'build', *options], cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn('0/6 setup', p.stderr)

    def test_empty_subset_needs_no_genesis_derivatives(self):
        subset = self.root / 'chapters'; subset.mkdir()
        (subset / '01.tex').write_text('No image references here: mandrake and seir are just words.')
        assets = module('assets', ROOT / 'bin/kdp-assets')
        with patch.object(sys, 'argv', ['kdp-assets', str(self.root / 'assets'), str(subset)]), \
             patch.object(assets, 'ROOT', self.root), \
             patch.object(assets.subprocess, 'check_output', return_value=b'fixture magick'), \
             patch.object(assets.subprocess, 'run') as convert:
            assets.main()
        convert.assert_not_called()
        self.assertEqual(json.loads((self.root / 'assets/assets.json').read_text()), [])

    def test_build_staging_with_fake_tex_and_real_pdf_inspection(self):
        pipeline = publishing.Pipeline('fixture', self.root / 'publish')
        passes = []
        def simulate(stage, operation, command, candidate=None, env=None):
            tool = command[0]
            if tool == 'bin/book-subset':
                work = Path(command[2]); (work / 'chapters').mkdir(parents=True)
                (work / 'fixture.tex').write_text(r'\include{generated/chapter}')
            elif tool == 'bin/kdp-assets':
                assets = Path(command[1]); assets.mkdir()
                (assets / 'assets.json').write_text('[]')
            elif tool == 'lualatex':
                self.assertTrue((Path(candidate).parent / 'generated').is_dir())
                self.assertTrue(Path(env['TEXMFVAR']).is_dir())
                passes.append(operation)
                pdf(candidate, [b''] * 24)
            elif tool == 'bin/kdp-cover':
                self.assertEqual(inspect(command[1])['pages'], 24)
                pdf(command[3], box=f'0 0 {72 * (14.25 + 24 * .002347)} 738')
            elif tool == 'bin/kdp-inspect':
                report = Path(command[2]); report.parent.mkdir(parents=True, exist_ok=True)
                report.write_text(json.dumps(inspect(command[1])))
            else:
                self.fail(f'unexpected command {command}')
        args = SimpleNamespace(book='fixture', paper='premium-color', cover_style='simple', spine='ld')
        with patch.object(pipeline, 'run', side_effect=simulate), patch.object(publishing, 'sources', return_value={}):
            record = pipeline.build(args, {}, {}, {})
        self.assertEqual(passes, ['LuaLaTeX pass 1', 'LuaLaTeX pass 2', 'LuaLaTeX pass 3'])
        self.assertEqual(len(record['files']), 2)
        self.assertTrue((pipeline.base / 'build.json').exists())
        self.assertFalse((pipeline.base / 'current').exists())

    def test_both_artifacts_promoted_together_and_failure_preserves_release(self):
        reference = self.root / 'reference'; reference.mkdir()
        # Searchable fixture with a built-in font tests real Ghostscript outlining.
        for name in ('interior', 'cover'):
            pdf(reference / (name + '.pdf'), [b'BT /F1 16 Tf 70 650 Td (Fixture) Tj ET\n'],
                resources='<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >>')
        record = dict(reference=str(reference), config={'variant': 'soft'}, sources={}, tools={}, dependencies={},
            files={str(p): inspect(p) for p in reference.glob('*.pdf')})
        pipeline = publishing.Pipeline('fixture', self.root / 'publish')
        # The composed command already has an interior build directory.
        (pipeline.run_dir / 'work/interior').mkdir(parents=True)
        with patch.object(publishing, 'sources', return_value={}), contextlib.redirect_stdout(io.StringIO()):
            pipeline.vectorize(record, record['config'], {}, {})
        base = pipeline.base
        manifest = json.loads((base / 'manifest.json').read_text())
        self.assertEqual(len(manifest['upload_files']), 2)
        for p in manifest['upload_files'].values():
            self.assertEqual(inspect(p)['font_count'], 0)
        publishing.assert_current(manifest, record['config'], {}, {}, uploads=True)
        previous = (base / 'current').readlink()
        failed = publishing.Pipeline('fixture', base)
        real_validate = failed.validate
        def fail_cover(artifact, *args):
            if artifact == 'cover': raise RuntimeError('damaged cover fixture')
            return real_validate(artifact, *args)
        with patch.object(publishing, 'sources', return_value={}), patch.object(failed, 'validate', side_effect=fail_cover), \
             contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, 'damaged cover'):
                failed.vectorize(record, record['config'], {}, {})
        self.assertEqual((base / 'current').readlink(), previous)
        self.assertEqual(json.loads((base / 'manifest.json').read_text()), manifest)


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='kdp-validator-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ref = self.root / 'ref.pdf'; pdf(self.ref)
        self.before = inspect(self.ref)

    def test_identity_and_visual_damage(self):
        self.assertTrue(validate(self.ref, self.ref, self.before, self.before)['passed'])
        visual.self_test()

    def test_geometry_and_page_drop(self):
        for extra in ('/UserUnit 2', '/Rotate 90', '/ArtBox [0 0 500 700]'):
            candidate = self.root / 'changed.pdf'; pdf(candidate, extra=extra)
            self.assertFalse(validate(self.ref, candidate, self.before, inspect(candidate))['passed'])
        two = self.root / 'two.pdf'; pdf(two, [b'', b''])
        self.assertFalse(validate(two, self.ref, inspect(two), self.before)['passed'])
        with self.assertRaisesRegex(ValueError, 'page count'):
            visual.compare(two, self.ref, self.root / 'visual')

    def test_remaining_fonts_and_quote_text(self):
        candidate = self.root / 'font.pdf'
        pdf(candidate, [b'BT /F1 12 Tf 60 60 Td (Hello) \' ET'],
            resources='<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >>')
        info = inspect(candidate)
        self.assertTrue(info['mupdf_font_resources'])
        self.assertGreater(info['mupdf_text_operations'], 0)
        self.assertFalse(validate(candidate, candidate, info, info)['passed'])

    def test_tool_failure_is_not_empty_success(self):
        with patch('kdp_pdf_lib.subprocess.run', return_value=subprocess.CompletedProcess([], 3, '', 'tool error')):
            with self.assertRaisesRegex(RuntimeError, 'tool error'):
                validate(self.ref, self.ref, self.before, self.before)

    def test_malformed_pdf_writes_failed_report(self):
        final = self.root / 'broken.pdf'; final.write_bytes(b'not a PDF')
        report = self.root / 'report.json'
        p = subprocess.run(['bin/kdp-validate', str(self.ref), str(final), str(report)], cwd=ROOT, capture_output=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertFalse(json.loads(report.read_text())['passed'])

    def test_new_raster_and_real_transparency(self):
        before = dict(self.before)
        after = dict(self.before, images=[dict(page=1, type='image', width=504, height=720, color='rgb', components=3, bpc=8)])
        self.assertFalse(validate(self.ref, self.ref, before, after)['passed'])
        candidate = self.root / 'alpha.pdf'
        for alpha, expected in ((1, False), (.5, True)):
            pdf(candidate, resources=f'<< /ExtGState << /G << /ca {alpha} /CA {alpha} /BM /Normal /SMask /None >> >> >>')
            self.assertEqual(inspect(candidate)['features']['transparency'], expected)


if __name__ == '__main__': unittest.main()
