#!/bin/sh
# Dean's dots/tick-marks/holes in a template
# python package pre-checkin script.

echo
echo
echo -- Unit tests --
echo
echo
test/test_holes.py -v 2>&1 | tee test/utresults.txt
echo
echo

if [ "$1" = "-s" ]; then
    echo
    echo Skipping profiling.
    echo
    echo
    echo
else
    echo
    echo
    echo -- Brief profiling --
    echo
    echo
    ./profhole.sh
fi

