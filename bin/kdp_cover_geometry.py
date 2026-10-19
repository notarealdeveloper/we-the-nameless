"""Cover geometry in inches, shared by rendering and publication checks.

Paperback constants: https://kdp.amazon.com/en_US/help/topic/G201953020
Hardcover requirements: https://kdp.amazon.com/en_US/help/topic/GDTKFJPNQCBTMRV6
Hardcover case model uses mm (the help page's 0.51in/15mm wrap is inconsistent).
15mm wrap, 5mm panel-width allowance, 6mm panel-height allowance, 4.8mm
spine allowance reproduce the recorded 224-page premium-color KDP template:
https://github.com/hackerbay/twenty-minute-table/blob/main/book/cover.py
This is a template-derived model, not an Amazon-published hardcover formula.
An exact calculator export may override it; see PUBLISH.md.
"""
import json
import math
from pathlib import Path

THICKNESS = {'white': .002252, 'cream': .0025,
             'standard-color': .002252, 'premium-color': .002347}
BINDINGS = {'paperback': ('book', 7, 10), 'hardcover': ('hard', 8.25, 11)}
ARTIFACTS = tuple(f'{kind}-{binding}' for binding in BINDINGS for kind in ('interior', 'cover'))


def geometry(pages, width, height, paper, binding='paperback', template=None):
    if binding not in ('paperback', 'hardcover'):
        raise ValueError(f'Unsupported binding: {binding}')
    if paper not in THICKNESS:
        raise ValueError(f'Unsupported paper: {paper}')
    if pages < 1 or width <= 0 or height <= 0:
        raise ValueError('Page count and trim dimensions must be positive')
    spine = pages * THICKNESS[paper]
    wrap, panel_width, panel_height, hinge = .125, width, height, 0
    if binding == 'hardcover':
        # Hardcover color is premium even when the paperback uses standard color.
        spine = pages * THICKNESS['premium-color'] + 4.8 / 25.4
        wrap, hinge = 15 / 25.4, 10 / 25.4
        panel_width, panel_height = width + 5 / 25.4, height + 6 / 25.4
        if template:
            exact = json.loads(Path(template).read_text())
            if (exact['pages'] != pages or exact['trim_width'] != width
                    or exact['trim_height'] != height or exact['paper'] != 'premium-color'):
                raise ValueError('Hardcover template does not match interior page count, trim, and premium-color stock')
            spine, wrap, hinge = (exact[k] for k in ('spine', 'wrap', 'hinge'))
            panel_width, panel_height = (exact[k] for k in ('panel_width', 'panel_height'))
    if (not all(math.isfinite(v) for v in (spine, wrap, panel_width, panel_height, hinge))
            or min(spine, wrap, panel_width, panel_height) <= 0 or hinge < 0
            or hinge >= panel_width):
        raise ValueError('Cover dimensions must be positive')
    return dict(spine=spine, wrap=wrap, hinge=hinge,
        panel_width=panel_width, panel_height=panel_height,
        width=2 * (wrap + panel_width) + spine, height=panel_height + 2 * wrap)


def tex_dimensions(g, width, height):
    # Original simple-cover coordinates measured from the bottom of its trim.
    baseline = g['wrap'] + (g['panel_height'] - height) / 2
    values = dict(CoverSheetWidth=g['width'], CoverSheetHeight=g['height'],
        CoverBleed=g['wrap'], CoverPanelWidth=g['panel_width'],
        CoverPanelHeight=g['panel_height'], CoverHinge=g['hinge'],
        CoverFrontLeft=g['wrap'] + g['panel_width'] + g['spine'],
        CoverSpineCenterX=g['wrap'] + g['panel_width'] + g['spine']/2,
        CoverSpineCenterY=g['height']/2, CoverFrontCenterX=g['panel_width']/2,
        CoverWeY=baseline + 7.2 * height/10,
        CoverNamelessY=baseline + 4.6 * height/10,
        CoverVolumeY=baseline + 1.3 * height/10)
    return '\n'.join(r'\newlength{\%s}\setlength{\%s}{%.8fin}' % (k,k,v)
                     for k,v in values.items()) + '\n'
