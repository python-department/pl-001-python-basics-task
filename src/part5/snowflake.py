from collections.abc import Callable
from time import time

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
    return int(time() * 1000) - epoch_ms


def decode_sequence_id(snowflake_id: int) -> int:
    return snowflake_id & SEQUENCE_ID_MAX


def decode_node_id(snowflake_id: int) -> int:
    return (snowflake_id >> SEQUENCE_ID_BITS) & NODE_ID_MAX


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    return (
        (snowflake_id >> NODE_ID_BITS + SEQUENCE_ID_BITS) & TIMESTAMP_MS_MAX
    ) + epoch_ms


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

    last_timestamp = -1
    sequence_id = 0

    def generator() -> int | None:
        nonlocal last_timestamp, sequence_id

        time_passed = read_current_millis(epoch_ms)

        if time_passed == last_timestamp:
            sequence_id += 1

            if sequence_id > SEQUENCE_ID_MAX:
                print(
                    f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], got {sequence_id}"
                )
                return None
        else:
            sequence_id = 0
            last_timestamp = time_passed

        if time_passed > TIMESTAMP_MS_MAX:
            print(f"timestamp {time_passed} ms overflows {TIMESTAMP_MS_MAX} ms")
            return None

        snowflake_id = (
            (time_passed << (NODE_ID_BITS + SEQUENCE_ID_BITS))
            | (node_id << SEQUENCE_ID_BITS)
            | sequence_id
        )

        return snowflake_id

    return generator
