"""
Holes implementation unit tests descend from TestHolesBase here like
Holes implementations descend from HolesBase in holes/_base.py.

This is in a separate module to prevent the unittest framework
from creating an instance of this abstract base class when I do...
    unittest.defaultTestLoader.loadTestsFromModule(test_holes)

Why all this monkeying around with a TestCase class hierarchy?

Perhaps there is a better way, but this is partially a workaround
for the fact that unit test frameworks might create instances of
our TestCase automatically, leaving no way to set a single
variable, the implementation key, via the class constructor.
There may also be benefit to separating bitwise-specific
testing out of a base class, since non-bitwise implementations
will not need it.
"""

import unittest
import sys
import types # For isInstance on generator type
from math import factorial as fact
import holes
from test_holes_data import results
from test_holes_util import assertLogsDean
#import test_holes_util


class TestHolesBase(unittest.TestCase):
    " Unit tests for holes package."

    # {{{ setup
    def setUp(self):
        raise NotImplementedError(''.join((
            'Please create a descendant of ', self.__class__.__name__,
            ' instead of instantiating it directly.')))

        # OVERRIDE setUp() in descendant classes to do the following:
        # 1. Create an instance of a HolesBase descendant
        # 2. Assign the instance to an h attribute of self (self.h)
        #impl_class = holes._base.implementations['iter']['_class']
        #self.h = impl_class()
    # }}}

    # custom assertions {{{
    def assertMatchesAllData(self, distance, dots, actual, msg=None):
        "Checks that actual's data matches the recorded combos"
        msg = 'Wrong data: distance {}, dots {}'.format(distance,dots)
        length = distance + 1
        expected = (combo.sequence for combo in results[length][dots])

        # Could assertCountEqual(), but its error message is unclear.
        # Could assertSetEqual(), but it might hide duplicates.
        self.assertSequenceEqual(sorted(actual),sorted(expected),msg)

    # def assertMatchesGoodData() tip?
    #[[c.sequence for c in r[l][dots] if c.measures] for dots in r[l]]

    def assertMatchesBestData(self, distance, actual, msg=None):
        # ToDo: Refactor commonality out of this and ...AllData?
        "Checks that actual's data matches the best recorded combos"
        msg = 'Wrong best: distance {}'.format(distance)
        length = distance + 1
        for dots in range(length + 1):
            expected = [combo.sequence
                        for combo in results[length][dots]
                        if combo.measures]
            if len(expected) > 0:
                break

        # Could assertCountEqual(), but its error message is unclear.
        # Could assertSetEqual(), but it might hide duplicates.
        self.assertSequenceEqual(sorted(actual),sorted(expected),msg)

    def assertMatchesAllCounts(self,distance,dots,actual,msg=None):
        """
        Checks that actual's number of combos matches expected value.
        Use for larger param values where recording
        all the data would be prohibitive.
        """
        msg='Wrong count: distance {}, dots {}'.format(distance,dots)
        length = distance + 1
        expected = (fact(length) // (fact(length-dots) * fact(dots)))
        self.assertEqual(len(tuple(actual)), expected, msg)

    # }}}

    # combos_with_n_dots() tests {{{
    # def test_combos_with_n_dots_1_bounds(self):
    #     # TODO: Deal with fact that generator args aren't validated
    #     #       until first iteration.  More notes in bitbased.py.
    #     # {{{
    #     why='I should probably return a generator for performance.'
    #     self.assertIsInstance(self.h.combos_with_n_dots(1,2),
    #                           types.GeneratorType,
    #                           msg=why)
    #     why='I should be raising an exception if distance param < 0'
    #     with self.assertRaises(ValueError, msg=why):
    #         self.h.combos_with_n_dots(-1,2)
    #     why='I should be raising an exception if dots param < 0.'
    #     with self.assertRaises(ValueError, msg=why):
    #         self.h.combos_with_n_dots(2,-2)
    #     with self.assertRaises(ValueError, msg=why):
    #         self.h.combos_with_n_dots(0,-1)
    #     why='I should be raising an exception if dots > distance+1'
    #     with self.assertRaises(ValueError, msg=why):
    #         self.h.combos_with_n_dots(0,2)
    #     with self.assertRaises(ValueError, msg=why):
    #         self.h.combos_with_n_dots(5,8)
    # }}}

    def test_combos_with_n_dots_2_degenerate(self):
        self.assertMatchesAllData(0, 0,
            self.h.combos_with_n_dots(0, 0))
        self.assertMatchesAllData(0, 1,
            self.h.combos_with_n_dots(0, 1))

    def test_combos_with_n_dots_3_tiny(self):
        for distance in (1, 2):
            for dots in range(distance + 1):
                self.assertMatchesAllData(distance, dots,
                    self.h.combos_with_n_dots(distance, dots))

    def test_combos_with_n_dots_4_small(self):
        for distance in (3, 4):
            for dots in range(distance + 1):
                self.assertMatchesAllData(distance, dots,
                    self.h.combos_with_n_dots(distance, dots))

    def test_combos_with_n_dots_5_medium(self):
        for distance in (6, 7, 13):
            for dots in range(distance + 1):
                self.assertMatchesAllCounts(distance, dots,
                    self.h.combos_with_n_dots(distance, dots))
    # }}}

    # best_combos() tests {{{
    def test_best_combos_1(self):
        for distance in range(5):
            self.assertMatchesBestData(distance,
                    self.h.best_combos(distance))

    def test_best_combos_2_logging(self):
        # Minimal sanity test, anyway.
        with assertLogsDean(logger='holes', level='DEBUG'): #as strio:
            sink = tuple(self.h.best_combos(4))
        #print(strio.getvalue())

    # TODO: Add tests of exception conditions.     
    # }}}
