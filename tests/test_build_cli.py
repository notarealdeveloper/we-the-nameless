"""Exercise routing and configuration without invoking TeX or building a book."""
import contextlib
import importlib.machinery
import importlib.util
import io
from itertools import product
import json
import os
from pathlib import Path
import shlex
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


class BuildCompletionTests(unittest.TestCase):
    def complete(self, *words):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            build.completions(list(words))
        return output.getvalue().splitlines()

    def shell(self, words, *, line=None, point=None, cword=None, command='bin/build'):
        words = [command, *words]
        line = ' '.join(words) if line is None else line
        script = '\n'.join([
            'source bin/completions/build.sh',
            'modes=(); compopt() { modes+=("$*"); }',
            'COMP_WORDS=(' + ' '.join(map(shlex.quote, words)) + ')',
            f'COMP_CWORD={len(words) - 1 if cword is None else cword}',
            'COMP_LINE=' + shlex.quote(line),
            f'COMP_POINT={len(line) if point is None else point}',
            '_wtn_build_complete',
            'if ((${#COMPREPLY[@]})); then printf "%s\\n" "${COMPREPLY[@]}"; fi',
            'printf "%s\\n" "${modes[@]}" >&2',
        ])
        result = subprocess.run(['bash', '-c', script], cwd=ROOT, text=True,
                                capture_output=True, check=True,
                                env={**os.environ, 'PATH': str(ROOT / 'bin') + ':' + os.environ['PATH']})
        return result.stdout.splitlines(), result.stderr.splitlines()

    def flags(self):
        return [flag for action in build.parser()._actions if action.help != build.argparse.SUPPRESS
                for flag in action.option_strings]

    def test_options_and_positionals_follow_the_current_slot(self):
        flags = self.flags()
        first = self.complete('')
        self.assertCountEqual(first, [*build.selection_names(), *flags])
        self.assertEqual(len(first), len(set(first)))
        for words in (['genesis', ''], ['--theme', 'dark', 'genesis', ''],
                      ['genesis', '--theme', 'dark', ''], ['--theme=dark', 'genesis', ''],
                      ['--provider', 'lulu', 'genesis', ''], ['--plan', 'genesis', ''],
                      ['--output-dir', 'a directory', 'genesis', '']):
            with self.subTest(words=words):
                self.assertCountEqual(self.complete(*words), [*PRESETS, *flags])
        self.assertCountEqual(self.complete('genesis', 'kdp', ''), flags)
        self.assertEqual(self.complete('genesis', 'kdp', 'anything'), [])

    def test_option_prefixes_and_separator(self):
        self.assertCountEqual(self.complete('-'), self.flags())
        long_flags = [flag for flag in self.flags() if flag.startswith('--')]
        self.assertCountEqual(self.complete('--'), long_flags)
        self.assertCountEqual(self.complete('--theme', '--'), long_flags)
        self.assertEqual(self.complete('--does-not-exist'), [])
        self.assertCountEqual(self.complete('--', ''), build.selection_names())
        self.assertEqual(self.complete('--', 'genesis', ''), list(PRESETS))
        self.assertEqual(self.complete('genesis', 'kdp', '--', ''), [])

    def test_every_declared_choice_and_alias(self):
        for action in build.parser()._actions:
            if action.choices is None or not action.option_strings:
                continue
            for flag in action.option_strings:
                with self.subTest(flag=flag):
                    choices = list(action.choices)
                    self.assertEqual(self.complete(flag, ''), choices)
                    self.assertEqual(self.complete(flag + '='), [flag + '=' + value for value in choices])
                    prefix = choices[0][:1]
                    self.assertEqual(self.complete(flag, prefix),
                                     [value for value in choices if value.startswith(prefix)])
                    self.assertEqual(self.complete(flag, 'not-an-allowed-value'), [])
        self.assertEqual(self.complete('--sta', ''), list(build.STAGES))
        self.assertEqual(self.complete('--pub', ''), list(build.PROVIDERS))
        self.assertEqual(self.complete('--prov', ''), list(build.PROVIDERS))

    def test_new_parser_options_and_choices_are_picked_up_automatically(self):
        parser = build.parser()
        parser.add_argument('--future-option', '--future-alias', choices=('one', 'two'))
        parser.add_argument('--future-switch', action='store_true')
        with patch.object(build, 'parser', return_value=parser):
            self.assertIn('--future-option', self.complete(''))
            self.assertIn('--future-alias', self.complete('--future-'))
            self.assertEqual(self.complete('--future-option', ''), ['one', 'two'])
            self.assertEqual(self.complete('--future-alias=',),
                             ['--future-alias=one', '--future-alias=two'])
            self.assertIn('genesis', self.complete('--future-switch', ''))

    def test_live_choices_and_make_targets(self):
        self.assertEqual(self.complete('--translation', ''), build.translation_names())
        self.assertEqual(self.complete('--cover', ''), ['none', *build.cover_names()])
        with patch.object(build, 'translation_names', return_value=['new-translation']):
            self.assertEqual(self.complete('--translation', 'new'), ['new-translation'])
        with patch.object(build, 'cover_names', return_value=['new cover']):
            self.assertEqual(self.complete('--cover', 'new '), ['new cover'])
        prefix = 'genesis-kdp-simplecover-vectorized-7x10'
        values = self.complete('--make-target', prefix)
        self.assertEqual(values, [prefix, *(prefix + '-' + stage for stage in ('build', 'vectorize', 'check'))])
        self.assertTrue(all(build.parse_target(value)['book'] == 'genesis' for value in values))

    def test_only_paths_request_filename_completion(self):
        for action in build.parser()._actions:
            if action.type is not Path:
                continue
            with self.subTest(flag=action.option_strings[0]):
                kind = '@directories' if action.dest.endswith('_dir') else '@filenames'
                self.assertEqual(self.complete(action.option_strings[0], '/tmp/a'), [kind, '/tmp/a', '0'])
        for words in (['--theme', 'invalid'], ['--source-date-epoch', ''],
                      ['--make-target', 'invalid'], ['unknown-book'], ['--unknown=']):
            with self.subTest(words=words):
                replies, modes = self.shell(words)
                self.assertEqual(replies, [])
                self.assertFalse(any(mode.startswith('-o ') for mode in modes))

    def test_bash_word_breaks_quotes_and_cursor(self):
        cases = [
            (['--theme', 'd'], 'bin/build --theme d'),
            (['--theme', '=', 'd'], 'bin/build --theme=d'),
            (['--theme=d'], 'bin/build --theme=d'),
            (['--theme', '=', '"d'], 'bin/build --theme="d'),
            (['--theme', "'d"], "bin/build --theme 'd"),
            (['--theme', 'd'], 'true; bin/build --theme d'),
            (['--theme', 'd'], 'printf x | bin/build --theme d'),
        ]
        for words, line in cases:
            with self.subTest(line=line, words=words):
                expected = '--theme=dark' if words == ['--theme=d'] else 'dark'
                self.assertEqual(self.shell(words, line=line)[0], [expected])
        self.assertEqual(self.shell(['--theme', '=', ''], line='bin/build --theme= ')[0],
                         self.complete(''))
        line = 'bin/build --theme drivel --plan'
        self.assertEqual(self.shell(['--theme', 'drivel', '--plan'], line=line,
                                    cword=2, point=line.index('drivel') + 1)[0], ['dark'])
        self.assertEqual(self.shell(['--theme', 'd'], command='build')[0], ['dark'])

    def test_bash_paths_preserve_spaces_colons_and_directory_slashes(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp) / 'colon:directory with space'
            directory.mkdir()
            (directory / 'nested').mkdir()
            artifact = directory / 'reference file.pdf'
            artifact.touch()
            prefix = str(directory)[:str(directory).index(':')]
            replies, modes = self.shell(['--output-dir', prefix, ':', 'dir'],
                line='bin/build --output-dir ' + prefix + ':dir')
            self.assertEqual(replies, ['directory with space/'])
            self.assertIn('-o filenames', modes)
            self.assertIn('-o nospace', modes)
            replies, _ = self.shell(['--artifact', '"' + str(directory) + '/ref'],
                line='bin/build --artifact "' + str(directory) + '/ref')
            self.assertEqual(replies, [str(artifact)])
            replies, _ = self.shell(['--output-dir', '=', '"' + str(directory) + '/ne'],
                line='bin/build --output-dir="' + str(directory) + '/ne')
            self.assertEqual(replies, [str(directory / 'nested')])


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
        shell = 'source bin/completions/build.sh\nCOMP_WORDS=(bin/build genesis --theme d)\nCOMP_CWORD=3\nCOMP_LINE="bin/build genesis --theme d"\nCOMP_POINT=${#COMP_LINE}\n_wtn_build_complete\nprintf "%s\\n" "${COMPREPLY[@]}"'
        self.assertEqual(subprocess.check_output(['bash', '-c', shell], cwd=ROOT, text=True).strip(), 'dark')
        path = subprocess.check_output([str(ROOT / 'bin/build'), '--complete', '--output-dir', '/tmp/new'], text=True)
        self.assertEqual(path.splitlines(), ['@directories', '/tmp/new', '0'])

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
