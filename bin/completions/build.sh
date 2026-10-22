# Bash: source bin/completions/build.sh (works with build on PATH or bin/build).
_wtn_build_complete() {
    local command=${COMP_WORDS[0]}
    local -a words=("${COMP_WORDS[@]:1:COMP_CWORD}")
    mapfile -t COMPREPLY < <("$command" --complete "${words[@]}")
    # Path arguments use Bash's filename completion, including paths with spaces.
    if ((${#COMPREPLY[@]} == 0)); then
        compopt -o default
    fi
}
complete -F _wtn_build_complete build bin/build
