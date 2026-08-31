#!/usr/bin/env python3
"""Plot selected terms in Exodus 28–40 and the Torah by documentary source."""
from __future__ import annotations
import argparse, math, re, unicodedata
from collections import Counter
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator, MultipleLocator
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "exodus-28-40-p-niqqud-counts.md"
OUTPUT = ROOT / "img/plots/exodus-28-40-word-counts"
TORAH = [ROOT / x for x in ("01-genesis", "02-exodus", "03-leviticus", "04-numbers", "05-deuteronomy")]
CHAPTERS = {28:("P",),29:("P",),30:("P",),31:("P",),32:("E",),33:("E",),34:("J","P"),35:("P",),36:("P",),37:("P",),38:("P",),39:("P",),40:("P",)}
SUMMARIES = {28:"Priest clothes",29:"Priests installed",30:"Incense; census; oil",31:"Bezalel; Sabbath",32:"Golden calf",33:"Tent; God's back",34:"New tablets",35:"Work begins",36:"Tabernacle built",37:"Ark; furniture made",38:"Altar; courtyard; inventory",39:"Priest clothes done",40:"Tabernacle complete"}
COLORS = ["#C79A2B","#285F8F","#B33A3A","#68458C","#E0B94B","#4E83AD","#D35B4F","#8A68A6","#9B7419","#173E63","#A52F32","#593473","#D6A928","#3975A3"]
PATTERNS = {
    "holy": r"hol(?:y|ies|iness)",
    "bases": r"bases?",
    "offering": r"offerings?",
    "chieftain": r"chieftains?",
    "command": r"command(?:s|ed|ing)?",
    "according to": r"according\s+to",
}
# Especially stark P vocabulary in Exodus 28–40 (P/J/E counts respectively):
# bases 30/0/0, offering 29/0/0, bronze 26/0/0, equipment 21/0/0.
P_SKEWED = ["bases", "offering", "bronze", "equipment"]

def selected_words(limit=10):
    totals = Counter()
    for line in TABLE.read_text(encoding="utf-8").splitlines():
        cells = [x.strip() for x in line.strip("|").split("|")]
        if line.startswith("|") and "---" not in line and len(cells)==16 and cells[14].isdigit() and cells[0] != "Tent of Meeting":
            word = "holy" if cells[0].lower() in {"holy","holies","holiness"} else cells[0]
            totals[word] += int(cells[14])
    words = [x for x,_ in totals.most_common(limit)]
    return words + [x for x in P_SKEWED if x not in words]

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

def style(ax,ymax=None,tick_step=5):
    if ymax is not None:
        ax.set_ylim(0,ymax)
    else:
        ax.set_ylim(bottom=0)
    if tick_step is None:
        ax.yaxis.set_major_locator(MaxNLocator(nbins=8,integer=True,min_n_ticks=5))
    else:
        ax.yaxis.set_major_locator(MultipleLocator(tick_step))
    ax.tick_params(axis="x",labelrotation=35)
    for label in ax.get_xticklabels(): label.set_ha("right")

def legend_handles(words):
    palette=[COLORS[i%len(COLORS)] for i in range(len(words))]
    return [Patch(facecolor=palette[i],label=w) for i,w in enumerate(words)]

def bars(ax,words,values,legend=True):
    palette=[COLORS[i%len(COLORS)] for i in range(len(words))]
    sns.barplot(x=words,y=values,hue=words,palette=palette,legend=False,ax=ax)
    ax.set(xlabel="",ylabel="Appearances")
    if legend:
        ax.legend(handles=legend_handles(words),title="Words",loc="upper left",bbox_to_anchor=(1.01,1),frameon=True)

def chapter_plot(chapter,source,words,variable_y=False):
    text=(ROOT/f"02-exodus/{chapter:02}.tex").read_text(encoding="utf-8")
    fig,ax=plt.subplots(figsize=(15,8)); bars(ax,words,counts(text,source,words)); style(ax,None if variable_y else 20)
    ax.text(.99,.98,percentages([chapter]),transform=ax.transAxes,ha="right",va="top",fontsize=12)
    fig.suptitle(f"Exodus {chapter}",fontsize=23,y=.995)
    fig.text(.5,.945,SUMMARIES[chapter],ha="center",va="top",fontsize=17)
    fig.tight_layout(rect=(0,0,1,.89))
    suffix="-y-axis-variable" if variable_y else ""
    fig.savefig(OUTPUT/f"exodus-{chapter:02}-{source.lower()}{suffix}.png",dpi=200,bbox_inches="tight"); plt.close(fig)

def source_totals(files,words):
    result={s:[0]*len(words) for s in "JEP"}
    for path in files:
        text=path.read_text(encoding="utf-8")
        for s in "JEP": result[s]=[a+b for a,b in zip(result[s],counts(text,s,words))]
    return result

def stacked(words,totals,scope,filename,auto_ticks=False):
    ymax=max(5,math.ceil(max(totals["P"])/5)*5)
    fig,axes=plt.subplots(3,1,figsize=(17,23),sharex=True,sharey=True)
    for ax,s in zip(axes,"JEP"):
        bars(ax,words,totals[s],legend=False); style(ax,ymax,None if auto_ticks else 5); ax.set_title(s,fontsize=19,pad=8)
        ax.tick_params(axis="x",labelbottom=True)
    fig.legend(handles=legend_handles(words),title="Words",loc="center left",bbox_to_anchor=(.89,.5),frameon=True)
    fig.suptitle(f"All selected terms: {scope}",fontsize=24,y=.995)
    fig.subplots_adjust(left=.08,right=.87,bottom=.08,top=.95,hspace=.42)
    fig.savefig(OUTPUT/filename,dpi=200,bbox_inches="tight"); plt.close(fig)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--limit",type=int,default=10,choices=range(5,11))
    parser.add_argument("--whole-torah-variants-only",action="store_true",
                        help="write only the supplemental whole-Torah figures")
    args=parser.parse_args()
    sns.set_theme(context="talk",style="whitegrid",rc={"axes.facecolor":"#FBF8F0","figure.facecolor":"#FBF8F0","grid.color":"#DDD4C2","axes.edgecolor":"#5C554B","text.color":"#29251F"})
    OUTPUT.mkdir(parents=True,exist_ok=True); words=selected_words(args.limit)
    torah=sorted(p for d in TORAH for p in d.glob("[0-9][0-9].tex"))
    if not args.whole_torah_variants_only:
        # Preserve the existing fixed-height chapter figures and add adaptive versions.
        for chapter,sources in CHAPTERS.items():
            for source in sources: chapter_plot(chapter,source,words,variable_y=True)
        exodus=[ROOT/f"02-exodus/{c:02}.tex" for c in CHAPTERS]
        stacked(words,source_totals(exodus,words),"Exodus 28–40","exodus-28-40-source-totals.png")
        stacked(words,source_totals(torah,words),"the whole Torah","torah-source-totals.png",auto_ticks=True)

    reduced_words=[word for word in words if word not in {"holy","Aaron","offering"}]
    expanded_words=words + [word for word in ("chieftain","command","according to") if word not in words]
    stacked(reduced_words,source_totals(torah,reduced_words),
            "the whole Torah (excluding holy, Aaron, and offering)",
            "torah-source-totals-without-holy-aaron-offering.png",auto_ticks=True)
    stacked(expanded_words,source_totals(torah,expanded_words),
            "the whole Torah (with chieftain, command, and according to)",
            "torah-source-totals-with-chieftain-command-according-to.png",auto_ticks=True)
    print(f"Base terms: {', '.join(words)}")
    print("Wrote 2 supplemental whole-Torah figures" if args.whole_torah_variants_only
          else f"Wrote {sum(map(len,CHAPTERS.values()))+4} figures")
if __name__=="__main__": main()
