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
from multiprocessing import Process, SimpleQueue
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


    def best_bit_combos(self, distance):
        # {{{
        """
        Copied from bitbased.py, but modified to account for the
        fact that in a parallelized implementation, things are
        returned a bit differently since filtering for good combos
        happens in the children before the parent consolidates
        the results.
        """
        found_one = False

        # distance+1 positions, inclusive on both ends, +1 for range()
        for dotcount in range(2, distance + 2):
            #combos = self.bit_combos_with_ends(distance, dotcount)
            combos = self.parallelize_good_combos(distance, dotcount)

            # With the action taking place in children, and them
            # filtering the results before this, this logging
            # is now misplaced.
            # TODO: Move this logging to the children, IF it is
            # safe to log from multiple threads (or use locking?)
            #label = 'bit_combos_with_ends({}, {})'.format(distance,
            #                                              dotcount)
            #combos = self.log_progress(combos, label, 100000000)

            # Combos prefiltered, thank you very much.
            #combos = self.bit_combos_that_measure(combos, distance)
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


    def parallelize_good_combos(self, distance, dotcount):
        # Get given patterns of some bits to give to parallel processes.
        def inner_givens(parallels, dotcount):
            # Find max power of two that doesn't go over parallel degrees.
            # AND doesn't result in too many given bits for the dotcount
            # being requested.  Dotcount - 2 is used to account for the
            # two end dots, which are always 1's, and not included in the
            # INNER givens.  (Example: If dot count is 3, no point trying to
            # parallelize it with inner given (1,1), since the start and
            # end dots already take two of the bits.)
            # TODO: Clarify or document and test the heck out of this.
            power_of_two = 0
            while (2**power_of_two <= parallels) and (power_of_two <= dotcount - 2):
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

        # Concatenate a 1 onto beginning of each inner_given tuple.
        leading_givens = ( (1,) + ig for ig in inner_givens(self.parallels, dotcount) )
        trailing_given = (1,)

        # Spawn worker processes.
        process_list = []
        for leading_given in leading_givens:
            #result = self.bit_combos_that_measure_with_givens(distance,
            #                                                  dotcount,
            #                                                  leading=leading_given,
            #                                                  trailing=(1,))
            # print('E', tuple(_util.sequence_from_bits(i) for i in tuple(result)))

            # Handy print statement, keep this one, even if commented.
            # print('C', dotcount, leading_given)
            queue = SimpleQueue()
            process = Process(target = self.parallelize_child_good_combos,
                              args = (queue, distance, dotcount),
                              kwargs = {"lead": leading_given,
                                        "trail": trailing_given})
            process.start()
            process_list.append((process, queue))

        # Collect worker processes
        results = []
        for (process, queue) in process_list:
            results.extend(queue.get())
            process.join()

        ###print('D', results)
        ###print('E', tuple(_util.sequence_from_bits(i) for i in results))
        # TODO: Consider yielding as a generator for consistency?
        return results


    def parallelize_child_good_combos(self, queue, distance, dotcount, lead=(), trail=()):
        result = self.bit_combos_that_measure_with_givens(distance,
                                                          dotcount,
                                                          leading=lead,
                                                          trailing=trail)
        queue.put(tuple(result))


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

