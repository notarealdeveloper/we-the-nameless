from __future__ import annotations
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Sequence
import json, math, re

GREY='\x1b[2;37m'; RED='\x1b[31m'; BLUE='\x1b[34m'; RESET='\x1b[0m'

class Word(str):
    """A whitespace-delimited corpus token."""

@dataclass(frozen=True)
class SourceSpan:
    source: str
    text: str
    start: int = 0
    end: int = 0
    raw_source: str | None = None
    def __post_init__(self):
        if not self.end: object.__setattr__(self, 'end', self.start + len(self.text))
    def to_dict(self): return {'source':self.source,'raw_source':self.raw_source or self.source,'text':self.text,'start':self.start,'end':self.end}

@dataclass
class Verse:
    book: str; chapter: int; verse: str
    hebrew: str=''; english: str=''
    hebrew_spans: list[SourceSpan]=field(default_factory=list)
    english_spans: list[SourceSpan]=field(default_factory=list)
    path: str | None=None
    @property
    def sources(self) -> tuple[str,...]:
        return tuple(dict.fromkeys(s.source for s in self.hebrew_spans + self.english_spans))
    @property
    def reference(self): return f'{self.book} {self.chapter}:{self.verse}'
    def __repr__(self): return f'{BLUE}<Verse {self.reference} [{"/".join(self.sources) or "?"}]>{RESET}'
    def to_dict(self):
        return {'book':self.book,'chapter':self.chapter,'verse':self.verse,'hebrew':self.hebrew,'english':self.english,
                'hebrew_spans':[s.to_dict() for s in self.hebrew_spans], 'english_spans':[s.to_dict() for s in self.english_spans]}
    @classmethod
    def from_dict(cls,d):
        return cls(d['book'],int(d['chapter']),str(d['verse']),d.get('hebrew',''),d.get('english',''),
                   [SourceSpan(**x) for x in d.get('hebrew_spans',[])],[SourceSpan(**x) for x in d.get('english_spans',[])])

class Verses(list[Verse]):
    def frequency(self, language='english', *, by_source=False, sources=None, niqqud=None, matres=None):
        from .frequency import frequency
        return frequency(self, language=language, by_source=by_source, sources=sources, niqqud=niqqud, matres=matres)
    def refs(self): return [v.reference for v in self]

@dataclass
class Chapter:
    book: str; number: int; verses: Verses=field(default_factory=Verses)
    def __iter__(self): return iter(self.verses)
    def __getitem__(self,k):
        if isinstance(k,int):
            for v in self.verses:
                if str(v.verse)==str(k): return v
        return self.verses[k]
    def __repr__(self): return f'{RED}<Chapter {self.book} {self.number}: {len(self.verses)} verses>{RESET}'

@dataclass
class Book:
    name: str; chapters: list[Chapter]=field(default_factory=list)
    def __iter__(self): return iter(self.chapters)
    def __getitem__(self,k):
        if isinstance(k,int):
            for c in self.chapters:
                if c.number==k: return c
        return self.chapters[k]
    @property
    def verses(self): return Verses(v for c in self.chapters for v in c.verses)
    def __repr__(self): return f'{GREY}<Book {self.name}: {len(self.chapters)} chapters, {len(self.verses)} verses>{RESET}'

class Frequency(Counter):
    """Counter with corpus metadata and convenience display methods."""
    def __init__(self,*a,language=None,source=None,**kw): super().__init__(*a,**kw); self.language=language; self.source=source
    def __repr__(self): return f'<Frequency {self.language or "?"}{"/"+self.source if self.source else ""}: {sum(self.values())} tokens, {len(self)} types>'
    def frame(self, n=None):
        rows=self.most_common(n)
        try:
            import pandas as pd
            return pd.DataFrame(rows,columns=['word','count'])
        except ImportError: return rows

class SourceFrequencies(dict[str,Frequency]):
    def __repr__(self): return '<SourceFrequencies ' + ', '.join(f'{k}:{sum(v.values())}' for k,v in self.items()) + '>'

PRIMARY_BOOKS=('Genesis','Exodus','Leviticus','Numbers','Deuteronomy','Joshua','Judges','1 Samuel','2 Samuel','1 Kings','2 Kings')
TORAH_BOOKS=PRIMARY_BOOKS[:5]

@dataclass
class Corpus:
    books: list[Book]
    root: str | None=None
    def __iter__(self): return iter(self.books)
    def __repr__(self): return f'<Corpus {len(self.books)} books, {len(self.verses)} verses>'
    @property
    def verses(self): return Verses(v for b in self.books for v in b.verses)
    def book(self,name):
        key=name.casefold().replace(' ','')
        for b in self.books:
            if b.name.casefold().replace(' ','')==key: return b
        raise KeyError(name)
    def subset(self, books=None):
        if books is None: books=PRIMARY_BOOKS
        wanted={x.casefold().replace(' ','') for x in books}
        return Verses(v for b in self.books if b.name.casefold().replace(' ','') in wanted for v in b.verses)
    def grep(self, query, *, language='english', regex=False, case=False, niqqud=None, spaces=None, matres=None, sources=None):
        from .search import grep
        return grep(self.verses,query,language=language,regex=regex,case=case,niqqud=niqqud,spaces=spaces,matres=matres,sources=sources)
    def english(self,q,**kw): return self.grep(q,language='english',**kw)
    def hebrew(self,q,**kw): return self.grep(q,language='hebrew',**kw)
    def frequency(self, language='english', *, books=None, **kw): return self.subset(books).frequency(language,**kw)
    def evidence(self,text,*,language='hebrew',training_books=TORAH_BOOKS,**kw):
        from .evidence import train
        return train(self,language=language,books=training_books,**kw).score(text)
    def to_jsonl(self,path):
        import gzip
        opener=gzip.open if str(path).endswith('.gz') else open
        with opener(path,'wt',encoding='utf8') as f:
            for v in self.verses: f.write(json.dumps(v.to_dict(),ensure_ascii=False)+'\n')
    @classmethod
    def from_jsonl(cls,path):
        import gzip
        opener=gzip.open if str(path).endswith('.gz') else open
        vs=[]
        with opener(path,'rt',encoding='utf8') as f:
            for line in f:
                if line.strip(): vs.append(Verse.from_dict(json.loads(line)))
        return corpus_from_verses(vs,root=str(path))

def corpus_from_verses(vs,root=None):
    books=[]; bmap={}
    for v in vs:
        if v.book not in bmap:
            b=Book(v.book); books.append(b); bmap[v.book]=b
        b=bmap[v.book]
        if not b.chapters or b.chapters[-1].number != v.chapter: b.chapters.append(Chapter(v.book,v.chapter))
        b.chapters[-1].verses.append(v)
    return Corpus(books,root=root)
