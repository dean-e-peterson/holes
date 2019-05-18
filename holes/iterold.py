# {{{ vim fold marker for module-level doctext
"""
This module finds the minimum number of ticks on a straightedge,
or HOLES in a template, such that you can still mark out any integer
length up the total length using pairs of the tick marks/dots/holes.

This older implementation still uses ITERators and or generators,
but without classes or code cleanups.  Still, it worked great,
and seemed quite optimized, so keeping it.
"""
# }}}


import logging  # {{{
import time
from itertools import combinations, chain
from . import _base
from . import _util
from ._util import logfunc

__version__ = _util.__version__
__all__ = []

logger = _util.logger
# }}}


class HolesIteratorOld(_base.HolesBase):
    # {{{
    """
    Wrapper class for old function-based iterator implementation.
    """
    implementation_key = 'iterold'
    implementation_name = 'old iterator-based implementation'

    def __init__(self):
        super().__init__()

    # Filling in gaps in old interfaces for unittest is low priority.
    #def combos_with_n_dots(self, length, ndots):
    #    # Included in class definition for unit testing.
    #    return combos_with_n_dots(length, ndots)

    def best_combos(self, distance):
        # Just use pre-existing non-class, module-level function.
        best = best_combos(distance)
        return best
    # }}}

_base.register_implementation(HolesIteratorOld)


def distances_covered(points):
    # {{{
    """
    Returns a list of the distances spanned by pairs of given points
    Returned set has duplicates removed.
    """

    distance_set = set()
    for i in points:
        for j in points:
            # Since i and j loop through identical values,
            # any negative distances should essentially
            # be duplicates of a positive distance resulting
            # from subtracting the values in the other order.
            # Therefore, by ignoring anything less than zero
            # we eliminate duplicates and save unneeded abs()
            # calls in a frequently executed function.
            # Since we want to ignore zeros as well,
            # we just need the positives.
            if (j-i) > 0:
                distance_set.add(j-i)

            # if not (j-i) == 0:
            #     distance_set.add( abs(j-i) )

    return distance_set
    # }}}


@logfunc
def combos_with_n_dots(length, ndots):
    # {{{
    """
    combos_w_given_number_of_dots
    Possible positions of a given number of dots in a given length.
    Note: +1 is because range() only goes up to one less than that.
    """

    # Verify parameters.
    if length < 1:
        raise ValueError('Length must be 1 or greater')
    if ndots < 2:
        raise ValueError('Length must be 2 or greater')
        # ... particularly since we want both endpoints
        #     included in result combos.

    potential_dots = range(0, length+1)
    all_combos = combinations(potential_dots, ndots)

    #print('combos_with_n_dots:', ndots)

    # Some combos won't include the 1st point (0) or last (length),
    # but those aren't really the right length, so filter for only the
    # combos that DO include at least the first and last points, i.e.
    # those that truly cover distance length.
    return (c for c in all_combos if ( (0 in c) and (length in c) ) )
    # }}}


@logfunc
def possible_combos(length):
    # {{{
    """
    All combinations of any number of dots for a given length.
    The combos_with_n_dots() function is called multiple times,
    once for each possible number of dots that would fit in the
    given length, starting with 2 dots, going up to length+1 dots
    (The +1 allows for a dot at the starting point, 0.  It says
     length+2 below because python likes counting up to but not
     including the last number, so we specify 1 more than we want.)
    """
    if length > 0:
        chainsaw = chain.from_iterable(
            combos_with_n_dots(length, n) for n in range(2, length+2)
            )
        result = chainsaw

        # log_progress moved into holes classes.
        # result = log_progress(chainsaw,
        #                       step=1000000,
        #                       label='(possible_combos)')

        ## Avoid iterator running out on the caller
        ## by converting to a list now.
        #return list(result)
        return result
    else:
        #return [(0,)]
        return iter((0,))
    # }}}


def combo_measures(points, length):
    # {{{
    """
    Returns True if the combination of points given can measure all
    integer distances 1 through length.  That is, if there are pairs
    of points each distance apart up through length.
    Returns False if points cannot measure all distances thru length.
    """
    dists_measured = distances_covered(points)
    dists_needed = range(1, length+1)
    dists_missing = set(dists_needed).difference(dists_measured)

    return (len(dists_missing) == 0)
    # }}}


@logfunc
def good_combos(length):
    # {{{
    """
    Return possible combinations of dots fitting within 0 to length,
    for which every distance up through length is covered;
    that is, only return combinations for which there are
    a pair of dots exactly 1 apart, a pair exactly 2 apart...
    all the way up to a pair exactly length apart (the ends).
    This should let you measure all distances up to length
    just using tick marks at the dot locations.
    """
    all_combos = possible_combos(length)

    # WARNING:  UGLY OPTIMIZATION.
    # Avoid calling combo_measures, a big time user for long lengths,
    # on those combos that cannot measure length-1 because they
    # have no dots 1 space from either end.
    #good_combos = (c for c in all_combos if combo_measures(c,length))
    good_combos = (
        c for c in all_combos
        if ( (1 in c or length-1 in c) and combo_measures(c,length) )
        )

    ## Make sure we return a list not an iterator.
    #return list(good_combos)
    return good_combos
    # }}}


@logfunc
def best_combos(length):
    # {{{
    """
    Return best combinations of dots fitting within 0 to length,
    for which every distance up through length is covered.
    This is like good combos, but instead of all combinations
    that include all distances, best combo returns only the
    good combinations with the smallest number of dots.
    NOTE: THIS ASSUMES good_combos RETURNS THE COMBOS WITH
          THE SMALLEST NUMBER OF DOTS FIRST!
    """
    ## Explicitly make it a list because if it's an iterator I'm
    ## afraid that my check of the first entry below would consume
    ## it and it would never be added to the results.
    ## There may be better ways to handle this.
    ## hopeful_combos = list(good_combos(length))

    # print('best_combos', time.strftime(_util.HOLEY_TIME_FORMAT))
    hopeful_combos = good_combos(length)
    # # For debug, to check that it's a generator for performance.
    # print('best_combos type of good_combos', type(hopeful_combos))
    # print('best_combos', time.strftime(_util.HOLEY_TIME_FORMAT))

    ## The following is not useable if hopeful_combos is a generator
    ## instead of a list.  Error said generators not subscriptable.
    ### First one should be gold standard.
    ### (Assumes at least 1 returned.)
    ##min_dots = len(hopeful_combos[0])

    ## Instead, handle it this way.
    results = []
    first = True
    for c in hopeful_combos:
        # Done inside loop to use first entry from non-subscriptable
        # generator as a gold standard of lowest number of dots.
        if first:
            min_dots = len(c)
            first = False

        # If this combination has more than the first one,
        # just break off and return what we've already got.
        if len(c) > min_dots:
            break

        # If this combination has the same number of dots as
        # the first one, include it as one of the best combos.
        results.append(c)

    return results
    # }}}


if __name__ == '__main__':
    print('Main command implementation moved to ../holey.py')

