from typing import Final


# Twitter's original Snowflake epoch: 2010-11-04 01:42:54.657 UTC.
EPOCH_MS_DEFAULT: Final[int] = 1288834974657

# Node identifier used when the caller does not supply one.
NODE_ID_DEFAULT: Final[int] = 1

# Width of each field, in bits.
TIMESTAMP_BITS: Final[int] = 41
NODE_ID_BITS: Final[int] = 10
SEQUENCE_ID_BITS: Final[int] = 12

# Largest value each field can hold.
TIMESTAMP_MS_MAX: Final[int] = 2**TIMESTAMP_BITS - 1
NODE_ID_MAX: Final[int] = 2**NODE_ID_BITS - 1
SEQUENCE_ID_MAX: Final[int] = 2**SEQUENCE_ID_BITS - 1

# Здесь можно добавить собственные вспомогательные константы
# (например, сдвиги полей при сборке идентификатора).
