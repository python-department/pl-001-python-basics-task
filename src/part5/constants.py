"""Bit layout and default epoch for the Twitter Snowflake ID generator.

A Snowflake identifier is a 63-bit positive integer packed as follows, from
the most significant bit downwards:

    1 bit   unused sign bit, always zero
    41 bits milliseconds elapsed since a custom epoch
    10 bits node identifier
    12 bits per-millisecond sequence counter

The shift and mask constants should be derived from the bit widths so that
changing a width keeps everything else consistent.
"""

from typing import Final


# Twitter's original Snowflake epoch: 2010-11-04 01:42:54.657 UTC.
EPOCH_MS_DEFAULT: Final = 1288834974657

# Node identifier used when the caller does not supply one.
NODE_ID_DEFAULT: Final = 1


# Width of each field, in bits.
def my_max_value(n: int) -> int:
    return int(2**n - 1)


TIMESTAMP_BITS: Final = (
    41  # число миллисекунд прощедщих с момента пользовательской эпохи
)
NODE_ID_BITS: Final = 10  # номер узла
SEQUENCE_ID_BITS: Final = 12  # порядковый номер

TIMESTAMP_SHIFT: Final = NODE_ID_BITS + SEQUENCE_ID_BITS

# так как номер и время(все три строчки) беззнаковые
TIMESTAMP_MS_MAX: Final = my_max_value(TIMESTAMP_BITS)
NODE_ID_MAX: Final = my_max_value(NODE_ID_BITS)
SEQUENCE_ID_MAX: Final = my_max_value(SEQUENCE_ID_BITS)
