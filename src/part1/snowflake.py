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

from .constants import *


def read_current_millis(epoch_ms: int) -> int:
    call_time = (
        time.time_ns() // 1_000_000  # наносекунды в милисекунды(time.time() - float)
    )
    return call_time - epoch_ms
    # """Read the number of milliseconds elapsed since the custom epoch.

    # Args:
    #     epoch_ms: The custom epoch expressed as Unix milliseconds.

    # Returns:
    #     The count of whole milliseconds between ``epoch_ms`` and now. May be
    #     negative if ``epoch_ms`` lies in the future.
    # """


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    return (snowflake_id >> TIMESTAMP_MOVE) + epoch_ms

    # """Read the timestamp field out of a Snowflake identifier.

    # Args:
    #     snowflake_id: An identifier produced against the same epoch.
    #     epoch_ms: The epoch the identifier was generated against. Defaults to
    #         the original Twitter epoch (2010-11-04 01:42:54.657 UTC).

    # Returns:
    #     The absolute Unix time in milliseconds at which the identifier was
    #     generated.
    # """


def decode_node_id(snowflake_id: int) -> int:
    return (snowflake_id >> SEQUENCE_ID_BITS) & NODE_ID_BITS


def decode_sequence_id(snowflake_id: int) -> int:
    return snowflake_id & SEQUENCE_ID_MAX


def generate_snowflake_id(
    sequence_id: int, node_id: int = NODE_ID_DEFAULT, epoch_ms: int = EPOCH_MS_DEFAULT
) -> int | None:
    time_call_gen = read_current_millis(epoch_ms)

    if node_id < 0 or node_id > NODE_ID_MAX:
        print("node_id must be in [0,", NODE_ID_MAX, "]")
        return None

    if sequence_id < 0 or sequence_id > SEQUENCE_ID_MAX:
        print("sequence_id must be in [0,", SEQUENCE_ID_MAX, "]")
        return None

    if time_call_gen > TIMESTAMP_MS_MAX:
        print("overflows time stamp")
        return None

    snowflake_id = (
        (time_call_gen << TIMESTAMP_MOVE) | (node_id << sequence_id) | sequence_id
    )
    return snowflake_id
