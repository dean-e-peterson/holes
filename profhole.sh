#!/bin/bash
# Example ./profhole.sh
#         cat perf/brief*.txt | less

LENGTH=23
PROF_FILE=misc/temp.prof
FORMAT_VER='~briefv01~'


# Args passed to this function are the args to call holey.py with.
function brief_performance_test() {
    # Record of this script's output version, holey length, and args.
    echo $FORMAT_VER  $(date "+%Y-%m-%d %H:%M:%S")
    echo
    echo ./holey.py "$@"
    echo

    # Shell timings...
    for i in {1..6}; do
        (time ./holey.py "$@") 2>&1 | grep real
    done

    # Profile...
    echo
    python3 -m cProfile -o $PROF_FILE ./holey.py "$@" > /dev/null
    # Non-EOF indents are OK; pstats doesn't mind leading spaces.
    python3 -m pstats $PROF_FILE << EOF | egrep 'ncalls|^\s*[0-9]'
        strip
        sort time
        stats 10
        quit
EOF

    # Output...?
    #python3 -m cProfile -s time./holey.py "$@"|grep -v "\s$LENGTH / "

    echo
    echo
} # end function brief_performance_test()


#exec > $OUTFILE
# Commented for now because rarely changing -i iter implementation.
#brief_performance_test -d -i $LENGTH  | tee hist/perf/brief.txt

brief_performance_test -d -b $LENGTH  | tee hist/perf/brief-bit.txt

brief_performance_test -d -n $LENGTH  | tee hist/perf/brief-bitnp.txt
