"""Lulu perfect-bound / casewrap dimensions, in inches (checked 2026-10-19).

https://help.api.lulu.com/en/support/solutions/articles/64000254616-how-is-spine-width-calculated-
https://help.lulu.com/en/support/solutions/articles/64000308572-creating-your-hardcover-casewrap-cover
Use 60# white uncoated stock, not magazine/comic 460-PPI paper.
"""
# Upper inclusive page bounds. Resolve overlapping early help-table boundaries
# using the Book Creation Guide's contiguous ranges.
CASEWRAP = ((84, .25), (140, .5), (168, .625), (194, .6875),
    (222, .75), (250, .8125), (278, .875), (306, .9375),
    (334, 1), (360, 1.0625), (388, 1.125), (416, 1.1875),
    (444, 1.25), (472, 1.3125), (500, 1.375), (528, 1.4375),
    (556, 1.5), (582, 1.5625), (610, 1.625), (638, 1.6875),
    (666, 1.75), (694, 1.8125), (722, 1.875), (750, 1.9375),
    (778, 2), (800, 2.0625))


def geometry(pages, width, height, paper, binding='paperback', template=None):
    if binding not in ('paperback', 'hardcover'):
        raise ValueError('Unsupported Lulu binding')
    minimum = 32 if binding == 'paperback' else 24
    if not minimum <= pages <= 800 or pages % 2:
        raise ValueError(f'Lulu {binding} requires an even page count in {minimum}..800')
    if (width, height) != (7, 10) or paper not in ('premium-color', 'standard-color') or template:
        raise ValueError('Lulu profile supports 7x10, color on 60# white, without KDP templates')
    spine = pages / 444 + .06
    wrap, panel_width, panel_height, hinge = .125, width, height, 0
    if binding == 'hardcover':
        spine = next(spine for maximum, spine in CASEWRAP if pages <= maximum)
        wrap, panel_width, panel_height, hinge = .75, width + .125, height + .25, .5
    return dict(spine=spine, wrap=wrap, hinge=hinge,
        panel_width=panel_width, panel_height=panel_height,
        width=2 * (wrap + panel_width) + spine, height=panel_height + 2 * wrap)
