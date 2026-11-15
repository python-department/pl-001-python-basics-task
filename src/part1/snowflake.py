import time

from .constants import (
    EPOCH_MS_DEFAULT,
    NODE_ID_DEFAULT,
    NODE_ID_MAX,
    NODE_ID_SHIFT,
    SEQUENCE_ID_MAX,
    TIMESTAMP_BITS,
    TIMESTAMP_MS_MAX,
    TIMESTAMP_SHIFT,
)


def read_current_millis(epoch_ms: int) -> int:
    current_ms = int(time.time() * 1000)
    return current_ms - epoch_ms


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    timestamp_part = snowflake_id >> TIMESTAMP_SHIFT
    return timestamp_part + epoch_ms


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

    timestamp_ms = read_current_millis(epoch_ms)
    if timestamp_ms > TIMESTAMP_MS_MAX:
        print(
            f"Timestamp overflows {TIMESTAMP_BITS} bits:"
            f"{timestamp_ms} > {TIMESTAMP_MS_MAX}"
        )
        return None

    snowflake_id = (
        (timestamp_ms << TIMESTAMP_SHIFT) | (node_id << NODE_ID_SHIFT) | sequence_id
    )

    return snowflake_id
