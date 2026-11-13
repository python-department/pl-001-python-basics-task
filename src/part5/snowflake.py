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
    return int(time.time() * 1000) - epoch_ms


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    return int((bin(snowflake_id)[2:]).zfill(64)[1:42], 2) + epoch_ms


def decode_node_id(snowflake_id: int) -> int:
    return int((bin(snowflake_id)[2:]).zfill(64)[42:52], 2)


def decode_sequence_id(snowflake_id: int) -> int:
    return int(bin(snowflake_id)[52:], 2)


def get_snowflake_id_generator(
    node_id: int = NODE_ID_DEFAULT,
    epoch_ms: int = EPOCH_MS_DEFAULT,
) -> Callable[[], int | None] | None:

    if node_id > NODE_ID_MAX or node_id < 0:
        print(f"node_id must be in [0, {NODE_ID_MAX}], got {node_id}")
        return None
    if read_current_millis(epoch_ms) < 0:
        print(f"epoch_ms must not be in the future, got {epoch_ms}")
        return None

    sequence_id = -1
    internal_time = time.time()

    def generator() -> int | None:
        nonlocal internal_time
        nonlocal sequence_id

        if internal_time != time.time():
            sequence_id = 0
            internal_time = time.time()
        else:
            sequence_id += 1

        if sequence_id > SEQUENCE_ID_MAX:
            print(f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], got {sequence_id}")
            return None

        time_id = read_current_millis(epoch_ms)
        if time_id > TIMESTAMP_MS_MAX:
            print(f"timestamp {time_id} ms overflows {TIMESTAMP_MS_MAX} ms")
            return None

        return int(
            bin(time_id)[2:].zfill(41)
            + bin(node_id)[2:].zfill(10)
            + bin(sequence_id)[2:].zfill(12),
            2,
        )

    return generator
