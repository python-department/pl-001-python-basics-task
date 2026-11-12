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
    NODE_ID_DEFAULT,
    NODE_ID_MAX,
    NODE_SHIFT,
    SEQUENCE_ID_MAX,
    SEQUENCE_SHIFT,
    TIMESTAMP_MS_MAX,
    TIMESTAMP_SHIFT,
)


def read_current_millis(epoch_ms: int) -> int:
    """Read the number of milliseconds elapsed since the custom epoch.

    Args:
        epoch_ms: The custom epoch expressed as Unix milliseconds.

    Returns:
        The count of whole milliseconds between ``epoch_ms`` and now. Negative
        if ``epoch_ms`` lies in the future.
    """
    now_ms = time.time_ns() // 1_000_000
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
    current_millis = snowflake_id >> TIMESTAMP_SHIFT
    return epoch_ms + current_millis


def decode_node_id(snowflake_id: int) -> int:
    """Read the node identifier field out of a Snowflake identifier.

    Args:
        snowflake_id: An identifier produced by a generator from
            :func:`get_snowflake_id_generator`.

    Returns:
        The node identifier packed into ``snowflake_id``, in the range
        ``[0, NODE_ID_MAX]``.
    """
    return snowflake_id >> NODE_SHIFT & NODE_ID_MAX


def decode_sequence_id(snowflake_id: int) -> int:
    """Read the sequence counter field out of a Snowflake identifier.

    Args:
        snowflake_id: An identifier produced by a generator from
            :func:`get_snowflake_id_generator`.

    Returns:
        The per-millisecond sequence counter packed into ``snowflake_id``, in
        the range ``[0, SEQUENCE_ID_MAX]``.
    """
    return snowflake_id & SEQUENCE_ID_MAX


def get_snowflake_id_generator(
    node_id: int = NODE_ID_DEFAULT,
    epoch_ms: int = EPOCH_MS_DEFAULT,
) -> Callable[[], int | None] | None:
    """Create a stateful Snowflake identifier generator bound to one node.

    The returned closure remembers the millisecond of its previous call and the
    per-millisecond sequence counter, so callers never pass them in.

    Args:
        node_id: The identifier of this node, in the range ``[0, NODE_ID_MAX]``.
            Optional; defaults to ``NODE_ID_DEFAULT``.
        epoch_ms: The start of the epoch as Unix milliseconds. Optional;
            defaults to the original Twitter epoch (2010-11-04 01:42:54.657
            UTC).

    Returns:
        A zero-argument function ``generate_snowflake_id``. Each call returns a
        positive 63-bit integer identifier. It returns ``None`` (after printing
        an explanatory message to stdout) if more than ``SEQUENCE_ID_MAX + 1``
        identifiers are requested within one millisecond, or if the elapsed
        time no longer fits in the timestamp field (roughly 69 years after
        ``epoch_ms``). A failed call does not break the generator: it recovers
        once the clock moves on to the next millisecond.

        ``None`` is returned instead of a generator, after printing a message
        to stdout, if ``node_id`` is outside ``[0, NODE_ID_MAX]`` or
        ``epoch_ms`` lies in the future.
    """
    if node_id > NODE_ID_MAX or node_id < 0:
        print(f"node_id must be in [0, {NODE_ID_MAX}], got {node_id}")
        return None

    if read_current_millis(epoch_ms) < 0:
        print(f"epoch_ms must not be in the future, got {epoch_ms}")
        return None

    sequence_id = 0
    last_millis = -1

    def generate_id() -> int | None:
        nonlocal sequence_id, last_millis

        current_millis = read_current_millis(epoch_ms)

        if current_millis > last_millis:
            last_millis = current_millis
            sequence_id = 0
        else:
            current_millis = last_millis
            sequence_id += 1

        if sequence_id > SEQUENCE_ID_MAX:
            print(f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], got {sequence_id}")
            return None

        if current_millis > TIMESTAMP_MS_MAX:
            print(
                f"timestamp {current_millis - TIMESTAMP_MS_MAX} ms overflows {TIMESTAMP_MS_MAX} ms"
            )
            return None

        snowflake_id = (
            current_millis << TIMESTAMP_SHIFT
            | node_id << NODE_SHIFT
            | sequence_id << SEQUENCE_SHIFT
        )

        return snowflake_id

    return generate_id
