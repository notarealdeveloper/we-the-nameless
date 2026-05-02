# Proto-Sinaitic Local Font — Minimal Working Project

Note: The glyphs are currently dummy files, not real Proto Sinaitic.

This is a tiny Linux-friendly font project for making a local experimental Proto-Sinaitic / early alphabet font from SVG glyphs.

It uses:

- `glyphs/*.svg` — one SVG per glyph
- `glyph_map.tsv` — glyph name → Unicode Private Use Area codepoint
- `scripts/build_font.py` — FontForge build script
- `Makefile` — convenience commands

The included SVGs are deliberately simple placeholder glyphs. Replace them with your own cleaned SVGs from drawings, tracings, or public-domain sources.

## Why Private Use Area?

Proto-Sinaitic is not encoded as a normal Unicode block. So this project maps the glyphs to the Unicode Private Use Area:

```text
U+E000 .. U+E015
```

That means the font works locally, but the text is only meaningful on machines with the font installed.

## Install dependencies

### Arch Linux

```bash
sudo pacman -S fontforge make
```

### Debian / Ubuntu

```bash
sudo apt install fontforge make
```

### Nix / NixOS

```bash
nix develop
```

or just:

```bash
nix shell nixpkgs#fontforge nixpkgs#gnugrep nixpkgs#gnumake
```

## Build the font

```bash
make
```

Output:

```text
dist/ProtoSinaiticLocal.ttf
```

## Install locally

```bash
make install
```

This copies the font to:

```text
~/.local/share/fonts
```

and runs:

```bash
fc-cache -fv
```

## Test in LibreOffice / browser / LaTeX

The file `sample.html` contains PUA characters using the font.

Open it in a browser after installing the font.

## LuaLaTeX test

```tex
\documentclass{article}
\usepackage{fontspec}
\newfontfamily\psfont{Proto Sinaitic Local}
\begin{document}
{\psfont \char"E000 \char"E001 \char"E002 \char"E003 \char"E004}
\end{document}
```

## Replacing the glyphs

Best path:

1. Prefer SVG over PNG.
2. If starting from PNG, trace it first with Inkscape or Potrace.
3. Keep each glyph inside a `1000 × 1000` SVG viewport.
4. Use black filled paths, not strokes, if possible.
5. Keep filenames matching `glyph_map.tsv`.
6. Rebuild with `make`.

## Notes

This project intentionally does not pretend that the included forms are scholarly-normalized Proto-Sinaitic. Treat it as infrastructure: a reproducible font pipeline you can replace glyph-by-glyph.
