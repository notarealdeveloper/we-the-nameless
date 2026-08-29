_egypt_complete() {
 local cur=${COMP_WORDS[COMP_CWORD]}
 if [[ $cur == -* ]]; then COMPREPLY=( $(compgen -W '--all --facts --format --category --codepoint --completion --help --update --version' -- "$cur") )
 else mapfile -t COMPREPLY < <(egypt --complete "$cur"); fi
}
complete -F _egypt_complete egypt
