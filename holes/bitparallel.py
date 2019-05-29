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
import functools
import itertools
import multiprocessing
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


    def parallelize(self, distance, dotcount):
        # Get given patterns of some bits to give to parallel processes.
        def inner_givens(parallels):
            # Find max power of two that doesn't go over parallel degrees.
            power_of_two = 0
            while 2**power_of_two <= parallels:
                power_of_two += 1
            power_of_two -= 1
            # TODO: Log if stepping down to a power of two.
            return itertools.product((0,1), repeat=power_of_two)

        # If single process, don't bother.
        # TODO: Change to an error check for < 1 if general case works for 1.
        if self.parallels <= 1:
            pass
            # Add degenerate case here perhaps
            # just calling bit_combos_that_measure_with_givens
            # with leading=(1,) and trailing=(1,)

        # Concatenate a tuple (1,) onto beginning of each inner_given.
        leading_givens = ( (1,) + ig for ig in inner_givens(self.parallels) )
        # trailing givens is always (1,)

        ### The following is definately broken
        # Multiprocessing pool can easily map inputs to a function that takes
        # one parameter as it's data.  Since the only thing we want to vary
        # between the parallel processes is are the leading_givens, we just
        # create a partial method that will call
        # bit_combos_that_measure_with_givens
        # with all other parameters set.
        bit_combos_partial = functools.partialmethod(
                                self.bit_combos_that_measure_with_givens,
                                (distance, dotcount),
                                {"trailing": (1,)})
        for leading_given in leading_givens:
            bit_combos_partial(leading=leading_given)
    
    # TODO: Consider if want to convert bit combos to sequence combos
    #       before returning from parallelized children?


    def bit_combos_that_measure_with_givens(
            self, distance, dotcount, leading=[], trailing=[]):
        """
        Good bitwise combos with dotcount dots that include some
        fixed given leading or trailing bits.  In this contect,
        good means it filters to only return combos that can measure
        distance, that is, where somewhere there are dots 1 apart,
        2 apart, ..., up to distance apart.
        This method is meant for parallelization or clustering
        scenarios, where you want to filter a bunch of possibilities
        with different givens that are being processed in parallel,
        then only return the useful combos to the driver process.
        """
        # Start only with those combinations that have given end bits.
        combos = self.bit_combos_with_givens(distance, dotcount,
                                             leading, trailing)
        # Let bitnumpy chunk it up and determine which are good.
        combos = self.bit_combos_that_measure(combos, distance)
        for combo in combos:
            yield combo


    def bit_combos_with_givens(
            self, distance, dotcount, leading=(), trailing=()):
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
        tuples of 0's and 1's.
        """
        # TODO: Move to _util ?
        def tuple_to_bits(tuple):
            bits = 0
            for value in tuple:
                bits <<= 1
                if value == 1:
                    bits |= 1
                elif value == 0:
                    pass
                else:
                    raise ValueError("Given tuple values must be 0's or 1's")
            return bits

        def bitmask_of_givens(distance, leading, trailing):
            length = distance + 1
            leading_bits = tuple_to_bits(leading)
            leading_bits <<= (length - len(leading))
            trailing_bits = tuple_to_bits(trailing)
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
        inner_length = inner_distance + 1
        inner_dotcount = dotcount - dotcount_of_givens(leading, trailing)
        if inner_length < 0:
            raise ValueError(("Distance {} must at least cover given " +
                              "leading ({}) and trailing({}) bits").format(
                               distance, leading, trailing))
        if inner_dotcount < 0:
            raise ValueError(("Dotcount {} must at least cover given " +
                              "leading ({}) and trailing({}) bits").format(
                               dotcount, leading, trailing))

        given_bits = bitmask_of_givens(distance, leading, trailing)

        # Avoid 0-length inner combo.
        if inner_length == 0:
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
        """
        For the moment, just override bitnumpy.py's implementation
        with an implementation using bit_combos_with_givens.
        """
        leading = [1]
        trailing = [1]
        for bit_combo in self.bit_combos_with_givens(distance,
                                                     dotcount,
                                                     leading,
                                                     trailing):
            # print(bin(bit_combo))
            yield bit_combo


_base.register_implementation(HolesBitwiseParallel)

