import time
from collections.abc import Callable

from .constants import (
    EPOCH_MS_DEFAULT,
    NODE_ID_BITS,
    NODE_ID_DEFAULT,
    NODE_ID_MAX,
    SEQUENCE_ID_BITS,
    SEQUENCE_ID_MAX,
    TIMESTAMP_MS_MAX,
)


def read_current_millis(epoch_ms: int) -> int:
    unix_epoch_time = time.time_ns() // 1_000_000  # get current time in milliseconds
    return unix_epoch_time - epoch_ms


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    return (snowflake_id >> (NODE_ID_BITS + SEQUENCE_ID_BITS)) + epoch_ms


def decode_node_id(snowflake_id: int) -> int:
    return (snowflake_id >> SEQUENCE_ID_BITS) & NODE_ID_MAX


def decode_sequence_id(snowflake_id: int) -> int:
    return snowflake_id & SEQUENCE_ID_MAX


def id_compose(timestamp_ms: int, node_id: int, counter: int) -> int:
    return (
        (timestamp_ms << (NODE_ID_BITS + SEQUENCE_ID_BITS))
        | (node_id << SEQUENCE_ID_BITS)
        | counter
    )


def get_snowflake_id_generator(
    node_id: int = NODE_ID_DEFAULT,
    epoch_ms: int = EPOCH_MS_DEFAULT,
) -> Callable[[], int | None] | None:

    if not (0 <= node_id <= NODE_ID_MAX):
        print(f"node_id must be in [0, {NODE_ID_MAX}], got {node_id}")
        return None
    elif read_current_millis(epoch_ms) < 0:
        print(f"epoch_ms must not be in the future, got {epoch_ms}")
        return None

    counter = -1  # -1 - метка того, что генерация id в новом генераторе будет впервые
    period_start = read_current_millis(epoch_ms)

    def generator() -> int | None:
        nonlocal counter, period_start

        timestamp_ms = read_current_millis(epoch_ms)
        time_difference = timestamp_ms - period_start

        if time_difference < 1:
            counter += 1
            if counter > SEQUENCE_ID_MAX:
                print(f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], got {counter}")
                return None
        else:
            counter = 0  # первый id в новой мс сразу получает counter = 0
            period_start = timestamp_ms

        if timestamp_ms > TIMESTAMP_MS_MAX:
            print(f"timestamp {timestamp_ms} ms overflows {TIMESTAMP_MS_MAX} ms")
            return None

        return id_compose(timestamp_ms, node_id, counter)

    return generator
