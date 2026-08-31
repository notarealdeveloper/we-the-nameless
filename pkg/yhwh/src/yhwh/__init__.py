"""yhwh: source-aware Hebrew/English corpus analysis."""
from ._version import __version__
from .ansi import color, color_enabled, set_color
from .attribution import AttributionResult, SourceAttributor, TokenEvidence
from .config import clean_cache, get_niqqud, niqqud, set_niqqud
from .corpus import PRIMARY_HISTORY, TORAH, Corpus
from .dataset import build_dataset
from .frequency import (
    Frequency,
    SourceFrequencies,
    Word,
    frequencies_by_source,
    frequency,
    frequency_text,
    full_frequency,
    source_frequencies,
    words,
)
from .model import Book, Chapter, Span, Verse, VerseRef, Verses
from .normalize import (
    MatresMode,
    TextMatch,
    find_english,
    find_hebrew,
    normalize_english,
    normalize_hebrew,
    strip_niqqud,
    whitespace_tokens,
)
from .search import VerseMatch, grep, grep_english, grep_hebrew
from .sources import DEFAULT_MODEL_SOURCES, DEFAULT_SOURCE_MAP, SourceMap, canonical_source
from .statistics import (
    DistinctiveWord,
    SourceProfile,
    SourceWordEvidence,
    characteristic_words,
    source_profile,
)
from .tex import ParsedFile, discover_source_suffixes, extract_language, parse_tex, parse_tex_file

__all__ = [
    "__version__",
    "AttributionResult",
    "Book",
    "Chapter",
    "Corpus",
    "DEFAULT_MODEL_SOURCES",
    "DEFAULT_SOURCE_MAP",
    "DistinctiveWord",
    "Frequency",
    "MatresMode",
    "PRIMARY_HISTORY",
    "ParsedFile",
    "SourceAttributor",
    "SourceFrequencies",
    "SourceMap",
    "SourceProfile",
    "SourceWordEvidence",
    "Span",
    "TORAH",
    "TextMatch",
    "TokenEvidence",
    "Verse",
    "VerseMatch",
    "VerseRef",
    "Verses",
    "Word",
    "build_dataset",
    "canonical_source",
    "characteristic_words",
    "clean_cache",
    "color",
    "color_enabled",
    "discover_source_suffixes",
    "extract_language",
    "find_english",
    "find_hebrew",
    "frequencies_by_source",
    "frequency",
    "frequency_text",
    "full_frequency",
    "get_niqqud",
    "grep",
    "grep_english",
    "grep_hebrew",
    "niqqud",
    "normalize_english",
    "normalize_hebrew",
    "parse_tex",
    "parse_tex_file",
    "set_color",
    "set_niqqud",
    "source_frequencies",
    "source_profile",
    "strip_niqqud",
    "whitespace_tokens",
    "words",
]
