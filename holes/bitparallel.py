# {{{ vim fold marker for module-level doctext
"""
This module finds the minimum number of dots/ticks on a straightedge,
or HOLES in a template, such that you can still mark out any integer
length up the total length using pairs of the tick marks/dots/holes.

This implementation of the holes base class uses parallelization
along with numpy to try to boost the speed of doing bitwise operations.
"""
# }}}


import logging  # {{{
import numpy as np
from . import _base
from . import _util
from . import bitnumpy

__version__ = _util.__version__
__all__ = []

logger = _util.logger
# }}}


class HolesBitwiseParallel(bitnumpy.HolesBitwiseNumpy):

    implementation_key = 'bitparallel'
    implementation_name = 'parallelized bitwise implementation with numpy'

    def __init__(self):
        super().__init__()
        # Two threads or processes by default.
        self.parallels = 2


    def bit_combos_with_givens(self, distance, dotcount, leading=[], trailing=[]):
        """
        All bitwise combos with dotcount dots that include some
        fixed given leading or trailing bits.  This can be useful
        A) to reduce the number of combinations generated if you
           already know both the first and last bit must be 1's, and
        B) to fill in other known bits, perhaps to break apart the
           overall generation across 2 cluster nodes by having
           one node generate all combos starting with 0, and the
           other node generate all combos starting with 1.
        The geven leading and trailing bits are passed as
        arrays of 0's and 1's.
        """
        # TODO: Move to _util ?
        def array_to_bits(array):
            bits = 0
            for value in array:
                bits <<= 1
                if value == 1:
                    bits |= 1
                elif value == 0:
                    pass
                else:
                    raise ValueError("Values in array must be 0's or 1's")
            return bits

        def bitmask_of_givens(distance, leading, trailing):
            length = distance + 1
            leading_bits = array_to_bits(leading)
            leading_bits <<= (length - len(leading))
            trailing_bits = array_to_bits(trailing)
            given_bits = leading_bits | trailing_bits
            return given_bits

        def dotcount_of_givens(leading, trailing):
            count = 0
            for value in leading:
                if value == 1:
                    count += 1
            for value in trailing:
                if value == 1:
                    count += 1
            return count

        inner_distance = distance - len(leading) - len(trailing)
        inner_dotcount = dotcount - dotcount_of_givens(leading, trailing)
        if inner_distance < 0:
            raise ValueError("Distance must at least cover given bits")
        if inner_dotcount < 0:
            raise ValueError("Dotcount must at least cover given bits")

        given_bits = bitmask_of_givens(distance, leading, trailing)

        # Avoid 0-length inner combo.
        if inner_distance == 0:
            bit_combo = given_bits
            yield bit_combo
            return

        inner_bit_combos = self.bit_combos_with_n_dots(inner_distance,
                                                       inner_dotcount)
        for bit_combo in inner_bit_combos:
            # Move inner bits over and stick given bits back on each end.
            bit_combo <<= len(trailing)
            bit_combo |= given_bits
            yield bit_combo


    def bit_combos_with_ends(self, distance, dotcount):
        leading = [1]
        trailing = [1]
        for bit_combo in self.bit_combos_with_givens(distance,
                                                     dotcount,
                                                     leading,
                                                     trailing):
            # print(bin(bit_combo))
            yield bit_combo

        #for bit_combo in super().bit_combos_with_ends(distance, dotcount):
        #    print(bin(bit_combo))
        #    yield bit_combo


_base.register_implementation(HolesBitwiseParallel)

