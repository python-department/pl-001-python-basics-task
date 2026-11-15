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


# TODO: замените заглушки (0) на корректные значения, см. TASK.md.
# Все константы, зависящие от ёмкостей *_BITS, должны вычисляться из них.

# Twitter's original Snowflake epoch: 2010-11-04 01:42:54.657 UTC.
EPOCH_MS_DEFAULT: Final[int] = 1288834974657

# Node identifier used when the caller does not supply one.
NODE_ID_DEFAULT: Final[int] = 1

# Width of each field, in bits.
TIMESTAMP_BITS: Final[int] = 41
NODE_ID_BITS: Final[int] = 10
SEQUENCE_ID_BITS: Final[int] = 12

# Largest value each field can hold.
TIMESTAMP_MS_MAX: Final[int] = (1 << TIMESTAMP_BITS) - 1
NODE_ID_MAX: Final[int] = (1 << NODE_ID_BITS) - 1
SEQUENCE_ID_MAX: Final[int] = (1 << SEQUENCE_ID_BITS) - 1

# Здесь можно добавить собственные вспомогательные константы
# (например, сдвиги полей при сборке идентификатора).
NODE_ID_SHIFT = SEQUENCE_ID_BITS
TIMESTAMP_SHIFT = NODE_ID_SHIFT + NODE_ID_BITS
