# Bash: source bin/completions/build.sh (works with build on PATH or bin/build).
_wtn_build_complete() {
    local command=${COMP_WORDS[0]}
    local current trim kind reply i
    mapfile -t COMPREPLY < <("$command" --complete --bash "$COMP_LINE" "$COMP_POINT" \
        "${COMP_WORDS[@]:0:COMP_CWORD+1}")
    # Empty enum/free-form results must not fall back to unrelated filenames.
    compopt +o default +o dirnames +o filenames +o nospace 2>/dev/null || :
    case ${COMPREPLY[0]-} in
        @directories|@filenames)
            kind=-f
            [[ ${COMPREPLY[0]} == @directories ]] && kind=-d
            current=${COMPREPLY[1]}
            trim=${COMPREPLY[2]}
            mapfile -t COMPREPLY < <(compgen "$kind" -- "$current")
            compopt -o filenames 2>/dev/null || :
            for i in "${!COMPREPLY[@]}"; do
                reply=${COMPREPLY[i]}
                if [[ -d $reply ]]; then
                    # Readline cannot stat a path after its word-break prefix
                    # has been removed. Supply that directory slash ourselves.
                    if [[ ! -d ${reply:trim} ]]; then
                        reply=${reply%/}/
                    fi
                    if ((${#COMPREPLY[@]} == 1)); then
                        compopt -o nospace 2>/dev/null || :
                    fi
                fi
                COMPREPLY[i]=${reply:trim}
            done
            ;;
    esac
}
complete -F _wtn_build_complete build bin/build
