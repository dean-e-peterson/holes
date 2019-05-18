# {{{ vim fold marker for module-level doctext
"""
This module finds the minimum number of dots/ticks on a straightedge,
or HOLES in a template, such that you can still mark out any integer
length up the total length using pairs of the tick marks/dots/holes.

This implementation of the holes base class uses numpy to try to
boost the speed of doing bitwise operations.
"""
# }}}


import logging  # {{{
import numpy as np
from . import _base
from . import _util
from . import bitbased
from . import gospers

__version__ = _util.__version__
__all__ = []

logger = _util.logger
# }}}


class HolesBitwiseNumpy(bitbased.HolesBitwise):
    # {{{
    # {{{ docstring & comments folded
    """
    Holes class implemented with bitwise operations using Numpy.
    It is descended from HolesBitwise, not directly from HolesBase.
    """
    # }}}


    implementation_key = 'bitnumpy'
    implementation_name = 'bitwise implementation with numpy'

    def __init__(self):
        super().__init__()


    def bit_combos_that_measure(self, bitcombos, distance):
        # {{{
        """
        Bitwise generator wrapper for bit_combo_measures()
        Filters the iterator bitcombos.
        Yields only combinations containing pairs of points (ones)
        spaced each integer distance apart up through length.
        """
        # ToDo: Change chunkinate to make ndarrarys, not tuples?
        # ToDo: Clean this whole mess up?
        chunksize=2**16
        chunks = _util.chunkinate(bitcombos, chunksize=chunksize)
        # label = 'np chunks of {}'.format(chunksize)
        # chunks = self.log_progress(chunks, label, step=2**8)
        for chunk in chunks:
            mchunk = self.bit_combos_measure_np(chunk, distance)
            # Replace yield from for Python 3.2 compatibility.
            for bitcombo in mchunk:
                yield bitcombo
        # }}}


    def bit_combos_measure_np(self, chunk, distance):
        # {{{
        """
        Test a sequence of bitwide combinations using numpy,
        Only return those with pairs separated by 1 through distance.
        """
        # Note: if line below fails, try wrapping chunk in tuple()
        combos = np.array(chunk, dtype=np.int_)
        spacings = np.array(range(1, distance + 1), dtype=np.int_)

        # Reshape array, adding dummy dimensions that the arrays are
        # only 1 long in, so that when we calculate the matrix of what
        # spacings are measured by what combos, numpy's broadcasting
        # rules will pretend the values have been copied along the
        # necessary axes to give us a 2-D table of all possible
        # combinations of combos and spacings.   For details,
        # Read up on numpy's "broadcasting".
        combos.shape = (len(combos), 1)
        spacings.shape = (1, len(spacings))
        #self.print_numpy_array_in_binary(combos)

        # Calculate a matrix showing, for each combo,
        # what distances does it have pairs that measure.
        combos_measure_matrix = (combos & (combos >> spacings)) != 0
        #self.print_numpy_array_in_binary(combos_measure_matrix)

        combos_measure = combos_measure_matrix.all(axis=1)
        #self.print_numpy_array_in_binary(combos_measure_sums)

        combos.shape = (len(combos))

        combos_which_measure = combos[combos_measure]
        #self.print_numpy_array_in_binary(combos_which_measure)

        return tuple(combos_which_measure)
        # }}}


    ## ToDo: Do something with this.
    def print_numpy_array_in_binary(self, array):
        # from http://stackoverflow.com/questions/23124694/
        string_array = np.array(tuple(map(bin, array.flatten())))
        string_array.shape = array.shape
        print(string_array)
        # Or http://docs.scipy.org/doc/numpy/reference/generated
        #          /numpy.set_printoptions.html
        #np.set_printoptions(formatter={'int_kind': bin})
        #print(array)
        #np.set_printoptions(formatter=None)


    # }}} end of vim class fold


_base.register_implementation(HolesBitwiseNumpy)

