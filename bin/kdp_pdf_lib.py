"""Shared fail-closed PDF inspection, independent of the publishing orchestrator."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET


def run(*args, allowed=(0,)):
    p = subprocess.run(list(map(str, args)), text=True, capture_output=True)
    if p.returncode not in allowed:
        raise RuntimeError(f'{args!r}: exit {p.returncode}\n{p.stdout}\n{p.stderr}')
    return p


def sha256(path):
    with open(path, 'rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()


def inspect(pdf):
    pdf = Path(pdf)
    data = json.loads(run('qpdf', '--json=1', '--json-key=objects', '--json-key=pages', pdf).stdout)
    objects = data['objects']

    def resolve(value):
        seen = set()
        while isinstance(value, str) and value in objects:
            if value in seen: raise ValueError('cyclic PDF object reference')
            seen.add(value); value = objects[value]
        return value

    def inherited(obj, key, default=None):
        seen = set()
        while key not in obj and '/Parent' in obj:
            parent = obj['/Parent']
            if parent in seen: raise ValueError('cyclic PDF page tree')
            seen.add(parent); obj = resolve(parent)
        return resolve(obj.get(key, default))

    geometry = []
    for n, page in enumerate(data['pages'], 1):
        obj = resolve(page['object'])
        media = inherited(obj, '/MediaBox')
        crop = inherited(obj, '/CropBox', media)
        boxes = dict(MediaBox=media, CropBox=crop,
            TrimBox=resolve(obj.get('/TrimBox', crop)), BleedBox=resolve(obj.get('/BleedBox', crop)),
            ArtBox=resolve(obj.get('/ArtBox', crop)))
        if any(not isinstance(b, list) or len(b) != 4 or not all(isinstance(v, (int, float)) for v in b) for b in boxes.values()):
            raise ValueError(f'cannot read page {n} boxes')
        geometry.append(dict(page=n, **boxes, rotation=inherited(obj, '/Rotate', 0), UserUnit=resolve(obj.get('/UserUnit', 1))))
    if not geometry: raise ValueError('PDF has no pages')
    font_output = run('pdffonts', pdf).stdout.splitlines()
    if len(font_output) < 2 or not font_output[0].startswith('name'):
        raise ValueError('unrecognized pdffonts output')
    fonts = [line for line in font_output[2:] if line.strip()]
    images = []
    rows = run('pdfimages', '-list', pdf).stdout.splitlines()
    if len(rows) < 2 or 'page' not in rows[0]: raise ValueError('unrecognized pdfimages output')
    for line in rows[2:]:
        c = line.split()
        if len(c) < 16: raise ValueError(f'unrecognized image row: {line}')
        images.append(dict(page=int(c[0]), num=int(c[1]), type=c[2], width=int(c[3]), height=int(c[4]),
            color=c[5], components=int(c[6]), bpc=int(c[7]), xppi=float(c[12]), yppi=float(c[13])))
    # MuPDF independently resolves PDF resources and interprets page/Form content,
    # including inherited resources, nested Forms, patterns and quote text operators.
    mupdf_objects = run('mutool', 'show', pdf, 'grep').stdout
    mupdf_fonts = bool(re.search(r'/Font(?:\b|/)|/Type\s*/Font\b', mupdf_objects))
    with tempfile.TemporaryDirectory(prefix='kdp-trace-') as td:
        trace = Path(td) / 'trace.xml'
        run('mutool', 'draw', '-q', '-F', 'trace', '-o', trace, pdf)
        text_operations = 0
        for _, element in ET.iterparse(trace):
            if element.tag in ('fill_text', 'stroke_text', 'clip_text', 'clip_stroke_text', 'ignore_text'):
                text_operations += 1
            element.clear()

    def walk(value):
        if isinstance(value, dict):
            yield value
            for child in value.values(): yield from walk(child)
        elif isinstance(value, list):
            for child in value: yield from walk(child)

    dictionaries = list(walk(objects))
    keys = {key for d in dictionaries for key in d}
    transparency = any(
        (d.get('/SMask', '/None') not in ('/None', None)) or
        any(isinstance(d.get(k), (float, int)) and d[k] < 1 for k in ('/ca', '/CA')) or
        ('/BM' in d and d['/BM'] not in ('/Normal', '/Compatible', ['/Normal'])) or
        d.get('/S') == '/Transparency' for d in dictionaries)
    return dict(file=str(pdf), sha256=sha256(pdf), bytes=pdf.stat().st_size,
        pages=len(geometry), page_geometry=geometry, font_count=len(fonts), fonts_raw=fonts,
        mupdf_font_resources=mupdf_fonts, mupdf_text_operations=text_operations,
        images=images, low_resolution_images=[i for i in images if i['type'] == 'image' and min(i['xppi'], i['yppi']) < 300],
        features=dict(annotations='/Annots' in keys, outlines='/Outlines' in keys,
            layers=bool(keys & {'/OCProperties', '/OCGs'}), transparency=transparency,
            actions=bool(keys & {'/OpenAction', '/AA', '/JavaScript', '/A'}),
            attachments='/EmbeddedFiles' in keys))


def validate(reference, final, before, after):
    failures, review = [], []
    # Exit 2 specifically means unencrypted for this qpdf probe; any other
    # unexpected exit is a tool failure, never an empty successful observation.
    run('qpdf', '--check', final)
    if run('qpdf', '--is-encrypted', final, allowed=(0, 2)).returncode == 0:
        failures.append('PDF is encrypted')
    for path, recorded in ((reference, before), (final, after)):
        if sha256(path) != recorded['sha256']: failures.append(f'inspection does not match PDF: {path}')
    if before['pages'] != after['pages']:
        failures.append('page count differs')
    for a, b in zip(before['page_geometry'], after['page_geometry']):
        for key in ('MediaBox', 'CropBox', 'TrimBox', 'BleedBox', 'ArtBox'):
            # Preserve the established 0.01-point allowance for PDF numeric
            # serialization (Ghostscript rounds cover sheet dimensions).
            if any(abs(x-y) > .01 for x, y in zip(a[key], b[key])):
                failures.append(f"page {a['page']} {key} differs")
        for key in ('page', 'rotation', 'UserUnit'):
            if a[key] != b[key]: failures.append(f"page {a['page']} {key} differs")
    if after['font_count']: failures.append('pdffonts reports remaining fonts')
    if run('pdftotext', final, '-').stdout.strip(): failures.append('pdftotext found remaining text')
    if after['mupdf_font_resources']: failures.append('MuPDF found font resources')
    if after['mupdf_text_operations']: failures.append('MuPDF found text-showing operations')
    for key, value in after['features'].items():
        if value and key != 'transparency': failures.append(f'unwanted feature remains: {key}')
    if after['features']['transparency']: review.append('live transparency detected; source-level review required')
    if after['bytes'] > 650_000_000: failures.append('file exceeds 650,000,000 bytes')
    def raster_counts(info):
        return Counter(tuple(i[k] for k in ('page', 'type', 'width', 'height', 'color', 'components', 'bpc')) for i in info['images'])
    added = raster_counts(after) - raster_counts(before)
    if added: failures.append(f'unexpected raster assets/placements (including possible page rasterization): {dict(added)}')
    if after['low_resolution_images']:
        review.append(f"{len(after['low_resolution_images'])} raster placements are below 300 PPI; see final inspection")
    return dict(reference=str(reference), final=str(final), passed=not failures, failures=failures,
        human_review=review, page_count=after['pages'], bytes=after['bytes'],
        size_growth=after['bytes']-before['bytes'], font_count=after['font_count'])
