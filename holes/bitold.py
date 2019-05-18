# {{{ vim fold marker for module-level doctext
"""
NO LONGER USING THIS IMPLEMENTATION.  See holes/bitbased.py for
new, class-based, faster implementation.  Keeping this for reference.

This module finds the minimum number of ticks on a straightedge,
or HOLES in a template, such that you can still mark out any integer
length up the total length using pairs of the tick marks/dots/holes.

This old function-based (as opposed to class-based) edition
of the module uses bitwise operations in an attempt to
improve performance (unsuccessfully, as of this writing ... gotta
love optimizing something that takes 2-3 seconds down to something
like a minute and a half :-)
"""
# }}}


import logging  # {{{
import time
from . import _base
from . import _util
from ._util import logfunc, points_from_bits

__version__ = _util.__version__
__all__ = []

logger = _util.logger
# }}}


class HolesBitwiseOld(_base.HolesBase):
    # {{{
    """
    Wrapper class for old function-based bitwise implementation.
    """
    implementation_key = 'bitold'
    implementation_name = 'old bitwise implementation'

    def __init__(self):
        super().__init__()

    def best_combos(self, distance):
        # Just use pre-existing functions and convert.
        best_bits = best_bit_combos(distance)
        combos = map(points_from_bits, best_bits)
        # _util.print_combos(combos)
        return combos
    # }}}

# No longer using this implementation.
#_base.register_implementation(HolesBitwiseOld)


# TODO: Consider performance help with n_dots_in_bit_combo() {{{
# http://www.toves.org/books/bitops/
# http://stackoverflow.com/questions/14555607
#        /explanation-required-number-of-bits-set-in-a-number
# http://graphics.stanford.edu/~seander
#        /bithacks.html#CountBitsSetTable
# https://en.wikipedia.org/wiki/Hamming_weight
# }}}
def n_dots_in_bit_combo(bits_int):
    # {{{
    """
    Return the number of digits in a binary number that are 1's.
    Takes a bitwise combo as an integer.

    An exact equivalent of this function is not needed for the
    non-bitwise operations, because combos_with_n_dots()
    uses itertools.combinations() to only generate sequences
    with a specific number of dots/elements in the first place.

    The bitwise combos, on the other hand, are generated as integers
    with range(), which returns combinations with different
    numbers of 1-digits (different numbers of dots) from a single
    range() call.  Therefore, we need to come back and evaluate
    which combos have the least 1-digits/dots, since those
    solutions are preferred.
    """
    # If there's a quick way to do this, I'd like to know it.
    # TODO: Factor out common parts of this and points_from_bits(),
    #       or at least move them next to each other?
    n_dots = 0

    bit_position = 0
    bit_value = 2**bit_position

    while bits_int >= bit_value:
        # Use bitwise AND to test the bit at bit_position.
        if bits_int & bit_value:
            n_dots += 1

        bit_position += 1
        bit_value = 2**bit_position

    return n_dots
    # }}}


@logfunc
def possible_bit_combos(length):
    # {{{
    """
    Bitwise version of a function to get all combinations of dots
    that can measure a given length.
    Possible positions of a given number of dots in a given length,
    Note: +1 is because range() only goes up to one less than that.
    Length here means the maximum distance that a set of tick marks
    or holes in a template can measure.  A 10 cm physical ruler, with
    tick marks every cm, would have 11 tick marks, because it needs
    both the 0 and the 10 to measure 10 lengths (10 minus 0 is 10).
    Described as an integer sequence, it would need to include both
    endpoints.
    """
    # Adjust for 0th point not counting as part of distance covered.
    length += 1

    # This would work, but see below for improvement on it.
    #potential_bit_combos = range(0, 2**length)

    # Some combos won't include the 1st point (0) or last (length),
    # but those aren't really the right length, so filter for only the
    # combos that DO include at least the first and last points, i.e.
    # those that truly cover distance length.
    # for a bitwise version this means the leftmost bit is one
    # that is, integer >= 2**(length-1).
    # To make sure the rightmost digit is a one, just ensure the
    # integer is odd by selecting an odd starting value and
    # then having range return every other integer, that is, step 2.
    potential_bit_combos = range(2**(length-1) + 1, 2**length, 2)

    return potential_bit_combos
    # }}}


def bit_combo_measures(bits_int, length):
    # {{{
    """
    Bitwise version of combo_measures()
    Returns True if the combination of points given can measure all
    integer distances 1 through length.  That is, if there are pairs
    of points each distance apart up through length.
    Returns False if points cannot measure all distances thru length.
    """
    for distance in range(1, length+1):
        # Check if bits_int and bits_int shifted by this distance
        # have any one's that line up using bitwise and (&).
        bits_int_shifted = bits_int >> distance
        if bits_int & bits_int_shifted == 0:
            # bits_int does not have one's this distance apart,
            # so it failed to measure all distances by definition.
            return False

    # We didn't bail out early, so bits_int measures them all. (Yay.)
    return True
    # }}}


@logfunc
def good_bit_combos(length):
    # {{{
    """
    Bitwise version of good_combos,
    Bit combos that can measure all distances up through length.
    """
    # TODO: Rename c as bc for bit combos here and elsewhere?
    return ( c for c in possible_bit_combos(length)
             if bit_combo_measures(c, length) )
    # }}}


@logfunc
def best_bit_combos(length):
    # {{{
    """
    Bitwise version of best_combos()
    Returns combos that do the measuring job with the fewest dots.
    That is, the best combinations of dots fitting within 0 to length,
    for which every distance up through length is covered.
    This is like good combos, but instead of all combinations
    that include all distances, best combo returns only the
    good combinations with the smallest number of dots.
    """
    best_combos_yet = []
    fewest_dots_yet = length + 1

    for bc in good_bit_combos(length):
        dots_in_bc = n_dots_in_bit_combo(bc)
        if dots_in_bc == fewest_dots_yet:
            best_combos_yet.append(bc)
        elif dots_in_bc < fewest_dots_yet:
            # New record.
            fewest_dots_yet = dots_in_bc
            # REPLACE any accumulated previous best_combos.
            best_combos_yet = [bc]
        # else:
            # This combo has more dots than current best, so ignore.
            # pass

    return best_combos_yet
    # }}}


def print_bit_combos(bit_combos):
    combos = map(points_from_bits, bit_combos)
    _util.print_combos(combos)


if __name__ == '__main__':

    print('Main command implementation moved to ../holey.py')

