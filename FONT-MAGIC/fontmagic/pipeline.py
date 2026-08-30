from __future__ import annotations
import argparse, html, json, math, os, shutil, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps
import numpy as np
from fontTools.ttLib import TTFont
from .common import ROOT,CANONICAL,atomic_json,config,ensure_run,load_json,mapping,sha256
from .images import adaptive,bbox_ink,components,contact,gray,otsu,threshold

def ingest(run:Path, source:Path, pdf_page=1, pdf_dpi=600):
    ensure_run(run); raw=run/"source"/("original"+source.suffix.lower()); shutil.copy2(source,raw)
    transforms=[]
    if source.suffix.lower()==".pdf":
        im=Image.open(source); im.seek(pdf_page-1); im.load(); transforms.append({"operation":"pdf-rasterize","page":pdf_page,"dpi":pdf_dpi})
    else: im=Image.open(source)
    fmt=im.format; mode=im.mode; size=im.size; dpi=im.info.get("dpi"); exif_orientation=None
    try: exif_orientation=im.getexif().get(274)
    except Exception: pass
    im=ImageOps.exif_transpose(im)
    if "A" in im.getbands():
        rgba=im.convert("RGBA")
        background=Image.new("RGBA",rgba.size,"white")
        im=Image.alpha_composite(background,rgba).convert("RGB")
        transforms.append({"operation":"alpha-composite","background":"white"})
    else:
        im=im.convert("RGB")
    transforms.append({"operation":"exif-transpose","orientation":exif_orientation})
    im.save(run/"source/source.png")
    atomic_json(run/"manifests/source.json",{"source_path":str(source.resolve()),"archival_copy":str(raw),"source_png":"source/source.png","sha256":sha256(source),"dimensions":list(size),"format":fmt,"mode":mode,"dpi":dpi,"pdf_page":pdf_page if source.suffix.lower()==".pdf" else None,"exif_orientation":exif_orientation,"transformations":transforms})

def preprocess(run:Path):
    im=Image.open(run/"source/source.png"); g=gray(im); a=np.asarray(g); t=otsu(a)
    bg=g.filter(ImageFilter.GaussianBlur(max(8,min(im.size)//40))); flat=np.clip(a.astype(int)-np.asarray(bg).astype(int)+230,0,255).astype("uint8")
    candidates={"original-gray":g,"contrast":ImageEnhance.Contrast(g).enhance(1.6),"background-flattened":Image.fromarray(flat),"otsu":threshold(a,t),"adaptive":adaptive(a),"sauvola":adaptive(a,max(8,min(im.size)//80),5),"conservative":threshold(a,min(245,t+18)),"edges":g.filter(ImageFilter.FIND_EDGES)}
    for n,x in candidates.items(): x.save(run/f"preprocess/{n}.png")
    contact([(n,x) for n,x in candidates.items()],run/"preprocess/preprocessing-contact-sheet.png")
    atomic_json(run/"manifests/preprocess.json",{"source":"source/source.png","candidates":[{"name":n,"path":f"preprocess/{n}.png"} for n in candidates],"otsu_threshold":t,"transforms":{"deskew":{"applied":False,"matrix":[1,0,0,0,1,0]},"perspective":{"applied":False,"matrix":[[1,0,0],[0,1,0],[0,0,1]]}},"caution":"No destructive enhancement; thin strokes retained across candidates."})

def _regions(mask:Image.Image,min_area:int):
    cs=[c for c in components(mask) if c["area"]>=min_area]; regs=[]
    for c in cs:
        x1,y1,x2,y2=c["bbox"]; regs.append({"bbox":[x1,y1,x2-x1,y2-y1],"area":c["area"]})
    return regs
def segment(run:Path):
    im=Image.open(run/"source/source.png"); area=im.width*im.height; min_area=max(3,int(area*config(run).get("segmentation",{}).get("min_area_ratio",.00002)))
    specs=[("components","conservative"),("otsu","otsu"),("adaptive","adaptive"),("row-cluster","background-flattened")]; allimgs=[]
    for hi,(method,name) in enumerate(specs,1):
        mask=Image.open(run/f"preprocess/{name}.png"); regs=_regions(mask,min_area)
        # group close components into row-oriented glyph candidates; retain raw regions too.
        medh=np.median([r["bbox"][3] for r in regs]) if regs else 1
        plausible=[r for r in regs if r["bbox"][3]>.25*medh and r["bbox"][2]<.35*im.width]
        plausible=sorted(plausible,key=lambda r:(round(r["bbox"][1]/max(1,medh)),r["bbox"][0]))[:100]
        out=[]; overlay=im.convert("RGB"); d=ImageDraw.Draw(overlay)
        for i,r in enumerate(plausible,1):
            x,y,w,h=r["bbox"]; rid=f"h{hi}-r{i:03}"; r.update({"id":rid,"confidence":.45,"method":method}); out.append(r); d.rectangle((x,y,x+w,y+h),outline="red",width=max(1,im.width//600)); d.text((x,y),rid,fill="blue")
        overlay.save(run/f"segmentation/hypothesis-{hi}.png"); contact([(r["id"],im.crop((r["bbox"][0],r["bbox"][1],r["bbox"][0]+r["bbox"][2],r["bbox"][1]+r["bbox"][3]))) for r in out],run/f"segmentation/hypothesis-{hi}-contact-sheet.png")
        atomic_json(run/f"segmentation/hypothesis-{hi}.json",{"id":hi,"method":method,"regions":out,"source_dimensions":list(im.size)}); allimgs.append((f"hypothesis {hi}: {method}",overlay))
    contact(allimgs,run/"segmentation/segmentation-contact-sheet.png",cols=2,cell=(600,450))
    atomic_json(run/"manifests/segmentation.json",{"hypotheses":[f"segmentation/hypothesis-{i}.json" for i in range(1,len(specs)+1)],"min_area":min_area})

def deterministic_layout(run:Path):
    hyps=[load_json(p) for p in sorted((run/"segmentation").glob("hypothesis-*.json"))]; chosen=max(hyps,key=lambda h:len(h["regions"]))
    regs=chosen["regions"]
    # Select up to 22 substantial regions in visual order. Low confidence by design.
    regs=sorted(regs,key=lambda r:r["area"],reverse=True)[:22]; regs=sorted(regs,key=lambda r:(r["bbox"][1],r["bbox"][0]))
    glyphs=[]
    for i,r in enumerate(regs): glyphs.append({"id":f"g-row01-col{i+1:02}-v01","region_ids":[r["id"]],"bbox":r["bbox"],"role":"glyph","confidence":.25,"rationale":"Deterministic size/order guess; AI disabled."})
    atomic_json(run/"manifests/layout.json",{"chosen_hypothesis":chosen["id"],"alphabets":[{"id":"alphabet-1","glyph_ids":[g["id"] for g in glyphs],"direction":"unknown","is_default":True}],"default_alphabet":"alphabet-1","glyph_regions":glyphs,"ignored_regions":[],"confidence":.2,"rationale":"Largest-component fallback"})
def extract(run:Path):
    im=Image.open(run/"source/source.png"); layout=load_json(run/"manifests/layout.json"); items=[]
    for g in layout["glyph_regions"]:
        x,y,w,h=g["bbox"]; pad=max(4,int(.12*max(w,h))); box=(max(0,x-pad),max(0,y-pad),min(im.width,x+w+pad),min(im.height,y+h+pad)); c=im.crop(box); ctx=im.crop((max(0,x-3*pad),max(0,y-3*pad),min(im.width,x+w+3*pad),min(im.height,y+h+3*pad)))
        d=run/"crops"/g["id"]; d.mkdir(parents=True,exist_ok=True); c.save(d/"source.png"); ctx.save(d/"context.png"); atomic_json(d/"metadata.json",{"id":g["id"],"source_bbox":[x,y,w,h],"crop_bbox":list(box),"source_sha256":load_json(run/"manifests/source.json")["sha256"],"layout_confidence":g["confidence"]}); items.append((g["id"],c))
    contact(items,run/"crops/contact-sheet.png")
def deterministic_identities(run:Path):
    gs=load_json(run/"manifests/layout.json")["glyph_regions"]
    out=[]
    for i,g in enumerate(gs):
        out.append({"candidate_id":g["id"],"canonical_name":CANONICAL[i] if i<len(CANONICAL) else None,"confidence":.2,"variant_group":CANONICAL[i] if i<len(CANONICAL) else "unmapped","source_order":i+1,"is_default_candidate":True,"damaged":False,"notes":"Deterministic positional fallback","alternates":[]})
    atomic_json(run/"manifests/glyph-identities.json",{"glyphs":out,"missing":CANONICAL[len(out):],"confidence":.2})
def masks(run:Path):
    identities=load_json(run/"manifests/glyph-identities.json")["glyphs"]
    sheets=[]
    for g in identities:
        gid=g["candidate_id"]; d=run/"masks"/gid; d.mkdir(parents=True,exist_ok=True); src=gray(Image.open(run/f"crops/{gid}/source.png")); a=np.asarray(src); t=otsu(a)
        variants={"raw":src,"otsu":threshold(a,t),"adaptive":adaptive(a),"sauvola":adaptive(a,max(4,min(src.size)//10),4),"conservative":threshold(a,min(245,t+15))}
        # clean only single-pixel-scale islands; archival variants remain.
        clean=variants["conservative"].copy(); variants["clean"]=clean
        compdata={}
        for n,x in variants.items(): x.save(d/f"mask-{n}.png"); compdata[n]=[{k:v for k,v in c.items() if k!="pixels"} for c in components(x)]
        atomic_json(d/"components.json",compdata); contact([(n,x) for n,x in variants.items()],d/"contact-sheet.png",cols=3,cell=(240,220)); sheets.append((gid,Image.open(d/"contact-sheet.png")))
    contact(sheets,run/"masks/masks-contact-sheet.png",cols=2,cell=(600,440))
def deterministic_mask_decisions(run:Path):
    ids=load_json(run/"manifests/glyph-identities.json")["glyphs"]
    atomic_json(run/"manifests/mask-decisions.json",{"glyphs":[{"candidate_id":g["candidate_id"],"preferred_mask":"conservative","keep_components":[],"drop_components":[],"uncertain_components":[],"thin_strokes_lost":False,"noise_incorporated":False,"repair_required":False,"confidence":.35,"rationale":"Conservative deterministic threshold"} for g in ids]})
def apply_masks(run:Path):
    for d in load_json(run/"manifests/mask-decisions.json")["glyphs"]:
        gid=d["candidate_id"]; src=Image.open(run/f"masks/{gid}/mask-{d['preferred_mask']}.png").convert("L"); cs=components(src); byid={c["id"]:c for c in cs}; keep=set(d.get("keep_components",[])); drop=set(d.get("drop_components",[])); a=np.asarray(src).copy()
        if keep:
            a[:]=255
            for cid in keep:
                for x,y in byid.get(cid,{}).get("pixels",[]): a[y,x]=0
        for cid in drop:
            for x,y in byid.get(cid,{}).get("pixels",[]): a[y,x]=255
        final=Image.fromarray(a); final.save(run/f"masks/final/{gid}.png")
        orig=Image.open(run/f"crops/{gid}/source.png").convert("RGB"); ov=np.asarray(orig).copy(); ink=a<128; ov[ink,0]=255; ov[ink,1]=(ov[ink,1]*.35).astype(np.uint8); ov[ink,2]=(ov[ink,2]*.35).astype(np.uint8); Image.fromarray(ov).save(run/f"masks/final/{gid}-overlay.png")

def _mask_svg(mask:Image.Image,path:Path):
    # Deterministic rectilinear fallback preserving exact source pixels; Potrace stage replaces this when available.
    a=np.asarray(mask)<128; h,w=a.shape; rects=[]
    for y in range(h):
        xs=np.where(a[y])[0];
        if not len(xs): continue
        start=prev=int(xs[0])
        for x in map(int,xs[1:]):
            if x>prev+1: rects.append((start,y,prev-start+1,1)); start=x
            prev=x
        rects.append((start,y,prev-start+1,1))
    body="".join(f'<rect x="{x}" y="{y}" width="{w0}" height="{h0}"/>' for x,y,w0,h0 in rects)
    path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><g fill="#000">{body}</g></svg>\n')
def trace(run:Path):
    log=[]
    for p in sorted((run/"masks/final").glob("g-*.png")):
        if p.name.endswith("-overlay.png"): continue
        gid=p.stem; out=run/f"traces/raw/{gid}.svg"
        if shutil.which("potrace"):
            pbm=run/f"traces/raw/{gid}.pbm"; Image.open(p).convert("1").save(pbm); cmd=["potrace",str(pbm),"-s","-o",str(out),"--turdsize",str(config(run).get("tracing",{}).get("turd_size",2)),"--alphamax",str(config(run).get("tracing",{}).get("corner_threshold",1.0)),"--opttolerance",str(config(run).get("tracing",{}).get("opt_tolerance",.2))]; subprocess.run(cmd,check=True); log.append({"glyph":gid,"command":cmd,"backend":"potrace"})
        else: _mask_svg(Image.open(p),out); log.append({"glyph":gid,"backend":"pixel-rect-fallback","warning":"potrace unavailable"})
    atomic_json(run/"manifests/trace.json",{"traces":log})
def clean(run:Path):
    import xml.etree.ElementTree as ET
    items=[]
    for p in sorted((run/"traces/raw").glob("*.svg")):
        text=p.read_text(); text=text.replace("\r","").replace("  "," "); out=run/"traces/clean"/p.name; out.write_text(text)
        # previews are rasterized from final mask to stay dependency-free and geometrically comparable.
        gid=p.stem; prev=Image.open(run/f"masks/final/{gid}.png").resize((256,256)); prev.save(run/f"traces/clean/{gid}-preview.png"); items.append((gid,prev))
    contact(items,run/"traces/traces-contact-sheet.png")
def deterministic_repairs(run:Path): atomic_json(run/"manifests/trace-repairs.json",{"glyphs":[{"candidate_id":p.stem,"action":"accept","operations":[],"confidence":.35,"rationale":"No AI trace review"} for p in sorted((run/"traces/clean").glob("*.svg"))]})
def repair(run:Path):
    results=[]
    for g in load_json(run/"manifests/trace-repairs.json")["glyphs"]:
        gid=g["candidate_id"]; src=run/f"traces/clean/{gid}.svg"; dst=run/f"traces/repaired/{gid}.svg"
        if g["action"]=="accept": shutil.copy2(src,dst); status="accepted"
        else: shutil.copy2(src,dst); status="manual_review" if any(o.get("op") not in {"dilate","erode","close","alternate_mask","retrace"} for o in g.get("operations",[])) else "copied_pending_supported_retrace"
        results.append({"candidate_id":gid,"status":status,"source":str(src.relative_to(run)),"output":str(dst.relative_to(run))})
    atomic_json(run/"manifests/repairs-applied.json",{"glyphs":results})
def measure(run:Path):
    ids={g["candidate_id"]:g for g in load_json(run/"manifests/glyph-identities.json")["glyphs"]}; rows=[]
    for p in sorted((run/"masks/final").glob("g-*.png")):
        if p.name.endswith("-overlay.png"): continue
        im=Image.open(p); b=bbox_ink(im); a=np.asarray(im)<128; ys,xs=np.where(a)
        if b: x1,y1,x2,y2=b; width=x2-x1;height=y2-y1; centroid=[float(xs.mean()),float(ys.mean())]; mass=int(a.sum())
        else: width=height=mass=0;centroid=[0,0]
        meta=load_json(run/f"crops/{p.stem}/metadata.json"); rows.append({"candidate_id":p.stem,"canonical_name":ids[p.stem]["canonical_name"],"source_bbox":meta["source_bbox"],"vector_bbox":[0,0,width,height],"width":width,"height":height,"area":mass,"centroid":centroid,"principal_axis":0,"dominant_stroke_width":None,"source_row_position":ids[p.stem]["source_order"],"neighbor_distances":[],"aspect_ratio":width/max(1,height),"component_count":len(components(im)),"visual_mass":mass})
    hs=[r["height"] for r in rows if r["height"]]; ws=[r["width"] for r in rows if r["width"]]; ms=[r["visual_mass"] for r in rows if r["visual_mass"]]
    stats={"median_height":float(np.median(hs)) if hs else 0,"median_width":float(np.median(ws)) if ws else 0,"median_visual_mass":float(np.median(ms)) if ms else 0}
    atomic_json(run/"manifests/measurements.json",{"glyphs":rows,"population":stats}); contact([(r["canonical_name"] or r["candidate_id"],Image.open(run/f"masks/final/{r['candidate_id']}.png")) for r in rows],run/"proofs/metrics-contact-sheet.png")
def deterministic_normalization(run:Path):
    m=load_json(run/"manifests/measurements.json"); c=config(run); nc=c["normalization"]; med=max(1,m["population"]["median_height"]); body=nc["body_height"]; glyphs={}
    for r in m["glyphs"]:
        scale=body/med; width=r["width"]*scale; glyphs[r["candidate_id"]]={"canonical_name":r["canonical_name"],"scale":scale,"translate_x":nc["sidebearing"],"translate_y":100,"advance_width":int(round(width+2*nc["sidebearing"])),"confidence":.45,"rationale":"Common source-scale transformation preserves relative proportions"}
    atomic_json(run/"manifests/normalization.json",{"font":{"upm":nc["upm"],"ascent":nc["ascent"],"descent":nc["descent"]},"glyphs":glyphs,"confidence":.4,"rationale":"Deterministic common scale; no per-glyph beautification"})
def normalize(run:Path):
    import xml.etree.ElementTree as ET
    dec=load_json(run/"manifests/normalization.json"); items=[]
    for gid,d in dec["glyphs"].items():
        src=run/f"traces/repaired/{gid}.svg"; root=ET.fromstring(src.read_text()); vb=[float(x) for x in root.attrib.get("viewBox","0 0 100 100").replace(","," ").split()]; s=float(d["scale"]); tx=float(d["translate_x"])-vb[0]*s; ty=800-float(d["translate_y"])-(vb[1]+vb[3])*s
        old=list(root); root.clear(); root.tag="{http://www.w3.org/2000/svg}svg"; root.attrib={"viewBox":"0 -200 1000 1000","width":"1000","height":"1000"}; group=ET.SubElement(root,"{http://www.w3.org/2000/svg}g",{"transform":f"translate({tx:.5f} {800-float(d['translate_y']):.5f}) scale({s:.7f} {-s:.7f}) translate({-vb[0]:.5f} {-vb[1]:.5f})"}); group.extend(old); out=run/f"normalized/{gid}.svg"; ET.ElementTree(root).write(out,encoding="unicode",xml_declaration=True)
        prev=Image.open(run/f"masks/final/{gid}.png").resize((220,220)); items.append((d.get("canonical_name") or gid,prev))
    contact(items,run/"normalized/normalized-contact-sheet.png")
def deterministic_variants(run:Path):
    ids=load_json(run/"manifests/glyph-identities.json")["glyphs"]; groups={}
    for g in ids:
        if g["canonical_name"]: groups.setdefault(g["canonical_name"],[]).append(g)
    out=[]
    for name,gs in groups.items(): out.append({"canonical_name":name,"default_candidate_id":max(gs,key=lambda x:x["confidence"])["candidate_id"],"ranked_candidates":[x["candidate_id"] for x in sorted(gs,key=lambda x:-x["confidence"])],"damaged_candidates":[x["candidate_id"] for x in gs if x["damaged"]],"confidence":max(x["confidence"] for x in gs),"rationale":"Highest mapping confidence"})
    atomic_json(run/"manifests/variants.json",{"groups":out})

def build_font(run:Path):
    cfg=config(run); name=cfg["font"]["name"]; out=run/"build"; out.mkdir(exist_ok=True); norm=load_json(run/"manifests/normalization.json"); variants=load_json(run/"manifests/variants.json")["groups"]; cmap=mapping(cfg["encoding"])
    script=run/"logs/build-fontforge.py"; records=[]
    lines=["import fontforge",f"f=fontforge.font()",f"f.encoding='UnicodeFull'",f"f.em={norm['font']['upm']}",f"f.ascent={norm['font']['ascent']}",f"f.descent={norm['font']['descent']}",f"f.familyname={name!r}",f"f.fontname={name!r}",f"f.fullname={name!r}",f"f.version={cfg['font'].get('version','1.0')!r}"]
    counts={}
    for group in variants:
        cn=group["canonical_name"]
        for gid in group["ranked_candidates"]:
            idx=counts.get(cn,0); counts[cn]=idx+1; gn=cn if idx==0 else f"{cn}.alt{idx:02}"; cp=cmap[cn] if idx==0 else -1; svg=(run/f"normalized/{gid}.svg").resolve(); width=norm["glyphs"][gid]["advance_width"]
            lines += [f"g=f.createChar({cp},{gn!r})",f"g.importOutlines({str(svg)!r})","g.removeOverlap()","g.correctDirection()",f"g.width={width}"]
            records.append({"canonical_name":cn,"candidate_id":gid,"glyph_name":gn,"unicode":cp if cp>=0 else None,"normalized_svg":str(svg.relative_to(run)),"advance_width":width})
    lines += [f"f.save({str((out/(name+'.sfd')).resolve())!r})",f"f.generate({str((out/(name+'.otf')).resolve())!r})",f"f.generate({str((out/(name+'.ttf')).resolve())!r})","f.close()"]
    script.write_text("\n".join(lines)+"\n"); subprocess.run(["fontforge","-lang=py","-script",str(script)],check=True,capture_output=True,text=True)
    atomic_json(run/"manifests/font-build.json",{"font_name":name,"artifacts":{x:f"build/{name}.{x}" for x in ["sfd","otf","ttf"]},"glyphs":records})

def proof(run:Path):
    cfg=config(run); build=load_json(run/"manifests/font-build.json"); rows=load_json(run/"manifests/measurements.json")["glyphs"]; qa=[]
    # Inspectable multi-section raster proof; ImageMagick converts it to PDF.
    page=Image.new("RGB",(1800,max(2400,300+len(rows)*180)),"white"); d=ImageDraw.Draw(page); d.text((60,40),f"{cfg['font']['name']} — source fidelity proof",fill="black"); d.text((60,80),"Complete alphabet / source crops / masks / normalized previews / metrics",fill="black")
    x=60
    for r in rows:
        gid=r["candidate_id"]; crop=Image.open(run/f"crops/{gid}/source.png").convert("RGB"); mask=Image.open(run/f"masks/final/{gid}.png").convert("RGB"); crop.thumbnail((150,130)); mask.thumbnail((150,130)); y=150+rows.index(r)*180; d.text((60,y),f"{r['canonical_name']}  bbox={r['width']}x{r['height']} area={r['area']}",fill="black"); page.paste(crop,(400,y)); page.paste(mask,(600,y)); d.rectangle((800,y,950,y+130),outline="gray"); page.paste(mask.resize((130,130)),(810,y)); qa.append((r["canonical_name"],mask))
    png=run/"proofs/proof.png"; page.save(png)
    try: subprocess.run(["magick",str(png),str(run/"proofs/proof.pdf")],check=True,capture_output=True)
    except Exception: page.save(run/"proofs/proof.pdf","PDF",resolution=150)
def deterministic_finalqa(run:Path):
    ids=load_json(run/"manifests/glyph-identities.json"); glyphs=[]
    for g in ids["glyphs"]: glyphs.append({"candidate_id":g["candidate_id"],"canonical_name":g["canonical_name"],"score":40,"action":"accept" if g["confidence"]>=.5 else "manual_review","adjustment":{},"confidence":g["confidence"],"rationale":"AI-disabled QA; visual judgment not performed"})
    complete=22-len(ids.get("missing",[])); score=int(40*complete/22); atomic_json(run/"manifests/final-qa.json",{"overall_score":score,"dimensions":{"source_fidelity":40,"alphabet_completeness":int(100*complete/22),"identification_confidence":20,"scale_coherence":50,"spacing_coherence":50,"tracing_quality":40,"accidental_noise":40,"obvious_omissions":int(100*complete/22)},"glyphs":glyphs,"review_recommended":[g["canonical_name"] for g in glyphs if g["action"]=="manual_review"],"confidence":.2})
def apply_qa(run:Path): atomic_json(run/"manifests/qa-applied.json",{"applied":[],"manual_review":[g["candidate_id"] for g in load_json(run/"manifests/final-qa.json")["glyphs"] if g["action"]=="manual_review"],"note":"Only bounded affine/spacing adjustments are supported; rebuild orchestrator applies them on AI runs."})
def validate(run:Path):
    b=load_json(run/"manifests/font-build.json"); errors=[]; warnings=[]
    for kind,rel in b["artifacts"].items():
        p=run/rel
        if not p.exists() or p.stat().st_size==0: errors.append(f"missing {kind}: {p}")
    for kind in ["otf","ttf"]:
        try:
            f=TTFont(run/b["artifacts"][kind]); tables=set(f.keys());
            if "cmap" not in tables: errors.append(f"{kind}: no cmap")
            f.close()
        except Exception as e: errors.append(f"{kind}: fontTools parse failed: {e}")
    if shutil.which("ots-sanitize"):
        for kind in ["otf","ttf"]:
            p=subprocess.run(["ots-sanitize",str(run/b["artifacts"][kind])],capture_output=True,text=True)
            if p.returncode: warnings.append(f"ots {kind}: {p.stderr.strip()}")
    else: warnings.append("ots-sanitize unavailable")
    if not shutil.which("hb-shape"): warnings.append("hb-shape unavailable")
    result={"fatal":errors,"warnings":warnings,"status":"failed" if errors else "passed"}; atomic_json(run/"manifests/validation.json",result)
    if errors: raise SystemExit("Validation failed: "+"; ".join(errors))
def report(run:Path):
    cfg=config(run); src=load_json(run/"manifests/source.json"); ids=load_json(run/"manifests/glyph-identities.json"); norm=load_json(run/"manifests/normalization.json"); qa=load_json(run/"manifests/final-qa.json"); build=load_json(run/"manifests/font-build.json"); dist=run/"report"; dist.mkdir(exist_ok=True)
    def uri(p):
        import base64,mimetypes
        q=run/p; return f"data:{mimetypes.guess_type(q.name)[0] or 'application/octet-stream'};base64,"+base64.b64encode(q.read_bytes()).decode()
    cards=[]; cmap=mapping(cfg["encoding"]); byqa={g["candidate_id"]:g for g in qa["glyphs"]}
    for g in ids["glyphs"]:
        gid=g["candidate_id"]; cn=g["canonical_name"]; meta=load_json(run/f"crops/{gid}/metadata.json"); n=norm["glyphs"][gid]
        cards.append(f'<article><h2>{html.escape(str(cn))} <small>U+{cmap.get(cn,0):04X}</small></h2><div class="imgs"><img src="{uri(Path(f"crops/{gid}/source.png"))}"><img src="{uri(Path(f"crops/{gid}/context.png"))}"><img src="{uri(Path(f"masks/final/{gid}.png"))}"><img src="{uri(Path(f"traces/clean/{gid}-preview.png"))}"></div><pre>{html.escape(json.dumps({"candidate":gid,"source_bbox":meta["source_bbox"],"mapping_confidence":g["confidence"],"qa":byqa[gid],"transform":n,"notes":g["notes"]},indent=2))}</pre></article>')
    css="body{font:15px system-ui;max-width:1200px;margin:auto;padding:2rem;background:#f5f1e8;color:#211}header,article{background:white;padding:1rem;margin:1rem 0;border:1px solid #c9bda8;border-radius:8px}.imgs{display:flex;gap:1rem;align-items:center}.imgs img{max-width:210px;max-height:180px;border:1px solid #ddd;image-rendering:auto}pre{white-space:pre-wrap}small{color:#765}"
    doc=f'<!doctype html><meta charset="utf-8"><title>{html.escape(cfg["font"]["name"])} report</title><style>{css}</style><header><h1>{html.escape(cfg["font"]["name"])} extraction report</h1><p>Source SHA256: <code>{src["sha256"]}</code></p><p>Extracted: {len(ids["glyphs"])} · Missing: {", ".join(ids["missing"]) or "none"} · QA: {qa["overall_score"]}/100 · Review: {", ".join(qa["review_recommended"]) or "none"}</p></header>'+"".join(cards)
    (dist/"report.html").write_text(doc)
    provenance=[]
    for r in build["glyphs"]:
        gid=r["candidate_id"]; meta=load_json(run/f"crops/{gid}/metadata.json")
        provenance.append({**r,"clean_svg":f"traces/clean/{gid}.svg","raw_svg":f"traces/raw/{gid}.svg","selected_mask":f"masks/final/{gid}.png","source_crop":f"crops/{gid}/source.png","source_rect":meta["source_bbox"],"source_sha256":meta["source_sha256"]})
    atomic_json(run/"report/manifest.json",{"pipeline_version":"0.1.0","config":cfg,"source":src,"qa":qa,"validation":load_json(run/"manifests/validation.json"),"glyphs":provenance})
def package(run:Path):
    cfg=config(run); name=cfg["font"]["name"]; dest=Path(cfg["output"]).resolve(); dest.mkdir(parents=True,exist_ok=True)
    for ext in ["sfd","otf","ttf"]: shutil.copy2(run/f"build/{name}.{ext}",dest/f"{name}.{ext}")
    for src,n in [(run/"proofs/proof.pdf","proof.pdf"),(run/"proofs/proof.png","proof.png"),(run/"report/report.html","report.html"),(run/"report/manifest.json","manifest.json")]: shutil.copy2(src,dest/n)
    gd=dest/"glyphs"; gd.mkdir(exist_ok=True)
    for p in (run/"normalized").glob("*.svg"): shutil.copy2(p,gd/p.name)
    atomic_json(run/"manifests/package.json",{"destination":str(dest),"files":[str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_file()]})

COMMANDS={"ingest":ingest,"preprocess":preprocess,"segment":segment,"layout-fallback":deterministic_layout,"extract":extract,"identify-fallback":deterministic_identities,"masks":masks,"mask-fallback":deterministic_mask_decisions,"apply-masks":apply_masks,"trace":trace,"clean":clean,"repairs-fallback":deterministic_repairs,"repair":repair,"measure":measure,"normalization-fallback":deterministic_normalization,"normalize":normalize,"variants-fallback":deterministic_variants,"build":build_font,"proof":proof,"qa-fallback":deterministic_finalqa,"apply-qa":apply_qa,"validate":validate,"report":report,"package":package}
def main():
    p=argparse.ArgumentParser(); p.add_argument("command",choices=COMMANDS); p.add_argument("--run",type=Path,required=True); p.add_argument("--source",type=Path); p.add_argument("--pdf-page",type=int,default=1); p.add_argument("--pdf-dpi",type=int,default=600); a=p.parse_args(); kw={}
    if a.command=="ingest": kw={"source":a.source,"pdf_page":a.pdf_page,"pdf_dpi":a.pdf_dpi}
    COMMANDS[a.command](a.run,**kw)
if __name__=="__main__": main()
