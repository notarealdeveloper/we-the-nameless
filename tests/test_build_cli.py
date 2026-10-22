"""Exercise routing and configuration without invoking TeX or building a book."""
import contextlib
import importlib.machinery
import importlib.util
import io
from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bin'))
from print_publish_config import BOOK_OPTIONS, DEFAULTS, PRESETS, TRIMS, master_defaults, profiles

loader = importlib.machinery.SourceFileLoader('build_cli', str(ROOT / 'bin/build'))
spec = importlib.util.spec_from_loader(loader.name, loader)
build = importlib.util.module_from_spec(spec)
loader.exec_module(build)


class BuildCliTests(unittest.TestCase):
    def plan(self, *args, cwd=ROOT):
        return json.loads(subprocess.check_output([str(ROOT / 'bin/build'), *args, '--plan'], cwd=cwd, text=True))

    def test_every_master_setting_is_public_and_reaches_tex(self):
        defaults = master_defaults(ROOT)
        self.assertEqual(build.arguments(['genesis']).tex_config, defaults)
        for flag, (tex, choices, _) in BOOK_OPTIONS.items():
            if choices is None:
                choices = ('default',) if flag == 'translation' else ('none',)
            for value in choices:
                with self.subTest(flag=flag, value=value):
                    args = build.arguments(['genesis', '--' + flag, value])
                    plan = build.pdf_plan(args)
                    self.assertEqual(plan['config'][tex], value)
                    self.assertIn('\\def\\' + tex + '{' + value + '}', plan['commands'][-1][-1])

    def test_publisher_cartesian_product_resolves(self):
        for provider, style, binding, trim, processing in product(
                ('kdp', 'lulu'), ('simple', 'fancy'), ('paperback', 'hardcover'), TRIMS,
                ('original', 'vectorized')):
            args = build.arguments(['genesis', provider, '--cover-style', style, '--binding', binding,
                                    '--trim', trim, '--processing', processing])
            resolved = profiles(args.provider, args.cover_style, args.trim, args.processing, args.binding)
            self.assertEqual([(p.style, p.binding, p.trim, p.processing) for p in resolved],
                             [(style, binding, trim, processing)])

    def test_named_binding_presets_are_explicit_argument_shorthand(self):
        for provider, values in DEFAULTS.items():
            for profile in values:
                short = self.plan('exodus', provider + '-' + profile.binding)
                full = self.plan('exodus', provider, '--cover-style', profile.style, '--binding', profile.binding,
                                 '--trim', profile.trim, '--processing', profile.processing)
                self.assertEqual(short, full)
                other = 'fancy' if profile.style == 'simple' else 'simple'
                override = self.plan('exodus', provider + '-' + profile.binding, '--cover-style', other)
                self.assertEqual(override['profiles'][0]['trim'], profile.trim)
                self.assertEqual(override['profiles'][0]['binding'], profile.binding)
                self.assertEqual(override['profiles'][0]['style'], other)

    def test_make_shorthands_match_cli_and_partial_targets_are_gone(self):
        for name, preset in (('genesis-kdp', 'kdp'), ('exodus-lulu-hardcover', 'lulu-hardcover')):
            made = json.loads(subprocess.check_output(['make', '--no-print-directory', name, 'PRINT_PLAN=1'], cwd=ROOT, text=True))
            self.assertEqual(made, self.plan(name.split('-')[0], preset))
        for target in ('genesis-kdp-fancycover', 'genesis-kdp-vectorized', 'genesis-lulu-7x10'):
            result = subprocess.run(['make', '-n', target], cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('No rule to make target', result.stderr)

    def test_make_explicit_display_settings_reach_print_plan(self):
        plan = json.loads(subprocess.check_output(['make', '--no-print-directory', 'genesis-lulu',
            'PRINT_PLAN=1', 'THEME=dark', 'COMMENTARY=false', 'PRINT_PAPER=standard-color'], cwd=ROOT, text=True))
        self.assertEqual(plan['config']['ConfigTheme'], 'dark')
        self.assertEqual(plan['config']['ConfigCommentary'], 'false')
        self.assertEqual(plan['ink'], 'standard-color')
        self.assertTrue(all(p['paper'] == 'standard-color' for p in plan['profiles']))
        made = json.loads(subprocess.check_output(['make', '--no-print-directory', 'genesis-kdp-paperback',
            'PRINT_PLAN=1', 'PRINT_COVER_STYLE=fancy'], cwd=ROOT, text=True))
        self.assertEqual(made, self.plan('genesis', 'kdp-paperback', '--cover-style', 'fancy'))

    def test_plans_from_other_directories_do_not_create_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            for preset in ('pdf', 'kdp', 'lulu-hardcover', 'ebook'):
                self.plan('genesis', preset, '--output-dir', 'new output', cwd=temp)
            self.assertEqual(list(Path(temp).iterdir()), [])

    def test_translation_preparation_and_explicit_geometry(self):
        plan = build.pdf_plan(build.arguments(['genesis', '--translation', 'kjv', '--output-mode', 'tech', '--trim', '7x10']))
        self.assertEqual(plan['commands'][1][:2], ['bin/book-translation-lua', 'kjv'])
        self.assertIn(r'\def\ConfigEnglishTranslationLuaFile{', plan['commands'][-1][-1])
        self.assertEqual(plan['config']['ConfigPrintTrimWidth'], '7in')
        self.assertEqual(plan['config']['ConfigOutputMode'], 'tech')

    def test_parallel_plan_preserves_all_config_and_does_not_open_pdf(self):
        plan = build.pdf_plan(build.arguments(['all', '--workflow', 'parallel', '--theme', 'dark', '--spine', 'nameless']))
        self.assertEqual(plan['environment']['WTN_THEME'], 'dark')
        self.assertEqual(plan['environment']['WTN_SPINE'], 'nameless')
        self.assertEqual(plan['commands'][-1], ['bin/parallel-build', '--plain', '--no-open'])
        self.assertNotIn('xdg-open', str(plan))

    def test_ebook_release_check_and_alias_paths(self):
        release = self.plan('01-genesis', 'ebook', '--stage', 'release')
        self.assertTrue(release['output'].endswith('/ebook/genesis.epub'))
        self.assertIn('--require-epubcheck', release['commands'][0])
        check = self.plan('genesis', 'ebook', '--stage', 'check')
        self.assertEqual(check['output'], release['output'])
        self.assertEqual(check['commands'][1][0], 'epubcheck')
        self.assertFalse(any('build.py' in str(cmd) for cmd in check['commands']))

    def test_invalid_options_fail_before_any_command_or_directory_creation(self):
        bad = [ ['genesis', 'ebook', '--theme', 'dark'], ['genesis', '--processing', 'vectorized'],
            ['all', '--source-date-epoch', '-1'], ['genesis', '--workflow', 'parallel'],
            ['genesis', '--translation', '../kjv'], ['genesis', '--stage', 'check'],
            ['genesis', 'ebook', '--paper', 'premium-color'],
            ['genesis', 'kdp', '--publisher', 'lulu'], ['genesis', 'lulu', '--stage', 'release'] ]
        for argv in bad:
            with self.subTest(argv=argv), patch.object(build.subprocess, 'run') as run, \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                build.main(argv)
            run.assert_not_called()

    def test_completion_lists_live_options_and_values(self):
        for words, expected in ((['--theme', 'd'], 'dark'), (['--translation', 'k'], 'kjv'),
                (['genesis', 'lulu-'], 'lulu-hardcover'), (['--sta'], '--stage')):
            result = subprocess.check_output([str(ROOT / 'bin/build'), '--complete', *words], text=True)
            self.assertIn(expected, result.splitlines())
        shell = 'source bin/completions/build.sh\nCOMP_WORDS=(bin/build genesis --theme d)\nCOMP_CWORD=3\n_wtn_build_complete\nprintf "%s\\n" "${COMPREPLY[@]}"'
        self.assertEqual(subprocess.check_output(['bash', '-c', shell], cwd=ROOT, text=True).strip(), 'dark')
        empty = subprocess.check_output([str(ROOT / 'bin/build'), '--complete', '--output-dir', '/tmp/new'], text=True)
        self.assertEqual(empty, '')

    def test_legacy_helpers_delegate_with_their_original_interpreters(self):
        for name, args in (('cover', ['/tmp/nonexistent-wtn-cover-interior.pdf']), ('inspect', []), ('validate', [])):
            with self.subTest(name=name):
                legacy = subprocess.run([str(ROOT/'bin'/('kdp-'+name)), *args], cwd=ROOT, capture_output=True, text=True)
                neutral = subprocess.run([str(ROOT/'bin'/('print-'+name)), *args], cwd=ROOT, capture_output=True, text=True)
                self.assertNotEqual(legacy.returncode, 0)
                self.assertEqual((legacy.returncode, legacy.stdout, legacy.stderr),
                                 (neutral.returncode, neutral.stdout, neutral.stderr))

    def test_reference_documents_cover_every_public_option(self):
        publish = (ROOT/'PUBLISH.md').read_text()
        manual = (ROOT/'man/pages/build.1').read_text().replace(r'\-', '-')
        for action in build.parser()._actions:
            if action.help == '==SUPPRESS==': continue
            for flag in action.option_strings:
                if flag.startswith('--'):
                    self.assertIn(flag, publish)
                    self.assertIn(flag, manual)
        self.assertNotIn('\n### ', publish)

    def test_pdf_execution_routes_only_to_planned_commands(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            def fake_run(command, **kw):
                if command[0] == 'bin/book-subset':
                    work = Path(command[2])
                    (work / '01-genesis.tex').write_text(r'\include{nested/chapter}')
                else:
                    (directory / 'work/01-genesis.pdf').write_bytes(b'fixture; no TeX invoked')
            with patch.object(build, 'canonical', return_value='01-genesis'), \
                    patch.object(build.subprocess, 'run', side_effect=fake_run) as run, contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(build.main(['genesis', '--build-dir', str(directory/'work'), '--output-dir', str(directory/'out')]), 0)
            self.assertEqual(run.call_count, 2)
            self.assertTrue((directory/'work/nested').is_dir())
            self.assertEqual((directory/'out/01-genesis.pdf').read_bytes(), b'fixture; no TeX invoked')


if __name__ == '__main__':
    unittest.main()
