import time

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


def generate_snowflake_id(
    sequence_id: int,
    node_id: int = NODE_ID_DEFAULT,
    epoch_ms: int = EPOCH_MS_DEFAULT,
) -> int | None:
    if node_id > NODE_ID_MAX or node_id < 0:
        m = f"node_id must be in [0,{NODE_ID_MAX}]"
        print(m)
        return None
    if sequence_id > SEQUENCE_ID_MAX or sequence_id < 0:
        m = f"sequence_id must be in [0,{SEQUENCE_ID_MAX}]"
        print(m)
        return None
    if epoch_ms > TIMESTAMP_MS_MAX and epoch_ms < 0:
        m = "overflows"
        print(m)
        return None
    return read_current_millis(epoch_ms) << 22 | node_id << 12 | sequence_id
