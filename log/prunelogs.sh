#!/bin/sh

# Assume log dir is the directory this script is in.
LOG_DIR=$(dirname $0)
CSV_MARKER='~perfv[0-9][0-9]~'
HEADER="$CSV_MARKER  ,script"
CSV_TEMP=$LOG_DIR/workfile.csv
CSV_KEEP=$LOG_DIR/logspruned.$(date +%Y-%m-%d.%H%M).csv


usage () {
    echo
    echo "$(basename $0):"
    echo
    echo "Prunes log files but keeps CSV lines from within them."
    echo "CSV lines of logs are identified with: $CSV_MARKER"
    echo "This script tries to prune only smaller holes runs."
    echo
    echo "$(basename $0) -n     Dry run, just list logs to be pruned."
    echo "$(basename $0) -p     Prune logs for real."
    echo "$(basename $0) [-h]   Display this help."
    echo
}


this_one_is_a_keeper () {
    # Takes a single log file, with no spaces in name, as only param.
    # Returns exit code 0 if log file is a keeper.
    # Returns exit code 1 if log file is not a keeper/is prunable.
    local log=$1

    # Default to not being a keeper.
    local KEEP=N

    # Does it has other files associated with it?  Are there
    # files other than it that match its name without extension?
    ls ${log%.log}* | grep -v "^$log$" > /dev/null
    [ $? -eq 0 ] && KEEP=Y

    # Does it contain a run with a high dot count?
    # (Test could accidentally catch high repeat counts instead.)
    grep "'[3-9][0-9]'" $log > /dev/null  && KEEP=Y
    # grep "'29'"         $log > /dev/null  && KEEP=Y  # changed mind.

    # Does it contain a run that took a long time?
    # Specifically is there a CSV line that also has a number with
    # a format like ...#,###.###, which is probably an elapsed time
    # over 1000 seconds?
    local REGEX="${CSV_MARKER}.*, *[0-9],[0-9]{3}\.[0-9]{3},"
    egrep "${REGEX}" $log > /dev/null  && KEEP=Y

    # Return the verdict.
    if [ "$KEEP" = "Y" ]; then
        return 0
    else
        return 1
    fi
} # end this_one_is_a_keeper


prune_it () {
    # Takes a single log file, with no spaces in name, as only param.
    local log=$1

    # Harvest any CSV performance records from the log, then prune it.
    grep "$CSV_MARKER" $log >> $CSV_TEMP
    rm $log
}


clean_up_csv () {
    grep "$HEADER" $CSV_TEMP | head -n 1 >> $CSV_KEEP
    grep "$CSV_MARKER" $CSV_TEMP | grep -v "$HEADER" >> $CSV_KEEP
    rm $CSV_TEMP

    echo CSV records from pruned logs consolidated in $CSV_KEEP
}

#
# main(ish)
#

if [ $# -eq 0 ]; then
    usage
    exit
elif [ $1 = -n ]; then
    PRUNE=N
elif [ $1 = -p ]; then
    PRUNE=Y
else
    usage
    exit
fi

# Make sure no prior CSV workfile is hanging around.
[ "$PRUNE" = "Y" ] && [ -f $CSV_TEMP ] && rm $CSV_TEMP

# Consider log files one by one.
for log in $LOG_DIR/*.log; do
    if this_one_is_a_keeper $log; then
        echo $log  kept
    else
        if [ "$PRUNE" = "Y" ]; then
            prune_it $log
            echo $log  PRUNED, CSV records extracted
        else
            echo $log  would be PRUNED, pass -p to do it for real.
        fi
    fi
done

# Clean up CSV file to get rid of duplicate headers.
[ "$PRUNE" = "Y" ] && clean_up_csv

echo

