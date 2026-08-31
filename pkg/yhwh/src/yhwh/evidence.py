"""Long-tail multinomial lexical evidence for source attribution."""
from __future__ import annotations
from dataclasses import dataclass
from collections import Counter
import math
from .normalize import words, hebrew_words
from .sources import CANONICAL_DEFAULT, canonical_source

@dataclass
class EvidenceResult:
    posteriors: dict[str,float]
    log_scores: dict[str,float]
    contributions: dict[str,list[tuple[str,float]]]
    tokens: list[str]
    training_tokens: dict[str,int]
    @property
    def best(self): return max(self.posteriors,key=self.posteriors.get)
    def __repr__(self): return '<Evidence ' + ' '.join(f'{k}={v:.3f}' for k,v in sorted(self.posteriors.items(),key=lambda x:-x[1])) + '>'
    def table(self): return [{'source':s,'posterior':p,'log_score':self.log_scores[s],'training_tokens':self.training_tokens[s]} for s,p in sorted(self.posteriors.items(),key=lambda x:-x[1])]

@dataclass
class EvidenceModel:
    counts: dict[str,Counter]
    language: str='hebrew'; alpha: float=.5
    def __post_init__(self):
        self.totals={s:sum(c.values()) for s,c in self.counts.items()}; self.vocab=set().union(*(c.keys() for c in self.counts.values()))
    def _tokens(self,text): return hebrew_words(text) if self.language.startswith('h') else words(text)
    def score(self,text):
        toks=self._tokens(text); V=max(1,len(self.vocab)); total_train=sum(self.totals.values())
        scores={}; contrib={}
        for s,c in self.counts.items():
            # empirical source prior; lexical evidence remains dominant as text grows
            prior=math.log((self.totals[s]+1)/(total_train+len(self.counts)))
            denom=self.totals[s]+self.alpha*V
            vals=[]; score=prior
            for w in toks:
                val=math.log((c[w]+self.alpha)/denom); score+=val; vals.append((w,val))
            scores[s]=score; contrib[s]=vals
        m=max(scores.values()); ex={s:math.exp(x-m) for s,x in scores.items()}; z=sum(ex.values())
        return EvidenceResult({s:x/z for s,x in ex.items()},scores,contrib,toks,self.totals)

def train(corpus, *, language='hebrew', books=('Genesis','Exodus','Leviticus','Numbers','Deuteronomy'), sources=CANONICAL_DEFAULT, alpha=.5):
    wanted=set(sources); counts={s:Counter() for s in sources}; attr='hebrew_spans' if language.startswith('h') else 'english_spans'
    for v in corpus.subset(books):
        for sp in getattr(v,attr):
            s=canonical_source(sp.source)
            if s not in wanted: continue
            toks=hebrew_words(sp.text) if language.startswith('h') else words(sp.text)
            counts[s].update(toks)
    # Keep requested classes, but omit classes with no training text rather than emit fake evidence.
    counts={s:c for s,c in counts.items() if c}
    if len(counts)<2: raise ValueError('need at least two nonempty source classes')
    return EvidenceModel(counts,language,alpha)
