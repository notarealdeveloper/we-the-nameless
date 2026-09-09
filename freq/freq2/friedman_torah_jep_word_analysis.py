#!/usr/bin/env python3
"""Reproduce the core J/E/P word metrics from words.txt."""
import re, math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import chi2

inp = Path("words.txt")
pat = re.compile(r'^([jep])\[(.*)\] = (\d+)$', re.M)
rows = {}
for s,w,c in pat.findall(inp.read_text()):
    rows.setdefault(w,{})[s] = int(c)
df = pd.DataFrame([(w,d["j"],d["e"],d["p"]) for w,d in rows.items()],
                  columns=["word","j_count","e_count","p_count"])
Ns = {s:int(df[f"{s}_count"].sum()) for s in "jep"}
N = sum(Ns.values())
q = {s:Ns[s]/N for s in "jep"}
df["total_count"] = df[["j_count","e_count","p_count"]].sum(axis=1)
for s in "jep":
    df[f"{s}_share"] = df[f"{s}_count"]/df.total_count
    df[f"{s}_rate_per_10k"] = df[f"{s}_count"]/Ns[s]*10000
    p_adj = (df[f"{s}_count"]+0.5)/(df.total_count+1.5)
    df[f"{s}_log2_enrichment"] = np.log2(p_adj/q[s])
    x=df[f"{s}_share"].astype(float)
    kl=np.zeros(len(df))
    m=x>0; kl[m]+=x[m]*np.log2(x[m]/q[s])
    m=x<1; kl[m]+=(1-x[m])*np.log2((1-x[m])/(1-q[s]))
    df[f"{s}_signed_info_bits"]=np.where(x>=q[s],1,-1)*df.total_count*kl
    cs=df[f"{s}_count"].astype(float); cr=df.total_count-cs
    Nr=N-Ns[s]
    df[f"{s}_woe_bits"]=np.log2(((cs+0.5)/(Ns[s]-cs+0.5))/((cr+0.5)/(Nr-cr+0.5)))
info=np.zeros(len(df))
for s in "jep":
    x=df[f"{s}_share"]; m=x>0
    info[m]+=df.loc[m,f"{s}_count"]*np.log2(x[m]/q[s])
df["global_surprise_bits"]=info
df["g2"]=2*np.log(2)*info
df["p_value"]=chi2.sf(df.g2,2)
order=np.argsort(df.p_value.to_numpy())
pv=df.p_value.to_numpy()[order]; M=len(pv)
qq=np.minimum.accumulate((pv*M/np.arange(1,M+1))[::-1])[::-1]
qout=np.empty(M); qout[order]=np.clip(qq,0,1)
df["q_value"]=qout
df.to_csv("friedman_torah_jep_word_metrics_core.csv",index=False)
