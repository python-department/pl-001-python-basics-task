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
    NODE_ID_DEFAULT,
    NODE_ID_MAX,
    NODE_ID_SHIFT,
    SEQUENCE_ID_MAX,
    TIMESTAMP_MS_MAX,
    TIMESTAMP_SHIFT,
)


def read_current_millis(epoch_ms: int) -> int:

    return int(time.time() * 1000) - epoch_ms


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:

    return (snowflake_id >> TIMESTAMP_SHIFT) + epoch_ms


def decode_node_id(snowflake_id: int) -> int:

    return (snowflake_id >> NODE_ID_SHIFT) & NODE_ID_MAX


def decode_sequence_id(snowflake_id: int) -> int:

    return snowflake_id & SEQUENCE_ID_MAX


def generate_snowflake_id(
    sequence_id: int,
    node_id: int = NODE_ID_DEFAULT,
    epoch_ms: int = EPOCH_MS_DEFAULT,
) -> int | None:
    if not 0 <= node_id <= NODE_ID_MAX:
        print(f"node_id must be in [0, {NODE_ID_MAX}], got {node_id}")
        return None
    if not 0 <= sequence_id <= SEQUENCE_ID_MAX:
        print(f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], got {sequence_id}")
        return None
    ms = read_current_millis(epoch_ms)
    if ms > TIMESTAMP_MS_MAX:
        print(f"timestamp overflows: {ms} > {TIMESTAMP_MS_MAX}")
        return None
    return (ms << TIMESTAMP_SHIFT) | (node_id << NODE_ID_SHIFT) | sequence_id
