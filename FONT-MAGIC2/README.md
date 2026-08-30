# FONT-MAGIC2

FONT-MAGIC2 turns a photographed, scanned, or drawn early-alphabet chart into inspectable SVG sources plus SFD, OTF, TTF, proof, and provenance report. Its governing rule is source fidelity: it keeps wobble, asymmetry, variable stroke weight, damage, variants, and uncertainty rather than modernizing them.

## One command

```sh
cd FONT-MAGIC2
bin/00-fontify.sh source.jpg --name Cross-800BC
```

The default is Paleo-Hebrew with Phoenician Unicode. Use `--encoding hebrew` or `--encoding pua`; `--output DIR`, `--from N`, `--to N`, `--force`, `--keep-work`, `--monospace`, `--package full|minimal`, and `--max-ai-repairs 2` are accepted. `--no-ai` runs deliberately low-confidence deterministic guesses for debugging and CI. Ordinary runs have no interactive questions.

Outputs appear in `dist/NAME/`; the stable work run is `work/NAME-SOURCEHASH/`. Edit a decision manifest or normalized SVG there and resume with `--from 19`. Open `NAME.sfd` directly in FontForge for optional finishing; reproducible source remains the image, manifests, crops/masks, normalized SVGs, and code.

## Flow

```text
IMAGE -> PREPROCESS -> SEGMENT -> LORD: LAYOUT -> CROPS
  -> MASK CANDIDATES -> LORD: MASK CHOICE -> POTRACE
  -> LORD: TRACE QA -> NORMALIZE -> FONTFORGE -> PROOF
  -> LORD: FINAL QA -> SFD + OTF + TTF
```

Software 1.0 in `bin/` owns pixels, transforms, components, masks, traces, metrics, builds, validation, caching artifacts, reports, and deterministic application. Software 2.0 in `bin2/` uses substantial `lord` prompts only for visual/semantic judgments and returns schema-validated JSON. Malformed output never replaces a good manifest.

Each report traces Unicode → normalized SVG → clean/raw SVG → selected mask → crop → source rectangle → source SHA256. Raw inputs and intermediate candidates are never overwritten.

## Dependencies

Required: Bash, Python 3.10+, Pillow, numpy, fontTools, and FontForge with Python support. `jsonschema` is recommended (a strict minimal validator fallback exists). Potrace is strongly recommended; without it the pipeline emits exact rectilinear pixel SVGs, which preserve shape but are large and less editable. ImageMagick improves PDF generation. Optional checks use HarfBuzz `hb-shape`, `ots-sanitize`, and FontBakery. AI runs require the existing `lord` command.

```sh
python3 -m pip install -r requirements.txt
bin/01-doctor.sh
```

PDF ingest uses Pillow support where available; ImageMagick or a system PDF rasterizer may be needed for some PDFs. No dependency is installed automatically.

## Inspection and tests

The offline HTML report and proof expose crops, context, masks, traces, transforms, confidence, and review flags. Every visual stage also writes a contact sheet.

```sh
PYTHONPATH=. python3 -m unittest tests/test_core.py
tests/test_e2e.sh
```

The generated fixture has 22 pseudo-signs, labels, grid rules, noise, rotation, size variation, and disconnected components; it tests plumbing, not paleographic intelligence. For a real smoke test, pass a locally held chart directly—FONT-MAGIC does not copy it outside its provenance-preserving work directory.
