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
    current_ms = int(time.time() * 1000)
    return current_ms - epoch_ms


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    timestamp = snowflake_id >> TIMESTAMP_SHIFT
    return timestamp + epoch_ms


def decode_node_id(snowflake_id: int) -> int:
    return (snowflake_id >> NODE_ID_SHIFT) & NODE_ID_MAX


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

    last_ms = -1
    sequence = 0

    def generate() -> int | None:
        nonlocal last_ms, sequence
        current_ms = read_current_millis(epoch_ms)

        if current_ms > TIMESTAMP_MS_MAX:
            print(f"timestamp {current_ms} ms overflows {TIMESTAMP_MS_MAX} ms")
            return None

        if current_ms > last_ms:
            last_ms = current_ms
            sequence = 0
        else:
            if sequence >= SEQUENCE_ID_MAX:
                print(
                    f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], got {sequence + 1}"
                )
                return None
            sequence += 1

        return (current_ms << TIMESTAMP_SHIFT) | (node_id << NODE_ID_SHIFT) | sequence

    return generate
