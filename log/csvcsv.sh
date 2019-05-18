#!/bin/sh

# Extract's CSV rows from CSV files to STDOUT and sort.

HEADER_MARKER='~perfv02~  ,script'
ROW_MARKER='~perfv02~'
CSV_FILES='log/*.csv'

# The -h prevents prefixing filename to each line.
grep -h "$HEADER_MARKER" $CSV_FILES | head -n 1
grep -h "$ROW_MARKER" $CSV_FILES | grep -v "$HEADER_MARKER" | sort

