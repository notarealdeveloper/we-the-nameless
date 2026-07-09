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
| `04-bc15c-proto-sinaitic-generic-b.ttf` | `s` | ש | `04-bc15c-proto-sinaitic-generic-b.ttf` | `g` |
| `04-bc15c-proto-sinaitic-generic-b.ttf` | `g` | ג | `04-bc15c-proto-sinaitic-generic-b.ttf` | `S` |
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
| `04-bc15c-proto-sinaitic-generic-a.ttf` | `z` | ז | `04-bc15c-proto-sinaitic-15th-century.ttf` | `z` |
| `04-bc15c-proto-sinaitic-generic-a.ttf` | `o` | ע | `04-bc15c-proto-sinaitic-15th-century.ttf` | `o` |
| `04-bc15c-proto-sinaitic-generic-a.ttf` | `q` | ק | `04-bc15c-proto-sinaitic-15th-century.ttf` | `q` |
| `04-bc15c-proto-sinaitic-generic-b.ttf` | `T` | ט | `04-bc15c-proto-sinaitic-generic-a.ttf` | `T` |
| `04-bc15c-proto-sinaitic-generic-b.ttf` | `z` | ז | `04-bc15c-proto-sinaitic-15th-century.ttf` | `z` |
| `04-bc15c-proto-sinaitic-generic-b.ttf` | `o` | ע | `04-bc15c-proto-sinaitic-15th-century.ttf` | `o` |
| `04-bc15c-proto-sinaitic-generic-b.ttf` | `q` | ק | `04-bc15c-proto-sinaitic-15th-century.ttf` | `q` |
| `04-bc15c-proto-sinaitic-generic-a.ttf` | `S` | ס | `08-bc10c-paleo-hebrew-gezer-a.ttf` | `S` |
| `04-bc15c-proto-sinaitic-generic-b.ttf` | `S` | ס | `08-bc10c-paleo-hebrew-gezer-b.ttf` | `S` |
| `08-bc10c-paleo-hebrew-gezer-a.ttf` | `g` | ג | `08-bc10c-paleo-hebrew-tel-zayit.ttf` | `g` |
| `08-bc10c-paleo-hebrew-gezer-a.ttf` | `e` | ה | `08-bc10c-paleo-hebrew-tel-zayit.ttf` | `e` |
| `08-bc10c-paleo-hebrew-gezer-a.ttf` | `T` | ט | `08-bc10c-paleo-hebrew-tel-zayit.ttf` | `T` |
| `08-bc10c-paleo-hebrew-gezer-a.ttf` | `n` | נ | `08-bc10c-paleo-hebrew-tel-zayit.ttf` | `n` |
| `08-bc10c-paleo-hebrew-gezer-b.ttf` | `g` | ג | `08-bc10c-paleo-hebrew-tel-zayit.ttf` | `g` |
| `08-bc10c-paleo-hebrew-gezer-b.ttf` | `e` | ה | `08-bc10c-paleo-hebrew-tel-zayit.ttf` | `e` |
| `08-bc10c-paleo-hebrew-gezer-b.ttf` | `T` | ט | `08-bc10c-paleo-hebrew-tel-zayit.ttf` | `T` |
| `08-bc10c-paleo-hebrew-gezer-b.ttf` | `n` | נ | `08-bc10c-paleo-hebrew-tel-zayit.ttf` | `n` |
| `09-bc09c-paleo-hebrew-mesha-stele-a.ttf` | `o` | ע | `09-bc09c-paleo-hebrew-tel-dan-a.ttf` | `o` |
| `09-bc09c-paleo-hebrew-mesha-stele-b.ttf` | `o` | ע | `09-bc09c-paleo-hebrew-tel-dan-a.ttf` | `o` |
| `09-bc09c-paleo-hebrew-standard-a.ttf` | `o` | ע | `09-bc09c-paleo-hebrew-tel-dan-a.ttf` | `o` |
| `09-bc09c-paleo-hebrew-standard-b.ttf` | `o` | ע | `09-bc09c-paleo-hebrew-tel-dan-a.ttf` | `o` |
| `02-bc19c-proto-sinaitic-wadi-el-hol-inscription.ttf` | `o` | ע | `fonts-proto-sinaitic-wadi-el-hol/Wadi_el-hol-O.svg` | `svg` |
| `04-bc15c-proto-sinaitic-generic-a.ttf` | `o` | ע | `fonts-proto-sinaitic-generic/Proto-semiticO-01.svg` | `svg` |
| `06-bc13c-proto-canaanite-a.ttf` | `o` | ע | `fonts-proto-sinaitic-generic/Proto-semiticO-01.svg` | `svg` |
| `06-bc13c-proto-canaanite-b.ttf` | `o` | ע | `fonts-proto-sinaitic-generic/Proto-semiticO-01.svg` | `svg` |
| `07-bc12c-proto-canaanite-izbet-sartah-a.ttf` | `o` | ע | `fonts-proto-sinaitic-generic/Proto-semiticO-01.svg` | `svg` |
| `07-bc12c-proto-canaanite-izbet-sartah-b.ttf` | `o` | ע | `fonts-proto-sinaitic-generic/Proto-semiticO-01.svg` | `svg` |
| `08-bc10c-paleo-hebrew-gezer-a.ttf` | `o` | ע | `fonts-proto-sinaitic-generic/Proto-semiticO-01.svg` | `svg` |
| `08-bc10c-paleo-hebrew-gezer-b.ttf` | `o` | ע | `fonts-proto-sinaitic-generic/Proto-semiticO-01.svg` | `svg` |
| `01-bc32c-egyptian-hieroglyphs-noto-sans.ttf` | `c` `q` `r` `s` `t` | צ ק ר ש ת | original Noto Egyptian signs | corrected ancestry order after deleting the extra Pe candidate |

Several missing or weak ayin forms were replaced from local Proto-Sinaitic SVG drawings or the Tel Dan ayin, as listed above.

The Serabit el-Khadim and Wadi el-Hol inscription fonts were also emboldened after substitution so their row weight matches the other Proto-Sinaitic comparison fonts more closely.
