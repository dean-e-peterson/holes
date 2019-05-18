# {{{ vim fold marker for module-level doctext
"""
This module finds the minimum number of dots/ticks on a straightedge,
or HOLES in a template, such that you can still mark out any integer
length up the total length using pairs of the tick marks/dots/holes.

This implementation of the holes base class uses ITERators,
generators, etc.  This improves performance, and reduces memory
usage, by letting the high level functions not consume all the many
combinations that the lower level functions produce.  For example,
after finding sets of 6 dots that measure every interval up to 13,
there might be no need to loop through all the sets of 7 or more dots
that might do the same.

"""
# }}}


import logging  # {{{
import time
import sys
from itertools import combinations, chain
from . import _base
from . import _util

__version__ = _util.__version__
__all__ = []

logger = _util.logger
# }}}


class HolesIterator(_base.HolesBase):
    # {{{
    # {{{
    """
    Holes class implemented with iterators and generators.
    """
    # Note: The HolesIterator code is peppered with +1's because:
    #    1) Python's range() only going to endpoint-1.
    #    2) We deal with a distance, and points at integer intervals,
    #       including both endpoints (for distance 2, points 0,1,2)
    # }}}


    implementation_key = 'iter'
    implementation_name = 'iterator-based implementation'

    def __init__(self):
        super().__init__()


    def combos_with_n_dots_count(self, distance, dotcount):
        # {{{
        """Number of combinations combos_with_n_dots() would return"""
        if distance < 0: raise ValueError()
        if dotcount < 0: raise ValueError()
        if dotcount > distance + 1:
            raise ValueError('dotcount must be <= distance + 1, ' +
                             'even including both endpoints.')
        count = _util.combinations_count(range(distance + 1),dotcount)
        return count
        # }}}


    def combos_with_n_dots(self, distance, dotcount, offset=0):
        # {{{
        """
        Only source of dot combos, courtesy of itertools.combinations.
        distance - the distance measured by the potential endpoints,
        which means there are DISTANCE+1 possible positions.
        Example: distance=3 chooses dots from 4 points, {0,1,2,3}
        offset - the low end of range of possible value in the combos,
        useful for optimizing combos_that_span()
        Example: combos_with_n_dots(2,2,0): (0,1),(0,2),(1,2)
                 combos_with_n_dots(2,2,1): (1,2),(1,3),(2,3)
                 combos_with_n_dots(2,2,5): (5,6),(5,7),(6,7)
        """
        # Possible optimization...
        #def log_completion(label):
        #    # Fake generator to stick after combinations with chain.
        #    if False: yield
        #    logger.debug('{:>25}  done'.format(label))
        #    return

        # ToDo: Factor out of here and bitbased.py?
        if distance < 0: raise ValueError()
        if dotcount < 0: raise ValueError()
        if dotcount > distance + 1:
            raise ValueError('dotcount must be <= distance + 1, ' +
                             'even including both endpoints.')

        possible_values = range(offset, offset + distance + 1)
        combos = combinations(possible_values, dotcount)

        label = 'combos_with_n_dots({}, {})'.format(distance,dotcount)
        # Slow? since log_progress consumes and re-yields each combo.
        combos = self.log_progress(
            combos,
            label,
            step=None)
        # Possible optimization...
        # Faster?  Sticks a fake generator on the end which runs only
        # once, yields no items, but logs completion as a side effect.
        #combos = chain(combos, log_completion(label))

        return combos
        # }}}


    def all_combos(self, distance, offset=0):
        # {{{
        # {{{ comments folded
        # NOTE: Looping through the count of n dots from low to high
        #       meets an important order requirement in best_combos().
        #       We want the ideal solutions with the least number of
        #       dots to be generated first, so we can cut off the
        #       generator after the best results for performance.
        # Note: distance + 2 is to cover all cases from no dots,
        #       to dots in every possible position, including both
        #       endpoints 0 and distance.  Example for distance 3:
        #   0 - for no dots, if the caller wants that degenerate case?
        #   1 - for 1st dot, in position 0 if going for max dots
        #   2 - for 2st dot, in position 1 if going for max dots
        #   3 - for 3rd dot, in position 2 if going for max dots
        #   4 - for 4th dot, in position 3 if going for max dots
        # Counting them gives 5 possible values for distance 3.
        # See combos_with_n_dots for explanation of offset.
        # }}}
        combos = chain.from_iterable(
            self.combos_with_n_dots(distance, n, offset)
            for n in range(distance + 2))
        # Slow, since log_progress consumes and re-yields each combo.
        # combos = self.log_progress(combos,
        #                            'all_combos',
        #                             step = 100000000)
        return combos
        # }}}


    def combos_that_span(self, distance):
        # {{{
        """
        Directly get combos that span the distance.
        That is, directly get combos that contain both endpoints,
        reducing the length of combos that must be generated by 2,
        since we already know the the 2 endpoints are included.
        """
        if distance == 1:
            combo = (0,1)
            return (combo,)
        else:
            inner_combos = self.all_combos(distance - 2, offset=1)
            combos = ( (0,) + c + (distance,) for c in inner_combos )
            return combos
        # }}}


    def best_combos(self, distance):
        # {{{
        # Optimization: Get spanning combos directly.
        # Note: all_combos() does log_progress itself.
        #combos = self.all_combos(distance)

        # Optimization: Get spanning combos directly.
        # Filter out combos without both endpoints, 0 and distance.
        # This is needed so that combo_measures() can automatically
        # determine the distance/length.  It also helps performance.
        #combos = (combo for combo in combos
        #          if 0 in combo
        #          and distance in combo)
        combos = self.combos_that_span(distance)
        combos = self.log_progress(combos, 'combos_that_span')

        # Optimization: Filter combos that cannot measure distance-1.
        combos = (combo for combo in combos
                  if 1 in combo
                  or (distance - 1) in combo)
        combos = self.log_progress(combos,'combos_spanning_minus_one')

        # combos=(c for c in combos if self.measures(c,distance))?TODO
        combos = filter(self.combo_measures, combos)
        combos = self.log_progress(combos, 'good_combos', step=1000)

        # This assumes that combos is ordered low dotcount to high.
        combos = self.until_len_changes(combos)
        combos = self.log_progress(combos, 'best_combos', step=None)

        return combos
        # }}}


    def combo_measures(self, combo, distance=None):
        # {{{
        """
        Returns True if the combination of points given can measure
        all integer lengths 1 through distance.  That is, if there
        are pairs of points each length apart up through distance.
        Returns False if combo cannot measure all lengths
        from 1 through distance.
        """
        if not distance:
            distance = max(combo) - min(combo)
        lengths_measured = self.lengths_covered(combo)
        lengths_needed = range(1, distance + 1)
        missing = set(lengths_needed).difference(lengths_measured)
        return (len(missing) == 0)
        # }}}


    def lengths_covered(self, combo):
        # {{{
        """
        Returns a list of the lengths spanned by pairs of points in
        the given combination.  Returned set has duplicates removed.
        """
        length_set = set()
        for i in combo:
            for j in combo:
                # Since i and j loop through identical values, any
                # negative lengths should essentially be duplicates
                # of a positive length resulting from subtracting
                # the values in the other order.  Therefore, by
                # ignoring anything less than zero we eliminate
                # duplicates and save unneeded abs() calls in a
                # frequently executed function.  Since we want to
                # ignore zeros as well, we just need the positives.
                if (j-i) > 0:
                    length_set.add(j-i)

                # if not (j-i) == 0:
                #     length_set.add( abs(j-i) )

        return length_set
        # }}}


    def until_len_changes(self, iterable):
        # {{{
        # TODO: Replace with itertools.takewhile() ?
        # This could be broken out as a general utility function.
        """
        This generator passes items through until it finds an item
        with a different length, at which point it terminates.
        iterable is an iterable/sequence whose items each have len(),
        like an iterable whose items are nested sequences themselves.
        """
        first_item = next(iterable)
        length = len(first_item)
        yield first_item

        for item in iterable:
            if len(item) != length:
                break  # cut sequence
            yield item
        # }}} end of vim method fold

    # }}} end of vim class fold


_base.register_implementation(HolesIterator)


if __name__ == '__main__':
    print('Main command implementation moved to ../holey.py')

