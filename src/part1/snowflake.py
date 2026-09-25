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

import time  # noqa: F401

from .constants import (  # noqa: F401
    EPOCH_MS_DEFAULT,
    NODE_ID_DEFAULT,
    NODE_ID_MAX,
    SEQUENCE_ID_MAX,
    TIMESTAMP_MS_MAX,
    NODE_ID_BITS,
    SEQUENCE_ID_BITS
)


def read_current_millis(epoch_ms: int) -> int:

    user_time = int(time.time() * 1000)
    
    differnse_time = user_time - epoch_ms

    return differnse_time


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:

    user_mc = snowflake_id >> (NODE_ID_BITS + SEQUENCE_ID_BITS)

    absolut_time = user_mc + epoch_ms

    return absolut_time


def decode_node_id(snowflake_id: int) -> int:
    """Read the node identifier field out of a Snowflake identifier.

    Args:
        snowflake_id: An identifier produced by :func:`generate_snowflake_id`.

    Returns:
        The node identifier packed into ``snowflake_id``, in the range
        ``[0, NODE_ID_MAX]``.
    """
    identifier_id = (snowflake_id >> SEQUENCE_ID_BITS) & NODE_ID_MAX
    return identifier_id


def decode_sequence_id(snowflake_id: int) -> int:
    """Read the sequence counter field out of a Snowflake identifier.

    Args:
        snowflake_id: An identifier produced by :func:`generate_snowflake_id`.

    Returns:
        The per-millisecond sequence counter packed into ``snowflake_id``, in
        the range ``[0, SEQUENCE_ID_MAX]``.
    """
    sequence_id = snowflake_id & SEQUENCE_ID_MAX
    return sequence_id


def generate_snowflake_id(
    sequence_id: int,
    node_id: int = NODE_ID_DEFAULT,
    epoch_ms: int = EPOCH_MS_DEFAULT,
) -> int | None:
    """Build and return a Snowflake identifier for the current millisecond.

    The function is stateless: the caller passes the per-millisecond sequence
    counter explicitly. It is the caller's responsibility to increment
    ``sequence_id`` for identifiers minted within the same millisecond and to
    reset it once the clock advances.

    Args:
        sequence_id: The per-millisecond sequence counter, in the range
            ``[0, SEQUENCE_ID_MAX]``.
        node_id: The identifier of this node, in the range ``[0, NODE_ID_MAX]``.
            Optional; defaults to ``NODE_ID_DEFAULT``.
        epoch_ms: The start of the epoch as Unix milliseconds. Optional;
            defaults to the original Twitter epoch (2010-11-04 01:42:54.657
            UTC).

    Returns:
        The Snowflake identifier as a positive 63-bit integer, or ``None`` if
        ``node_id`` is outside ``[0, NODE_ID_MAX]``, ``sequence_id`` is outside
        ``[0, SEQUENCE_ID_MAX]``, or the elapsed time no longer fits in the
        timestamp field (roughly 69 years after ``epoch_ms``). In each of those
        cases an explanatory message is printed to stdout first.
    """
    if node_id < 0 or node_id > NODE_ID_MAX:
        print(f"node_id must be in [0, {NODE_ID_MAX}], got {node_id}")
        return None
    if sequence_id < 0 or sequence_id > SEQUENCE_ID_MAX:
        print(f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], got {sequence_id}")
        return None
    elapsed_ms = read_current_millis(epoch_ms)
    if elapsed_ms > TIMESTAMP_MS_MAX:
        print(f"timestamp overflows: {elapsed_ms} > {TIMESTAMP_MS_MAX}")
        return None
    snowflake_id = (
        (elapsed_ms << (NODE_ID_BITS + SEQUENCE_ID_BITS))
        | (node_id << SEQUENCE_ID_BITS)
        | sequence_id
    )
    return snowflake_id

