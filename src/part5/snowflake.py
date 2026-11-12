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
    current_time = int(time.time() * 1000)

    return current_time - epoch_ms


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    time_mark = snowflake_id >> (NODE_ID_BITS + SEQUENCE_ID_BITS)

    return time_mark + epoch_ms


def decode_node_id(snowflake_id: int) -> int:
    without_seq = snowflake_id >> SEQUENCE_ID_BITS
    node_id = without_seq & NODE_ID_MAX

    return node_id


def decode_sequence_id(snowflake_id: int) -> int:
    sequence_id = snowflake_id & SEQUENCE_ID_MAX

    return sequence_id


def get_snowflake_id_generator(
    node_id: int = NODE_ID_DEFAULT,
    epoch_ms: int = EPOCH_MS_DEFAULT,
) -> Callable[[], int | None] | None:
    if node_id < 0 or node_id > NODE_ID_MAX:
        print(f"node_id must be in [0, {NODE_ID_MAX}], got {node_id}")
        return None

    if read_current_millis(epoch_ms) < 0:
        print(f"epoch_ms must not be in the future, got {epoch_ms}")
        return None

    sequence_id = 0
    previous_time = -1

    def generator() -> int | None:
        nonlocal sequence_id, previous_time
        current_time = read_current_millis(epoch_ms)
        if current_time > TIMESTAMP_MS_MAX:
            print(f"timestamp {current_time} ms overflows {TIMESTAMP_MS_MAX} ms")
            return None

        if current_time != previous_time:
            sequence_id = 0
            previous_time = current_time
        else:
            sequence_id += 1

        if sequence_id > SEQUENCE_ID_MAX:
            print(f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], got {sequence_id}")
            return None

        else:
            snowflake_id = (
                (current_time << (NODE_ID_BITS + SEQUENCE_ID_BITS))
                | (node_id << SEQUENCE_ID_BITS)
                | sequence_id
            )

        return snowflake_id

    return generator
