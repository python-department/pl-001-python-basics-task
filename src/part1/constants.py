from typing import Final


EPOCH_MS_DEFAULT: Final[int] = 1288834974657

NODE_ID_DEFAULT: Final[int] = 1

TIMESTAMP_BITS: Final[int] = 41
NODE_ID_BITS: Final[int] = 10
SEQUENCE_ID_BITS: Final[int] = 12


TIMESTAMP_MS_MAX: Final[int] = 2**TIMESTAMP_BITS - 1
NODE_ID_MAX: Final[int] = 2**NODE_ID_BITS - 1
SEQUENCE_ID_MAX: Final[int] = 2**SEQUENCE_ID_BITS - 1
