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
    TIMESTAMP_BITS,
    NODE_ID_BITS,
    SEQUENCE_ID_BITS,
    NODE_ID_MAX,
    SEQUENCE_ID_MAX,
    TIMESTAMP_MS_MAX,
)


def read_current_millis(epoch_ms: int) -> int:
    """Read the number of milliseconds elapsed since the custom epoch.

    Args:
        epoch_ms: The custom epoch expressed as Unix milliseconds.

    Returns:
        The count of whole milliseconds between ``epoch_ms`` and now. Negative
        if ``epoch_ms`` lies in the future.
    """
    return int(time.time() * 1000 - epoch_ms)


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
    timestamp_ms = (snowflake_id >> (NODE_ID_BITS + SEQUENCE_ID_BITS)) & (
        2**TIMESTAMP_BITS - 1
    )
    return int(timestamp_ms + epoch_ms)


def decode_node_id(snowflake_id: int) -> int:
    """Read the node identifier field out of a Snowflake identifier.

    Args:
        snowflake_id: An identifier produced by a generator from
            :func:`get_snowflake_id_generator`.

    Returns:
        The node identifier packed into ``snowflake_id``, in the range
        ``[0, NODE_ID_MAX]``.
    """
    return int((snowflake_id >> (SEQUENCE_ID_BITS)) & (2**NODE_ID_BITS - 1))


def decode_sequence_id(snowflake_id: int) -> int:
    """Read the sequence counter field out of a Snowflake identifier.

    Args:
        snowflake_id: An identifier produced by a generator from
            :func:`get_snowflake_id_generator`.

    Returns:
        The per-millisecond sequence counter packed into ``snowflake_id``, in
        the range ``[0, SEQUENCE_ID_MAX]``.
    """
    return int(snowflake_id & (2**SEQUENCE_ID_BITS - 1))


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
    if not (0 <= node_id <= NODE_ID_MAX):
        print(f"node_id must be in [0, {NODE_ID_MAX}], got {node_id}")
        return None
    if read_current_millis(epoch_ms) < 0:
        print(f"epoch_ms must not be in the future, got {epoch_ms}")
        return None

    sequence_id = 0
    epoch = epoch_ms

    def generator() -> int | None:
        nonlocal sequence_id, epoch
        snowflake_id = 0
        current_epoch = read_current_millis(epoch_ms)

        if not (0 <= sequence_id <= SEQUENCE_ID_MAX):
            print(
                f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], got {sequence_id + 1}"
            )
            return None
        if current_epoch > TIMESTAMP_MS_MAX:
            print(f"timestamp {current_epoch} ms overflows {TIMESTAMP_MS_MAX} ms")
            return None

        if current_epoch == epoch:
            snowflake_id = (
                (0b0 << (TIMESTAMP_BITS + NODE_ID_BITS + SEQUENCE_ID_BITS))
                | (current_epoch << (NODE_ID_BITS + SEQUENCE_ID_BITS))
                | (node_id << (SEQUENCE_ID_BITS))
                | (sequence_id)
            )
            sequence_id += 1
        else:
            sequence_id = 0
            epoch = current_epoch
            snowflake_id = (
                (0b0 << (TIMESTAMP_BITS + NODE_ID_BITS + SEQUENCE_ID_BITS))
                | (current_epoch << (NODE_ID_BITS + SEQUENCE_ID_BITS))
                | (node_id << (SEQUENCE_ID_BITS))
                | (sequence_id)
            )

        return snowflake_id

    return generator
