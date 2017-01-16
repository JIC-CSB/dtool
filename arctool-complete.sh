_arctool_completion() {
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   _ARCTOOL_COMPLETE=complete $1 ) )
    return 0
}

complete -F _arctool_completion -o default arctool;
