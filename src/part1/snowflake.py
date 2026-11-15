import time

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

    timestamp_ms = read_current_millis(epoch_ms)
    if not (0 <= timestamp_ms <= TIMESTAMP_MS_MAX):
        print(
            f"timestamp_ms value is overflows {TIMESTAMP_BITS} bits:"
            f"{timestamp_ms} > {TIMESTAMP_MS_MAX}"
        )
        return None

    snowflake_id = (
        (timestamp_ms << (NODE_ID_BITS + SEQUENCE_ID_BITS))
        | (node_id << SEQUENCE_ID_BITS)
        | sequence_id
    )
    return snowflake_id
