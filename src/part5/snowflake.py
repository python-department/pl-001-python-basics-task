import time
from collections.abc import Callable

from .constants import (
    EPOCH_MS_DEFAULT,
    NODE_ID_DEFAULT,
    NODE_ID_MAX,
    SEQUENCE_ID_MAX,
    TIMESTAMP_MS_MAX,
)


def read_current_millis(epoch_ms: int) -> int:
    a = int(time.time() * 1000)

    return a - epoch_ms


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    a = snowflake_id >> 22

    return a + epoch_ms


def decode_node_id(snowflake_id: int) -> int:
    a = (snowflake_id >> 12) & 0b1111111111

    return a


def decode_sequence_id(snowflake_id: int) -> int:
    a = snowflake_id & 0b111111111111

    return a


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

    sequence = 0
    last_timestamp = -1

    def generate_id():
        nonlocal last_timestamp, sequence
        current_timestamp = read_current_millis(epoch_ms)
        if current_timestamp > TIMESTAMP_MS_MAX:
            print(f"timestamp {current_timestamp} ms overflows {TIMESTAMP_MS_MAX} ms")
            return None

        if current_timestamp == last_timestamp:
            sequence += 1
            if sequence > SEQUENCE_ID_MAX:
                print(f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], got {sequence}")
                return None
            id = current_timestamp << 22 | node_id << 12 | (sequence - 1)

        elif current_timestamp > last_timestamp:
            sequence = 0
            last_timestamp = current_timestamp
            id = current_timestamp << 22 | node_id << 12 | sequence
            sequence += 1
        return id
