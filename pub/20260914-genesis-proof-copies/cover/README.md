# Paperback covers

`simple/` contains the original restrained TeX cover. `fancy/` uses the
text-free `fancy/assets/back.png` artwork for both panels and a central crop
on the spine, framed by fine gold rules. Front and spine text share the
simple cover’s vertical positions; the front also uses its font sizes.
`fancy/assets/front.png` is the original artwork with embedded titles.

From the repository root:

```sh
make genesis-cover
make genesis-cover COVER_STYLE=fancy
make genesis-kdp KDP_COVER_STYLE=fancy
```

The two mini-projects can also be invoked directly from the repository root
with `make -C pub/cover/simple` or `make -C pub/cover/fancy`. They write
`pub/01-genesis/01-genesis-cover-simple.pdf` and
`pub/01-genesis/01-genesis-cover-fancy.pdf`, respectively.

`bin/kdp-cover` reads the final interior PDF's page count. For the default
Standard Color stock it uses a `page_count * 0.002252 in` spine, a
`14.25 in + spine` wrap width, and a `10.25 in` wrap height. Spine labels are
constrained to the spine width minus `0.125 in`, leaving the required
`0.0625 in` clearance at each fold.

The staged publishing workflow, separate upload paths, and validation reports are
documented in [doc/publishing.md](../../doc/publishing.md).
