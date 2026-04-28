---
title: "Pandoc → LuaLaTeX POC"
author: "J"
lang: en
fontsize: 11pt
documentclass: article
geometry:
  - margin=1in
mainfont: Libertinus Serif
monofont: Libertinus Mono
colorlinks: true
toc: false
header-includes:
  - |
    \usepackage{fontspec}
    \usepackage{xcolor}
    \usepackage{longtable}
    \usepackage{booktabs}
    \usepackage{fancyvrb}
    \newcommand{\Psrc}[1]{\textcolor{blue}{\textbf{#1}}}
    \newcommand{\Jsrc}[1]{\textcolor{green!50!black}{#1}}
    \newcommand{\Rsrc}[1]{\textcolor{cyan!50!black}{#1}}
---

# Plain markdown still works

This is ordinary Pandoc Markdown with **bold**, *italics*, tables, lists, code, and block quotes.

## Semantic spans

[P source]{.P}  
[J source]{.J}  
[Redactor]{.R}

## Semantic divs

::: {.P}
This whole block is tagged as Priestly material.
:::

::: {.J}
This whole block is tagged as J material.
:::

## A verse-like structure

::: {.verse}
::: {.hebrew}
בְּיוֹם עֲשׂוֹת יְהוָה אֱלֹהִים אֶרֶץ וְשָׁמָיִם
:::

::: {.english}
In the day that YHWH God made earth and skies.
:::
:::

## Table

| Source | Color | Notes |
|---|---|---|
| P | blue | bold |
| J | green | plain |
| R | cyan | plain |

## Code

```python
print("hello")
```

That uses only Markdown, metadata, and semantic classes. The classes are what your filter will target.

---

## `filters/verse.lua`

This is a **Pandoc Lua filter**, not LuaLaTeX. It rewrites semantic classes into LaTeX-ish output at the writer stage, while letting you keep the source in Markdown. Pandoc has a built-in Lua interpreter for filters, so this works without external Lua dependencies. 4

```lua
function Span(el)
    local classes = el.classes

    if classes:includes("P") then
        return pandoc.RawInline("latex", "\\Psrc{")
            .. el.content
            .. pandoc.RawInline("latex", "}")
    end

    if classes:includes("J") then
        return pandoc.RawInline("latex", "\\Jsrc{")
            .. el.content
            .. pandoc.RawInline("latex", "}")
    end

    if classes:includes("R") then
        return pandoc.RawInline("latex", "\\Rsrc{")
            .. el.content
            .. pandoc.RawInline("latex", "}")
    end
end

function Div(el)
    local classes = el.classes

    if classes:includes("P") then
        return {
            pandoc.RawBlock("latex", "\\begin{quote}\\Psrc{"),
            el.content,
            pandoc.RawBlock("latex", "}\\end{quote}")
        }
    end

    if classes:includes("J") then
        return {
            pandoc.RawBlock("latex", "\\begin{quote}\\Jsrc{"),
            el.content,
            pandoc.RawBlock("latex", "}\\end{quote}")
        }
    end

    if classes:includes("R") then
        return {
            pandoc.RawBlock("latex", "\\begin{quote}\\Rsrc{"),
            el.content,
            pandoc.RawBlock("latex", "}\\end{quote}")
        }
    end

    if classes:includes("verse") then
        local hebrew = {}
        local english = {}

        for _, child in ipairs(el.content) do
            if child.t == "Div" and child.classes:includes("hebrew") then
                hebrew = child.content
            elseif child.t == "Div" and child.classes:includes("english") then
                english = child.content
            end
        end

        return {
            pandoc.RawBlock("latex", "\\begin{longtable}{p{0.48\\textwidth} p{0.48\\textwidth}}"),
            pandoc.Plain(english),
            pandoc.RawBlock("latex", " & "),
            pandoc.Plain(hebrew),
            pandoc.RawBlock("latex", "\\\\"),
            pandoc.RawBlock("latex", "\\end{longtable}")
        }
    end
end
```