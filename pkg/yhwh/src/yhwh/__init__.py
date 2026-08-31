"""Source-aware lexical analysis of the Hebrew Bible corpus."""
from .model import Word,SourceSpan,Verse,Verses,Chapter,Book,Corpus,Frequency,SourceFrequencies,PRIMARY_BOOKS,TORAH_BOOKS
from .load import load,find_data
from .tex import parse_tex_text,parse_directory,latex_to_text
from .normalize import normalize_hebrew,normalize_english,strip_niqqud,set_niqqud,get_niqqud,words,hebrew_words
from .frequency import frequency,word_by_source
from .evidence import EvidenceModel,EvidenceResult,train
from .cache import cache_dir,clean_cache
__all__=[x for x in globals() if not x.startswith('_')]
__version__ = "0.1.0"
