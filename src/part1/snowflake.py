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
    return int(time.time() * 1000) - epoch_ms


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    relative_time = (
        snowflake_id >> SEQUENCE_ID_BITS >> NODE_ID_BITS
    ) & TIMESTAMP_MS_MAX
    return epoch_ms + relative_time


def decode_node_id(snowflake_id: int) -> int:
    return (snowflake_id >> SEQUENCE_ID_BITS) & NODE_ID_MAX


def decode_sequence_id(snowflake_id: int) -> int:
    return snowflake_id & SEQUENCE_ID_MAX


def generate_snowflake_id(
    sequence_id: int,
    node_id: int = NODE_ID_DEFAULT,
    epoch_ms: int = EPOCH_MS_DEFAULT,
) -> int | None:
    current_millis = read_current_millis(epoch_ms)

    if node_id not in range(NODE_ID_MAX + 1):
        print(f"node_id is {node_id}, but must be in [0, {NODE_ID_MAX}]")
        return None
    elif sequence_id not in range(SEQUENCE_ID_MAX + 1):
        print(f"sequence_id is {sequence_id}, but must be in [0, {SEQUENCE_ID_MAX}]")
        return None
    else:
        if current_millis > TIMESTAMP_MS_MAX:
            print("overflows")
            return None

    snowflake_id = int(
        "0"
        + bin(current_millis)[2:].zfill(TIMESTAMP_BITS)
        + bin(node_id)[2:].zfill(NODE_ID_BITS)
        + bin(sequence_id)[2:].zfill(SEQUENCE_ID_BITS),
        base=2,
    )
    # print(decode_node_id(snowflake_id) == node_id,
    #       decode_sequence_id(snowflake_id) == sequence_id,
    #       decode_timestamp_ms(snowflake_id, epoch_ms) == current_millis + epoch_ms)
    return snowflake_id
