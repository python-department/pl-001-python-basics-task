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
    TIMESTAMP_BITS,
    TIMESTAMP_MS_MAX,
)


def read_current_millis(epoch_ms: int) -> int:
    return int(time.time()) * 1000 - epoch_ms - EPOCH_MS_DEFAULT


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    creation_time = (snowflake_id >> SEQUENCE_ID_BITS >> NODE_ID_BITS) & (
        (1 << TIMESTAMP_BITS) - 1
    )
    return creation_time + epoch_ms


def decode_node_id(snowflake_id: int) -> int:
    return (snowflake_id >> SEQUENCE_ID_BITS) & ((1 << NODE_ID_BITS) - 1)


def decode_sequence_id(snowflake_id: int) -> int:
    return (snowflake_id) & ((1 << SEQUENCE_ID_BITS) - 1)


def generate_snowflake_id(
    sequence_id: int,
    node_id: int = NODE_ID_DEFAULT,
    epoch_ms: int = EPOCH_MS_DEFAULT,
) -> int | None:
    if not (0 <= node_id < NODE_ID_MAX):
        print(f"node_id must be in [0, {NODE_ID_MAX}], but it is {node_id}")
        return None
    if not (0 <= sequence_id < SEQUENCE_ID_MAX):
        print(f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], but it is {sequence_id}")
        return None

    epoch_ms = int(time.time()) * 1000 - EPOCH_MS_DEFAULT
    if not (0 <= epoch_ms < TIMESTAMP_MS_MAX):
        print("overflow")
        return None

    return (
        (epoch_ms << NODE_ID_MAX << SEQUENCE_ID_MAX) | (node_id << SEQUENCE_ID_MAX)
    ) | sequence_id
