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


    
_base.register_implementation(HolesBitwiseParallel)

