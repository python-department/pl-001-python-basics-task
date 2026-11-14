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
    creation_time = (snowflake_id >> SEQUENCE_ID_BITS >> NODE_ID_BITS) & (
        TIMESTAMP_MS_MAX
    )
    return creation_time + epoch_ms


def decode_node_id(snowflake_id: int) -> int:
    return (snowflake_id >> SEQUENCE_ID_BITS) & (NODE_ID_MAX)


def decode_sequence_id(snowflake_id: int) -> int:
    return (snowflake_id) & (SEQUENCE_ID_MAX)


def get_snowflake_id_generator(
    node_id: int = NODE_ID_DEFAULT,
    epoch_ms: int = EPOCH_MS_DEFAULT,
) -> Callable[[], int | None] | None:
    if not (0 <= node_id <= NODE_ID_MAX):
        print(f"node_id must be in [0, {NODE_ID_MAX}], got {node_id}")
        return None

    last_millisec = read_current_millis(epoch_ms)
    if last_millisec < 0:
        print(f"epoch_ms must not be in the future, got {epoch_ms}")
        return None

    last_sequence_id = 0

    def get_snowflake_id() -> int | None:
        nonlocal last_millisec, last_sequence_id
        went_from_epoch = read_current_millis(epoch_ms)
        if went_from_epoch > TIMESTAMP_MS_MAX:
            print(f"timestamp {went_from_epoch} ms overflows {TIMESTAMP_MS_MAX} ms")
            return None
        sequence_id = 0
        if went_from_epoch == last_millisec:
            sequence_id = last_sequence_id
            if sequence_id > SEQUENCE_ID_MAX:
                print(
                    f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], got {sequence_id}"
                )
                return None
            last_sequence_id += 1
        else:
            last_millisec = went_from_epoch
            last_sequence_id = sequence_id

        return (
            (went_from_epoch << NODE_ID_BITS << SEQUENCE_ID_BITS)
            | (node_id << SEQUENCE_ID_BITS)
        ) | sequence_id

    return get_snowflake_id
