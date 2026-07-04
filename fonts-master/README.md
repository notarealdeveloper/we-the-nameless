# WTN Master Font Repairs

These fonts encode one semantic value space: the Hebrew alphabet rendered in several historical hands.
The canonical key map is `../bin/alphabet`; every Hebrew, Latin, Greek, and Cyrillic alias in that map is copied from the corresponding repaired master glyph inside each font.

The following master-letter glyphs were absent, encoded as `.notdef`, or represented by a 1x1 placeholder and were substituted from nearby historical fonts.

| Font | Letter key | Hebrew value | Donor font | Donor key |
| --- | --- | --- | --- | --- |
| none in this repair pass | | | | |

The following glyphs existed but were judged historically or visually wrong for their assigned letter and were replaced deliberately.

| Font | Letter key | Hebrew value | Donor font | Donor key |
| --- | --- | --- | --- | --- |
| `02-bc19c-proto-sinaitic-wadi-el-hol-inscription.ttf` | `T` | ט | `04-bc15c-proto-sinaitic-15th-century.ttf` | `T` |
| `02-bc19c-proto-sinaitic-wadi-el-hol-inscription.ttf` | `z` | ז | `04-bc15c-proto-sinaitic-15th-century.ttf` | `z` |
| `02-bc19c-proto-sinaitic-wadi-el-hol-inscription.ttf` | `o` | ע | `04-bc15c-proto-sinaitic-15th-century.ttf` | `o` |
| `02-bc19c-proto-sinaitic-wadi-el-hol-inscription.ttf` | `q` | ק | `04-bc15c-proto-sinaitic-15th-century.ttf` | `q` |
| `02-bc19c-proto-sinaitic-wadi-el-hol-inscription.ttf` | `k` | כ | `04-bc15c-proto-sinaitic-15th-century.ttf` | `k` |
| `02-bc19c-proto-sinaitic-wadi-el-hol-inscription.ttf` | `l` | ל | `04-bc15c-proto-sinaitic-15th-century.ttf` | `l` |
| `02-bc19c-proto-sinaitic-wadi-el-hol-inscription.ttf` | `S` | ס | `04-bc15c-proto-sinaitic-15th-century.ttf` | `S` |
| `02-bc19c-proto-sinaitic-wadi-el-hol-inscription.ttf` | `c` | צ | `04-bc15c-proto-sinaitic-15th-century.ttf` | `c` |
| `02-bc19c-proto-sinaitic-wadi-el-hol-inscription.ttf` | `n` | נ | `04-bc15c-proto-sinaitic-15th-century.ttf` | `n` |
| `03-bc18c-proto-sinaitic-serabit-el-khadim-inscription.ttf` | `T` | ט | `04-bc15c-proto-sinaitic-15th-century.ttf` | `T` |
| `03-bc18c-proto-sinaitic-serabit-el-khadim-inscription.ttf` | `z` | ז | `04-bc15c-proto-sinaitic-15th-century.ttf` | `z` |
| `03-bc18c-proto-sinaitic-serabit-el-khadim-inscription.ttf` | `o` | ע | `04-bc15c-proto-sinaitic-15th-century.ttf` | `o` |
| `03-bc18c-proto-sinaitic-serabit-el-khadim-inscription.ttf` | `q` | ק | `04-bc15c-proto-sinaitic-15th-century.ttf` | `q` |
| `03-bc18c-proto-sinaitic-serabit-el-khadim-inscription.ttf` | `s` | ש | `04-bc15c-proto-sinaitic-15th-century.ttf` | `s` |
| `04-bc15c-proto-sinaitic-generic-a.ttf` | `T` | ט | `04-bc15c-proto-sinaitic-15th-century.ttf` | `T` |
| `04-bc15c-proto-sinaitic-generic-b.ttf` | `T` | ט | `04-bc15c-proto-sinaitic-15th-century.ttf` | `T` |
| `01-bc32c-egyptian-hieroglyphs-noto-sans.ttf` | `c`-`t` | צ-ת | same font plus original Noto Egyptian Taw sign | shifted after deleting the extra Pe candidate |

The Serabit el-Khadim and Wadi el-Hol inscription fonts were also emboldened after substitution so their row weight matches the other Proto-Sinaitic comparison fonts more closely. The Egyptian row receives only a small outline stroke to keep it slightly darker without turning it into a bold style.
