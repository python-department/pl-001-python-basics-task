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
    """Read the number of milliseconds elapsed since the custom epoch.

    Args:
        epoch_ms: The custom epoch expressed as Unix milliseconds.

    Returns:
        The count of whole milliseconds between ``epoch_ms`` and now. May be
        negative if ``epoch_ms`` lies in the future.
    """
    return time.time_ns() // 10**6 - epoch_ms


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    """Read the timestamp field out of a Snowflake identifier.

    Args:
        snowflake_id: An identifier produced against the same epoch.
        epoch_ms: The epoch the identifier was generated against. Defaults to
            the original Twitter epoch (2010-11-04 01:42:54.657 UTC).

    Returns:
        The absolute Unix time in milliseconds at which the identifier was
        generated.
    """
    del_time = (snowflake_id >> (NODE_ID_BITS + TIMESTAMP_BITS)) & TIMESTAMP_MS_MAX

    return epoch_ms + del_time


def decode_node_id(snowflake_id: int) -> int:
    """Read the node identifier field out of a Snowflake identifier.

    Args:
        snowflake_id: An identifier produced by :func:`generate_snowflake_id`.

    Returns:
        The node identifier packed into ``snowflake_id``, in the range
        ``[0, NODE_ID_MAX]``.
    """

    return (snowflake_id >> SEQUENCE_ID_BITS) & NODE_ID_MAX


def decode_sequence_id(snowflake_id: int) -> int:
    """Read the sequence counter field out of a Snowflake identifier.

    Args:
        snowflake_id: An identifier produced by :func:`generate_snowflake_id`.

    Returns:
        The per-millisecond sequence counter packed into ``snowflake_id``, in
        the range ``[0, SEQUENCE_ID_MAX]``.
    """
    return snowflake_id & SEQUENCE_ID_MAX


def generate_snowflake_id(
    sequence_id: int,
    node_id: int = NODE_ID_DEFAULT,
    epoch_ms: int = EPOCH_MS_DEFAULT,
) -> int | None:
    if not (0 <= node_id <= NODE_ID_MAX):
        print(f"node_id must be in [0, {NODE_ID_MAX}]. Your id {node_id}")
        return None
    elif not (0 <= sequence_id <= SEQUENCE_ID_MAX):
        print(f"sequence_id must be in [0, {SEQUENCE_ID_MAX}] Your id {sequence_id}")
        return None

    else:
        if 0 <= epoch_ms <= TIMESTAMP_MS_MAX:
            return (
                epoch_ms
                << (SEQUENCE_ID_BITS + NODE_ID_BITS) + node_id
                << SEQUENCE_ID_BITS + sequence_id
            )
        else:
            print("overflows")
            return None
