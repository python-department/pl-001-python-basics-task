import time

from .constants import (
    EPOCH_MS_DEFAULT,
    NODE_ID_DEFAULT,
    NODE_ID_MAX,
    NODE_ID_SHIFT,
    SEQUENCE_ID_MAX,
    TIMESTAMP_MS_MAX,
    TIMESTAMP_SHIFT,
)


def read_current_millis(epoch_ms: int) -> int:
    return int(int(time.time() * 1000) - epoch_ms)


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    return int(snowflake_id // (2**TIMESTAMP_SHIFT) + epoch_ms)


def decode_node_id(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    return int(
        (
            snowflake_id
            - (
                (decode_timestamp_ms(snowflake_id, epoch_ms) - epoch_ms)
                * 2**TIMESTAMP_SHIFT
            )
        )
        // (2**NODE_ID_SHIFT)
    )


def decode_sequence_id(snowflake_id: int) -> int:
    return int(snowflake_id - ((snowflake_id // 2**NODE_ID_SHIFT) * (2**NODE_ID_SHIFT)))


def generate_snowflake_id(
    sequence_id: int, node_id: int = NODE_ID_DEFAULT, epoch_ms: int = EPOCH_MS_DEFAULT
) -> int | None:
    current_millis = read_current_millis(epoch_ms)
    if current_millis < 0 or current_millis > TIMESTAMP_MS_MAX:
        raise ValueError("Превышен максимальный лимит времени")
    if node_id < 0 or node_id > NODE_ID_MAX:
        raise ValueError("Node Id выходит за допустимые пределы")
    if sequence_id < 0 or sequence_id > SEQUENCE_ID_MAX:
        raise ValueError("Sequence Id выходит за допустимые пределы")
    return int(
        (current_millis * (2**TIMESTAMP_SHIFT))
        + (node_id * (2**NODE_ID_SHIFT) + sequence_id)
    )
