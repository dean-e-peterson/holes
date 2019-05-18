"""
Holes base class module.
"""

import sys
import platform
import time
import os.path
from . import _util

__all__ = []
__version__ = _util.__version__

logger = _util.logger


def register_implementation(descendant_class):
    # {{{
    """
    Modules with descendant classes can register their implementations
    by overriding implementation_key & _name, and calling this.
    """
    key = descendant_class.implementation_key
    implementations[key] = {
        'key': key,
        'name': descendant_class.implementation_name,
        '_class': descendant_class,
        '_module': descendant_class.__module__ }

implementations = dict()
"""Check this for a list of holes implementations."""  # }}}


class HolesBase:
    # {{{
    # {{{
    """
    HolesBase is the base class for classes which find combinations
    of dots/holes/tick-marks that can measure all integer distances
    up through a given length.  "Measure" just means there is at
    least one pair of dots that distance apart.
    """ # }}}

    implementation_key = 'overrideme'
    implementation_name = 'base class - please override'

    def __init__(self):
        self.stats = dict()


    # Suggested methods.  Subclasses do not have to implement. {{{
    # def all_combos(self, distance):
    #     # {{{
    #     """
    #     All combinations of dots that fit within a given distance.
    #     Specifically, all_combos returns a sequence of combinations.
    #     Each combination is a unique set of 1 or more dots that
    #     fit within the given distance.  Because 0 is considered a
    #     valid point, the maximum number of dots in the set is
    #     actually distance + 1.
    #     """
    #     raise NotImplementedError()
    #     # }}}
    #
    # def combos_that_span(self, distance):
    #     # {{{
    #     """
    #     All combinations of dots that include both endpoints.
    #     In other words, it is the subset of all_combos() where
    #     all combinations returned contain both 0 and distance.
    #     This is in the base class largely as an optional step in
    #     the filtering for descendant classes.
    #     """
    #     raise NotImplementedError()
    #     # }}}
    #
    # def good_combos(self, distance):
    #     # {{{
    #     """
    #     All combinations of dots that measure all integer distances
    #     from 1 through distance.  It may include combinations with
    #     more dots than the minumum number needed to accomplish this.
    #     """
    #     raise NotImplementedError()
    #     # }}}
    # end suggested methods }}}


    def best_combos(self, distance):
        # {{{
        """
        All combinations of dots that measure all integer distances
        from 1 through distance.  It will only return combinations
        that have the minimum number of dots required.
        """
        raise NotImplementedError()
        # }}}


    def do_run(self, distance):
        # {{{
        """
        Do a best_combos run, gathering results & performance summary.
        """
        # Reset stats.
        self.stats = dict()

        # Log start
        logger.info('-' * 30)
        logger.info('Best combos for length {} ...'.format(distance))
        logger.debug('Using {}'.format(self.implementation_name))

        # Do everything, converting to a tuple to make sure it
        # fully iterates everything before we record completion time.
        start_time = time.time()
        combos = tuple(self.best_combos(distance))
        end_time = time.time()

        # Log completion
        elapsed_time = end_time - start_time
        count = len(combos)
        n_dots = len(combos[0])
        FMT='Best combos for length {} - found {} - took {:.3f} sec'
        logger.info(FMT.format(distance, count, elapsed_time))

        # Log performance summary.
        for line in self._stats_display_lines():
            logger.debug(line)
        run_summary = {
            'action': 'best_combos',
            'distance': distance,
            'time_elapsed': elapsed_time,
            'result_n_dots': n_dots,
            'result_count': count,}
        self.log_performance(run_summary)

        return combos
        # }}}


    def log_progress(self, iterable, label='', step=1000000):
        # {{{
        """
        Logs start, progress, final count, time in a generator
        pipeline.  Logs progress every step intervals unless
        step is None.  Was originally in _util.py, not in a class.
        """
        def log_start():
            logger.debug('{:>30}  started'.format(
                         label))
        def log_count():
            logger.debug('{:>30}  emitted {:,d} so far'.format(
                         label,
                         count))
        def log_complete():
            timestamp = time.time()
            elapsed = timestamp - start_time
            if label:
                self.stats[label] = {
                         'count': count,
                         'elapsed': elapsed,
                         'timestamp': timestamp }
            logger.debug('{:>30}  emitted {:,d} in {:.6f} sec'.format(
                         label,
                         count,
                         elapsed))
        #def log_except(): ?

        count = 0 #Avoid error logging final count for empty iterable.
        log_start()
        start_time = time.time()
        try:
            for count, item in enumerate(iterable, start=1):
                if step and count % step == 0:
                    log_count()
                yield item
        finally:
            # Log final count sometime after final request.
            # If consumer never drains the iterator completely,
            # this final count might not get logged until
            # garbage collection or program shutdown?
            log_complete()
        # }}}


    def log_performance(self, run_summary):
        # {{{
        """
        Log a parseable/machine-readable performance summary.
        """
        # Gather information.
        # ToDo: Make class for action/run/result summaries? stats?
        perf_summary = {
            'script': os.path.basename(sys.argv[0]),
            'version': __version__,
            'impl': self.implementation_key,
            'timestamp': time.strftime(_util.HOLEY_TIME_FORMAT),
            'args': sys.argv[1:],
            }
        perf_summary.update(run_summary)

        # Things I am testing for next REV of perf summary CSV format.
        # ToDo: Gather this, script, script version, and args
        #       elsewhere, only once, on module import, not each call?
        perf_provisional = {
            'pyver': platform.python_version(),
            'pyimpl': platform.python_implementation(),
            'arch': platform.machine(),
            'system': platform.system(),
            'release': platform.release(),
            'host': platform.node(),
            }
        prov_headers={keyname:keyname for keyname in perf_provisional}

        # "Gather" headers.  Formatting them the same way as the data
        # makes it easier to keep the header and data formats in sync.
        headers = { keyname: keyname for keyname in perf_summary }

        # Format to be CSV parseable (and maybe human readable)
        PERF_FORMAT_V02 = ''.join((
            '  ~perfv02~  ',
            ',{script:<8} ,{version:<22}, {distance:>9d}, ',
            '{time_elapsed:>12,.3f}, {impl:<8} ',
            ',{action:<12}, ',
            '{result_n_dots:>13d}, {result_count:>12d}, ',
            '{timestamp:<20s} ',
            ',"{args}"'  # double quotes allow commas in args in csv
            ))
        PROVISIONAL_FORMAT = ''.join((
            '  ~supplement~  ',
            ',{pyver:<6} ,{pyimpl:<9} ',
            ',{arch:<7} ,{system:<7} ,{release:<25} ,{host:<25} ',
            ))
        HEAD_FORMAT_V02 = PERF_FORMAT_V02
        HEAD_FORMAT_V02 = HEAD_FORMAT_V02.replace('d}','s}')
        HEAD_FORMAT_V02 = HEAD_FORMAT_V02.replace('12,.3f}','12s}')

        # Log it.
        logger.info(HEAD_FORMAT_V02.format(** headers))
        logger.info(PERF_FORMAT_V02.format(** perf_summary))

        # Log provisional additions for next perf format.
        logger.debug(PROVISIONAL_FORMAT.format(** prov_headers))
        logger.debug(PROVISIONAL_FORMAT.format(** perf_provisional))
        # }}}


    def _stats_display_str(self):
        return '\n'.join(self._stats_display_lines())


    def _stats_display_lines(self):
        # {{{
        if not self.stats:
            return ['No stats',]
        else:
            HEAD_FMT = '{:>17s}  {:<30s}  {:>9s}'
            BODY_FMT = '{:>17,d}  {:<30s}  {:>9.3f} sec'

            header = []
            header.append(HEAD_FMT.format('count','label','elapsed'))
            header.append(HEAD_FMT.format('-----','-----','-------'))

            body = []
            for label in self._stats_display_order():
                line = BODY_FMT.format(self.stats[label]['count'],
                                       label,
                                       self.stats[label]['elapsed'])
                body.append(line)

            return header + body
        # }}}


    def _stats_display_order(self):
        # {{{
        # I want feeders like combos_with_n_dots first,
        # then the main generator pipeline.
        feeders = []
        mainline = []
        for label in self.stats.keys():
            # ToDo: Move feeder names to subclasses..or something.
            if (label.startswith('combos_with_n_dots') or
                label.startswith('bit_combos_with_ends')):
                feeders.append(label)
            else:
                mainline.append(label)

        # Sort feeders based on when they completed.
        feeders.sort(
            key=lambda label: self.stats[label]['timestamp'])

        # Sort mainline by count descending to show filtering.
        mainline.sort(
            key=lambda label: self.stats[label]['count'],
            reverse=True)

        return feeders + mainline
        # }}}
    # }}}

