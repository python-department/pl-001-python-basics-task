import time
from collections.abc import Callable

from .constants import (
    EPOCH_MS_DEFAULT,
    NODE_ID_BITS,
    NODE_ID_DEFAULT,
    NODE_ID_MAX,
    SEQUENCE_ID_BITS,
    SEQUENCE_ID_MAX,
    TIMESTAMP_BITS,
    TIMESTAMP_MS_MAX,
)


def read_current_millis(epoch_ms: int) -> int:
    return time.time_ns() // 10**6 - epoch_ms


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    stored_time = snowflake_id >> (NODE_ID_BITS + SEQUENCE_ID_BITS)
    return stored_time + epoch_ms


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

    timestamp_ms = read_current_millis(epoch_ms)
    if timestamp_ms < 0:
        print(f"epoch_ms must not be in the future, got {epoch_ms}")
        return None

    last_timestamp_ms = -1
    sequence_id = 0

    def generate_id() -> int | None:
        nonlocal last_timestamp_ms, sequence_id

        timestamp_ms = read_current_millis(epoch_ms)

        if timestamp_ms == last_timestamp_ms:
            sequence_id += 1
            if sequence_id > SEQUENCE_ID_MAX:
                print(
                    f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], got {sequence_id}"
                )
                return None
        else:
            last_timestamp_ms = timestamp_ms
            sequence_id = 0

        if timestamp_ms > TIMESTAMP_MS_MAX:
            print(f"timestamp {timestamp_ms} ms overflows {TIMESTAMP_BITS} bits")
            return None

        snowflake_id = (
            (timestamp_ms << (NODE_ID_BITS + SEQUENCE_ID_BITS))
            | (node_id << SEQUENCE_ID_BITS)
            | sequence_id
        )
        return snowflake_id

    return generate_id
