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
    now_ms = (time.time_ns()) // 1_000_000
    return now_ms - epoch_ms


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    relative_time_ms = snowflake_id >> (NODE_ID_BITS + SEQUENCE_ID_BITS)
    absolute_time_ms = relative_time_ms + epoch_ms

    return absolute_time_ms


def decode_node_id(snowflake_id: int) -> int:
    node_id = (snowflake_id >> SEQUENCE_ID_BITS) & NODE_ID_BITS
    return node_id


def decode_sequence_id(snowflake_id: int) -> int:
    sequence_id = snowflake_id & SEQUENCE_ID_MAX
    return sequence_id


def get_snowflake_id_generator(
    node_id: int = NODE_ID_DEFAULT,
    epoch_ms: int = EPOCH_MS_DEFAULT,
) -> Callable[[], int | None] | None:
    if not 0 <= node_id <= NODE_ID_MAX:
        print(f"node_id must be in [0, {NODE_ID_MAX}], got {node_id}")
        return None

    if read_current_millis(epoch_ms) < 0:
        print(f"epoch_ms must not be in the future, got {epoch_ms}")
        return None

    last_ms: int | None = None
    sequence_id = 0

    def generate() -> int | None:
        nonlocal last_ms, sequence_id

        current_ms = read_current_millis(epoch_ms)

        if last_ms is None or current_ms != last_ms:
            last_ms = current_ms
            sequence_id = 0
        else:
            sequence_id += 1
            if sequence_id > SEQUENCE_ID_MAX:
                print(
                    f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], got {sequence_id}"
                )
                return None

        if current_ms > TIMESTAMP_MS_MAX:
            print(f"timestamp {current_ms} ms overflows {TIMESTAMP_MS_MAX} ms")
            return None

        return (
            (current_ms << (NODE_ID_BITS + SEQUENCE_ID_BITS))
            | (node_id << SEQUENCE_ID_BITS)
            | sequence_id
        )

    return generate
