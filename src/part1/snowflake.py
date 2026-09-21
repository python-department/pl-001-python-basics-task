import time

from .constants import (
    EPOCH_MS_DEFAULT,
    NODE_ID_DEFAULT,
    NODE_ID_MAX,
    SEQUENCE_ID_MAX,
    TIMESTAMP_MS_MAX,
)


def read_current_millis(epoch_ms: int) -> int:
    current_time = int(time.time() * 1000)

    return current_time - epoch_ms


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    default_time = snowflake_id >> 22

    return default_time + epoch_ms


def decode_node_id(snowflake_id: int) -> int:
    node_id = (snowflake_id >> 12) & 0b1111111111

    return node_id


def decode_sequence_id(snowflake_id: int) -> int:
    sequence_id = snowflake_id & 0b111111111111

    return sequence_id


def generate_snowflake_id(
    sequence_id: int,
    node_id: int = NODE_ID_DEFAULT,
    epoch_ms: int = EPOCH_MS_DEFAULT,
) -> int | None:
    if node_id < 0 or node_id > NODE_ID_MAX:
        print("node_id must be in range[0; 1023]")
        return None
    elif sequence_id < 0 or sequence_id > SEQUENCE_ID_MAX:
        print("sequence_id must be in [0; 4095]")
        return None
    elif decode_timestamp_ms(epoch_ms) > TIMESTAMP_MS_MAX:
        print("overflows")
        return None

    return read_current_millis(epoch_ms) << 22 | node_id << 12 | sequence_id
