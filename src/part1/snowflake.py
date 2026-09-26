import time

from part1.constants import (
    EPOCH_MS_DEFAULT,
    NODE_ID_DEFAULT,
    NODE_ID_MAX,
    NODE_ID_SHIFT,
    SEQUENCE_ID_MAX,
    TIMESTAMP_MS_MAX,
    TIMESTAMP_SHIFT,
)


def read_current_millis(epoch_ms: int) -> int:
    return time.time_ns() // 1000000 - epoch_ms


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    stored_ms = snowflake_id >> TIMESTAMP_SHIFT
    return stored_ms + epoch_ms


def decode_node_id(snowflake_id: int) -> int:
    return (snowflake_id >> NODE_ID_SHIFT) & NODE_ID_MAX


def decode_sequence_id(snowflake_id: int) -> int:
    return snowflake_id & SEQUENCE_ID_MAX


def generate_snowflake_id(
    sequence_id: int,
    node_id: int = NODE_ID_DEFAULT,
    epoch_ms: int = EPOCH_MS_DEFAULT,
) -> int | None:
    if not (0 <= node_id <= NODE_ID_MAX):
        print(f"node_id must be in [0, {NODE_ID_MAX}], got {node_id}")
        return None

    if not (0 <= sequence_id <= SEQUENCE_ID_MAX):
        print(f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], got {sequence_id}")
        return None

    elapsed_ms = read_current_millis(epoch_ms)
    if elapsed_ms > TIMESTAMP_MS_MAX:
        print(f"timestamp overflows: {elapsed_ms} > {TIMESTAMP_MS_MAX}")
        return None

    return (elapsed_ms << TIMESTAMP_SHIFT) | (node_id << NODE_ID_SHIFT) | sequence_id
