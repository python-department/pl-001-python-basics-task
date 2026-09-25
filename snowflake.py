import time
from constants import *

def read_current_millis(epoch_ms: int) -> int:
    current_time_ms = int(time.time() * 1000)
    timestamp_ms = current_time_ms - epoch_ms
    return timestamp_ms


def decode_timestamp_ms(snowflake_id: int,
    epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    timestamp_ms = snowflake_id >> (SEQUENCE_ID_BITS + NODE_ID_BITS)
    current_time_ms = timestamp_ms + epoch_ms
    return current_time_ms


def decode_node_id(snowflake_id: int) -> int:
    node_id = (snowflake_id & (NODE_ID_MAX << SEQUENCE_ID_BITS)) >> SEQUENCE_ID_BITS
    return node_id


def decode_sequence_id(snowflake_id: int) -> int:
    sequence_id = snowflake_id & (SEQUENCE_ID_MAX )
    return sequence_id


def generate_snowflake_id(sequence_id: int, 
    node_id: int = NODE_ID_DEFAULT, 
    epoch_ms: int = EPOCH_MS_DEFAULT) -> int | None:

    if not(0 <= node_id <= NODE_ID_MAX):
        return print(f"node_id ({node_id}) must be in [0, {NODE_ID_MAX}]")
    if not(0 <= sequence_id <= SEQUENCE_ID_MAX):
        return print(f"sequence_id ({sequence_id}) must be in [0, {SEQUENCE_ID_MAX}]")
    timestamp_ms = read_current_millis(epoch_ms)
    if (timestamp_ms > TIMESTAMP_MS_MAX):
        return print("overflows") 
    
    timestamp_ms_snowflake_id = timestamp_ms << (SEQUENCE_ID_BITS + NODE_ID_BITS)
    node_snowflake_id = node_id << SEQUENCE_ID_BITS
    sequence_snowflake_id = sequence_id
    snowflake_id =  timestamp_ms_snowflake_id + node_snowflake_id + sequence_snowflake_id
    return snowflake_id