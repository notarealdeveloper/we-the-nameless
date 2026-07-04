# WTN Master Font Repairs

These fonts encode one semantic value space: the Hebrew alphabet rendered in several historical hands.
The canonical key map is `../bin/alphabet`; every Hebrew, Latin, Greek, and Cyrillic alias in that map is copied from the corresponding repaired master glyph inside each font.

The following master-letter glyphs were absent, encoded as `.notdef`, or represented by a 1x1 placeholder and were substituted from nearby historical fonts.

| Font | Letter key | Hebrew value | Donor font | Donor key |
| --- | --- | --- | --- | --- |
| `03-bc15c-proto-sinaitic-15th-century-a.ttf` | `o` | ע | `01-bc32c-egyptian-hieroglyphs-noto-sans.ttf` | `o` |
| `03-bc15c-proto-sinaitic-15th-century-b.ttf` | `o` | ע | `03-bc15c-proto-sinaitic-15th-century-a.ttf` | `o` |
| `03-bc15c-proto-sinaitic-generic-a.ttf` | `o` | ע | `03-bc15c-proto-sinaitic-15th-century.ttf` | `o` |
| `03-bc15c-proto-sinaitic-generic-b.ttf` | `o` | ע | `03-bc15c-proto-sinaitic-generic-a.ttf` | `o` |
| `03-bc15c-proto-sinaitic-serabit-el-khadim-inscription.ttf` | `e` | ה | `03-bc15c-proto-sinaitic-15th-century.ttf` | `e` |
| `03-bc15c-proto-sinaitic-wadi-el-hol-inscription.ttf` | `d` | ד | `03-bc15c-proto-sinaitic-serabit-el-khadim-inscription.ttf` | `d` |
| `05-bc13c-proto-canaanite-a.ttf` | `o` | ע | `04-bc14c-ugaritic-noto-sans.ttf` | `o` |
| `05-bc13c-proto-canaanite-b.ttf` | `o` | ע | `05-bc13c-proto-canaanite-a.ttf` | `o` |
| `06-bc12c-proto-canaanite-izbet-sartah-a.ttf` | `m` | מ | `05-bc13c-proto-canaanite-b.ttf` | `m` |
| `06-bc12c-proto-canaanite-izbet-sartah-a.ttf` | `o` | ע | `05-bc13c-proto-canaanite-b.ttf` | `o` |
| `06-bc12c-proto-canaanite-izbet-sartah-b.ttf` | `m` | מ | `06-bc12c-proto-canaanite-izbet-sartah-a.ttf` | `m` |
| `06-bc12c-proto-canaanite-izbet-sartah-b.ttf` | `o` | ע | `06-bc12c-proto-canaanite-izbet-sartah-a.ttf` | `o` |
| `07-bc10c-paleo-hebrew-gezer-a.ttf` | `g` | ג | `06-bc12c-proto-canaanite-izbet-sartah-b.ttf` | `g` |
| `07-bc10c-paleo-hebrew-gezer-a.ttf` | `e` | ה | `06-bc12c-proto-canaanite-izbet-sartah-b.ttf` | `e` |
| `07-bc10c-paleo-hebrew-gezer-a.ttf` | `T` | ט | `06-bc12c-proto-canaanite-izbet-sartah-b.ttf` | `T` |
| `07-bc10c-paleo-hebrew-gezer-a.ttf` | `n` | נ | `06-bc12c-proto-canaanite-izbet-sartah-b.ttf` | `n` |
| `07-bc10c-paleo-hebrew-gezer-a.ttf` | `o` | ע | `06-bc12c-proto-canaanite-izbet-sartah-b.ttf` | `o` |
| `07-bc10c-paleo-hebrew-gezer-b.ttf` | `g` | ג | `07-bc10c-paleo-hebrew-gezer-a.ttf` | `g` |
| `07-bc10c-paleo-hebrew-gezer-b.ttf` | `e` | ה | `07-bc10c-paleo-hebrew-gezer-a.ttf` | `e` |
| `07-bc10c-paleo-hebrew-gezer-b.ttf` | `T` | ט | `07-bc10c-paleo-hebrew-gezer-a.ttf` | `T` |
| `07-bc10c-paleo-hebrew-gezer-b.ttf` | `n` | נ | `07-bc10c-paleo-hebrew-gezer-a.ttf` | `n` |
| `07-bc10c-paleo-hebrew-gezer-b.ttf` | `o` | ע | `07-bc10c-paleo-hebrew-gezer-a.ttf` | `o` |
| `07-bc10c-paleo-hebrew-tel-zayit.ttf` | `o` | ע | `07-bc10c-paleo-hebrew-gezer-b.ttf` | `o` |
| `08-bc09c-paleo-hebrew-mesha-stele-a.ttf` | `o` | ע | `07-bc10c-phoenician-noto-sans.ttf` | `o` |
| `08-bc09c-paleo-hebrew-mesha-stele-b.ttf` | `o` | ע | `08-bc09c-paleo-hebrew-mesha-stele-a.ttf` | `o` |
| `08-bc09c-paleo-hebrew-standard-a.ttf` | `o` | ע | `08-bc09c-paleo-hebrew-robo.ttf` | `o` |
| `08-bc09c-paleo-hebrew-standard-b.ttf` | `o` | ע | `08-bc09c-paleo-hebrew-standard-a.ttf` | `o` |
| `13-bc02c-paleo-hebrew-isaiah-scroll-a.ttf` | `o` | ע | `12-bc05c-imperial-aramaic-noto-sans.ttf` | `o` |
| `13-bc02c-paleo-hebrew-isaiah-scroll-b.ttf` | `o` | ע | `13-bc02c-paleo-hebrew-isaiah-scroll-a.ttf` | `o` |

The Serabit el-Khadim and Wadi el-Hol inscription fonts were also emboldened after substitution so their row weight matches the other fifteenth-century Proto-Sinaitic comparison fonts more closely.
