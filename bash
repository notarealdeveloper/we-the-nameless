#!/usr/bin/env bash
set -euo pipefail

API_BASE="https://www.sefaria.org/api/v3/texts"

PREFERRED_ENGLISH_VERSIONS=(
  "HarperCollins Study Bible, New Revised Standard Version"
  "Harper Collins Study Bible, New Revised Standard Version"
  "New Revised Standard Version"
  "NRSV"
)

SIMILAR_ENGLISH_VERSIONS=(
  "Tanakh: The Holy Scriptures, published by JPS"
  "The Contemporary Torah, Jewish Publication Society, 2006"
)

BOOKS=(
  "Genesis" "Exodus" "Leviticus" "Numbers" "Deuteronomy"
  "Joshua" "Judges" "I Samuel" "II Samuel" "I Kings" "II Kings"
  "Isaiah" "Jeremiah" "Ezekiel" "Hosea" "Joel" "Amos" "Obadiah"
  "Jonah" "Micah" "Nahum" "Habakkuk" "Zephaniah" "Haggai"
  "Zechariah" "Malachi" "Psalms" "Proverbs" "Job"
  "Song of Songs" "Ruth" "Lamentations" "Ecclesiastes" "Esther"
  "Daniel" "Ezra" "Nehemiah" "I Chronicles" "II Chronicles"
)

usage() {
  cat >&2 <<'EOF'
Usage: sefaria REF... [-o OUTPUT] [-l he|en|both] [-v VERSION] [-s] [--json]

Examples:
  sefaria gen 1 1
  sefaria Genesis 1 1
  sefaria "Genesis 1:1"
  sefaria "I Samuel" 17 4
  sefaria 1sam 17 4
  sefaria song 2 3
  sefaria gen 1 1 --lang both
  sefaria gen 1 1 --strip-niqqud
  sefaria gen 1 1 -o gen-1-1.md
  sefaria gen 1 1 --json
  sefaria gen
EOF
  exit 2
}

norm() {
  printf '%s' "$1" |
    tr '[:upper:]' '[:lower:]' |
    sed 's/[^a-z0-9]//g'
}

alias_book() {
  case "$(norm "$1")" in
    gen) echo "Genesis" ;;
    exo|ex) echo "Exodus" ;;
    lev) echo "Leviticus" ;;
    num) echo "Numbers" ;;
    deut|deu) echo "Deuteronomy" ;;
    josh) echo "Joshua" ;;
    judg) echo "Judges" ;;
    1sam|isam|1sa) echo "I Samuel" ;;
    2sam|iisam|2sa) echo "II Samuel" ;;
    1kgs|1kings|1ki) echo "I Kings" ;;
    2kgs|2kings|2ki) echo "II Kings" ;;
    isa) echo "Isaiah" ;;
    jer) echo "Jeremiah" ;;
    ezek) echo "Ezekiel" ;;
    ps|psa) echo "Psalms" ;;
    prov) echo "Proverbs" ;;
    song|sos) echo "Song of Songs" ;;
    eccl|qoh) echo "Ecclesiastes" ;;
    lam) echo "Lamentations" ;;
    dan) echo "Daniel" ;;
    neh) echo "Nehemiah" ;;
    1chr|1chron) echo "I Chronicles" ;;
    2chr|2chron) echo "II Chronicles" ;;
    *) return 1 ;;
  esac
}

resolve_book() {
  local name="$1" key exact=() matches=() b
  key="$(norm "$name")"

  if alias_book "$name" >/dev/null; then
    alias_book "$name"
    return
  fi

  for b in "${BOOKS[@]}"; do
    [[ "$(norm "$b")" == "$key" ]] && exact+=("$b")
  done
  if ((${#exact[@]})); then
    printf '%s\n' "${exact[0]}"
    return
  fi

  for b in "${BOOKS[@]}"; do
    [[ "$(norm "$b")" == "$key"* ]] && matches+=("$b")
  done

  if ((${#matches[@]} == 1)); then
    printf '%s\n' "${matches[0]}"
  elif ((${#matches[@]} > 1)); then
    printf "Ambiguous book prefix %q: " "$name" >&2
    local IFS=", "
    printf '%s\n' "${matches[*]}" >&2
    exit 1
  else
    printf '%s\n' "$name"
  fi
}

slugify() {
  local s
  s="$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9][^a-z0-9]*/-/g; s/^-//; s/-$//')"
  printf '%s\n' "${s:-book}"
}

urlencode() {
  jq -nr --arg s "$1" '$s|@uri'
}

build_ref() {
  local n=$# book
  (($n >= 1)) || usage

  if (($n == 1)); then
    resolve_book "$1"
    return
  fi

  local last="${!n}"
  local prev_i=$((n - 1))
  local prev="${!prev_i}"

  if (($n >= 3)) && [[ "${last//-/}" =~ ^[0-9]+$ ]] && [[ "$prev" =~ ^[0-9]+$ ]]; then
    book="$(resolve_book "${*:1:n-2}")"
    printf '%s %s:%s\n' "$book" "$prev" "$last"
  elif [[ "$last" =~ ^[0-9]+$ ]]; then
    book="$(resolve_book "${*:1:n-1}")"
    printf '%s %s\n' "$book" "$last"
  else
    resolve_book "$*"
  fi
}

is_whole_book() {
  [[ "$1" != *:* && ! "$1" =~ [[:space:]][0-9]+$ ]]
}

fetch_one() {
  local ref="$1" lang="$2" version="${3:-}" v enc url body code tmp
  if [[ -n "$version" ]]; then
    v="$version"
  elif [[ "$lang" == he ]]; then
    v="hebrew"
  else
    v="english"
  fi

  enc="$(urlencode "$ref")"
  url="$API_BASE/$enc?return_format=text_only&version=$(urlencode "$v")"
  tmp="$(mktemp)"
  code="$(
    curl -sS -L \
      -A sefaria \
      --max-time 30 \
      -w '%{http_code}' \
      -o "$tmp" \
      "$url" || true
  )"
  body="$(cat "$tmp")"
  rm -f "$tmp"

  if [[ "$code" != 2* ]]; then
    printf 'Sefaria HTTP error %s: %s\n' "$code" "$body" >&2
    exit 1
  fi

  printf '%s\n' "$body"
}

jq_norm='def norm: ascii_downcase | gsub("[^a-z0-9]+"; "");'

find_version() {
  local data="$1"; shift
  jq -r --argjson candidates "$(printf '%s\n' "$@" | jq -R . | jq -s .)" "$jq_norm"'
    def ev:
      (.available_versions // [])
      | map(select(.language == "en"))
      | map(select((.actualLanguage // "en") == "en" or .languageFamilyName == "english"));

    first(
      $candidates[] as $c
      | ($c | norm) as $k
      | (
          ev[]
          | select(((.versionTitle // "") | norm) == $k or ((.shortVersionTitle // "") | norm) == $k)
          | .versionTitle
        )
    ) //
    first(
      $candidates[] as $c
      | ($c | norm) as $k
      | (
          ev[]
          | select(
              ($k != "") and
              ((((.versionTitle // "") | norm) | contains($k)) or (((.shortVersionTitle // "") | norm) | contains($k)))
            )
          | .versionTitle
        )
    ) // empty
  ' <<<"$data"
}

get_version_title() {
  jq -r --arg lang "$2" '
    first((.versions // [])[] | select(.language == $lang and .text) | .versionTitle) // empty
  ' <<<"$1"
}

fetch_data() {
  local ref="$1" lang="$2" version="${3:-}" data def cur he en

  if [[ -n "$version" || "$lang" == he ]]; then
    fetch_one "$ref" "$lang" "$version"
    return
  fi

  if [[ "$lang" == en ]]; then
    data="$(fetch_one "$ref" en)"
    def="$(find_version "$data" "${PREFERRED_ENGLISH_VERSIONS[@]}")"
    [[ -n "$def" ]] || def="$(find_version "$data" "${SIMILAR_ENGLISH_VERSIONS[@]}")"
    cur="$(get_version_title "$data" en)"
    if [[ -n "$def" && "$def" != "$cur" ]]; then
      fetch_one "$ref" en "$def"
    else
      printf '%s\n' "$data"
    fi
    return
  fi

  he="$(fetch_one "$ref" he)"
  en="$(fetch_data "$ref" en)"
  jq -s '.[0] + {versions: ((.[0].versions // []) + (.[1].versions // []))}' \
    <(printf '%s\n' "$he") \
    <(printf '%s\n' "$en")
}

format_text() {
  local data="$1" lang="$2" strip="${3:-0}"

  jq -r --arg lang "$lang" --argjson strip "$strip" '
    def strip_niqqud: gsub("[\u0591-\u05BD\u05BF-\u05C7]"; "");

    def fmt_ref($book; $sections):
      if ($sections | length) == 0 then $book
      elif ($sections | length) == 1 then "\($book) \($sections[0])"
      else "\($book) \($sections[0]):\($sections[1:] | map(tostring) | join(":"))"
      end;

    def lines($text; $book; $sections; $to_sections):
      if ($text | type) == "string" then
        [[fmt_ref($book; $sections), $text]]
      elif ($text | type) != "array" then
        []
      elif all($text[]?; type == "string") then
        ($sections as $s | $to_sections as $t |
         ($s|length) > 0 and ($t|length) == ($s|length) and ($s[:-1] == $t[:-1]) and ($s[-1] != $t[-1])) as $simple
        | [range(0; $text|length) as $i
          | if $simple then
              [fmt_ref($book; ($sections[:-1] + [($sections[-1] + $i)])), $text[$i]]
            else
              [fmt_ref($book; ($sections + [$i + 1])), $text[$i]]
            end]
      else
        [range(0; $text|length) as $i
          | lines($text[$i]; $book; ($sections + [$i + 1]); $to_sections)[]]
      end;

    def get_text($l):
      first((.versions // [])[] | select(.language == $l and .text) | .text)
      // error("No \($l) text returned.");

    def format_lines($text; $do_strip):
      (.book // ((.ref // "") | split(" ")[0]) // "Book") as $book
      | (.sections // []) as $sections
      | (.toSections // []) as $to_sections
      | lines($text; $book; $sections; $to_sections)[]
      | "\(.[0])\t\(if $do_strip then (.[1] | strip_niqqud) else .[1] end)";

    if .error then error("Sefaria error: \(.error)") else . end
    | [
        if $lang == "he" or $lang == "both" then
          [format_lines(get_text("he"); $strip)] | join("\n")
        else empty end,
        if $lang == "en" or $lang == "both" then
          [format_lines(get_text("en"); false)] | join("\n")
        else empty end
      ]
    | join("\n")
  ' <<<"$data"
}

write_book() {
  local data="$1" outdir="$2" lang="$3" strip="${4:-0}" n width i path

  mkdir -p "$outdir"

  n="$(
    jq -r --arg lang "$lang" '
      def get_text($l): first((.versions // [])[] | select(.language == $l and .text) | .text);
      if ($lang == "he" or $lang == "both") then get_text("he")
      else get_text("en")
      end
      | if type == "array" then length else empty end
    ' <<<"$data"
  )"

  [[ -n "$n" ]] || {
    printf 'Whole-book request did not return chapter-level text.\n' >&2
    exit 1
  }

  width=${#n}
  ((width < 2)) && width=2

  for ((i = 1; i <= n; i++)); do
    path="$outdir/$(printf "%0${width}d.md" "$i")"
    jq -r --argjson chapter "$i" --arg lang "$lang" --argjson strip "$strip" '
      def strip_niqqud: gsub("[\u0591-\u05BD\u05BF-\u05C7]"; "");

      def fmt_ref($book; $sections):
        if ($sections | length) == 0 then $book
        elif ($sections | length) == 1 then "\($book) \($sections[0])"
        else "\($book) \($sections[0]):\($sections[1:] | map(tostring) | join(":"))"
        end;

      def lines($text; $book; $sections):
        if ($text | type) == "string" then
          [[fmt_ref($book; $sections), $text]]
        elif ($text | type) != "array" then
          []
        elif all($text[]?; type == "string") then
          [range(0; $text|length) as $i | [fmt_ref($book; ($sections + [$i + 1])), $text[$i]]]
        else
          [range(0; $text|length) as $i | lines($text[$i]; $book; ($sections + [$i + 1]))[]]
        end;

      def get_text($l):
        first((.versions // [])[] | select(.language == $l and .text) | .text)
        // error("No \($l) text returned.");

      def format_lines($text; $do_strip):
        (.book // ((.ref // "") | split(" ")[0]) // "Book") as $book
        | lines($text; $book; [$chapter])[]
        | "\(.[0])\t\(if $do_strip then (.[1] | strip_niqqud) else .[1] end)";

      [
        if $lang == "he" or $lang == "both" then
          [format_lines(get_text("he")[$chapter - 1]; $strip)] | join("\n")
        else empty end,
        if $lang == "en" or $lang == "both" then
          [format_lines(get_text("en")[$chapter - 1]; false)] | join("\n")
        else empty end
      ]
      | join("\n\n")
    ' <<<"$data" >"$path"
    printf '\n' >>"$path"
  done

  printf '%s\n' "$n"
}

output=
lang=en
version=
strip=0
raw_json=0
refs=()

while (($#)); do
  case "$1" in
    -o|--output)
      (($# >= 2)) || usage
      output="$2"
      shift 2
      ;;
    -l|--lang)
      (($# >= 2)) || usage
      case "$2" in he|en|both) lang="$2" ;; *) usage ;; esac
      shift 2
      ;;
    -v|--version)
      (($# >= 2)) || usage
      version="$2"
      shift 2
      ;;
    -s|--strip-niqqud)
      strip=1
      shift
      ;;
    --json|--raw-json)
      raw_json=1
      shift
      ;;
    -h|--help)
      usage
      ;;
    --)
      shift
      refs+=("$@")
      break
      ;;
    -*)
      usage
      ;;
    *)
      refs+=("$1")
      shift
      ;;
  esac
done

((${#refs[@]})) || usage

ref="$(build_ref "${refs[@]}")"
data="$(fetch_data "$ref" "$lang" "$version")"

if ((raw_json)); then
  if [[ -n "$output" ]]; then
    jq . <<<"$data" >"$output"
  else
    jq . <<<"$data"
  fi
  exit 0
fi

if is_whole_book "$ref"; then
  outdir="${output:-$(slugify "$ref")}"
  count="$(write_book "$data" "$outdir" "$lang" "$strip")"
  printf 'Wrote %s chapters to %s\n' "$count" "$outdir" >&2
  exit 0
fi

if [[ -n "$output" ]]; then
  format_text "$data" "$lang" "$strip" >"$output"
  printf '\n' >>"$output"
else
  format_text "$data" "$lang" "$strip"
fi
