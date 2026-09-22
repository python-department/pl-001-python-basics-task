#!/usr/bin/env python3

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


def read_current_millis(epoch_ms: int) -> int:
    return int(time.time() * 1000 - epoch_ms)


def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    return snowflake_id >> (NODE_ID_BITS + SEQUENCE_ID_BITS) + epoch_ms


def decode_node_id(snowflake_id: int) -> int:
    mask = (1 << NODE_ID_BITS) - 1
    return (snowflake_id >> SEQUENCE_ID_BITS) & mask


def decode_sequence_id(snowflake_id: int) -> int:
    mask = (1 << SEQUENCE_ID_BITS) - 1
    return snowflake_id & mask


def generate_snowflake_id(
    sequence_id: int,
    node_id: int = NODE_ID_DEFAULT,
    epoch_ms: int = EPOCH_MS_DEFAULT,
) -> int | None:
    if not (0 < node_id < NODE_ID_MAX):
        print("node_id must be in [0, " + str(NODE_ID_MAX) + "], got " + str(node_id))
    elif not (0 < sequence_id < SEQUENCE_ID_MAX):
        print(
            "sequence_id must be in [0, "
            + str(SEQUENCE_ID_MAX)
            + "], got "
            + str(sequence_id)
        )
    elif read_current_millis(epoch_ms) > TIMESTAMP_MS_MAX:
        print("overflows")
    return (
        (read_current_millis(epoch_ms) << (NODE_ID_BITS + SEQUENCE_ID_BITS))
        | (node_id << NODE_ID_BITS)
        | (sequence_id)
    )
