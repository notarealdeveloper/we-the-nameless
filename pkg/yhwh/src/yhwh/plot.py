from __future__ import annotations

def frequency(freq,n=30,ax=None,title=None):
    import matplotlib.pyplot as plt
    if ax is None: _,ax=plt.subplots()
    rows=freq.most_common(n); labels=[x for x,_ in rows][::-1]; vals=[y for _,y in rows][::-1]
    ax.barh(labels,vals); ax.set_xlabel('count'); ax.set_title(title or repr(freq)); return ax

def sources(source_freqs,word,ax=None):
    import matplotlib.pyplot as plt
    if ax is None: _,ax=plt.subplots()
    labels=list(source_freqs); vals=[source_freqs[s][word] for s in labels]
    ax.bar(labels,vals); ax.set_ylabel('count'); ax.set_title(str(word)); return ax

def evidence(result,ax=None):
    import matplotlib.pyplot as plt
    if ax is None: _,ax=plt.subplots()
    labels=list(result.posteriors); vals=[result.posteriors[s] for s in labels]
    ax.bar(labels,vals); ax.set_ylim(0,1); ax.set_ylabel('posterior probability'); return ax
