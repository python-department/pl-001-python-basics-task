import time

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


def generate_snowflake_id(
    sequence_id: int,
    node_id: int = NODE_ID_DEFAULT,
    epoch_ms: int = EPOCH_MS_DEFAULT,
) -> int | None:
    if not (0 <= node_id <= NODE_ID_MAX):
        print(f"node_id must be in [0, {NODE_ID_MAX}], current node_id is {node_id}")
        return None
    elif not (0 <= sequence_id <= SEQUENCE_ID_MAX):
        print(
            f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], current sequence_id is {sequence_id}"
        )
        return None
    else:
        if epoch_ms <= read_current_millis(epoch_ms) <= TIMESTAMP_MS_MAX:
            snowflake_id = (
                (read_current_millis(epoch_ms) << (NODE_ID_BITS + SEQUENCE_ID_BITS))
                | (node_id << (SEQUENCE_ID_BITS))
                | sequence_id
            )
            return snowflake_id
        else:
            print("overflows")
            return None
