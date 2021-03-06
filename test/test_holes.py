#!/usr/bin/env python3
"""
Unit tests for the holes package, HolesBase class descendants.
Requires a symlink to the holes package in this script's directory.
"""

import unittest
import sys
import types # For isInstance on generator type
from math import factorial as fact
import holes
from test_holes_data import results
from test_holes_data import results_w_givens
import test_holes_util
import test_holes_base


class TestHolesIterator(test_holes_base.TestHolesBase):
    def setUp(self):
        impl_class = holes._base.implementations['iter']['_class']
        self.h = impl_class()

    def test_combos_with_n_dots_logging(self):
        # Only HolesIterator() does logging inside combos_with_n_dots.
        with test_holes_util.assertLogsDean(
                logger='holes',
                level='DEBUG'): #as strio:
            sink = tuple(self.h.combos_with_n_dots(4,3))
        #print(strio.getvalue())


class TestHolesBitwise(test_holes_base.TestHolesBase):
    def setUp(self):
        impl_class = holes._base.implementations['bitwise']['_class']
        self.h = impl_class()

class TestHolesBitwiseNumpy(test_holes_base.TestHolesBase):
    def setUp(self):
        impl_class = holes._base.implementations['bitnumpy']['_class']
        self.h = impl_class()

### TODO: Change base class back and uncomment more-specific tests
# Note: Chnage base class to unittest.TestCase to skip normal tests
#       and just do the parallelized-specific tests.
class TestHolesBitwiseParallel(test_holes_base.TestHolesBase):
    def setUp(self):
        impl_class = holes._base.implementations['bitparallel']['_class']
        self.h = impl_class()

    def test_bit_combos_with_givens(self):
        distance = 8
        leading = (1, 0, 0)
        trailing = (1, 1)
        for dots in range(3, 8):
            actual_bits = self.h.bit_combos_with_givens(distance,
                                                        dots,
                                                        leading,
                                                        trailing)
            actual = (holes._util.sequence_from_bits(ab) for ab in actual_bits)
            self.assertMatchesAllData(distance, dots, actual, results_w_givens)

    def test_bit_combos_that_measure_with_givens(self):
        distance = 8
        leading = (1, 0, 0)
        trailing = (1, 1)
        dots = 5
        actual_bits = self.h.bit_combos_that_measure_with_givens(distance,
                                                                 dots,
                                                                 leading,
                                                                 trailing)
        actual = (holes._util.sequence_from_bits(ab) for ab in actual_bits)
        self.assertMatchesBestData(distance, actual, results_w_givens)

    def test_parallelize_good_combos(self):
        distance = 5
        dotcount = 4
        self.h.parallels = 4
        try:
            self.h.parallelize_good_combos(distance, dotcount)
        finally:
            self.h.parallels = 2 # Default

# Old implementations {{{
# Filling in gaps in the old interfaces is low priority.
#class TestHolesIteratorOld(test_holes_base.TestHolesBase):
#    def setUp(self):
#        impl_class = holes._base.implementations['iterold']['_class']
#        self.h = impl_class()

# No longer using this implementation.
#class TestHolesBitwiseOld(test_holes_base.TestHolesBase):
#    def setUp(self):
#        impl_class = holes._base.implementations['bitold']['_class']
#        self.h = impl_class()
# }}}


def main(args):
    #unittest.main() {{{

    if len(sys.argv) > 1 and sys.argv[1] == '-v':
        verbosity=2
    else:
        verbosity=1
    test_modules = (
        test_holes_util,        # Test _util 1st, in case tests use it
        sys.modules[__name__],) # This module itself

    allsuite = unittest.TestSuite()
    for mod in test_modules:
        suite = unittest.defaultTestLoader.loadTestsFromModule(mod)
        allsuite.addTest(suite)

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(allsuite)

    if result.errors: return 4
    if result.failures: return 3
    return 0
    # }}}

if __name__ == '__main__':
    sys.exit(main(sys.argv))

