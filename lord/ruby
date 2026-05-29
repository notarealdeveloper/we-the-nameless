#!/usr/bin/env ruby

=begin
Examples:

  sefaria gen
  sefaria exo --lang both -o exodus
  sefaria Genesis 1 1
  sefaria "Song of Songs" 2 3
  sefaria gen 1 1 --strip-niqqud
  sefaria gen 1 1 --lang both
  sefaria gen 1 1 --list-translations
  sefaria gen 1 1 --json
=end

require "fileutils"
require "json"
require "net/http"
require "optparse"
require "pathname"
require "uri"

BASE = "https://www.sefaria.org/api/v3/texts"
HEBREW_MARKS_RE = /[\u0591-\u05BD\u05BF-\u05C7]/
PREFERRED_ENGLISH_VERSIONS = [
  "HarperCollins Study Bible, New Revised Standard Version",
  "Harper Collins Study Bible, New Revised Standard Version",
  "New Revised Standard Version",
  "NRSV",
]
SIMILAR_ENGLISH_VERSIONS = [
  "Tanakh: The Holy Scriptures, published by JPS",
  "The Contemporary Torah, Jewish Publication Society, 2006",
]

BOOKS = [
  "Genesis",
  "Exodus",
  "Leviticus",
  "Numbers",
  "Deuteronomy",
  "Joshua",
  "Judges",
  "I Samuel",
  "II Samuel",
  "I Kings",
  "II Kings",
  "Isaiah",
  "Jeremiah",
  "Ezekiel",
  "Hosea",
  "Joel",
  "Amos",
  "Obadiah",
  "Jonah",
  "Micah",
  "Nahum",
  "Habakkuk",
  "Zephaniah",
  "Haggai",
  "Zechariah",
  "Malachi",
  "Psalms",
  "Proverbs",
  "Job",
  "Song of Songs",
  "Ruth",
  "Lamentations",
  "Ecclesiastes",
  "Esther",
  "Daniel",
  "Ezra",
  "Nehemiah",
  "I Chronicles",
  "II Chronicles",
]

def norm(s)
  s.downcase.gsub(/[^a-z0-9]/, "")
end

def strip_niqqud(text)
  text.gsub(HEBREW_MARKS_RE, "")
end

def book_name(s)
  key = norm(s)
  hits = BOOKS.select { |b| norm(b).start_with?(key) }

  if hits.length == 1
    hits[0]
  elsif hits.length > 1
    abort "Ambiguous book name #{s.inspect}: #{hits.join(', ')}"
  else
    s
  end
end

def slug(s)
  out = s.downcase.gsub(/[^0-9A-Za-z]+/, "-").gsub(/\A-+|-+\z/, "")
  out.empty? ? "book" : out
end

def ref_from_parts(parts)
  if parts.length >= 3 && parts[-1] =~ /^\d+$/ && parts[-2] =~ /^\d+$/
    "#{book_name(parts[0...-2].join(' '))} #{parts[-2]}:#{parts[-1]}"
  elsif parts.length >= 2 && parts[-1] =~ /^\d+$/
    "#{book_name(parts[0...-1].join(' '))} #{parts[-1]}"
  else
    book_name(parts.join(" "))
  end
end

def is_book_ref(parts, ref)
  !ref.include?(":") && !(parts.length >= 2 && parts[-1] =~ /^\d+$/)
end

def fetch_version(ref, lang: "he", version: nil)
  qs = {
    "return_format" => "text_only",
    "version" => version || { "he" => "hebrew", "en" => "english" }[lang],
  }

  uri = URI("#{BASE}/#{URI.encode_www_form_component(ref)}")
  uri.query = URI.encode_www_form(qs)

  req = Net::HTTP::Get.new(uri)
  req["User-Agent"] = "sefaria"

  res = Net::HTTP.start(uri.host, uri.port, use_ssl: true, read_timeout: 30, open_timeout: 30) do |http|
    http.request(req)
  end

  JSON.parse(res.body)
end

def available_versions(data, lang = nil)
  versions = data.fetch("available_versions", [])
  lang ? versions.select { |v| v["language"] == lang } : versions
end

def english_versions(data)
  available_versions(data, "en").select do |v|
    v.fetch("actualLanguage", "en") == "en" ||
      v["languageFamilyName"] == "english"
  end
end

def find_version(data, candidates)
  versions = english_versions(data)
  by_title = versions.to_h { |v| [norm(v["versionTitle"] || ""), v] }
  by_short = versions.to_h { |v| [norm(v["shortVersionTitle"] || ""), v] }

  candidates.each do |candidate|
    key = norm(candidate)
    return by_title[key]["versionTitle"] if by_title.key?(key)
    return by_short[key]["versionTitle"] if by_short.key?(key)
  end

  candidates.each do |candidate|
    key = norm(candidate)
    versions.each do |v|
      title = norm(v["versionTitle"] || "")
      short = norm(v["shortVersionTitle"] || "")
      return v["versionTitle"] if !key.empty? && (title.include?(key) || short.include?(key))
    end
  end

  nil
end

def default_english_version(data)
  find_version(data, PREFERRED_ENGLISH_VERSIONS) ||
    find_version(data, SIMILAR_ENGLISH_VERSIONS)
end

def fetch(ref, lang: "he", version: nil)
  return fetch_version(ref, lang: lang, version: version) if version || lang != "en"

  data = fetch_version(ref, lang: lang)
  default_version = default_english_version(data)
  if default_version && default_version != get_version_title(data, "en")
    fetch_version(ref, lang: lang, version: default_version)
  else
    data
  end
end

def fetch_all(ref, lang, version)
  return fetch(ref, lang: lang, version: version) unless lang == "both"
  abort "--version cannot be used with --lang both" if version

  he = fetch(ref, lang: "he")
  en = fetch(ref, lang: "en")
  data = he.dup
  data["versions"] = he.fetch("versions", []) + en.fetch("versions", [])
  data
end

def flatten(x)
  case x
  when String
    [x]
  when Array
    x.flat_map { |y| flatten(y) }
  else
    []
  end
end

def split_ref(ref)
  m = ref.match(/\A(?<book>.+?)\s+(?<chapter>\d+)(?::(?<verse>\d+))?\z/)
  return [m[:book], m[:chapter].to_i, (m[:verse] || 1).to_i] if m

  [ref, 1, 1]
end

def prefixed_lines(text, book, chapter = 1, verse = 1, strip: false)
  if text.is_a?(String)
    line = strip ? strip_niqqud(text) : text
    return ["#{book} #{chapter}:#{verse} #{line}"]
  end

  return [] unless text.is_a?(Array)

  out = []
  text.each_with_index do |item, i|
    if item.is_a?(Array)
      out.concat(prefixed_lines(item, book, chapter + i, 1, strip: strip))
    else
      out.concat(prefixed_lines(item, book, chapter, verse + i, strip: strip))
    end
  end
  out
end

def get_text(data, lang)
  abort "Sefaria error: #{data['error']}" if data["error"]

  data.fetch("versions", []).each do |v|
    return [v["text"], v["versionTitle"]] if v["language"] == lang && v["text"]
  end

  abort "No #{lang} text returned."
end

def get_version_title(data, lang)
  data.fetch("versions", []).each do |v|
    return v["versionTitle"] if v["language"] == lang && v["text"]
  end
  nil
end

def format_translations(data, lang)
  versions = available_versions(data)
  versions = versions.select { |v| v["language"] == lang } unless lang == "both"

  rows = versions.map do |v|
    title = v["versionTitle"] || "(untitled)"
    actual = v["actualLanguage"] || v["language"]
    short = v["shortVersionTitle"]
    suffix = short && short != title ? " (#{short})" : ""
    [actual || "", title + suffix]
  end

  rows.sort_by! { |actual, title| [actual, norm(title)] }
  rows.map { |actual, title| actual.empty? ? title : "#{actual}\t#{title}" }.join("\n")
end

def lines(data, lang, ref, strip: false)
  text, title = get_text(data, lang)
  book, chapter, verse = split_ref(ref)
  out = prefixed_lines(text, book, chapter, verse, strip: strip && lang == "he")
  [out, title]
end

def format_text(data, ref, lang, strip: false)
  if lang == "both"
    he, he_title = lines(data, "he", ref, strip: strip)
    en, en_title = lines(data, "en", ref)
    [
      "## Hebrew - #{he_title}\n#{he.join("\n")}",
      "## English - #{en_title}\n#{en.join("\n")}",
    ].join("\n\n")
  else
    out, = lines(data, lang, ref, strip: strip)
    out.join("\n")
  end
end

def write_book(data, outdir, ref, lang, strip: false)
  FileUtils.mkdir_p(outdir)
  book, = split_ref(ref)
  books = []

  if ["he", "both"].include?(lang)
    text, = get_text(data, "he")
    books << ["Hebrew", text]
  end

  if ["en", "both"].include?(lang)
    text, = get_text(data, "en")
    books << ["English", text]
  end

  count = books[0][1].length
  width = [2, count.to_s.length].max

  count.times do |i|
    parts = []
    books.each do |label, text|
      out = prefixed_lines(text[i], book, i + 1, strip: strip && label == "Hebrew")
      block = out.join("\n")
      parts << (lang == "both" ? "## #{label}\n#{block}" : block)
    end

    path = File.join(outdir, format("%0#{width}d.md", i + 1))
    File.write(path, parts.join("\n\n") + "\n", encoding: "UTF-8")
  end

  count
end

def parse_args(argv)
  args = {
    lang: "en",
    version: nil,
    list_translations: false,
    strip_niqqud: false,
    output: nil,
    json: false,
    ref: [],
  }

  parser = OptionParser.new do |p|
    p.banner = "Usage: sefaria [options] ref..."
    p.separator ""
    p.separator "Download Hebrew and/or English Bible text from Sefaria."
    p.separator ""
    p.separator DATA.read if defined?(DATA)

    p.on("-l", "--lang LANG", ["he", "en", "both"]) { |v| args[:lang] = v }
    p.on("-v", "--version VERSION") { |v| args[:version] = v }
    p.on("-t", "--list-translations") { args[:list_translations] = true }
    p.on("-s", "--strip-niqqud") { args[:strip_niqqud] = true }
    p.on("-o", "--output PATH") { |v| args[:output] = Pathname(v) }
    p.on("--json") { args[:json] = true }
  end

  parser.parse!(argv)
  args[:ref] = argv
  abort parser.to_s if args[:ref].empty?
  args
end

def main
  args = parse_args(ARGV)

  ref = ref_from_parts(args[:ref])
  data = fetch_all(ref, args[:lang], args[:version])

  if args[:json]
    text = JSON.pretty_generate(data)
  elsif args[:list_translations]
    text = format_translations(data, args[:lang])
  elsif is_book_ref(args[:ref], ref)
    outdir = args[:output] || Pathname(slug(ref))
    n = write_book(data, outdir, ref, args[:lang], strip: args[:strip_niqqud])
    warn "Wrote #{n} chapters to #{outdir}"
    return
  else
    text = format_text(data, ref, args[:lang], strip: args[:strip_niqqud])
  end

  if args[:output]
    File.write(args[:output], text + "\n", encoding: "UTF-8")
  else
    puts text
  end
end

main if $PROGRAM_NAME == __FILE__
