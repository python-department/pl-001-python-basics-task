import time
from collections.abc import Callable

from .constants import (
    EPOCH_MS_DEFAULT,
    NODE_ID_DEFAULT,
    NODE_ID_MAX,
    NODE_ID_SHIFT,
    SEQUENCE_ID_MAX,
    TIMESTAMP_MS_MAX,
    TIMESTAMP_SHIFT,
)


def read_current_millis(epoch_ms: int) -> int:
    return time.time_ns() // 1_000_000 - epoch_ms


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    stored_ms = snowflake_id >> TIMESTAMP_SHIFT
    return stored_ms + epoch_ms


def decode_node_id(snowflake_id: int) -> int:
    return (snowflake_id >> NODE_ID_SHIFT) & NODE_ID_MAX


def decode_sequence_id(snowflake_id: int) -> int:
    return snowflake_id & SEQUENCE_ID_MAX


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

    last_millis: int | None = None
    sequence_id = -1

    def generate() -> int | None:
        nonlocal last_millis, sequence_id

        current_millis = read_current_millis(epoch_ms)

        if last_millis is None or current_millis > last_millis:
            last_millis = current_millis
            sequence_id = 0
        elif current_millis == last_millis:
            if sequence_id >= SEQUENCE_ID_MAX:
                print(
                    f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], "
                    f"got {sequence_id + 1}"
                )
                return None
            sequence_id += 1
        else:
            current_millis = last_millis
            if sequence_id >= SEQUENCE_ID_MAX:
                print(
                    f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], "
                    f"got {sequence_id + 1}"
                )
                return None
            sequence_id += 1

        if current_millis > TIMESTAMP_MS_MAX:
            print(f"timestamp {current_millis} ms overflows {TIMESTAMP_MS_MAX} ms")
            return None

        return (
            (current_millis << TIMESTAMP_SHIFT)
            | (node_id << NODE_ID_SHIFT)
            | sequence_id
        )

    return generate
