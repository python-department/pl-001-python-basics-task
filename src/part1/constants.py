from typing import Final


def bits_value_max(n: int) -> int:
    return 2**n - 1


EPOCH_MS_DEFAULT: Final[int] = 1219190400

# Node identifier used when the caller does not supply one.
NODE_ID_DEFAULT: Final[int] = 1

# Width of each field, in bits.
TIMESTAMP_BITS: Final[int] = 41
NODE_ID_BITS: Final[int] = 10
SEQUENCE_ID_BITS: Final[int] = 12


TIMESTAMP_MS_MAX: Final[int] = bits_value_max(TIMESTAMP_BITS)
NODE_ID_MAX: Final[int] = bits_value_max(NODE_ID_BITS)
SEQUENCE_ID_MAX: Final[int] = bits_value_max(SEQUENCE_ID_BITS)

TIMESTAMP_MOVE: Final[int] = NODE_ID_BITS + SEQUENCE_ID_BITS
