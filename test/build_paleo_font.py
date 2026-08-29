#!/usr/bin/env python3
"""Build a Hebrew-Unicode font from the paleo GIF letterforms."""

from pathlib import Path
import os
import subprocess
import tempfile

from PIL import Image


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "hebrewgraphics"
OUTPUT = ROOT / "paleo-hebrew-images.ttf"

# Hebrew letters in Unicode order.  The five contextual final forms reuse the
# corresponding paleo letter: the source alphabet has no separate final forms.
LETTERS = [
    ("aleph", 0x05D0), ("beyt", 0x05D1), ("gimel", 0x05D2),
    ("dalet", 0x05D3), ("hey", 0x05D4), ("vav", 0x05D5),
    ("zayin", 0x05D6), ("chet", 0x05D7), ("tet", 0x05D8),
    ("yud", 0x05D9), ("kaph", 0x05DB), ("lamed", 0x05DC),
    ("mem", 0x05DE), ("nun", 0x05E0), ("samech", 0x05E1),
    ("ayin", 0x05E2), ("pey", 0x05E4), ("tsade", 0x05E6),
    ("quph", 0x05E7), ("resh", 0x05E8), ("shin", 0x05E9),
    ("tav", 0x05EA),
]
FINAL_FORMS = {
    0x05DA: 0x05DB,  # final kaf
    0x05DD: 0x05DE,  # final mem
    0x05DF: 0x05E0,  # final nun
    0x05E3: 0x05E4,  # final pe
    0x05E5: 0x05E6,  # final tsadi
}

PIXEL = 10
BASELINE_ROW = 98
LEFT_BEARING = 45
RIGHT_BEARING = 45


def pixel_svg(source: Path, target: Path) -> None:
    """Write the GIF's exact nontransparent silhouette as an SVG union."""
    image = Image.open(source)
    transparent = image.info["transparency"]
    pixels = image.load()
    rectangles = []
    for y in range(image.height):
        x = 0
        while x < image.width:
            if pixels[x, y] == transparent:
                x += 1
                continue
            start = x
            while x < image.width and pixels[x, y] != transparent:
                x += 1
            rectangles.append(
                f'<rect x="{start * PIXEL}" y="{y * PIXEL}" '
                f'width="{(x - start) * PIXEL}" height="{PIXEL}"/>'
            )
    target.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg">'
        + "".join(rectangles)
        + "</svg>"
    )


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="paleo-font-") as temporary:
        temporary = Path(temporary)
        glyphs = []
        for name, codepoint in LETTERS:
            svg = temporary / f"{name}.svg"
            source = SOURCE / f"paleo_{name}.gif"
            pixel_svg(source, svg)
            image = Image.open(source)
            transparent = image.info["transparency"]
            silhouette = image.point(
                lambda value: 0 if value == transparent else 255, mode="1"
            )
            bottom = silhouette.getbbox()[3]
            glyphs.append((name, codepoint, svg, image.width, bottom))

        fontforge_script = temporary / "build.py"
        fontforge_script.write_text(
            "import fontforge\n"
            "font = fontforge.font()\n"
            "font.encoding = 'UnicodeFull'\n"
            "font.fontname = 'PaleoHebrewImages'\n"
            "font.familyname = 'Paleo Hebrew Images'\n"
            "font.fullname = 'Paleo Hebrew Images Regular'\n"
            "font.weight = 'Regular'\n"
            "font.version = '1.0'\n"
            "font.copyright = 'Digitized from the supplied paleo-hebrew images.'\n"
            "font.ascent = 950\n"
            "font.descent = 50\n"
            "font.createChar(0x20, 'space').width = 360\n"
            + "".join(
                f"g=font.createChar({cp},'uni{cp:04X}');"
                f"g.importOutlines({str(svg)!r});"
                "g.removeOverlap();g.correctDirection();"
                "g.transform((1,0,0,-1,45,980));"
                f"g.transform((1,0,0,1,0,{(BASELINE_ROW - bottom) * PIXEL}-g.boundingBox()[1]));"
                "g.simplify(1.5,('mergelines','smoothcurves'));"
                "g.removeOverlap();g.addExtrema('only_good');g.correctDirection();g.round();"
                f"g.width={width * PIXEL + LEFT_BEARING + RIGHT_BEARING}\n"
                for name, cp, svg, width, bottom in glyphs
            )
            + "\n".join(
                f"g=font.createChar({final});g.addReference(font[{base}].glyphname);"
                f"g.width=font[{base}].width"
                for final, base in FINAL_FORMS.items()
            )
            + f"\nfont.generate({str(OUTPUT)!r}, flags=('opentype',))\n"
        )
        environment = os.environ.copy()
        environment["XDG_CONFIG_HOME"] = str(temporary)
        subprocess.run(
            ["fontforge", "-lang=py", "-script", str(fontforge_script)],
            check=True,
            env=environment,
        )


if __name__ == "__main__":
    main()
