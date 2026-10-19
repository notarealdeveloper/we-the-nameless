"""Print presets and target grammar; no PDF generation or filesystem writes."""
from dataclasses import dataclass
from itertools import product
import re

TRIMS = {'7x10': (7, 10), '8.25x11': (8.25, 11)}
PROVIDERS = ('kdp', 'lulu')
STYLES = ('simple', 'fancy')
PROCESSING = ('original', 'vectorized')
STAGES = ('all', 'build', 'vectorize', 'check')


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
    return values


def target_suffixes():
    # Used by Make itself so target completion and CLI parsing share a grammar.
    for provider, style, processing, trim, stage in product(PROVIDERS,
            ('', *(s + 'cover' for s in STYLES)), ('', *PROCESSING),
            ('', *TRIMS, 'default'), ('', *(s for s in STAGES if s != 'all'))):
        yield '-'.join(x for x in (provider, style, processing, trim, stage) if x)


if __name__ == '__main__':
    print(' '.join(target_suffixes()))
