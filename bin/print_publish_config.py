"""Print presets and target grammar; no PDF generation or filesystem writes."""
from dataclasses import dataclass
from itertools import product
import re

TRIMS = {'7x10': (7, 10), '8.25x11': (8.25, 11)}
PROVIDERS = ('kdp', 'lulu')
STYLES = ('simple', 'fancy')
PROCESSING = ('original', 'vectorized')
STAGES = ('all', 'build', 'vectorize', 'check')
BINDINGS = ('paperback', 'hardcover')
PRESETS = ('pdf', 'ebook', *(name for provider in PROVIDERS
    for name in (provider, *(f'{provider}-{binding}' for binding in BINDINGS))))

# Each public TeX setting is declared once for argument parsing, completion and
# documentation. Ordinary PDF defaults come from master.tex; print presets are
# deliberately stable even when the author's active reading settings change.
BOOK_OPTIONS = {
    'output-mode': ('ConfigOutputMode', ('book', 'hard', 'tech', 'even'), 'page layout and typography'),
    'theme': ('ConfigTheme', ('lite', 'dark'), 'light or dark page theme'),
    'verse-layout': ('ConfigVerseLayout', ('horizontal', 'vertical'), 'verse arrangement'),
    'commentary': ('ConfigCommentary', ('true', 'false'), 'include commentary'),
    'translation': ('ConfigEnglishTranslation', None, 'default inline English or a translations/ directory'),
    'title-page-style': ('IndividualBookTitlePageStyle', ('plain', 'fancy'), 'individual book title pages'),
    'colors': ('ConfigColors', ('default', 'lighter'), 'theme palette'),
    'apocrypha': ('ConfigApocrypha', ('apocryphal', 'canonical'), 'include or omit apocrypha'),
    'redactor': ('ConfigRedactor', ('censored', 'uncensored'), 'redaction policy'),
    'cover': ('ConfigCover', None, 'none or an image basename in img/covers/'),
    'cover-style': ('ConfigCoverStyle', STYLES, 'simple typography or saved fancy artwork'),
    'spine': ('ConfigSpine', ('nameless', 'ld'), 'spine lettering'),
    'print-safe': ('ConfigKDP', ('true', 'false'), 'print assets, heavier rules, and even final page count'),
}
PRINT_CONFIG = dict(ConfigOutputMode='book', ConfigTheme='lite',
    ConfigVerseLayout='horizontal', ConfigCommentary='true',
    ConfigEnglishTranslation='default', IndividualBookTitlePageStyle='fancy',
    ConfigColors='default', ConfigApocrypha='apocryphal', ConfigRedactor='uncensored',
    ConfigCover='none', ConfigCoverStyle='simple', ConfigSpine='ld', ConfigKDP='true')


def master_defaults(root):
    text = (root / 'master.tex').read_text()
    return {name: re.search(r'\\def\\' + name + r'\s*\{([^}]+)\}', text)[1]
            for name, _, _ in BOOK_OPTIONS.values()}


@dataclass(frozen=True)
class Profile:
    style: str
    binding: str
    trim: str
    processing: str

    @property
    def key(self):
        return f'{self.style}cover-{self.trim}'

    @property
    def dimensions(self):
        return TRIMS[self.trim]


# Short commands select these complete presets. Every qualified parameter
# overrides only its own field; cover construction remains a separate input.
DEFAULTS = {
    'kdp': (Profile('simple', 'paperback', '7x10', 'vectorized'),
            Profile('fancy', 'hardcover', '8.25x11', 'vectorized')),
    'lulu': (Profile('simple', 'paperback', '7x10', 'original'),
             Profile('fancy', 'hardcover', '7x10', 'original')),
}


def profiles(provider='kdp', style=None, trim='default', processing=None, binding=None):
    if provider not in PROVIDERS or style not in (*STYLES, None):
        raise ValueError('unsupported publisher or cover style')
    if trim not in (*TRIMS, 'default', None) or processing not in (*PROCESSING, None):
        raise ValueError('supported trims: 7x10, 8.25x11, default; processing: original, vectorized')
    if binding not in ('paperback', 'hardcover', None):
        raise ValueError('unsupported cover construction')
    return tuple(Profile(p.style, binding or p.binding,
                         p.trim if trim in ('default', None) else trim,
                         processing or p.processing)
                 for p in DEFAULTS[provider] if style is None or p.style == style)


def paper_for(profile, provider, paper):
    return 'premium-color' if provider == 'kdp' and profile.binding == 'hardcover' else paper


TARGET = re.compile(r'(?P<book>.+)-(?P<provider>kdp|lulu)'
    r'(?:-(?P<preset_binding>paperback|hardcover))?'
    r'(?:-(?P<style>simplecover|fancycover))?'
    r'(?:-(?P<processing>original|vectorized))?'
    r'(?:-(?P<trim>7x10|8\.25x11|default))?'
    r'(?:-(?P<stage>build|vectorize|check))?')


def parse_target(target):
    match = TARGET.fullmatch(target)
    if not match:
        raise ValueError(f'Invalid print target: {target}; see PUBLISH.md')
    values = {k: v for k, v in match.groupdict().items() if v is not None}
    # 'default' is an alias for omission, including when CLI/Make sets trim.
    if values.get('trim') == 'default':
        del values['trim']
    if 'style' in values:
        values['cover_style'] = values.pop('style').removesuffix('cover')
    if 'preset_binding' in values:
        binding = values.pop('preset_binding')
        values.update(binding=binding, cover_style='simple' if binding == 'paperback' else 'fancy')
    return values


def target_suffixes():
    # Preserve the historical optional qualifiers and newer binding presets.
    for provider, style, processing, trim, stage in product(PROVIDERS,
            ('', *(s + 'cover' for s in STYLES)), ('', *PROCESSING),
            ('', *TRIMS, 'default'), ('', *(s for s in STAGES if s != 'all'))):
        yield '-'.join(x for x in (provider, style, processing, trim, stage) if x)
    for provider, binding, stage in product(PROVIDERS, BINDINGS, STAGES):
        target = f'{provider}-{binding}'
        yield target if stage == 'all' else f'{target}-{stage}'



if __name__ == '__main__':
    print(' '.join(target_suffixes()))
