#!/usr/bin/env python3
""" Script to run for the holes package.  main(), argparse, etc."""

import sys #{{{
import os
import time
import argparse
import logging
import holes
import holes._util as _util
import holes._base as _base

__all__ = []
__version__ = _util.__version__

logger = _util.logger
###outlog = _util.outlog
# }}}


def main():
    # {{{
    # Parse args before logging starts to avoid logging --help.
    args = parse_command_line()

    configure_logging(debug=args.debug)
    logger.info('-' * 40)
    logger.info('Run started - {} - ver {} - args {}'.format(
                sys.argv[0],
                __version__,
                sys.argv[1:]))

    try:
        # Determine which holes implementation subclass to use.
        holesclass=_base.implementations[args.impl]['_class']
        holes = holesclass()

        # If requested, loop from 1 through (-t) the specified length.
        if args.thru:
            lengths = range(1, args.length + 1)
        else:
            lengths = (args.length,)

        # Loop through lengths (or just one length, if no -t)
        for length in lengths:
            best = holes.do_run(length)
            print()
            _util.print_combos(best)
            print()
            print(holes._stats_display_str())
            print()

    except Exception:
        logger.exception('An exception occurred.  Re-raising it.')
        raise

    else:  # No exception, so log normal finish.
        logger.info('Run finished')
        logger.info('-' * 40)

    return
    # }}}


def configure_logging(debug=False):
    # {{{
    # Configures the logging output for the script/application.
    # Does not configure the holes package/library logging inputs.
    if debug:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    FMT = '%(asctime)s.%(msecs)03d (%(levelname)#1.1s)   %(message)s'
    logging.basicConfig(
        filename=log_filename(),
        level=loglevel,
        format=FMT,
        datefmt=_util.HOLEY_TIME_FORMAT  # '%H:%M:%S'
        )
        # Note: datefmt determines format of %(asctime)s in the
        # overall format string, then .%(msecs)03d adds milliseconds.
        # Links to a couple useful pages in the python 3.5.1 docs.
        # The second is more for background.
        # docs.python.org/3/library/logging.html#logrecord-attributes
        #     .../logging.html#logging.Formatter.formatTime
        # Oh, and %(levelname)#1.1s, with # and the .1 precision,
        # truncates the levelname at 1 character long.

    return
    # }}}


def parse_command_line():
    # {{{
    COMMAND_DESC = ''.join((
        'Find sets of dots that include dot pairs all ',
        'integer distances apart, from 1 through n. ',
        'The dots could represent the minimum number of ',
        'tick marks on a straightedge or holes in a template ',
        'that could measure all distances <= n.'))
    parser = argparse.ArgumentParser(description=COMMAND_DESC)

    # const values here are implementation_key values, see holes._base
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-b',
        dest='impl',
        action='store_const',
        const='bitwise',
        default='bitwise',
        help='Use bitwise operation implementation (the default).')
    group.add_argument(
        '-i',
        dest='impl',
        action='store_const',
        const='iter',
        help='Use iterator-based implementation.')
    group.add_argument(
        '-o',
        dest='impl',
        action='store_const',
        const='iterold',
        help='Use old, non-class-based iterator implementation.')
    group.add_argument(
        '-n',
        dest='impl',
        action='store_const',
        const='bitnumpy',
        help='Use bitwise implementation with numpy.')

    parser.add_argument(
        '-d',
        dest='debug',
        action='store_true',
        default=False,
        help='Enable additional debug logging.')
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s '+__version__)
        # %{prog}s is defined by argparse and defaults to sys.argv[0]
    parser.add_argument(
        '-t',
        dest='thru',
        action='store_true',
        default=False,
        help='Show best combos for all lengths 1 thru given length.')
    parser.add_argument(
        '-m',
        dest='message',
        default='',
        help='Optional user message, unused but logged in logfile.')
    parser.add_argument(
        'length',
        type=int,
        help='Show best dot combos for this length.')

    args = parser.parse_args()

    # Validate the non-obvious.
    if args.impl not in _base.implementations:
        if args.impl == 'bitnumpy':
            raise Exception('Numpy implementation unavailable.')
        else:
            raise Exception('Invalid implementation specified.')

    return args
    # }}}


def log_filename():
    # {{{
    # Use script's name in the logfile name, but remove extension.
    script = sys.argv[0]
    (basename_no_ext,ext) = os.path.splitext(os.path.basename(script))

    # If a subdirectory named log exists, put the log there.
    script_dir = os.path.dirname(script)
    log_dir = os.path.join(script_dir, 'log')
    if not os.path.isdir(log_dir):
        log_dir = script_dir

    # Put together dir, script basename, datetime, and .log extension
    log_basename = '.'.join((basename_no_ext,
                             time.strftime('%Y-%m-%d.%H%M'),
                             'log'))
    return os.path.join(log_dir, log_basename)
    # }}}


if __name__ == '__main__':

    main()

