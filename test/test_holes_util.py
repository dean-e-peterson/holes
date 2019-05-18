"""
Unit tests for the holes package, _utils module.
Requires a symlink to the holes package in this script's directory.
"""
import unittest
import itertools
import logging
import io
from contextlib import contextmanager
import holes
import holes._util as _util

# ToDo: Stuff to help test logging.
# Workaround until Python 3.4's TestCase.assertLogs() context manager.
# holes_logger = logging.getLogger('holes')
# out_logger = logging.getLogger('holes.output')
# ? How should I go about this...
#   - Keep StringIO stream reference in global? closure? context mgr?
#   - Just check that anything was logged at all?
#   - Check # of lines logged at each level with collections.Counter?
#   - Return everything logged in a wad and let caller regex it?
# Ans:Check that something was logged >= a given level with ctx mgr?

@contextmanager
def assertLogsDean(logger=None, level=None):
    "Dean's bargain basement simulation of Python 3.4's assertLogs()"
    log_stream = io.StringIO()
    log = logging.getLogger(logger)
    if not level: level = logging.INFO
    log.setLevel(level)
    handler = logging.StreamHandler(stream=log_stream)
    log.addHandler(handler)

    # Execute code in the user's with block,
    # giving user access to the log_stream if they with ... as var
    # Although they might want to be careful using seek() on it :-/
    yield log_stream

    handler.flush()  # Needed?
    if not log_stream.getvalue():
        raise AssertionError('Nothing logged to {} level>={}'.format(
                             logger,
                             level))


class TestHolesUtil(unittest.TestCase):

    def assertCountItemsInIter(self, length, iterable, msg=None):
        "Checks that there are exactly count items in iterable."
        if not msg:
            msg = 'Wrong number of items in iterable'
        self.assertEqual(length, len(tuple(iterable)), msg)


    def test_dots(self): # {{{
        # (sequence, spacing=2)

        why = 'An exception should be raised if spacing < 1'
        with self.assertRaises(ValueError, msg=why):
            _util.dots((), spacing=-1)
        with self.assertRaises(ValueError, msg=why):
            _util.dots((), spacing=0)

        why = 'An exception should be raised for negative points'
        with self.assertRaises(ValueError, msg=why):
            _util.dots((-1,0,1,2))

        eq = self.assertEqual
        eq(_util.dots((0, 1)), '. . ', msg='default spacing is 2')
        eq(_util.dots(()), '')
        eq(_util.dots((), spacing=3), '')
        eq(_util.dots((0,), spacing=1), '.')
        eq(_util.dots((0,), spacing=2), '. ')
        eq(_util.dots((0,), spacing=3), '.  ')
        eq(_util.dots((1,), spacing=1), ' .')
        eq(_util.dots((1,), spacing=2), '  . ')
        eq(_util.dots((1,), spacing=3), '   .  ')
        eq(_util.dots((0,1), spacing=1), '..')
        eq(_util.dots((0,1), spacing=2), '. . ')
        eq(_util.dots((0,1), spacing=3), '.  .  ')
        eq(_util.dots((0,2), spacing=1), '. .')
        eq(_util.dots((0,2), spacing=2), '.   . ')
        eq(_util.dots((0,2), spacing=3), '.     .  ')
        eq(_util.dots((0,1,4,5,6), spacing=1),'..  ...')
        eq(_util.dots((0,1,4,5,6), spacing=2),'. .     . . . ')
        eq(_util.dots((0,1,4,5,6)),           '. .     . . . ')
        eq(_util.dots((0,1,4,5,6), spacing=3),'.  .        .  .  .  ')
    # }}}

    #def test_ruler_ticks(self):
        # (length, spacing=2, unittick="'", fivetick="|")

    #def test_ruler_numbers(self):
        # (length, spacing=2)

    # rsplit_size() tests {{{
    def test_rsplit_size_default(self):
        # Commented out doc_strings for clearer
        # output from TextTestRunner when verbosity=2.
        # "Testing rsplit_size() using default size of 4."
        # (string, size=4)
        seqeq = self.assertSequenceEqual

        # Following tests assume size=4 is a default for rsplit_size.
        seqeq(_util.rsplit_size(''), ())
        seqeq(_util.rsplit_size('a'), ('a',))
        seqeq(_util.rsplit_size('abcd'), ('abcd',))
        seqeq(_util.rsplit_size('abcdef'), ('cdef', 'ab'))
        seqeq(_util.rsplit_size('abcdefghijk'),
                               ('hijk', 'defg', 'abc'))
        seqeq(_util.rsplit_size('abcdefghijkl'),
                               ('ijkl', 'efgh', 'abcd'))
        seqeq(_util.rsplit_size('abcdefghijklm'),
                               ('jklm', 'fghi', 'bcde', 'a'))

    #def test_rsplit_size_bounds(self):
        # "Testing rsplit_size() bounds."
        # ToDo: Test passing size=0, and maybe passing None for str.

    def test_rsplit_size_1(self):
        # "Testing rsplit_size() using size of 1."
        seqeq = self.assertSequenceEqual

        seqeq(_util.rsplit_size('', size=1), ())
        seqeq(_util.rsplit_size('a', size=1), ('a',))
        seqeq(_util.rsplit_size('ab', size=1), ('b', 'a'))
        seqeq(_util.rsplit_size('abcde', size=1),
                               ('e', 'd', 'c', 'b', 'a'))

    def test_rsplit_size_3(self):
        # "Testing rsplit_size() using size of 3."
        seqeq = self.assertSequenceEqual

        seqeq(_util.rsplit_size('', size=3), ())
        seqeq(_util.rsplit_size('a', size=3), ('a',))
        seqeq(_util.rsplit_size('abcd', size=3), ('bcd', 'a'))
        seqeq(_util.rsplit_size('abcdef', size=3), ('def', 'abc'))
        seqeq(_util.rsplit_size('abcdefgh', size=3),
                               ('fgh', 'cde', 'ab'))

    def test_rsplit_size_4(self):
        # "Testing rsplit_size() using explicitly passed size of 4."
        seqeq = self.assertSequenceEqual

        seqeq(_util.rsplit_size('a', size=4), ('a',))
        seqeq(_util.rsplit_size('abcd', size=4), ('abcd',))
        seqeq(_util.rsplit_size('abcdef', size=4), ('cdef', 'ab'))
        seqeq(_util.rsplit_size('abcdefghijkl', size=4),
                               ('ijkl', 'efgh', 'abcd'))

    def test_rsplit_size_16(self):
        # "Testing rsplit_size() using size of 16."
        seqeq = self.assertSequenceEqual

        seqeq(_util.rsplit_size('abcdefghijklmnop', size=16),
                               ('abcdefghijklmnop',))
        seqeq(_util.rsplit_size('abcdefghijklmnopq', size=16),
                               ('bcdefghijklmnopq', 'a'))
    # }}}

    # format_binary() tests {{{
    def test_format_binary_default(self):
        eq = self.assertEqual

        eq(_util.format_binary(0), '0')
        eq(_util.format_binary(1), '1')
        eq(_util.format_binary(2), '10')
        eq(_util.format_binary(15), '1111')
        eq(_util.format_binary(16), '1 0000')
        eq(_util.format_binary(99), '110 0011')
        eq(_util.format_binary(127), '111 1111')
        eq(_util.format_binary(128), '1000 0000')
        eq(_util.format_binary(299), '1 0010 1011')
        # ToDo: negative #'s?

    def test_format_binary_nondefault(self):
        # (number, digits=0, sections=4)
        eq = self.assertEqual

        eq(_util.format_binary(0, digits=4), '0000')
        eq(_util.format_binary(14, digits=8), '0000 1110')
        eq(_util.format_binary(299, digits=8), '1 0010 1011')
        eq(_util.format_binary(299, digits=10), '01 0010 1011')

        eq(_util.format_binary(0, sections=5), '0')
        eq(_util.format_binary(255, sections=5), '111 11111')

        eq(_util.format_binary(5, digits=4, sections=8), '0101')
        eq(_util.format_binary(299, digits=11, sections=8),
                               '001 00101011')
        # ToDo: negative #'s?

    # }}}

    # sequence_from_bits() tests {{{
    def test_sequence_from_bits(self):
        # (bits_int)
        seqeq = self.assertSequenceEqual

        seqeq(_util.sequence_from_bits(0b0), ())
        seqeq(_util.sequence_from_bits(0b1), (0,))
        seqeq(_util.sequence_from_bits(0b10), (1,))
        seqeq(_util.sequence_from_bits(0b11), (0,1))
        seqeq(_util.sequence_from_bits(0b10101), (0, 2, 4))
        seqeq(_util.sequence_from_bits(0b01010), (1, 3))
        seqeq(_util.sequence_from_bits(0b11111), (0, 1, 2, 3, 4))
        seqeq(_util.sequence_from_bits(0b100000), (5,))
        seqeq(_util.sequence_from_bits(0b101101), (0, 2, 3, 5))
    # }}}

    # bits_from_sequence() tests {{{
    def test_bits_from_sequence(self):
        # (sequence):
        eq = self.assertEqual

        eq(_util.bits_from_sequence(()), 0b0)
        eq(_util.bits_from_sequence((0,)), 0b1)
        eq(_util.bits_from_sequence((1,)), 0b10)
        eq(_util.bits_from_sequence((0,1)), 0b11)
        eq(_util.bits_from_sequence((0, 2, 4)), 0b10101)
        eq(_util.bits_from_sequence((1, 3)), 0b01010)
        eq(_util.bits_from_sequence((0, 1, 2, 3, 4)), 0b11111)
        eq(_util.bits_from_sequence((5,)), 0b100000)
        eq(_util.bits_from_sequence((0, 2, 3, 5)), 0b101101)
    # }}}

    # combinations_count() tests {{{   ## TODO: Not working at all

    def test_combinations_count_1_small(self):
        # (iterable, r)
        #Note: Do small counts by actually running
        #      itertools.combinations for ease and accuracy.
        itercount = self.assertCountItemsInIter

        itercount(_util.combinations_count((), 0),
                    itertools.combinations((), 0))
        itercount(_util.combinations_count((), 1),
                    itertools.combinations((), 1))
        itercount(_util.combinations_count((1,), 0),
                    itertools.combinations((1,), 0))
        itercount(_util.combinations_count((1,), 1),
                    itertools.combinations((1,), 1))
        itercount(_util.combinations_count((), 1),
                    itertools.combinations((), 1))
        itercount(_util.combinations_count((-1,0,2), 2),
                    itertools.combinations((-1,0,2), 2))
        itercount(_util.combinations_count(('a', 'b', 123, (1,1)), 2),
                    itertools.combinations(('a', 'b', 123, (1,1)), 2))
        itercount(_util.combinations_count((1,2,3,4), 0),
                    itertools.combinations((1,2,3,4), 0))
        itercount(_util.combinations_count((1,2,3,4), 1),
                    itertools.combinations((1,2,3,4), 1))
        itercount(_util.combinations_count((1,2,3,4), 2),
                    itertools.combinations((1,2,3,4), 2))
        itercount(_util.combinations_count((1,2,3,4), 3),
                    itertools.combinations((1,2,3,4), 3))
        itercount(_util.combinations_count((1,2,3,4), 4),
                    itertools.combinations((1,2,3,4), 4))
        itercount(_util.combinations_count((1,2,3,4), 5),
                    itertools.combinations((1,2,3,4), 5))
        # Finally, since strings are sequences of characters.
        itercount(_util.combinations_count('To be or not', 5),
                    itertools.combinations('To be or not', 5))


    def test_combinations_count_2_large(self):
        # (iterable, r)
        # Test some big combos with hard-coded values to save the
        # time it would take to iterate over a large iterable.
        eq = self.assertEqual

        # These hardcoded numbers were obtained by running...
        # len(tuple(itertools.combinations(range(23), 12)))
        eq(_util.combinations_count(range(23), 0), 1)
        eq(_util.combinations_count(range(23), 1), 23)
        eq(_util.combinations_count(range(23), 2), 253)
        eq(_util.combinations_count(range(23), 12), 1352078)
        eq(_util.combinations_count(range(23), 17), 100947)
        eq(_util.combinations_count(range(23), 22), 23)
        eq(_util.combinations_count(range(23), 23), 1)
        eq(_util.combinations_count(range(23), 24), 0)

    def test_combinations_count_bounds(self):
        # (iterable, r)
        with self.assertRaises(ValueError):
            _util.combinations_count((1,2,3,4), -1)
        with self.assertRaises(TypeError):
            _util.combinations_count(1, 1)  # Not a sequence/iterator


    # }}}
