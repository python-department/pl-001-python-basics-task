#!/usr/bin/env python3

import time

from .constants import (
    EPOCH_MS_DEFAULT,
    NODE_ID_BITS,
    NODE_ID_DEFAULT,
    NODE_ID_MAX,
    NODE_ID_SHIFT,
    SEQUENCE_ID_BITS,
    SEQUENCE_ID_MAX,
    TIMESTAMP_MS_MAX,
    TIMESTAMP_SHIFT,
)


def read_current_millis(epoch_ms: int) -> int:
    return int(time.time() * 1000) - epoch_ms


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    return (snowflake_id >> (TIMESTAMP_SHIFT)) + epoch_ms


def decode_node_id(snowflake_id: int) -> int:
    mask = (1 << NODE_ID_BITS) - 1
    return (snowflake_id >> NODE_ID_SHIFT) & mask


def decode_sequence_id(snowflake_id: int) -> int:
    mask = (1 << SEQUENCE_ID_BITS) - 1
    return snowflake_id & mask


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

    current_millis = read_current_millis(epoch_ms)

    if not (0 <= current_millis <= TIMESTAMP_MS_MAX):
        print("overflows")
        return None
    return (
        (current_millis << (TIMESTAMP_SHIFT))
        | (node_id << NODE_ID_SHIFT)
        | (sequence_id)
    )
