"""
Gosper's hack, or something like it, for bit combination generation.

Based ultimately on Gosper's hack in HAKMEM 175.
Based directly on code.stephenmorley.org/articles/hakmem-item-175/
"""

def bit_combos_gospers(length, dots):
    # TODO: Correct name and documentation for gosper's hack.

    if dots == 0:
        yield 0
        return

    # Could replace with exceptions, but it might be better to
    # validate input before calling a generator anyway.
    assert length > 0
    assert dots > 0
    assert dots <= length

    # Gosper's hack finds the next highest integer
    # with the same number of 1 bits,
    # so start with the smallest integer with dot 1 bits.
    # As an aid, I will put bits going through the operations
    # in comments above the operation.  To read, follow a given
    # example down its column through the operations.
    # Examples will all have 3 dots, that is, 3 one bits.
    #               Example 1
    #              (read down)
    # start value   0000 0111
    bits = (1 << dots) - 1

    while True:
        yield bits

        # Note that everything inside the loop is based on
        # Gosper's hack, and needs only the input bits integer.
        # The following needs no prior knowledge of the
        # number of dots/1-bits.  We only needed to pass dots
        # to this generator function to create the starting value.

        # Find rightmost 1 bit.
        # (two's-complement negation does a NOT followed by +1)
        #           Example 1   Example 2   Example 3
        #            (contd)   (read down) (read down)
        # bits      0000 0111   0100 1100   1110 0000
        # !bits     1111 1000   1011 0011   0001 1111
        # -bits     1111 1001   1011 0100   0010 0000
        # ...&bits  0000 0001   0000 0100   0010 0000
        rightmost = -bits & bits

        # Get left bits of answer set up by taking original bits,
        # and adding the rightmost 1 again.  This add causes a
        # rippling carry along rightmost contiguous ones,
        # thereby setting the rightmost non-trailing 0 bit to one.
        # and clearing out everything right of the newly set 1.
        # bits      0000 0111   0100 1100   1110 0000
        # r-most    0000 0001   0000 0100   0010 0000
        # leftbits  0000 1000   0101 0000  10000 0000 (overflow, 1110 0000 was last 8-bit combo)
        #           ^^^^ ^      ^^^^
        leftbits = bits + rightmost

        # Test for overflow/went too far, and bail out.
        # The zero check is for if we truly overflowed
        # whatever integer size is being used.
        # The length check is for if we overflowed
        # our own, specified limits.
        if leftbits & (1 << length) != 0 or leftbits == 0:
            break  # <--Loop exit point.

        # Use XOR to determine what bits have changed so far.
        # (XOR)     0000 1111   0001 1100  11110 0000
        changed = bits ^ leftbits

        # If the original rightmost bit was part of a contiguous
        # run of 1 bits, the earlier add and carry got rid of some.
        # We need them back, but far on the right.
        # They were among the changed bits the XOR found,
        # So move the XOR results all the way to the right
        # by dividing by the original rightmost bit.
        # changed   0000 1111   0001 1100  11110 0000
        # r-most    0000 0001   0000 0100   0010 0000
        # (divide)  0000 1111   0000 0111   0000 1111
        lostbits = changed // rightmost

        # In addition to the lost bits, the changed bits
        # also included the leftmost of the one(s) that
        # was eliminated by the carry from the original add,
        # and the rightmost non-trailing 0 that that one
        # carried to.  In other words, we have two too many
        # rightmost ones.  Shift 2 of them off the right end.
        # This leaves us the correct right side bits
        # of our answer.
        # lostbits  0000 1111   0000 0111   0000 1111
        # ...>>2    0000 0011   0000 0001   0000 0011
        #                  ^^           ^
        rightbits = lostbits >> 2

        # Finally, we OR together the left side bits we calculated
        # before with the right side bits we just got.
        # leftbits  0000 1000   0101 0000  10000 0000
        # r-bits    0000 0011   0000 0001   0000 0011
        # answer    0000 1011   0101 0001  10000 0011
        #
        # This is our answer, the next highest integer with the
        # same number of 1 bits as the input at the top of the loop.
        bits = leftbits | rightbits

    # }}}

