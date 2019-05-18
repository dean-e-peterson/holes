# {{{ vim fold marker for module-level doctext
"""
This module finds the minimum number of dots/ticks on a straightedge,
or HOLES in a template, such that you can still mark out any integer
length up the total length using pairs of the tick marks/dots/holes.

This implementation of the holes base class uses BITwise operations.
Internally it represents dot combinations as binary numbers,
with 1's in digit positions that have dots, and 0's elsewhere.
This is done in an attempt to improve CPU-bound speed and have fun.
"""
# }}}


import logging  # {{{
import functools
from . import _base
from . import _util
from . import gospers

__version__ = _util.__version__
__all__ = []

logger = _util.logger
# }}}


class HolesBitwise(_base.HolesBase):
    # {{{
    # {{{
    """
    Holes class implemented with bitwise operations.
    Many method names are different from non-bitwise implementations
    because they accept or return combos in bitwise integer format,
    preventing them from being directly interchangable.
    See _util.sequence_from_bits() and _util.bits_from_sequence() for
    converting a combo from bitwise to sequence form or vice versa.
    """
    # }}}


    implementation_key = 'bitwise'
    implementation_name = 'bitwise implementation'

    def __init__(self):
        super().__init__()


    def combos_with_n_dots(self, distance, dotcount):
        # Non-bitwise version originally included for unit testing.
        bit_combos = self.bit_combos_with_n_dots(distance, dotcount)
        return (_util.sequence_from_bits(bc) for bc in bit_combos)


    def bit_combos_with_n_dots(self, distance, dotcount):
        # {{{
        """
        The source of bitwise combinations of dots.
        distance - the distance measured by the potential endpoints,
        which means there are DISTANCE+1 possible positions.
        Example: distance=3 generates 4 digit binary #'s
        """

        # ToDo: Factor out of here and iterbased.py?
        # TODO: Consider dealing with the fact that params
        #       don't get checked immediately if generator
        #       next is not called right away?
        # Options:
        #   1.  Ignore it, fact of life, and adjust unittests
        #       to call next(retval) once or something.
        #   2.  Adjust unittests but add a warning in error message.
        #   3.  Try defining generator as an inner function,
        #       then validate params in an outer function that
        #       does NOT call yield itsefl, and return the
        #       inner function as the return val off the outer?
        if distance < 0: raise ValueError()
        if dotcount < 0: raise ValueError()
        if dotcount > distance + 1:
            raise ValueError('dotcount must be <= distance + 1, ' +
                             'even including both endpoints.')

        length = distance + 1

        # Replace yield from for Python 3.2 compatibility.
        for bit_combo in gospers.bit_combos_gospers(length, dotcount):
            yield bit_combo
        # }}}


    def bit_combos_with_ends(self, distance, dotcount):
        # {{{
        """
        All bitwise combos with n dots that contain both endpoints.
        This is more efficient than using bit_combos_with_n_dots()
        and then filtering combos without the endpoints.
        distance - the distance of max endpoint - min endpoint,
        which means there are DISTANCE+1 possible point positions.
        Ex: distance=3 makes 4 digit binary #s, with outer digits 1.
        """
        # Distance 1 is a special case to avoid 0-length inner combo.
        if distance == 1 and dotcount == 2:
            bit_combo = 0b11
            yield bit_combo
            return

        # Get bit combos 2 bits shorter with 2 fewer dots.
        inner_bit_combos = self.bit_combos_with_n_dots(distance - 2,
                                                       dotcount - 2)
        for bit_combo in inner_bit_combos:
            # Stick "1" bits on both ends to represent the endpoints.
            bit_combo = bit_combo << 1  # inner combo shift to middle
            bit_combo |= 1              # rightmost bit/endpoint
            bit_combo |= 1 << distance  # leftmost bit/endpoint
            yield bit_combo

        # }}}


    #def good_bit_combos_with_n_dots(self, distance, dotcount):


    def best_combos(self, distance):
        bit_combos = self.best_bit_combos(distance)
        bit_combos = self.log_progress(bit_combos,
                                       'best_bit_combos',
                                       step=1000)
        combos = map(_util.sequence_from_bits, bit_combos)
        return combos


    def best_bit_combos(self, distance):
        # {{{
        found_one = False

        # distance+1 positions, inclusive on both ends, +1 for range()
        for dotcount in range(2, distance + 2):
            combos = self.bit_combos_with_ends(distance, dotcount)
            label = 'bit_combos_with_ends({}, {})'.format(distance,
                                                          dotcount)
            combos = self.log_progress(combos, label, 100000000)
            combos = self.bit_combos_that_measure(combos, distance)
            for c in combos:
                # Don't keep looking at longer dotcounts.
                found_one = True
                yield c

            # Test found_one in the outer for loop, not the inner, so
            # we can collect all good combos with same best dotcount.
            # We just don't want to keep looking at higher dotcounts.
            if found_one:
                break
        # }}}


    def bit_combos_that_measure(self, bitcombos, distance):
        # {{{
        "Filters for combos that measure distance."
        # Create a bit_combo_measures function with the distance param
        # hardcoded, because filter() will only pass one param.
        measures_dist = functools.partial(
            self.bit_combo_measures,
            distance=distance)
        filtered = filter(measures_dist, bitcombos)
        return filtered
        # }}}


    def bit_combo_measures(self, bitcombo, distance):
        # {{{
        """
        Bitwise version of combo_measures()
        Returns True if the combination of points given can measure
        all integer distances 1 through length; that is, if there are
        pairs of points spaced each distance apart up through length.
        Returns False if points cannot measure all those distances.
        """
        for spacing in range(1, distance + 1):
            # Check if bitcombo shifted by this many digits
            # has any 1's that line up with unshifted bitcombo.
            bitcombo_shifted = bitcombo >> spacing
            if bitcombo & bitcombo_shifted == 0:
                # bitcombo does not have one's this spacing apart.
                # Now that it's failed to measure current spacing,
                # don't bother checking the rest.
                return False

        # We didn't return early, so bitcombo measures them all.
        return True
        # }}}

    # }}} end of vim class fold

_base.register_implementation(HolesBitwise)

