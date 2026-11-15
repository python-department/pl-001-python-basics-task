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

    return int(time.time() * 1000) - epoch_ms


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:

    return (snowflake_id >> (SEQUENCE_ID_BITS + NODE_ID_BITS)) + epoch_ms


def decode_node_id(snowflake_id: int) -> int:

    return (snowflake_id >> SEQUENCE_ID_BITS) & NODE_ID_MAX


def decode_sequence_id(snowflake_id: int) -> int:

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

    time_after_epoch = -1
    sequence_id = -1

    def generator() -> int | None:
        nonlocal time_after_epoch, sequence_id

        now = read_current_millis(epoch_ms)

        now = max(now, time_after_epoch)

        if now == time_after_epoch:
            if sequence_id == SEQUENCE_ID_MAX:
                print(
                    f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], got {sequence_id + 1}"
                )
                return None
            sequence_id += 1

        else:
            time_after_epoch = now
            sequence_id = 0

        if time_after_epoch > TIMESTAMP_MS_MAX:
            print(f"timestamp {time_after_epoch} ms overflows {TIMESTAMP_MS_MAX} ms")
            return None

        return (
            time_after_epoch << (SEQUENCE_ID_BITS + NODE_ID_BITS)
            | node_id << SEQUENCE_ID_BITS
            | sequence_id
        )

    return generator
