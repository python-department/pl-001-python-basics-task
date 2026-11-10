"""Twitter Snowflake identifier generator.

Snowflake produces roughly time-ordered 64-bit integer identifiers without
coordination between nodes. Each identifier packs the milliseconds elapsed
since a custom epoch, a node identifier and a per-millisecond sequence counter
into a single 63-bit positive integer (see ``constants`` for the layout).

The public entry point is :func:`get_snowflake_id_generator`. It validates the
node identifier once and returns a closure that keeps the sequence counter and
the last seen millisecond itself, so each new identifier needs only a call
without arguments.

Each packed field can be read back on its own with :func:`decode_timestamp_ms`,
:func:`decode_node_id` and :func:`decode_sequence_id`.
"""

import time
from collections.abc import Callable

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
    """Read the number of milliseconds elapsed since the custom epoch.

    Args:
        epoch_ms: The custom epoch expressed as Unix milliseconds.

    Returns:
        The count of whole milliseconds between ``epoch_ms`` and now. May be
        negative if ``epoch_ms`` lies in the future.
    """
    # TODO: реализуйте функцию
    now_ms = int(time.time() * 1000)
    return now_ms - epoch_ms


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
    snowflake_id_time = snowflake_id >> (NODE_ID_BITS + SEQUENCE_ID_BITS)
    return snowflake_id_time + epoch_ms


def decode_node_id(snowflake_id: int) -> int:
    """Read the node identifier field out of a Snowflake identifier.

    Args:
        snowflake_id: An identifier produced by :func:`generate_snowflake_id`.

    Returns:
        The node identifier packed into ``snowflake_id``, in the range
        ``[0, NODE_ID_MAX]``.
    """
    # TODO: реализуйте функцию
    snowflake_id_knot = snowflake_id >> SEQUENCE_ID_BITS
    snowflake_id_knot = snowflake_id_knot & NODE_ID_MAX
    return snowflake_id_knot


def decode_sequence_id(snowflake_id: int) -> int:
    """Read the sequence counter field out of a Snowflake identifier.

    Args:
        snowflake_id: An identifier produced by :func:`generate_snowflake_id`.

    Returns:
        The per-millisecond sequence counter packed into ``snowflake_id``, in
        the range ``[0, SEQUENCE_ID_MAX]``.
    """
    # TODO: реализуйте функцию
    return snowflake_id & SEQUENCE_ID_MAX


def get_snowflake_id_generator(
    node_id: int = NODE_ID_DEFAULT,
    epoch_ms: int = EPOCH_MS_DEFAULT,
) -> Callable[[], int | None] | None:
    if not (0 <= node_id <= NODE_ID_MAX):
        print(f"node_id must be in [0, {NODE_ID_MAX}], got {node_id}")
        return None
    if read_current_millis(epoch_ms) < 0:
        print(f"epoch_ms must not be in the future, got {epoch_ms}")
        return None
    last_time = read_current_millis(epoch_ms)
    sequence_id = -1

    def get_snowflake_id() -> int | None:
        nonlocal last_time, sequence_id
        now_time = read_current_millis(epoch_ms)
        if last_time != now_time:
            last_time = now_time
            sequence_id = 0
        else:
            sequence_id += 1
        if sequence_id > SEQUENCE_ID_MAX:
            print(f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], got {sequence_id}")
            return None
        if now_time > TIMESTAMP_MS_MAX:
            print(f"timestamp {now_time} ms overflows {TIMESTAMP_MS_MAX} ms")
            return None
        snowflake_id = (
            (now_time << (NODE_ID_BITS + SEQUENCE_ID_BITS))
            | (node_id << SEQUENCE_ID_BITS)
            | sequence_id
        )
        return snowflake_id

    return get_snowflake_id
