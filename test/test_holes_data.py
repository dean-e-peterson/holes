#!/usr/bin/env python3
"""Testing potential data structures for expected test results."""

#from pprint import pprint

class combo:
    # {{{
    def __init__(self, length, dotcount, bitcombo,
                 spans=False,
                 measures=False):
        self.length = length        # Possible items/max distance+1
        self.dotcount = dotcount    # Number of actual elements.
        self.bitcombo = bitcombo    # Integer giving sequence bitwise.
        self.spans = spans          # Does it contain endpoints?
        self.measures = measures    # Has pairs all distances apart?

    @property
    def sequence(self):
        "The combo, internally a bitwise integer, as a sequence"
        result = []
        for pos in range(self.length):
            if self.bitcombo & (1 << pos):
                result.append(pos)
        return tuple(result)

    def delta_set_str(self):
        """
        Binary reversed and with dots for zeros,
        for comparing with http://www.jjj.de/fxt/#fxtbook
        """
        binary_str = '{0:0{1}b}'.format(self.bitcombo, self.length)
        return binary_str[::-1].replace('0', '.')

    def __repr__(self):
        spans_str = 'Spans' if self.spans else '-'
        measures_str = 'Measures' if self.measures else '-'
        sequence_str = str(self.sequence).replace(' ','')
        FMT=''.join('({length}/{dotcount})  ' +
                    '{spans:^5s}  ' +
                    '{measures:^8s}  ' +
                    '0b{bitcombo:0{length}b}  ' +
                    '{deltaset}  ' +
                    '{sequence}')
        fmt_dict = {'length': self.length,
                    'dotcount': self.dotcount,
                    'spans':    'Spans' if self.spans else '-',
                    'measures': 'Measures' if self.measures else '-',
                    'bitcombo': self.bitcombo,
                    'deltaset': self.delta_set_str(),
                    'sequence': sequence_str}
        return FMT.format(** fmt_dict)
    # }}}

def print_combos(nested_dict):
    "Print combos in nested dict form, for checking the test data."
    for length_dict in nested_dict.values():
        for dotcount_list in length_dict.values():
            for combination in dotcount_list:
                print(combination)


# Expected result combos.
results = {
    # {{{
    # First key is length (distance+1).
    # Nested inner key is dotcount.
    0: {0: (combo(0, 0, 0b0),), # Actually 0b with 0 digits, but...
        },
    1: {0: (combo(1, 0, 0b0),),
        1: (combo(1, 1, 0b1),),
        },
    2: {0: (combo(2, 0, 0b00),),
        1: (combo(2, 1, 0b01),
            combo(2, 1, 0b10),),
        2: (combo(2, 2, 0b11, spans=True, measures=True),),
        },
    3: {0: (combo(3, 0, 0b000),),
        1: (combo(3, 1, 0b001),
            combo(3, 1, 0b010),
            combo(3, 1, 0b100),),
        2: (combo(3, 2, 0b011),
            combo(3, 2, 0b101, spans=True),
            combo(3, 2, 0b110, ),),
        3: (combo(3, 3, 0b111, spans=True, measures=True),),
        },
    4: {0: (combo(4, 0, 0b0000),),
        1: (combo(4, 1, 0b0001),
            combo(4, 1, 0b0010),
            combo(4, 1, 0b0100),
            combo(4, 1, 0b1000),),
        2: (combo(4, 2, 0b0011),
            combo(4, 2, 0b0101),
            combo(4, 2, 0b1001, spans=True),
            combo(4, 2, 0b0110),
            combo(4, 2, 0b1010),
            combo(4, 2, 0b1100),),
        3: (combo(4, 3, 0b0111),
            combo(4, 3, 0b1011, spans=True, measures=True),
            combo(4, 3, 0b1101, spans=True, measures=True),
            combo(4, 3, 0b1110),),
        4: (combo(4, 4, 0b1111, spans=True, measures=True),),
        },
    5: {0: (combo(5, 0, 0b00000),),
        1: (combo(5, 1, 0b00001),
            combo(5, 1, 0b00010),
            combo(5, 1, 0b00100),
            combo(5, 1, 0b01000),
            combo(5, 1, 0b10000),),
        2: (combo(5, 2, 0b00011),
            combo(5, 2, 0b00101),
            combo(5, 2, 0b01001),
            combo(5, 2, 0b10001, spans=True),
            combo(5, 2, 0b00110),
            combo(5, 2, 0b01010),
            combo(5, 2, 0b10010),
            combo(5, 2, 0b01100),
            combo(5, 2, 0b10100),
            combo(5, 2, 0b11000),),
        3: (combo(5, 3, 0b00111),
            combo(5, 3, 0b01011),
            combo(5, 3, 0b10011, spans=True),
            combo(5, 3, 0b01101),
            combo(5, 3, 0b10101, spans=True),
            combo(5, 3, 0b11001, spans=True),
            combo(5, 3, 0b01110),
            combo(5, 3, 0b10110),
            combo(5, 3, 0b11010),
            combo(5, 3, 0b11100),),
        4: (combo(5, 4, 0b01111),
            combo(5, 4, 0b10111, spans=True, measures=True),
            combo(5, 4, 0b11011, spans=True, measures=True),
            combo(5, 4, 0b11101, spans=True, measures=True),
            combo(5, 4, 0b11110),),
        5: (combo(5, 5, 0b11111, spans=True, measures=True),),
        },
} # End results combos }}}

if __name__ == '__main__':

    print_combos(results)

