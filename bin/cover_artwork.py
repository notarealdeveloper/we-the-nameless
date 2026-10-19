"""Prepare print-resolution copies without changing the source artwork."""
import math
from pathlib import Path


def prepare_artwork(geometry, destination):
    from PIL import Image

    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    for name in ('back', 'front-textless'):
        with Image.open(Path('pub/covers/fancy/assets') / f'{name}.png') as source:
            width, height = source.size
            # Back artwork is also stretched across the entire sheet and used
            # at its natural aspect ratio through the spine. Account for every
            # placement, including portions hidden by clipping.
            placements = [(geometry['panel_width'], geometry['panel_height'])]
            if name == 'back':
                placements += [(geometry['width'], geometry['height']),
                               (geometry['height'] * width / height, geometry['height'])]
            scale = max(1, *(300 * max(w / width, h / height) for w, h in placements))
            size = (math.ceil(width * scale), math.ceil(height * scale))
            artwork = source.resize(size, Image.Resampling.LANCZOS)
            artwork.save(destination / f'{name}.png', dpi=(300, 300))
