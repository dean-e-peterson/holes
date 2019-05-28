"""
holes package utility functions, common constants, etc.
"""

import logging
import time
import math
from math import factorial
import itertools
import functools

# Module global stuff {{{
__all__ = []
__version__ = '0.6.0.multi'
__author__ = 'lethargo'

HOLEY_TIME_FORMAT = '%Y/%m/%d %H:%M:%S'
HOLEY_LOGGER = 'holes'
logger = logging.getLogger(HOLEY_LOGGER)
logger.addHandler(logging.NullHandler())  # Libraries seen, not heard.

###
# TODO: OR, should I make the distinction logging/results,
#       not try to create console output in the library here,
#
#       BUT, provide a utility function for a printable string
#       of one combo, which callers can map() across combos plural?
#       Or, make the results combo objects with a __str__() method?
#
# Write suggested STDOUT output to logging subsystem, so that users of
# this can log it and/or output it to the console, or just ignore it.
#HOLEY_OUTPUT = 'holes.output'
#outlog = logging.getLogger(HOLEY_OUTPUT)
# }}}


def logfunc(func):
    # {{{
    """ Decorator to time and log a function call. """
    # @functools.wraps ensures that the decorated function's __name__
    # is the name of the decorated function, not 'func_wrapper'.
    @functools.wraps(func)
    def func_wrapper(*args, **kwargs):
        # If you log function arguments beware of consuming iterators.
        t1 = time.time()

        result = func(*args, **kwargs)

        t2 = time.time()
        logger.debug('{:>25} - returned - elapsed {:.6f} sec'.format(
            func.__name__ + '()',
            t2 - t1))
        return result

    # Don't call it here, just return it as a callable wrapper.
    return func_wrapper
    # }}}


# Try getting rid of...
# def printlog(* args):
    # # {{{
    # """ {{{
    # Both print something and log it.
    # Mimics print by accepting multiple (or no) args, BUT,
    # Caution: Unlike print(), when passing multiple args,
    #          all args must already be strings.  So you may
    #          need to call str() on some args yourself...
    #              printlog('number', 42)       # Fails
    #              printlog('number', str(42))  # Succeeds
    # """
    # # }}}
    #
    # # Print it.
    # print(* args)
    #
    # # Convert n args to just 1 arg so logging can handle it.
    # if len(args)==0:
    #     log_arg = ''
    # elif len(args)==1:
    #     log_arg = args[0]
    # elif len(args) >= 2:
    #     # Mimic print('a','b'),
    #     # BUT, unlike print, the following join call
    #     # cannot accept things like numeric literals.
    #     log_arg = ' '.join(args)
    #
    # # Log the resulting singular arg.
    # logger.info(log_arg)
    # # }}}


def print_combos(combos):
    # {{{
    format_str  = ' {len:>3d} / {ndots:<3d}  {dots:s}     {points}'

    first = True
    for c in combos:
        if first:
            # Print ruler before first entry.
            # Done inside loop to use first entry to guage ruler size.
            # TODO: Add optional length param to allow avoiding max(c)
            length = max(c)
            padding = " " * 12
            print(padding + ruler_numbers(length))
            print(padding + ruler_ticks(length))
            print()
            first = False

        # Print this combo's info.
        info = { 'len': max(c),
                 'ndots': len(c),
                 'dots': dots(c),
                 'points': tuple(c) }
        print(format_str.format( **info ))  # Log but as debug?
    # }}}


def dots(sequence, spacing=2):
    # {{{
    """
    A string with sequence shown as dots on an invisible number line.
    sequence is a sequence or set of non-negative integers.
    spacing is how many characters apart each position is.
    Positions not in the sequence are left blank, like 0 & 3 in...
    Example: dots((1,2,4,7,8), 2) would give '  . .   .     . .',
    """
    if spacing < 1: raise ValueError('spacing must be >= 1')

    result=''
    if len(sequence) > 0:
        if min(sequence) < 0:raise ValueError('sequence must be >= 0')

        for pos in range(0, max(sequence)+1):
            if pos in sequence:
                result += '.' + ' ' * (spacing-1)
            else:
                result += ' ' * spacing
    return result
    # }}}


def ruler_ticks(length, spacing=2, unittick="'", fivetick="|"):
    # {{{
    """
    A string of tick marks suitable for a fixed-width font ruler.
    spacing is how many characters wide a single ruler unit should be.
    length is in ruler units, & will be rounded to next multiple of 5.
    """
    if length < 0: raise ValueError('length must be >= 0')
    if spacing < 1: raise ValueError('spacing must be >= 1')

    # How many sections of 5 units, rounding up.
    section_count = math.ceil(length / 5)
    spaces = " " * (spacing - 1)
    section = ((spaces + unittick) * 4) + spaces + fivetick
    ruler = fivetick + (section * section_count)
    return ruler
    # }}}


def ruler_numbers(length, spacing=2):
    # {{{
    """
    A string of spaced numbers suitable for use with ruler_tickmarks.
    spacing is how many characters wide a single ruler unit should be.
    length is in ruler units, & will be rounded to next multiple of 5.
    """
    if length < 0: raise ValueError('length must be >= 0')
    if spacing < 1: raise ValueError('spacing must be >= 1')

    # How many sections of 5 units, rounding up.
    section_count = math.ceil(length / 5)
    section_spacing = spacing * 5
    section_fmt = "{:>" + str(section_spacing) + "}"
    number_fmt = "0" + section_fmt * section_count

    numbers = range(0, (section_count * 5) + 1, 5)
    # Chop off the leading 0, which was manually formatted as 1 wide.
    numbers = tuple(numbers)[1:]
    return number_fmt.format( *numbers)
    # }}}


def rsplit_size(string, size=4):
    # {{{
    """
    Split the string every size characters working right to left.
    Return a tuple containing the resulting segments, rightmost first.
    """
    remaining = string
    sections = []
    while remaining:
        remaining, section = remaining[:-size], remaining[-size:]
        sections.append(section)
    return tuple(sections)
    # }}}


def format_binary(number, digits=0, sections=4):
    # {{{
    """
    Returns a string containing number as a formatted binary number.
    If digits is greater than the actual number of digits, it
    zero fills to the left.  The digits are then broken into
    space-separated sections, by default into 4 digit nibbles.
    """
    # ToDo: Bounds check to disallow negatives, or handle them better.
    binstr = '{:b}'.format(number)
    binstr = binstr.zfill(digits)
    binstr_sections = reversed(rsplit_size(binstr, sections))
    formatted = ' '.join(binstr_sections)
    return formatted
    # }}}


def sequence_from_bits(bits_int):
    # {{{
    """
    Convert bitwise encoding of points in an integer to a sequence.
    The right-most binary digit is digit 0, then 1,2,3...
    If a given binary digit is a 1, that digit's number is added to
    the returned sequence.
    Example:
        sequence_from_bits(0b01001101)
        Interpreted right to left, the binary number contains...
            digit 0 is a 1, so 0 is in the sequence,
            digit 1 is a 0, so 1 is NOT in the sequence,
            digit 2 is a 1, so 2 is in the sequence,
            digit 3 is a 1, so 3 is in the sequence,
            digit 4 is a 0, so 4 is NOT in the sequence,
            digit 5 is a 0, so 5 is NOT in the sequence,
            digit 6 is a 1, so 6 is in the sequence,
            digit 7 is a 0, so 7 is NOT in the sequence,
        ...so the sequence returned would be (0,2,3,6)
    """
    sequence = []
    bit_position = 0
    bit_value = 2**bit_position

    while bits_int >= bit_value:

        # Use bitwise AND to test the bit at bit_position.
        if bits_int & bit_value:
            sequence.append(bit_position)

        bit_position += 1
        bit_value = 2**bit_position

    # Convert to a tuple for consistency and possibly performance.
    return tuple(sequence)
    # }}}


def bits_from_sequence(sequence):
    # {{{
    """
    Encode a sequence of positive numbers as 1 bits in an integer.
    The right-most binary digit is digit 0, then 1,2,3...
    In essense this is the inverse of sequence_from_bits().
    Example:
        bits_from_sequence((0,2,3,6)) would return 0b1001101
    """
    bits_int = 0

    if sequence == (): return 0  # Handle the empty sequence case.

    for bit_position in range(0, max(sequence) + 1):
        if bit_position in sequence:
            # Use bitwise OR to include the bit at bit_position.
            bit_value = 1 << bit_position
            bits_int = bits_int | bit_value

    return bits_int
    # }}}


def combinations_count(iterable, r):
    # {{{
    """
    The number of combos itertools.combinations() will generate.
    The formula used is from the Python 3.5.1 documentation on the
    itertools.combinations() function itself.  Specifically...
        The number of items returned is ...
        n! / r! / (n-r)! when 0 <= r <= n
        ... or ...
        zero when r > n
    """
    n = len(iterable)
    if r < 0:
        raise ValueError(
            'Negative number passed to combinations_count for r.')
    elif r > n:
        return 0
    elif r >= 0:
        # Integer division // because we know # of combos is integer.
        return factorial(n) // (factorial(r) * factorial(n-r))
    # }}}


def chunkinate(iterable, chunksize):
    # {{{
    """Gather elements from an iterable and emit them in chunks."""
    def get_chunk():
        # TODO: Replace tuple() with numpy array when do it for real?
        # If you return a bare islice, "while chunk" cannot tell when
        # the input iterable is empty.  It seems consumer can't!?
        #return itertools.islice(iterable, chunksize)
        return tuple(itertools.islice(iterable, chunksize))

    assert chunksize > 0
    chunk = get_chunk()
    while chunk:
        yield chunk
        chunk = get_chunk()
    # }}}


def dechunk(iterable):
    return itertools.chain.from_iterable(iterable)

