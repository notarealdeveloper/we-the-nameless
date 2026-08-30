#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import random
out=Path(__file__).parent/"fixtures"/"synthetic-chart.png"; out.parent.mkdir(parents=True,exist_ok=True)
im=Image.new("RGB",(1800,620),"#eee9dc"); d=ImageDraw.Draw(im); random.seed(7)
d.text((45,20),"SYNTHETIC ALPHABET PLATE — labels are not glyphs",fill="#333")
for i in range(22):
 x=40+i%11*158; y=80+i//11*250; d.rectangle((x,y,x+140,y+225),outline="#aaa",width=2)
 cx=x+70+random.randint(-8,8); cy=y+100+random.randint(-8,8); s=38+random.randint(-5,7)
 # one deliberately disconnected, asymmetric pseudo-sign per cell
 d.line((cx-s,cy+s,cx,cy-s,cx+s,cy+s),fill="#17130e",width=random.randint(8,14))
 d.line((cx-s//2,cy,cx+s//2,cy+random.randint(-7,7)),fill="#17130e",width=9)
 if i%4==0: d.ellipse((cx+s+8,cy-s,cx+s+18,cy-s+10),fill="#17130e")
 d.text((x+8,y+195),f"label {i+1:02}",fill="#555")
for _ in range(120):
 x=random.randrange(im.width); y=random.randrange(im.height); d.point((x,y),fill="#999")
im.rotate(.45,resample=Image.Resampling.BICUBIC,expand=False,fillcolor="#eee9dc").save(out,dpi=(300,300))
print(out)
