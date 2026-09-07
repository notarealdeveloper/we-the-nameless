# Paperback covers

`simple/` contains the original restrained TeX cover. `fancy/` uses
`img/covers/we-cover-10.png` on the front and the wordless companion artwork
in `fancy/assets/back.png` on the back.

From the repository root:

```sh
make genesis-cover
make genesis-cover COVER_STYLE=fancy
make genesis-kdp COVER_STYLE=fancy
```

The two mini-projects can also be invoked directly with `make -C
cover/simple` or `make -C cover/fancy`.

`bin/kdp-cover` reads the final interior PDF's page count. For the default
Standard Color stock it uses a `page_count * 0.002252 in` spine, a
`14.25 in + spine` wrap width, and a `10.25 in` wrap height. Spine labels are
constrained to the spine width minus `0.125 in`, leaving the required
`0.0625 in` clearance at each fold.
