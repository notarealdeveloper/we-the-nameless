"""Publishing checks use synthetic PDFs only; never invoke a book build."""
import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bin'))
from kdp_pdf_lib import inspect, validate
from kdp_fixtures import pdf
from print_publish_config import profiles, parse_target, target_suffixes, TRIMS


def module(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec); loader.exec_module(mod)
    return mod


publishing = module('publishing', ROOT / 'bin/print_publish.py')
visual = module('visual', ROOT / 'bin/print-visual-compare')


class PublishingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='kdp-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_make_completion_and_resolution(self):
        query = subprocess.run(['make', '-qp'], cwd=ROOT, text=True, capture_output=True)
        self.assertIn(query.returncode, (0, 1))
        targets = set(re.findall(r'^(\S+):', query.stdout, re.MULTILINE))
        names = subprocess.check_output(['bin/book-subset', '--make-targets'], cwd=ROOT, text=True).split()
        chapters = subprocess.check_output(['bin/book-subset', '--make-chapter-targets'], cwd=ROOT, text=True).split()
        for name in names + chapters:
            for suffix in target_suffixes():
                self.assertIn(name + '-' + suffix, targets)
            for suffix in ('kdp-simplecover', 'kdp-fancycover', 'lulu-original', 'kdp-7x10', 'kdp-default'):
                self.assertNotIn(name + '-' + suffix, targets)
        for alias in ('genesis', '1-genesis', '01-genesis'):
            self.assertEqual(subprocess.check_output(['bin/book-subset', '--output-name', alias], cwd=ROOT, text=True).strip(), '01-genesis')
        for target in ('genesis-kdp-paperback', 'J-kdp-hardcover', 'P-lulu', 'genesis-1-kdp', 'genesis-kdp-simplecover-original-8.25x11', 'J-lulu-fancycover-vectorized-7x10'):
            dry = subprocess.check_output(['make', '-n', target], cwd=ROOT, text=True)
            self.assertIn('bin/build', dry)
            self.assertNotIn('lualatex', dry)

    def test_make_routes_every_qualifier_combination(self):
        targets = ['genesis-' + suffix for suffix in target_suffixes()]
        dry = subprocess.check_output(['make', '--no-print-directory', '-n', *targets], cwd=ROOT, text=True)
        self.assertEqual(len(dry.splitlines()), len(targets))
        for target in targets:
            self.assertIn('--make-target "' + target + '"', dry)
        self.assertNotIn('lualatex', dry)

    def test_target_matrix_and_precedence(self):
        # Every enumerated spelling resolves, including chapter and numbered names.
        for suffix in target_suffixes():
            for book in ('genesis', 'genesis-1', '1-samuel', '1-samuel-1', 'J', 'j'):
                args = publishing.arguments(['--make-target', book + '-' + suffix])
                self.assertEqual(args.book, book)
                selected = profiles(args.provider, args.cover_style, args.trim, args.processing)
                self.assertEqual(len(selected), 1 if args.cover_style else 2)
                if args.trim not in ('default', None):
                    self.assertTrue(all(p.trim == args.trim for p in selected))
                if args.processing:
                    self.assertTrue(all(p.processing == args.processing for p in selected))
                if '-default' in suffix:
                    omitted = publishing.arguments(['--make-target', book + '-' + suffix.replace('-default', '')])
                    self.assertEqual(selected, profiles(omitted.provider, omitted.cover_style, omitted.trim, omitted.processing))
        args = publishing.arguments(['--make-target', 'genesis-lulu-fancycover-vectorized-7x10',
            '--provider', 'kdp', '--cover-style', 'simple', '--trim', '8.25x11', '--processing', 'original'])
        self.assertEqual((args.provider, args.cover_style, args.trim, args.processing), ('lulu', 'fancy', '7x10', 'vectorized'))
        args = publishing.arguments(['--make-target', 'genesis-kdp-fancycover-default', '--trim', '7x10'])
        self.assertEqual(profiles(args.provider, args.cover_style, args.trim)[0].trim, '7x10')
        omitted = publishing.arguments(['--make-target', 'genesis-kdp-fancycover', '--trim', '7x10'])
        self.assertEqual(profiles(args.provider, args.cover_style, args.trim),
                         profiles(omitted.provider, omitted.cover_style, omitted.trim))
        # Artwork and construction are independent through the script API.
        self.assertEqual(profiles('lulu', 'simple', '8.25x11', 'vectorized', 'hardcover')[0].binding, 'hardcover')

    def test_default_plans_and_make_overrides_without_writes(self):
        for provider, trim, processing in (('kdp', '8.25x11', 'vectorized'), ('lulu', '7x10', 'original')):
            command = ['bin/kdp-publish', 'genesis', 'all', '--provider', provider, '--plan']
            direct = json.loads(subprocess.check_output(command, cwd=ROOT, text=True))
            made = json.loads(subprocess.check_output(['make', '--no-print-directory', 'genesis-' + provider, 'PRINT_PLAN=1'], cwd=ROOT, text=True))
            self.assertEqual(direct, made)
            self.assertEqual([(p['style'], p['binding'], p['trim'], p['processing']) for p in direct['profiles']],
                [('simple', 'paperback', '7x10', processing), ('fancy', 'hardcover', trim, processing)])
            for p in direct['profiles']:
                for paths in p['files'].values():
                    self.assertTrue(all('/pub/' + provider + '/' in path for path in paths))
                    self.assertFalse(any('paperback' in path or 'hardcover' in path or '-alt-' in path for path in paths))
        plan = json.loads(subprocess.check_output(['make', '--no-print-directory',
            'exodus-lulu-fancycover-vectorized-8.25x11', 'PRINT_PLAN=1', 'KDP_TRIM=7x10',
            'KDP_COVER_STYLE=simple', 'PRINT_PROCESSING=original'], cwd=ROOT, text=True))
        self.assertEqual(plan['book'], '02-exodus')
        self.assertEqual([(p['style'], p['trim'], p['processing']) for p in plan['profiles']],
                         [('fancy', '8.25x11', 'vectorized')])

    def test_binding_geometry_and_exact_template(self):
        paperback = publishing.geometry(224, 8.25, 11, 'premium-color')
        hardcover = publishing.geometry(224, 8.25, 11, 'premium-color', 'hardcover')
        self.assertAlmostEqual(paperback['width'], 17.275728)
        # Independent measured KDP template at this trim/page count.
        self.assertAlmostEqual(hardcover['width'], 18.790, delta=.001)
        self.assertAlmostEqual(hardcover['height'], 12.417, delta=.001)
        self.assertAlmostEqual(hardcover['spine'], .715, delta=.001)
        other = publishing.geometry(300, 7, 10, 'standard-color', 'hardcover')
        self.assertAlmostEqual(other['spine'] - hardcover['spine'], 76*.002347)
        exact = self.root / 'template.json'
        data = dict(pages=224, trim_width=8.25, trim_height=11, paper='premium-color',
            spine=.715, wrap=.591, hinge=.394, panel_width=8.447, panel_height=11.236)
        exact.write_text(json.dumps(data))
        measured = publishing.geometry(224, 8.25, 11, 'premium-color', 'hardcover', exact)
        self.assertEqual(measured['spine'], .715)
        with self.assertRaisesRegex(ValueError, 'does not match'):
            publishing.geometry(226, 8.25, 11, 'premium-color', 'hardcover', exact)

    def test_source_changes_name_files_and_save_report(self):
        image = 'pub/covers/fancy/assets/front-textless.png'
        with patch.object(publishing, 'sources', return_value={image: 'new', 'added.tex': 'a'}):
            with self.assertRaisesRegex(RuntimeError, image):
                publishing.check_sources({image: 'old', 'removed.tex': 'r'}, self.root)
        self.assertEqual(json.loads((self.root / 'reports/source-changes.json').read_text()),
                         dict(added=['added.tex'], removed=['removed.tex'], modified=[image]))

    def test_unchanged_sources_pass(self):
        with patch.object(publishing, 'sources', return_value={'chapter.tex': 'same'}):
            publishing.check_sources({'chapter.tex': 'same'}, self.root)
        self.assertFalse((self.root / 'reports').exists())

    def test_failure_keeps_command_and_full_log(self):
        pipeline = publishing.Pipeline('fixture', self.root / 'build', self.root / 'pub')
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
        with patch.object(sys, 'argv', ['kdp-publish', 'genesis', 'build']), \
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
        assets = module('assets', ROOT / 'bin/print-assets')
        with patch.object(sys, 'argv', ['kdp-assets', str(self.root / 'assets'), str(subset)]), \
             patch.object(assets, 'ROOT', self.root), \
             patch.object(assets.subprocess, 'check_output', return_value=b'fixture magick'), \
             patch.object(assets.subprocess, 'run') as convert:
            assets.main()
        convert.assert_not_called()
        self.assertEqual(json.loads((self.root / 'assets/assets.json').read_text()), [])

    def test_build_staging_with_fake_tex_and_real_pdf_inspection(self):
        self.build_fixture('both')

    def test_paperback_build_only(self):
        self.build_fixture('paperback')

    def test_hardcover_build_only(self):
        self.build_fixture('hardcover')

    def test_build_matrix_uses_independent_artwork_trim_and_publisher(self):
        for provider in ('kdp', 'lulu'):
            for binding in ('paperback', 'hardcover'):
                for trim in TRIMS:
                    with self.subTest(provider=provider, binding=binding, trim=trim):
                        self.build_fixture(binding, provider, trim, 'standard-color')

    def test_custom_interior_settings_and_translation_reach_print_tex(self):
        self.build_fixture('paperback', 'lulu', '8.25x11', tex_config=dict(
            publishing.PRINT_CONFIG, ConfigOutputMode='tech', ConfigTheme='dark',
            ConfigCommentary='false', ConfigEnglishTranslation='kjv',
            ConfigApocrypha='canonical', ConfigVerseLayout='vertical'))

    def build_fixture(self, binding, provider='kdp', trim='default', paper='premium-color', tex_config=None):
        selected = profiles(provider, {'both': None, 'paperback': 'simple', 'hardcover': 'fancy'}[binding], trim)
        base = self.root / provider / binding / trim / paper
        pipeline = publishing.Pipeline('fixture', base / 'build', base / 'pub', selected, provider)
        passes = []
        def simulate(stage, operation, command, candidate=None, env=None):
            tool = command[0]
            if tool == 'bin/book-subset':
                work = Path(command[2]); (work / 'chapters').mkdir(parents=True)
                (work / 'fixture.tex').write_text(r'\include{generated/chapter}')
            elif tool == 'bin/print-assets':
                assets = Path(command[1]); assets.mkdir()
                (assets / 'assets.json').write_text('[]')
            elif tool == 'bin/book-translation-lua':
                Path(command[2]).write_text('-- synthetic translation')
            elif tool == 'lualatex':
                self.assertTrue((Path(candidate).parent / 'generated').is_dir())
                self.assertTrue(Path(env['TEXMFVAR']).is_dir())
                passes.append(operation)
                profile = next(p for p in selected if p.key in str(candidate))
                width, height = profile.dimensions
                self.assertIn(r'\def\ConfigPrintTrimWidth{' + f'{width}in' + '}', command[-1])
                self.assertIn(r'\def\ConfigPrintTrimHeight{' + f'{height}in' + '}', command[-1])
                for key, value in (tex_config or publishing.PRINT_CONFIG).items():
                    if key not in ('ConfigCoverStyle', 'ConfigSpine'):
                        self.assertIn('\\def\\' + key + '{' + value + '}', command[-1])
                if tex_config and tex_config['ConfigEnglishTranslation'] != 'default':
                    self.assertIn(r'\def\ConfigEnglishTranslationLuaFile{', command[-1])
                    self.assertTrue((Path(candidate).parent / 'translation-kjv.lua').is_file())
                pdf(candidate, [b''] * 80, box=f'0 0 {width*72} {height*72}')
            elif tool == 'bin/print-cover':
                profile = next(p for p in selected if p.key in str(command[1]))
                self.assertEqual(command[10], provider)
                self.assertEqual(command[5], profile.style)
                self.assertEqual(command[8], profile.binding)
                self.assertEqual(command[2], 'premium-color' if provider == 'kdp' and profile.binding == 'hardcover' else paper)
                self.assertEqual(inspect(command[1])['pages'], 80)
                self.assertEqual(Path(command[1]), pipeline.pdf_path('interior-' + profile.key, 'original'))
                geometry = publishing.geometry if provider == 'kdp' else publishing.lulu_geometry
                g = geometry(80, *profile.dimensions, command[2], profile.binding)
                pdf(command[3], box=f"0 0 {72*g['width']} {72*g['height']}")
            elif tool == 'bin/print-inspect':
                report = Path(command[2]); report.parent.mkdir(parents=True, exist_ok=True)
                report.write_text(json.dumps(inspect(command[1])))
            else:
                self.fail(f'unexpected command {command}')
        args = SimpleNamespace(book='fixture', paper=paper, spine='ld')
        if tex_config: args.tex_config = tex_config
        with patch.object(pipeline, 'run', side_effect=simulate), patch.object(publishing, 'sources', return_value={}):
            record = pipeline.build(args, {}, {}, {})
        self.assertEqual(passes, ['LuaLaTeX pass 1', 'LuaLaTeX pass 2', 'LuaLaTeX pass 3'] * len(pipeline.profiles))
        self.assertEqual(len(record['files']), len(pipeline.artifacts))
        self.assertEqual(len(list(pipeline.output_dir.glob('*.pdf'))), len(pipeline.artifacts))
        for artifact in pipeline.artifacts:
            self.assertTrue(pipeline.pdf_path(artifact, 'original').is_file())
            self.assertEqual(pipeline.pdf_path(artifact, 'original').parent, base / 'pub')
        self.assertTrue((pipeline.base / 'build.json').exists())
        self.assertFalse((pipeline.base / 'current').exists())

    def test_binding_selection_requires_only_its_artifacts(self):
        for binding in ('paperback', 'hardcover'):
            selected = profiles(style='simple' if binding == 'paperback' else 'fancy')
            pipeline = publishing.Pipeline('fixture', self.root / binding, self.root / binding / 'pub', selected)
            self.assertEqual(pipeline.artifacts, tuple(k + '-' + selected[0].key for k in ('interior', 'cover')))
            for artifact in pipeline.artifacts:
                pdf(pipeline.pdf_path(artifact, 'original'))
            with contextlib.redirect_stdout(io.StringIO()):
                pipeline.vectorize({'variant': 'soft'})
            self.assertEqual(len(list(pipeline.output_dir.glob('*-vectorized.pdf'))), len(pipeline.artifacts))

    def test_vectorize_and_check_use_editable_pub_files_without_manifest(self):
        pipeline = publishing.Pipeline('fixture', self.root / 'build', self.root / 'pub')
        for name in pipeline.artifacts:
            pdf(pipeline.pdf_path(name, 'original'), [b'BT /F1 16 Tf 70 650 Td (Fixture) Tj ET\n'],
                resources='<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >>')
        with contextlib.redirect_stdout(io.StringIO()):
            pipeline.vectorize({'variant': 'soft'})
        self.assertFalse(any('bin/print-visual-compare' in c['argv'] for c in pipeline.commands))
        for name in pipeline.artifacts:
            self.assertEqual(inspect(pipeline.pdf_path(name, 'vectorized'))['font_count'], 0)
            self.assertGreater(inspect(pipeline.pdf_path(name, 'original'))['font_count'], 0)
        previous = {a: pipeline.pdf_path(a, 'vectorized').read_bytes() for a in pipeline.artifacts}
        # A user can replace a stable input; no stale manifest blocks conversion.
        pdf(pipeline.pdf_path('interior-simplecover-7x10', 'original'))
        real_validate = pipeline.validate
        def fail_cover(artifact, *args, **kwargs):
            if artifact == 'cover-fancycover-8.25x11': raise RuntimeError('damaged cover fixture')
            return real_validate(artifact, *args, **kwargs)
        with patch.object(pipeline, 'validate', side_effect=fail_cover), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, 'damaged cover'):
                pipeline.vectorize({'variant': 'soft'})
        for a in previous:
            self.assertEqual(pipeline.pdf_path(a, 'vectorized').read_bytes(), previous[a])
        with contextlib.redirect_stdout(io.StringIO()):
            pipeline.vectorize({'variant': 'soft'})
            pipeline.check()
        comparisons = [c for c in pipeline.commands if c['argv'][0] == 'bin/print-visual-compare']
        self.assertEqual(len(comparisons), 5)  # Self-test plus four PDFs, only in check.
        for command in comparisons[1:]:
            self.assertEqual(Path(command['argv'][1]).parent, self.root / 'pub')
            self.assertEqual(Path(command['argv'][2]).parent, self.root / 'pub')

    def test_parallel_bindings_have_isolated_state_and_independent_vectorization(self):
        pipeline = publishing.Pipeline('fixture', self.root / 'build', self.root / 'pub')
        pipeline.environment = {'SOURCE_DATE_EPOCH': '1'}
        barrier = threading.Barrier(2)
        workers = []
        events = []
        def build(worker, *args):
            workers.append(worker)
            events.append(('build', worker.profiles[0].key))
            barrier.wait(timeout=5)
            return dict(files={}, dependencies={}, assets=[])
        def vectorize(worker, config):
            events.append(('vectorize', worker.profiles[0].key))
            barrier.wait(timeout=5)
        with patch.object(publishing.Pipeline, 'build', build), \
             patch.object(publishing.Pipeline, 'vectorize', vectorize):
            pipeline.parallel(SimpleNamespace(stage='all'), {}, {}, {})
        self.assertEqual(len(workers), 2)
        self.assertNotEqual(workers[0].run_dir, workers[1].run_dir)
        self.assertNotEqual(workers[0].base, workers[1].base)
        self.assertTrue(set(workers[0].artifacts).isdisjoint(workers[1].artifacts))
        for worker in workers:
            binding = worker.profiles[0].key
            self.assertEqual(worker.environment, pipeline.environment)
            self.assertLess(events.index(('build', binding)), events.index(('vectorize', binding)))
        record = json.loads((pipeline.base / 'build.json').read_text())
        self.assertEqual(set(record['profile_runs']), {'simplecover-7x10', 'fancycover-8.25x11'})
        self.assertEqual(len(record['reference_files']), 4)

    def test_processing_dispatch_for_both_publishers(self):
        for provider in ('kdp', 'lulu'):
            for processing in ('original', 'vectorized'):
                for stage in ('all', 'build', 'vectorize'):
                    selected = profiles(provider, processing=processing)
                    base = self.root / provider / processing / stage
                    pipeline = publishing.Pipeline('fixture', base, base / 'pub', selected, provider)
                    pipeline.environment = {}
                    with patch.object(publishing.Pipeline, 'build', return_value=dict(files={}, dependencies={}, assets=[])) as build, \
                         patch.object(publishing.Pipeline, 'vectorize') as convert:
                        pipeline.parallel(SimpleNamespace(stage=stage), {}, {}, {})
                    self.assertEqual(build.call_count, 0 if stage == 'vectorize' else 2)
                    expected = stage == 'vectorize' or (stage == 'all' and processing == 'vectorized')
                    self.assertEqual(convert.call_count, 2 if expected else 0)

    def test_plan_creates_no_artifacts_and_does_not_probe_build_tools(self):
        with patch.object(sys, 'argv', ['kdp-publish', 'genesis', 'build', '--plan']), \
             patch.object(publishing, 'ROOT', self.root), \
             patch.object(publishing.subprocess, 'check_output', side_effect=lambda cmd, **kw: '1\n' if cmd[0] == 'git' else 'fixture\n'), \
             patch.object(publishing, 'Pipeline') as pipeline, \
             patch.object(publishing, 'versions') as versions, \
             patch.object(publishing, 'sources') as sources, \
             contextlib.redirect_stdout(io.StringIO()) as output:
            try: self.assertEqual(publishing.main(), 0)
            finally: os.chdir(ROOT)
        pipeline.assert_not_called()
        versions.assert_not_called()
        sources.assert_not_called()
        self.assertEqual(list(self.root.iterdir()), [])
        for p in json.loads(output.getvalue())['profiles']:
            self.assertEqual(set(p['files']), {'original'})

    def test_parallel_failure_waits_for_other_binding(self):
        pipeline = publishing.Pipeline('fixture', self.root / 'build', self.root / 'pub')
        pipeline.environment = {}
        barrier = threading.Barrier(2)
        finished = threading.Event()
        def vectorize(worker, config):
            barrier.wait(timeout=5)
            if worker.profiles[0].style == 'simple':
                raise RuntimeError('conversion failed')
            finished.set()
        with patch.object(publishing.Pipeline, 'vectorize', vectorize), \
             contextlib.redirect_stdout(io.StringIO()) as terminal:
            with self.assertRaisesRegex(RuntimeError, 'conversion failed'):
                pipeline.parallel(SimpleNamespace(stage='vectorize'), {}, {}, {})
        self.assertTrue(finished.is_set())
        self.assertIn('simplecover-7x10', terminal.getvalue())


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
        p = subprocess.run(['bin/print-validate', str(self.ref), str(final), str(report)], cwd=ROOT, capture_output=True)
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
