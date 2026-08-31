#!/usr/bin/env python3
"""Plot selected terms in Exodus 28–40 and the Torah by documentary source."""
from __future__ import annotations
import argparse, math, re, unicodedata
from collections import Counter
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "exodus-28-40-p-niqqud-counts.md"
OUTPUT = ROOT / "img/plots/exodus-28-40-word-counts"
TORAH = [ROOT / x for x in ("01-genesis", "02-exodus", "03-leviticus", "04-numbers", "05-deuteronomy")]
CHAPTERS = {28:("P",),29:("P",),30:("P",),31:("P",),32:("E",),33:("E",),34:("J","P"),35:("P",),36:("P",),37:("P",),38:("P",),39:("P",),40:("P",)}
SUMMARIES = {28:"Priest clothes",29:"Priests installed",30:"Incense; census; oil",31:"Bezalel; Sabbath",32:"Golden calf",33:"Tent; God's back",34:"New tablets",35:"Work begins",36:"Tabernacle built",37:"Ark; furniture made",38:"Altar; courtyard; inventory",39:"Priest clothes done",40:"Tabernacle complete"}
COLORS = ["#C79A2B","#285F8F","#B33A3A","#68458C","#E0B94B","#4E83AD","#D35B4F","#8A68A6","#9B7419","#173E63","#A52F32","#593473","#D6A928","#3975A3"]
PATTERNS = {"holy":r"hol(?:y|ies|iness)","congregation":r"congregations?","chieftain":r"chieftains?","command":r"command(?:ed)?","Tabernacle":r"Tabernacles?"}
ADDED = ["congregation", "chieftain", "command", "Tabernacle"]

def selected_words(limit=10):
    totals = Counter()
    for line in TABLE.read_text(encoding="utf-8").splitlines():
        cells = [x.strip() for x in line.strip("|").split("|")]
        if line.startswith("|") and "---" not in line and len(cells)==16 and cells[14].isdigit() and cells[0] != "Tent of Meeting":
            word = "holy" if cells[0].lower() in {"holy","holies","holiness"} else cells[0]
            totals[word] += int(cells[14])
    words = [x for x,_ in totals.most_common(limit)]
    return words + [x for x in ADDED if x not in words]

def macro_contents(text, source):
    out = []
    for match in re.finditer(r"\\e([A-Z]+)\{", text):
        if source not in match.group(1): continue
        start=match.end(); cursor=start; depth=1
        while cursor < len(text) and depth:
            if text[cursor]=="{" and text[cursor-1]!="\\": depth += 1
            elif text[cursor]=="}" and text[cursor-1]!="\\": depth -= 1
            cursor += 1
        if depth: raise ValueError(f"Unbalanced source macro near {match.start()}")
        out.append(text[start:cursor-1])
    return out

def plain(text):
    return "".join(c for c in unicodedata.normalize("NFD",text) if not 0x0591 <= ord(c) <= 0x05C7)

def word_count(text, word):
    pattern = PATTERNS.get(word,re.escape(word))
    suffix = r"(?:['\u2019]s)?" if word=="Aaron" else ""
    return len(re.findall(rf"(?<![A-Za-z])(?:{pattern}){suffix}(?![A-Za-z])",plain(text),re.I))

def counts(text, source, words):
    source_text = "\n".join(macro_contents(text,source))
    return [word_count(source_text,w) for w in words]

def percentages(chapters):
    shares=Counter({s:0.0 for s in "JEP"}); n=0
    for chapter in chapters:
        text=(ROOT/f"02-exodus/{chapter:02}.tex").read_text(encoding="utf-8")
        for verse in re.split(r"(?=\\Verse\{\d+\})",text)[1:]:
            tags=re.findall(r"\\e([A-Z]+)\{",verse)
            sources={s for s in "JEP" if any(s in tag for tag in tags)}
            if sources:
                n += 1
                for s in sources: shares[s] += 1/len(sources)
    return "  ".join(f"{s}: {100*shares[s]/n:.1f}%" for s in "JEP")

def style(ax,ymax=None):
    if ymax is not None: ax.set_ylim(0,ymax)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.tick_params(axis="x",labelrotation=35)
    for label in ax.get_xticklabels(): label.set_ha("right")

def bars(ax,words,values):
    palette=[COLORS[i%len(COLORS)] for i in range(len(words))]
    sns.barplot(x=words,y=values,hue=words,palette=palette,legend=False,ax=ax)
    ax.set(xlabel="",ylabel="Appearances")
    ax.legend(handles=[Patch(facecolor=palette[i],label=w) for i,w in enumerate(words)],title="Words",loc="upper left",bbox_to_anchor=(1.01,1),frameon=True)

def chapter_plot(chapter,source,words):
    text=(ROOT/f"02-exodus/{chapter:02}.tex").read_text(encoding="utf-8")
    fig,ax=plt.subplots(figsize=(15,8)); bars(ax,words,counts(text,source,words)); style(ax,20)
    ax.set_title(SUMMARIES[chapter],fontsize=17,pad=10)
    ax.text(.01,.98,percentages([chapter]),transform=ax.transAxes,va="top",fontsize=12)
    fig.suptitle(f"Exodus {chapter}",fontsize=23,y=.99); fig.tight_layout(rect=(0,0,1,.94))
    fig.savefig(OUTPUT/f"exodus-{chapter:02}-{source.lower()}.png",dpi=200,bbox_inches="tight"); plt.close(fig)

def source_totals(files,words):
    result={s:[0]*len(words) for s in "JEP"}
    for path in files:
        text=path.read_text(encoding="utf-8")
        for s in "JEP": result[s]=[a+b for a,b in zip(result[s],counts(text,s,words))]
    return result

def stacked(words,totals,scope,filename):
    ymax=max(1,math.ceil(max(totals["P"])/10)*10)
    fig,axes=plt.subplots(3,1,figsize=(15,21),sharex=True,sharey=True)
    for ax,s in zip(axes,"JEP"):
        bars(ax,words,totals[s]); style(ax,ymax); ax.set_title(s,fontsize=19,pad=8)
    axes[-1].tick_params(axis="x",labelbottom=True)
    fig.suptitle(f"All selected terms: {scope}",fontsize=24,y=.995); fig.tight_layout(rect=(0,0,1,.98))
    fig.savefig(OUTPUT/filename,dpi=200,bbox_inches="tight"); plt.close(fig)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--limit",type=int,default=10,choices=range(5,11)); args=parser.parse_args()
    sns.set_theme(context="talk",style="whitegrid",rc={"axes.facecolor":"#FBF8F0","figure.facecolor":"#FBF8F0","grid.color":"#DDD4C2","axes.edgecolor":"#5C554B","text.color":"#29251F"})
    OUTPUT.mkdir(parents=True,exist_ok=True); words=selected_words(args.limit)
    for chapter,sources in CHAPTERS.items():
        for source in sources: chapter_plot(chapter,source,words)
    exodus=[ROOT/f"02-exodus/{c:02}.tex" for c in CHAPTERS]
    stacked(words,source_totals(exodus,words),"Exodus 28–40","exodus-28-40-source-totals.png")
    torah=sorted(p for d in TORAH for p in d.glob("[0-9][0-9].tex"))
    stacked(words,source_totals(torah,words),"the whole Torah","torah-source-totals.png")
    print(f"Plotted {', '.join(words)}"); print(f"Wrote {sum(map(len,CHAPTERS.values()))+2} figures")
if __name__=="__main__": main()
