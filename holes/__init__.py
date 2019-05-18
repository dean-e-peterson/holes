#!/usr/bin/env python3
# {{{ vim fold marker for hiding lines
"""
holes package

The holes package contains implementations which find combinations
of dots/holes/tick-marks that can measure all integer distances
up through a given length.

For example, you could use it to find the fewest number of
tick-marks that you could mark on a straightedge and still
find pairs of tick-marks measuring all distances from
1, 2, 3, ... , n-1, n.

I will try to start using following terms consistently:
    length
        Number of possible positions including 0. Equals distance + 1.
    dots
        Positions that actually have a dot/hole/tick-mark.
    distance
        Highest position minus lowest(0).  Equals length - 1.
        (I first thought of the problem as dots on a ruler spanning a
         given "distance", but I found that combinatorics math
         uses the "length" of a set of elements, including my zero.
         Example: 0--1--2 is a ruler 2 long, with 3 integer positions)
    measures
        Means there is at least one pair of dots that distance apart.


"""
# }}}

# Import implementation class modules so they can register themselves.
# Import utility module(s) for consistency.
from . import _util
from . import _base
from . import iterbased
from . import bitbased
from . import iterold
# from . import bitold  # Implementation no longer in service.

# Make numpy dependency of bitnumpy optional.
try:
    from . import bitnumpy
except ImportError as err:
    # print('\nNote: numpy implementation unavailable:', err, '\n')
    pass

__all__ = []

