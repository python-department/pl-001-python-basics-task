"""Twitter Snowflake identifier generator.

Snowflake produces roughly time-ordered 64-bit integer identifiers without
coordination between nodes. Each identifier packs the milliseconds elapsed
since a custom epoch, a node identifier and a per-millisecond sequence counter
into a single 63-bit positive integer (see ``constants`` for the layout).

The public entry point is :func:`generate_snowflake_id`. It is stateless: the
caller passes the sequence counter on every call and is responsible for
advancing it within a millisecond and resetting it when the clock ticks over.

Each packed field can be read back on its own with :func:`decode_timestamp_ms`,
:func:`decode_node_id` and :func:`decode_sequence_id`.
"""

import time

from .constants import (
    EPOCH_MS_DEFAULT,
    NODE_ID_BITS,
    NODE_ID_DEFAULT,
    NODE_ID_MAX,
    SEQUENCE_ID_BITS,
    SEQUENCE_ID_MAX,
    TIMESTAMP_MS_MAX,
)


def read_current_millis(epoch_ms: int) -> int:

    a = int(time.time()) * 1000 - epoch_ms
    return a


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:

    b = (snowflake_id >> (SEQUENCE_ID_BITS + NODE_ID_BITS)) + epoch_ms
    return b


def decode_node_id(snowflake_id: int) -> int:

    c = (snowflake_id >> SEQUENCE_ID_BITS) & NODE_ID_MAX

    return c


def decode_sequence_id(snowflake_id: int) -> int:

    d = snowflake_id & SEQUENCE_ID_MAX
    return d


def generate_snowflake_id(
    sequence_id: int,
    node_id: int = NODE_ID_DEFAULT,
    epoch_ms: int = EPOCH_MS_DEFAULT,
) -> int | None:

    if not (0 <= node_id <= NODE_ID_MAX):
        print(f"node_id must be in [0, {NODE_ID_MAX}]", f"{node_id}", sep="\n")
        return None

    if not (0 <= sequence_id <= SEQUENCE_ID_MAX):
        print(
            f"sequence_id must be in [0, {SEQUENCE_ID_MAX}]", f"{sequence_id}", sep="\n"
        )
        return None
    time_after_epoch = read_current_millis(epoch_ms)

    if time_after_epoch > TIMESTAMP_MS_MAX:
        print("overflows")
        return None
    return (
        time_after_epoch << (SEQUENCE_ID_BITS + NODE_ID_BITS)
        | node_id << SEQUENCE_ID_BITS
        | sequence_id
    )
