#!/bin/sh

# Extract's CSV rows from log files to STDOUT.

HEADER_MARKER='~perfv02~  ,script'
ROW_MARKER='~perfv02~'
LOG_FILES='log/*.log'

# The -h prevents prefixing filename to each line.
grep -h "$HEADER_MARKER" $LOG_FILES | head -n 1
grep -h "$ROW_MARKER" $LOG_FILES | grep -v "$HEADER_MARKER"

