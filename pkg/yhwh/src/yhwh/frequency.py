from __future__ import annotations
from .model import Frequency, SourceFrequencies, Word
from .normalize import words, hebrew_words
from .sources import matches_source

def _tokens(text,language,niqqud=None,matres=None):
    if language.startswith('h'): return [Word(x) for x in hebrew_words(text,niqqud=niqqud,matres=matres)]
    return [Word(x) for x in words(text)]

def frequency(verses, *, language='english', by_source=False, sources=None, niqqud=None, matres=None):
    spans_attr='hebrew_spans' if language.startswith('h') else 'english_spans'
    if by_source:
        labels=[]
        if sources is None:
            for v in verses:
                for sp in getattr(v,spans_attr):
                    if sp.source not in labels: labels.append(sp.source)
        else: labels=[sources] if isinstance(sources,str) else list(sources)
        out=SourceFrequencies()
        for source in labels:
            c=Frequency(language=language,source=source)
            for v in verses:
                for sp in getattr(v,spans_attr):
                    if matches_source(sp.source,source): c.update(_tokens(sp.text,language,niqqud,matres))
            out[source]=c
        return out
    c=Frequency(language=language)
    for v in verses:
        text=v.hebrew if language.startswith('h') else v.english
        c.update(_tokens(text,language,niqqud,matres))
    return c

def word_by_source(verses, word, *, language='english', sources=None, niqqud=None, matres=None):
    freqs=frequency(verses,language=language,by_source=True,sources=sources,niqqud=niqqud,matres=matres)
    key=_tokens(word,language,niqqud,matres)
    if len(key)!=1: raise ValueError('word_by_source expects one whitespace-delimited word')
    return {s:f[key[0]] for s,f in freqs.items()}
