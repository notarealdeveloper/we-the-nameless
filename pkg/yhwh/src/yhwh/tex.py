"""Parser for the project's source-tagged TeX. Independent from search/statistics."""
from __future__ import annotations
from pathlib import Path
import re
from .model import Verse, SourceSpan, corpus_from_verses

BOOK_DIRS={'01-genesis':'Genesis','02-exodus':'Exodus','03-leviticus':'Leviticus','04-numbers':'Numbers','05-deuteronomy':'Deuteronomy',
'06-joshua':'Joshua','07-judges':'Judges','08-samuel':'Samuel','09-kings':'Kings'}
SOURCE_PREFIXES=('h','e')
# Formatting commands whose contents are text, not source labels.
FORMAT_COMMANDS={'emph','textit','textbf','textsc','underline','heb','egypt','redacted','sout','textsuperscript','mbox','hbox','makebox'}
DROP_COMMANDS={'nl','par','newline','smallskip','medskip','bigskip'}

def _balanced(s,i):
    # i points to {
    depth=0; j=i
    while j<len(s):
        if s[j]=='\\': j+=2; continue
        if s[j]=='{': depth+=1
        elif s[j]=='}':
            depth-=1
            if depth==0: return s[i+1:j],j+1
        j+=1
    raise ValueError(f'unbalanced brace at offset {i}')

def _strip_comments(s):
    return re.sub(r'(?<!\\)%[^\n]*','',s)

def latex_to_text(s):
    s=_strip_comments(s).replace('~',' ')
    # common typographic commands / escaped chars
    s=s.replace('``','“').replace("''",'”').replace('---','—').replace('--','–')
    s=re.sub(r'\\(?:nl|par|newline)\b', ' ', s)
    # repeatedly unwrap one-argument formatting commands
    pat=re.compile(r'\\([A-Za-z]+)\s*\{')
    out=[]; i=0
    while i<len(s):
        m=pat.search(s,i)
        if not m: out.append(s[i:]); break
        out.append(s[i:m.start()])
        cmd=m.group(1); content,end=_balanced(s,m.end()-1)
        if cmd in FORMAT_COMMANDS or cmd.startswith(('text','hl')):
            out.append(latex_to_text(content))
        else:
            # Unknown wrapper inside a source span: retain its textual payload.
            out.append(latex_to_text(content))
        i=end
    text=''.join(out)
    text=re.sub(r'\\[A-Za-z@]+\*?(?:\[[^\]]*\])?', '', text)
    text=text.replace('\\%','%').replace('\\&','&').replace('\\_','_').replace('\\{','{').replace('\\}','}')
    text=re.sub(r'\s+',' ',text).strip()
    return text

def _source_spans(group, lang):
    prefix='h' if lang=='hebrew' else 'e'
    spans=[]; text_parts=[]; pos=0; i=0
    pat=re.compile(r'\\([he])([A-Z][A-Za-z0-9]*)\s*\{')
    while True:
        m=pat.search(group,i)
        if not m: break
        if m.group(1)!=prefix:
            i=m.end(); continue
        raw=m.group(2)
        content,end=_balanced(group,m.end()-1)
        txt=latex_to_text(content)
        if txt:
            if text_parts and not (text_parts[-1].endswith((' ','\n')) or txt.startswith((' ','.',',',';',':','!','?','”','׃'))):
                text_parts.append(' '); pos+=1
            start=pos; text_parts.append(txt); pos+=len(txt)
            spans.append(SourceSpan(raw,txt,start,pos,raw_source=raw))
        i=end
    return ''.join(text_parts).strip(),spans

def parse_tex_text(text, *, book='Unknown', chapter=None, path=None):
    text=_strip_comments(text)
    cm=re.search(r'\\Chapter\s*\{([^}]+)\}',text)
    if chapter is None: chapter=int(cm.group(1)) if cm and cm.group(1).isdigit() else 0
    # A few editorial files contain an explicitly reproduced second copy of a chapter.
    # A chapter file represents its first chapter block for corpus purposes.
    if cm:
        next_ch=re.search(r'\\Chapter\s*\{', text[cm.end():])
        if next_ch: text=text[:cm.end()+next_ch.start()]
    verses=[]; i=0; vr=re.compile(r'\\Verse\s*\{([^}]+)\}')
    while True:
        m=vr.search(text,i)
        if not m: break
        num=m.group(1).strip(); p=m.end()
        groups=[]
        for _ in range(2):
            ws=re.match(r'\s*',text[p:]); p+=ws.end()
            if p>=len(text) or text[p]!='{': break
            g,p=_balanced(text,p); groups.append(g)
        if len(groups)>=2:
            h,hs=_source_spans(groups[0],'hebrew'); e,es=_source_spans(groups[1],'english')
            verses.append(Verse(book,chapter,num,h,e,hs,es,str(path) if path else None))
        i=p
    return verses

def _book_from_path(p,root):
    rel=p.relative_to(root); d=rel.parts[0].lower()
    base=BOOK_DIRS.get(d,d.split('-',1)[-1].replace('-',' ').title())
    if d in {'08-samuel','09-kings'}:
        stem=p.stem
        part=stem.split('-',1)[0] if '-' in stem else '1'
        base=f'{part} {base}'
    return base

def discover_tex(root):
    root=Path(root)
    paths=[]
    for p in root.rglob('*.tex'):
        # chapter files only: numeric or 1-01 / 2-01; skip raw/apocrypha/build artifacts
        if re.fullmatch(r'(?:[12]-)?\d{2}',p.stem): paths.append(p)
    def key(p):
        rel=p.relative_to(root); parts=rel.parts
        nums=[int(x) for x in re.findall(r'\d+',parts[0]+'-'+p.stem)]
        return nums
    return sorted(paths,key=key)

def parse_directory(root):
    root=Path(root); vs=[]
    for p in discover_tex(root):
        book=_book_from_path(p,root)
        nums=re.findall(r'\d+',p.stem); chapter=int(nums[-1])
        vs.extend(parse_tex_text(p.read_text(encoding='utf8',errors='replace'),book=book,chapter=chapter,path=p))
    return corpus_from_verses(vs,root=str(root))
