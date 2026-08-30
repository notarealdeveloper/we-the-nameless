#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
usage(){ echo "usage: bin/00-fontify.sh IMAGE [--name NAME] [--script paleo-hebrew] [--encoding phoenician|hebrew|pua] [--output DIR] [--config FILE] [--from N] [--to N] [--force] [--keep-work] [--no-ai] [--max-ai-repairs N] [--monospace] [--package full|minimal]"; }
[[ $# -ge 1 ]] || { usage; exit 2; }; SOURCE=$1; shift; [[ -r "$SOURCE" ]] || { echo "fatal: unreadable source: $SOURCE" >&2; exit 2; }
NAME=$(basename "$SOURCE"); NAME=${NAME%.*}; SCRIPT=paleo-hebrew; ENCODING=phoenician; OUTPUT=; FROM=1; TO=25; FORCE=0; KEEP=0; NOAI=0; REPAIRS=2; MONO=0; PACKAGE=full; CONFIG=
while (($#)); do case $1 in
 --name) NAME=$2; shift 2;; --script) SCRIPT=$2; shift 2;; --encoding) ENCODING=$2; shift 2;; --output) OUTPUT=$2; shift 2;; --config) CONFIG=$2; shift 2;; --from) FROM=$2; shift 2;; --to) TO=$2; shift 2;; --force) FORCE=1; shift;; --keep-work) KEEP=1; shift;; --no-ai) NOAI=1; shift;; --max-ai-repairs) REPAIRS=$2; shift 2;; --monospace) MONO=1; shift;; --package) PACKAGE=$2; shift 2;; -h|--help) usage; exit;; *) echo "unknown option: $1" >&2; usage; exit 2;; esac; done
case $ENCODING in phoenician|hebrew|pua) ;; *) echo "invalid encoding: $ENCODING" >&2; exit 2;; esac
NAME=$(printf '%s' "$NAME" | sed 's/[^A-Za-z0-9_.-]/-/g'); [[ -n "$OUTPUT" ]] || OUTPUT="$ROOT/dist/$NAME"
SRC_HASH=$(sha256sum "$SOURCE" | cut -c1-12); RUN_ID="${NAME}-${SRC_HASH}"; RUN="$ROOT/work/$RUN_ID"; mkdir -p "$RUN/manifests" "$RUN/logs"
PYTHONPATH="$ROOT" python3 - "$ROOT/config/default.json" "$CONFIG" "$RUN/manifests/config.json" "$NAME" "$SCRIPT" "$ENCODING" "$OUTPUT" "$REPAIRS" "$MONO" "$PACKAGE" <<'PY'
import json,sys,os,tempfile
default,custom,out,name,script,encoding,output,repairs,mono,package=sys.argv[1:]
d=json.load(open(default))
if custom:
 c=json.load(open(custom))
 def merge(a,b):
  for k,v in b.items(): a[k]=merge(a.get(k,{}),v) if isinstance(v,dict) and isinstance(a.get(k),dict) else v
  return a
 merge(d,c)
d['script']=script; d['encoding']=encoding; d['font']['name']=name; d['output']=os.path.abspath(output); d['ai']['max_repairs']=int(repairs); d['normalization']['monospace']=bool(int(mono)); d['package']=package
fd,tmp=tempfile.mkstemp(dir=os.path.dirname(out)); os.close(fd); open(tmp,'w').write(json.dumps(d,indent=2)+'\n'); os.replace(tmp,out)
PY
run(){ local n=$1 label=$2; shift 2; (( n < FROM || n > TO )) && return 0; local log="$RUN/logs/$(printf '%02d' "$n")-$label.log"; echo "[$(printf '%02d' "$n")] $label"; "$@" > >(tee "$log") 2> >(tee -a "$log" >&2); }
stage(){ run "$1" "$2" env PYTHONPATH="$ROOT" python3 "$ROOT/bin/run-stage.py" "$3" --run "$RUN" "${@:4}"; }
run 1 doctor "$ROOT/bin/01-doctor.sh" --runtime
stage 2 ingest ingest --source "$SOURCE"; stage 3 preprocess preprocess; stage 4 segment segment
if ((NOAI)); then stage 5 layout-fallback layout-fallback; else run 5 understand-layout "$ROOT/bin2/05-understand-layout.sh" "$RUN"; fi
stage 6 extract extract
if ((NOAI)); then stage 7 identify-fallback identify-fallback; else run 7 identify-glyphs "$ROOT/bin2/07-identify-glyphs.sh" "$RUN"; fi
stage 8 masks masks
if ((NOAI)); then stage 9 mask-fallback mask-fallback; else run 9 choose-masks "$ROOT/bin2/09-choose-masks.sh" "$RUN"; fi
stage 10 apply-mask-decisions apply-masks; stage 11 trace trace; stage 12 clean-outlines clean
if ((NOAI)); then stage 13 repairs-fallback repairs-fallback; else run 13 judge-traces "$ROOT/bin2/13-judge-traces.sh" "$RUN"; fi
stage 14 repair-and-retrace repair; stage 15 measure measure
if ((NOAI)); then stage 16 normalization-fallback normalization-fallback; else run 16 design-normalization "$ROOT/bin2/16-design-normalization.sh" "$RUN"; fi
stage 17 normalize normalize
if ((NOAI)); then stage 18 variants-fallback variants-fallback; else run 18 select-variants "$ROOT/bin2/18-select-variants.sh" "$RUN"; fi
stage 19 build-font build; stage 20 proof proof
if ((NOAI)); then stage 21 qa-fallback qa-fallback; else run 21 qa-font "$ROOT/bin2/21-qa-font.sh" "$RUN"; fi
stage 22 apply-qa apply-qa; stage 23 validate validate; stage 24 report report; stage 25 package package
if (( TO >= 25 )); then
 QA=$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d["overall_score"]); print(", ".join(d["review_recommended"]) or "none")' "$RUN/manifests/final-qa.json")
 SCORE=$(printf '%s\n' "$QA" | sed -n '1p'); REVIEW=$(printf '%s\n' "$QA" | sed -n '2p')
 printf '\nFont built successfully.\n\nOTF:   %s/%s.otf\nTTF:   %s/%s.ttf\nSFD:   %s/%s.sfd\nProof: %s/proof.pdf\nReport: %s/report.html\n\nQA score: %s/100\nReview recommended: %s\n' "$OUTPUT" "$NAME" "$OUTPUT" "$NAME" "$OUTPUT" "$NAME" "$OUTPUT" "$OUTPUT" "$SCORE" "$REVIEW"
fi
