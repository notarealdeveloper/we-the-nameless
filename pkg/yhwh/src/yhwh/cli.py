from __future__ import annotations
import argparse,json
from . import load,clean_cache,word_by_source,train

def _corpus(args): return load(args.data)
def main(argv=None):
    p=argparse.ArgumentParser(prog='yhwh',description='Source-aware Hebrew Bible lexical analysis')
    p.add_argument('--data',help='corpus directory or generated JSONL[.gz] (also YHWH_DATA_DIR)')
    sub=p.add_subparsers(dest='cmd',required=True)
    g=sub.add_parser('grep'); g.add_argument('query'); g.add_argument('-l','--language',choices=['english','hebrew'],default='english'); g.add_argument('-r','--regex',action='store_true'); g.add_argument('--spaces',action='store_true'); g.add_argument('--niqqud',action='store_true'); g.add_argument('--source',action='append'); g.add_argument('--matres',choices=['internal','all'])
    f=sub.add_parser('freq'); f.add_argument('-l','--language',choices=['english','hebrew'],default='english'); f.add_argument('--book',action='append'); f.add_argument('--source',action='append'); f.add_argument('-n',type=int,default=30); f.add_argument('--json',action='store_true')
    w=sub.add_parser('word'); w.add_argument('word'); w.add_argument('-l','--language',choices=['english','hebrew'],default='english'); w.add_argument('--book',action='append')
    e=sub.add_parser('evidence'); e.add_argument('text'); e.add_argument('-l','--language',choices=['english','hebrew'],default='hebrew'); e.add_argument('--alpha',type=float,default=.5); e.add_argument('--json',action='store_true')
    d=sub.add_parser('dataset'); d.add_argument('output')
    sub.add_parser('cache-clean')
    a=p.parse_args(argv)
    if a.cmd=='cache-clean': clean_cache(); return 0
    c=_corpus(a)
    if a.cmd=='grep':
        vs=c.grep(a.query,language=a.language,regex=a.regex,spaces=a.spaces if a.language=='hebrew' else True,niqqud=a.niqqud if a.language=='hebrew' else None,sources=a.source,matres=a.matres)
        for v in vs: print(f'{v.reference}\t{",".join(v.sources)}\t{v.hebrew if a.language=="hebrew" else v.english}')
    elif a.cmd=='freq':
        fr=c.frequency(a.language,books=a.book,by_source=bool(a.source),sources=a.source)
        if a.source:
            obj={s:dict(x.most_common(a.n)) for s,x in fr.items()}
        else: obj=dict(fr.most_common(a.n))
        print(json.dumps(obj,ensure_ascii=False,indent=2) if a.json else '\n'.join(f'{k}\t{v}' for k,v in obj.items()))
    elif a.cmd=='word': print(json.dumps(word_by_source(c.subset(a.book),a.word,language=a.language),ensure_ascii=False,indent=2))
    elif a.cmd=='evidence':
        r=train(c,language=a.language,alpha=a.alpha).score(a.text); print(json.dumps(r.table(),ensure_ascii=False,indent=2) if a.json else repr(r))
    elif a.cmd=='dataset': c.to_jsonl(a.output)
    return 0
if __name__=='__main__': raise SystemExit(main())
