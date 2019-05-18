#!/usr/bin/python3
"""
Test routines to exercise code in holes.py.
Not real unit tests, but attempts to have pretty
wide code coverage as far as executing routines.
Output could be compared with output from
previous versions, possibly with doctest.
"""


import unittest
import timeit
import types
# from collections import OrderedDictionary
import holes


class TestHoles(unittest.TestCase):


    COMBOS_WITH_N_DOTS_RESULTS = {  # {{{ <- vim folding marker.
            #length
                    #n_dots
                            #results
            # Results for length 3 are not currently used  {{{
            # from here because they are small enough to
            # be included inline in the test method.
            # However, I am leaving them here to demonstrate
            # how results for multiple lengths can be included.
            #3:{
            #        4:(
            #                (0,1,2,3),          # 3,4
            #          ),
            #        3:(
            #                (0,1,3),            # 3.3
            #                (0,2,3)
            #          )
            #  },  # }}}
            5:{
                    2:(
                            (0,5),              # 5,2
                      ),
                    3:(
                            (0, 1, 5),          # 5,3
                            (0, 2, 5),
                            (0, 3, 5),
                            (0, 4, 5)
                      ),
                    4:(
                            (0, 1, 2, 5),       # 5,4
                            (0, 1, 3, 5),
                            (0, 1, 4, 5),
                            (0, 2, 3, 5),
                            (0, 2, 4, 5),
                            (0, 3, 4, 5)
                      ),
                    5:(
                            (0, 1, 2, 3, 5),    # 5,5
                            (0, 1, 2, 4, 5),
                            (0, 1, 3, 4, 5),
                            (0, 2, 3, 4, 5)

                      ),
                    6:(
                            (0, 1, 2, 3, 4, 5), # 5,6
                      )
              }

    } # End COMBOS_WITH_N_DOTS_RESULTS  }}}

    def test_combos_with_n_dots(self):
        # def combos_with_n_dots(length, ndots):

        # I do not know how to specify a generator type.
        # Therefore, I create a dummy generator expression,
        # and call type on it to get the type for comparison.
        #generator_type = type((n for n in (1,2)))
        # Ah, found it in std library module "types"

        # Check if what is returned is a generator,
        # which could be important for performance,
        # and just for knowing if something changed.
        self.assertIsInstance(holes.combos_with_n_dots(1,2),
                              types.GeneratorType)

        # Oddly enough, itertools.combinations(), running inside
        # combos_with_n_dots(), does not LIKE picking negative
        # numbers of elements out of a set.
        with self.assertRaises(ValueError):
            holes.combos_with_n_dots(1,-1)

        why = 'I should be raising an exception if length param < 1.'
        with self.assertRaises(ValueError, msg=why):
            holes.combos_with_n_dots(-1,2)
        with self.assertRaises(ValueError, msg=why):
            holes.combos_with_n_dots(0,2)

        why = 'I should be raising an exception if ndots param < 2.'
        with self.assertRaises(ValueError, msg=why):
            holes.combos_with_n_dots(2,0)
        with self.assertRaises(ValueError, msg=why):
            holes.combos_with_n_dots(1,1)

        # self.assertCountEqual()
        # Note: I could use this on sequences if I don't care about
        # the order of (top level) elements.  Nested sub-elements
        # can still matter.  For example...
        # self.assertCountEqual( (2,1,0),(1,2,0) )   # Asserts true
        # self.assertCountEqual( ((0,1,2),(2,1,0)) ,
        #                        ((0,1,2),(1,2,0)) ) # Asserts false
        # AssertionError: Element counts were not equal:
        # First has 1, Second has 0:  (2, 1, 0)
        # First has 0, Second has 1:  (1, 2, 0)

        self.assertSequenceEqual(tuple(holes.combos_with_n_dots(1,2)),
                                 ((0,1),))
        self.assertSequenceEqual(tuple(holes.combos_with_n_dots(1,3)),
                                 ()          )

        why = ('Results that do not contain both endpoints, ' +
               '0 and length, should be filtered out.')
        self.assertNotIn((0,1), holes.combos_with_n_dots(2,2), msg=why)
        self.assertNotIn((1,2), holes.combos_with_n_dots(2,2), msg=why)

        self.assertSequenceEqual(tuple(holes.combos_with_n_dots(2,2)),
                                 ((0,2),))
        self.assertSequenceEqual(tuple(holes.combos_with_n_dots(3,2)),
                                 ((0,3),))
        self.assertSequenceEqual(tuple(holes.combos_with_n_dots(2,3)),
                                 ((0,1,2),))
        self.assertSequenceEqual(tuple(holes.combos_with_n_dots(3,4)),
                                 ((0,1,2,3),))
        # First with multiple results because of contraint in
        # holes.combos_with_n_dots() which restricts valid
        # results to those that include at least the first (0th)
        # and last (length) items in the sequence.
        self.assertSequenceEqual(tuple(holes.combos_with_n_dots(3,3)),
                                 ((0,1,3),
                                  (0,2,3)))

        # TODO: Remove length 3 results from COMBOS_WITH_N_DOTS_RESULTS
        #       or USE them above for testing.

        # Test different ndots for length 5.
        for ndots in range(2, 5+2):
            msg = 'Failed combos_with_n_dots({},{})'.format(5,ndots)
            expected = self.COMBOS_WITH_N_DOTS_RESULTS[5][ndots]
            self.assertSequenceEqual(
                tuple(holes.combos_with_n_dots(5,ndots)),
                expected,
                msg=msg)

        # Not completely verified, but looked right.
        self.assertEqual(len(tuple(holes.combos_with_n_dots(11,5))),
                         120)

        return


    def test_possible_combos(self):
        # def possible_combos(length):

        # TODO: Add for shortest lengths.

        # Loop through expected combos_with_n_dots()
        # results for length 5 but different number of dots,
        # and accumulate all possible expected results
        # for length 5 into a single sequence.
        expected = []
        for ndots in range(2, 5+2):
            expected.extend(self.COMBOS_WITH_N_DOTS_RESULTS[5][ndots])

        self.assertSequenceEqual(list(holes.possible_combos(5)),
                                 expected)
        return


    DISTANCES_COVERED_RESULTS = (  # {{{
        # In tuples of ((input points), (result set))
        ( () , set() ),
        ( (0,), set() ),
        ( (0,1), set((1,)) ),
        ( (0,2), set((2,)) ),
        ( (0,1,2), set((1,2)) ),
        ( (0,3), set((3,)) ),
        ( (1,3), set((2,)) ),
        ( (0,1,3), set((1,2,3)) ),
        ( (0,2,3), set((1,2,3)) ),
        # ( (1,3,2), set((1,2,3)) ),  TODO: Doc that input must be sorted?
        ( (0,2,4), set((2,4)) ),
        ( (0,1,3,6), set((1,2,3,  5,6)) ),
        ( (0,1,4,6), set((1,2,3,4,5,6)) ),
        ( (0,1,4,7,9), set(range(1,9+1)) ),  # all of 0,1,2,3,4,5,6,7,8,9
        ( (0,2,4,7,9), set(range(1,9+1)) - set((1,6,8)) ), # no 1,6,8
        ( (0,1,3,6,11,17,21,22,24), set(range(1,24+1)) - set((9,12)) ),
        ( (0,1,3,6,13,20,27,31,35,36), set(range(1,36+1)) ),

    ) # End DISTANCES_COVERED_RESULTS  }}}

    def test_distances_covered(self):
        #def distances_covered(points):

        for p, results in self.DISTANCES_COVERED_RESULTS:
            msg = 'Wrong results for distances_covered({})'.format(p)
            self.assertSetEqual(holes.distances_covered(p),
                                results,
                                msg)

        # TODO: Test what happens with negatives in sequence.
        return


# {{{  Bitwise debug_print functions brought in with bitwise merge.
def debug_print_bits_2_points_2_dots(length):
    # Adjust for 0th point not counting as part of distance covered.
    length += 1

    # Bits/Dots/Points format.
    # BDP_FORMAT = 'bits: {0:>16b} / {0:<5d}  {1:>32s}  {2:s}'  # ~16 bit
    BDP_FORMAT = 'bits: {0:>12b} / {0:<4d}  {1:>24s}  {2:s}'  # ~12 bit

    # Get all the combos!
    combos_as_bits = range(0, 2**length)
    for bits_int in combos_as_bits:
        points = points_from_bits(bits_int)
        line_of_dots = dots(points)
        print(BDP_FORMAT.format(bits_int, line_of_dots, points))


def debug_print_bits():

    # Test bitwise functions
    print(len(tuple(                            possible_bit_combos(5))))
    print(    tuple('0b{:b}'.format(c) for c in possible_bit_combos(5)) )
    for c in possible_bit_combos(5):
        print('0b{:b}'.format(c))
    for c in possible_bit_combos(5):
        print('0b{:b}  {}'.format(c, bit_combo_measures(c, 5)))
    print()
    for c in good_bit_combos(5):
        print('0b{:b}  {}'.format(c, bit_combo_measures(c, 5)))
    print()
    for c in good_bit_combos(5):
        print('0b{:b}  {}  ndots:{}'.format(
            c,
            bit_combo_measures(c, 5),
            n_dots_in_bit_combo(c) ))

    print('Testing points_from_bits() and bits_from_points()...')
    points = (0,2,3,6)
    bits_int = 0b1001101
    print('points_from_bits(0b{0:b}) is {1}. It should be {2}'.format(
        bits_int,
        points_from_bits(bits_int),
        points))
    print('bits_from_points({0}) is 0b{1:b}. It should be 0b{2:b}'.format(
        points,
        bits_from_points(points),
        bits_int))
    print()

    debug_print_bits_2_points_2_dots(1)
    debug_print_bits_2_points_2_dots(2)
    debug_print_bits_2_points_2_dots(5)
    debug_print_bits_2_points_2_dots(9)


    print('\n')
    print( 'best_bit_combos', 5 )
    print()
    bit_combos = best_bit_combos(5)
    combos_as_points = map(points_from_bits, bit_combos)
    print_combos( combos_as_points )
    # }}}


def do_printlog():  # (* args):
    print()
    holes.printlog('Real hello')
    holes.printlog()
    holes.printlog('Test', 'hello')
    holes.printlog('')
    holes.printlog(('Test','hello','from','tupleville'))
    holes.printlog('\n')
    holes.printlog('Are we good?')
    print('not logged')
    print()
    holes.printlog('ten', str(4))

def do_points_from_bits():  # (bits_int):
    pass

def do_bits_from_points():  # (points):
    pass

def do_distances_covered():  # (points):
    pass

def time_distances_covered():  # (points):

    DISTANCES_COVERED_TIMING_SETS = {  # {{{
        '1 - Low Maximum': (
            (),       # result empty set (valid?)
            (0,),     # result empty set (valid?)
            (2,),     # result empty set (valid?)
            (0,1),    # result set((1,))
            (0,2),    # result set((2,))
            #(1,3,2), # input must be sorted?
            (0,2,3),  # result set((1,2,3))
        ),
        '2 - High Maximum, Low Count': (
            (37,),
            (0,37),
            (0,1,2,3,37),
            (0,10,20,30,37),
            (0,34,35,36,37),
        ),
        '3 - High Maximum, Best Count': (
            (0, 1, 2, 3, 4, 5, 11, 18, 24, 30),         # 30 best, 1st
            (0, 6, 12, 19, 25, 26, 27, 28, 29, 30),     # 2nd to last
            (0, 1, 3, 6, 13, 20, 27, 31, 35, 36),
            (0, 1, 5, 9, 16, 23, 30, 33, 35, 36),
            (0, 1, 2, 3, 4, 5, 6, 14, 22, 30, 37),      # 37 best, 1st
            (0, 6, 13, 19, 25, 32, 33, 34, 35, 36, 37), # 2nd to last
        ),
        '4 - High Maximum, Medium Count': (
            tuple(range(0, 36+1, 2)), # evens (I think)
            (0,1,2,3,5,7,9,11,14,15,16,22,23,25,29,30,33,35,37),
        ),
        '5 - High Maximum, High Count': (
            tuple(range(0, 36+1)),  # All, I think
            set(range(0, 36+1)),    # All, with set()
            set(range(0, 36+1)) - set((2,5,12,29,32)),  # A few missing
        ),
        #'6 - Hi Numbers, but perhaps Low Sanity': (
        #    (0, 500),
        #    tuple(range(0, 500+1,20)),
        #    tuple(range(0, 500+1,3)),
        #    tuple(range(0, 500+1)),
        #),
    } # }}}

    repeat = 3
    loops = 100
    setup = 'import holes'
    stmt_fmt = 'holes.distances_covered({})'

    # TODO: Consolidate with time_combos_with_n_dots(),
    #       print formats and their use was copied from.
    REPEAT_FMT = ' {:.6f}  ' * repeat
    RUNS_FMT = '  {} runs of {} loops took:  ' + REPEAT_FMT + 'sec'
    LOOPTIME_FMT = '  {:.9f} sec/loop on fastest run'

    print('\n')
    print('distances_covered() timings')
    for group_name in sorted(DISTANCES_COVERED_TIMING_SETS):
        print('\n')
        print(group_name + ' timings')
        print()
        point_sets = DISTANCES_COVERED_TIMING_SETS[group_name]
        for point_set in point_sets:
            stmt_w_spaces = stmt_fmt.format(point_set)
            # For long tuple args, output easier to read sans spaces.
            stmt = stmt_w_spaces.replace(' ','')
            print(stmt)
            times = timeit.repeat(stmt=stmt,
                                  setup=setup,
                                  repeat=repeat,
                                  number=loops)
            print(RUNS_FMT.format(repeat, loops, * times))
            print(LOOPTIME_FMT.format( min(times)/loops ))
            print()
    return


def do_combinations_count():  # (iterable, r):
    #print(holes.combinations_count((1,2,4,6,7), -1))  # Exception
    print(holes.combinations_count((1,2,4,6,7), 6))    # Should be zero
    print(holes.combinations_count((1,2,4,6,7), 5))
    print(holes.combinations_count((1,2,4,6,7), 3))
    print(holes.combinations_count((1,2,4,6,7), 1))
    print(holes.combinations_count((1,2,4,6,7), 0))

def do_combos_with_n_dots():  # (length, ndots):
    for p in holes.combos_with_n_dots(4, 2):
        print(holes.dots(p), p)
    for p in holes.combos_with_n_dots(5, 6):
        print(holes.dots(p), p)

def time_combos_with_n_dots():  # (length, ndots):
    """ Example of using timer from command line instead:  {{{
    $ python3 -m timeit -v -s 'import holes' 'holes.combos_with_n_dots(1,2)'
    10 loops -> 0.000236 secs
    100 loops -> 0.00215 secs
    1000 loops -> 0.0212 secs
    10000 loops -> 0.213 secs
    raw times: 0.212 0.213 0.212
    10000 loops, best of 3: 21.2 usec per loop
    """  # }}}
    def timeits_map(stmt_fmt, params_iter, setup, repeat, loops):
        """
        Generator function that takes an iterator of param tuples,
        and yields the param dictionaries with timeit results added.
        """
        for params in params_iter:
            stmt = stmt_fmt.format(*params)
            #print(stmt)
            results = timeit.repeat(
                stmt=stmt,
                setup=setup,
                repeat=repeat,
                number=loops)
            #print(results)
            yield results

    def timeits_print(stmt_fmt, params_iter, setup, repeat, loops, results):
        """Function printing the timeit results from timeits_map"""
        REPEAT_FMT = ' {:.6f}  ' * repeat
        RUNS_FMT = '{} runs of {} loops took:  ' + REPEAT_FMT + 'sec'
        LOOPTIME_FMT = '{:.6f} sec/loop on fastest run'

        print()
        for params in params_iter:
            times = results.__next__()  # TODO: Should I be calling this?
            stmt = stmt_fmt.format(*params)
            print(stmt)
            print(RUNS_FMT.format(repeat, loops, * times))
            # min_time_per_loop = min(times)/loops
            print(LOOPTIME_FMT.format( min(times)/loops ))
            print()

    repeat = 3
    loops = 1000
    setup = 'import holes'
    stmt_fmt = 'holes.combos_with_n_dots({0}, {1})'
    params_to_time = ((1, 2), (1, 3), (2, 2), (5, 2),
                      (5, 3), (5, 4), (5, 5), (5, 6),
                      (9, 3), (9, 5), (9, 6), (9, 8),
                      (13,3), (13,6), (13,7), (13,8))

    # Get a generator for the results of timeit for the params.
    results = timeits_map(stmt_fmt, params_to_time, setup, repeat, loops)

    # Consume the generator, formatting and printing results.
    timeits_print(stmt_fmt, params_to_time, setup, repeat, loops, results)

    print()

    # Now do the same, but in the statement, explicitly ensure
    # that any iterator that combos_with_n_dots() returns is drained.
    stmt_fmt = 'tuple(holes.combos_with_n_dots({0}, {1}))'
    results = timeits_map(stmt_fmt, params_to_time, setup, repeat, loops)
    timeits_print(stmt_fmt, params_to_time, setup, repeat, loops, results)


def do_n_dots_in_bit_combo():  # (bits_int):
    pass

def do_possible_combos():  # (length):
    print(tuple(holes.possible_combos(-1)))
    print(tuple(holes.possible_combos(0)))
    print(tuple(holes.possible_combos(1)))
    print(tuple(holes.possible_combos(2)))
    print(tuple(holes.possible_combos(5)))

def do_possible_bit_combos():  # (length):
    pass

def do_combo_measures():  # (points, length):
    # Check hopefully unused corner cases,
    # example, sequence longer than given length.
    print(holes.combo_measures((0,) ,0))
    print(holes.combo_measures((0,2,3,4,5,6,8) ,4))
    print(holes.combo_measures((0,3,4,8) ,4))

def do_bit_combo_measures():  # (bits_int, length):
    pass

def do_good_combos():  # (length):
    # print(tuple(holes.good_combos(0)))
    print(tuple(holes.good_combos(1)))
    print(tuple(holes.good_combos(2)))
    print('\n')
    print( 'holes.good_combos(5)' )
    print()
    holes.print_combos( holes.good_combos(5) )

def do_good_bit_combos():  # (length):
    pass

def do_best_combos():  # (length):
    print('\n')
    print( 'holes.best_combos(5)' )
    print()
    holes.print_combos( holes.best_combos(5) )

def do_best_bit_combos():  # (length):
    pass

def do_dots():  # (points):
    pass

def do_rulers():  # (length, left_padding=0):
    print(holes.rulers(10))
    numbers, ticks = holes.rulers(11)
    print('numbers: ' + numbers)
    print('ticks:   ' + ticks)
    (numbers, ticks) = holes.rulers(length=12)
    print(numbers + '\n' + ticks)
    print()
    print(numbers)
    print(ticks)
    (numbers, ticks) = holes.rulers(length=12, left_padding=8)
    print(numbers)
    print(ticks)

def do_ruler():  # (length=30, left_padding=0):
    print(holes.ruler(15))
    print(holes.ruler(16))
    print(holes.ruler(19))
    print(holes.ruler(20))
    print(holes.ruler(20, 2))

def do_print_combos():  # (combos):
    # Done implicitly in many other tests.
    # TODO: Consider putting simple print_combos_for_test()
    #       here in test module, to separate explicit testing
    #       of holes.print_combos().  Similar issue with holes.dots()
    #   OR: Better yet, test real holes.print_combos(), etc. carefully
    #       first in testing order, WARN if they are bad maybe,
    #       then use normal holes.dots() and holes.print_combos() so that
    #       testing output matches real output.
    pass

def do_print_bit_combos():  # (bit_combos):
    pass

def do_print_best_combos():  # (length):
    pass

def do_print_best_bit_combos():  # (length):
    pass

def do_print_best_combos_thru():  # (max_length):
    pass

def do_print_best_bit_combos_thru():  # (max_length):
    pass

def do_log_filename():
    print(holes.log_filename())


def print_points_for_test(points):
    print(holes.dots(points), points)
    # print(holes.pair_distances(points))
    dc = holes.distances_covered(points)
    print(dc)
    if len(dc) > 0:
        distances_wanted = set(range(1, max(dc)+1))
        print(distances_wanted)
        print(dc == distances_wanted)

def execute_sanity_tests():
    # Lots of changes possibly since these were tested.
    print_points_for_test( range(0, 15+1) )
    print_points_for_test( set() )
    print_points_for_test( set((0,1,4,3)) )
    print_points_for_test( (0,1,4,6) )
    print_points_for_test( (0,1,3,6,10,12,13) )

    # do_printlog()   # Add logging to test_holes.py first.
    # do_points_from_bits()
    # do_bits_from_points()

    # do_distances_covered()
    do_combinations_count()
    do_combos_with_n_dots()
    # do_n_dots_in_bit_combo()
    do_possible_combos()
    # do_possible_bit_combos()
    do_combo_measures()
    # do_bit_combo_measures()
    do_good_combos()
    # do_good_bit_combos()
    do_best_combos()
    # do_best_bit_combos()

    # do_dots()
    do_rulers()
    do_ruler()

    # do_print_combos()
    # do_print_bit_combos()
    # do_print_best_combos()
    # do_print_best_bit_combos()
    # do_print_best_combos_thru()
    # do_print_best_bit_combos_thru()

    # do_log_filename()   # Add logging to test_holes.py first.

    return


if __name__ == '__main__':

    #print('Version: ' + __version__)
    #execute_sanity_tests()
    #import doctest
    #doctest.testfile('test_holes.txt')

    #unittest.main()
    time_combos_with_n_dots()
    time_distances_covered()


