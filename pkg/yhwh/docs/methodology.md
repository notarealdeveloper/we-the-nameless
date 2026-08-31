# Methodology

## Parsing contract

The parser is a balanced-brace scanner, not a full TeX interpreter. It handles
comments, nested groups, source commands, common transparent formatting wrappers,
and explicit annotation wrappers. It retains the complete raw verse slice so a
future parser can recover anything the renderer did not understand.

Source macro suffixes are discovered from paired `hSOURCE`/`eSOURCE` commands.
They are not limited to J/E/P. Nested source commands create nested character
ranges; the innermost active assignment controls rendered characters.

## Search normalization

English literal search is NFC-normalized, whitespace-collapsed, and casefolded by
default. One-token literals use whitespace boundaries. Phrases preserve spaces.

Hebrew search uses NFD internally to remove Hebrew combining marks when niqqud is
not significant. It removes all whitespace by default. A position map projects
normalized regex/literal matches back to original rendered strings.

`matres="internal"` removes א, ה, ו, and י only when internal to a
whitespace-delimited token. `matres="all"` removes them everywhere. Neither is
default because both intentionally merge distinct forms.

## Frequency contract

A token is one maximal run of non-whitespace Unicode code points. Punctuation,
maqaf, apostrophes, and dashes are not stripped. This deliberately keeps the
notion of `Word` simple and observable.

For a mixed token, fractional attribution computes overlap in rendered character
space and normalizes it to one total token. Alternative modes are exposed because
no single choice answers every philological question.

## Lexical evidence

A source profile reports:

- raw occurrence count;
- rate per million source tokens;
- smoothed `P(word | source)` and surprisal;
- `P(source | word)` within observed occurrences;
- log2 enrichment against all other sources;
- shrinkage-adjusted weighted log-odds z-score;
- pointwise mutual information;
- count-weighted information contribution.

The informative beta prior is pooled from the whole analyzed corpus. This keeps a
hapax from outranking a stable repeated difference merely because its raw ratio is
infinite.

## Attribution model

The default training scope is Torah only. Literal labels are mapped to J/E/P/R/D
for the default classifier; the mapping is configurable. Every whitespace token
enters a smoothed multinomial model. Character 2–5-grams provide bounded backoff
for unseen words. N-gram log probabilities are averaged per unknown token so long
forms cannot generate unlimited pseudo-independent evidence.

Naive Bayes assumes conditional token independence and is not a historical author
oracle. It is useful as a reproducible evidence meter. Compare raw evidence bits,
coverage, and token contributions; do not report only the winning label.
