from __future__ import annotations
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

def gray(im: Image.Image)->Image.Image: return ImageOps.grayscale(im)
def threshold(a: np.ndarray,t: np.ndarray|float)->Image.Image: return Image.fromarray(np.where(a<t,0,255).astype("uint8"),"L")
def otsu(a: np.ndarray)->int:
    hist=np.bincount(a.ravel(),minlength=256).astype(float); total=a.size; sum_all=np.dot(np.arange(256),hist)
    wb=0.; sb=0.; best=0.; level=127
    for i,n in enumerate(hist):
        wb+=n
        if wb==0: continue
        wf=total-wb
        if wf==0: break
        sb+=i*n; score=wb*wf*((sb/wb)-((sum_all-sb)/wf))**2
        if score>best: best=score; level=i
    return level
def adaptive(a:np.ndarray, radius=15, bias=8)->Image.Image:
    mean=np.asarray(Image.fromarray(a).filter(ImageFilter.BoxBlur(radius)),dtype=float)
    return threshold(a,mean-bias)
def components(mask: Image.Image)->list[dict]:
    a=np.asarray(mask)<128; h,w=a.shape; seen=np.zeros_like(a,bool); out=[]
    for y,x in zip(*np.where(a & ~seen)):
        if seen[y,x]: continue
        stack=[(int(x),int(y))]; seen[y,x]=1; pts=[]
        while stack:
            px,py=stack.pop(); pts.append((px,py))
            for nx,ny in ((px-1,py),(px+1,py),(px,py-1),(px,py+1)):
                if 0<=nx<w and 0<=ny<h and a[ny,nx] and not seen[ny,nx]: seen[ny,nx]=1; stack.append((nx,ny))
        xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
        out.append({"id":f"c{len(out)+1:03}","bbox":[min(xs),min(ys),max(xs)+1,max(ys)+1],"area":len(pts),"pixels":pts})
    return sorted(out,key=lambda c:c["area"],reverse=True)
def contact(items:list[tuple[str,Image.Image]], path:Path, cols=4, cell=(320,260))->None:
    rows=max(1,math.ceil(len(items)/cols)); sheet=Image.new("RGB",(cols*cell[0],rows*cell[1]),"white"); d=ImageDraw.Draw(sheet)
    for i,(label,im) in enumerate(items):
        x=(i%cols)*cell[0]; y=(i//cols)*cell[1]; thumb=im.convert("RGB"); thumb.thumbnail((cell[0]-20,cell[1]-45))
        sheet.paste(thumb,(x+10,y+30)); d.text((x+8,y+7),label,fill="black")
    path.parent.mkdir(parents=True,exist_ok=True); sheet.save(path)
def bbox_ink(im:Image.Image)->tuple[int,int,int,int]|None:
    a=np.asarray(gray(im))<220; ys,xs=np.where(a)
    return None if len(xs)==0 else (int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1))
