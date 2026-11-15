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


def read_current_millis(epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    return time.time_ns() // 1_000_000 - epoch_ms


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    current_time = (snowflake_id >> (NODE_ID_BITS + SEQUENCE_ID_BITS)) + epoch_ms
    return current_time


def decode_node_id(snowflake_id: int) -> int:
    node_id = (snowflake_id >> SEQUENCE_ID_BITS) & NODE_ID_MAX
    return node_id


def decode_sequence_id(snowflake_id: int) -> int:
    sequence_id = snowflake_id & SEQUENCE_ID_MAX
    return sequence_id


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

    last_time = -1
    sequence = 0

    def generate_sequence() -> int | None:
        nonlocal last_time, sequence
        current_passed_ms = read_current_millis(epoch_ms)

        if current_passed_ms == last_time:
            next_sequence = sequence + 1
            if next_sequence > SEQUENCE_ID_MAX:
                sequence = next_sequence
                print(f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], got {sequence}")
                return None
        else:
            next_sequence = 0

        if current_passed_ms > TIMESTAMP_MS_MAX:
            print(f"timestamp {current_passed_ms} ms overflows {TIMESTAMP_MS_MAX} ms")
            return None

        last_time = current_passed_ms
        sequence = next_sequence

        snowflake = (
            (current_passed_ms << (NODE_ID_BITS + SEQUENCE_ID_BITS))
            | (node_id << SEQUENCE_ID_BITS)
            | sequence
        )
        return snowflake

    return generate_sequence
