#!/usr/bin/env python3
"""Print the PUA codepoints and literal characters from glyph_map.tsv."""
import csv

with open('glyph_map.tsv', encoding='utf-8') as f:
    for row in csv.reader(f, delimiter='\t'):
        if not row or row[0].startswith('#'):
            continue
        name, cp_hex = row[0], row[1]
        cp = int(cp_hex, 16)
        print(f'{name:8s} U+{cp_hex} {chr(cp)}')
