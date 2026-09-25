import time 
from constants import *

def read_current_millis(epoch_ms: int) -> int:
    now_ms = time.time_ns() // 1_000_000 # текущий моент 
    return now_ms - epoch_ms

def decode_timestamp_ms(snowflake_id: int, 
 epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    return (snowflake_id >> TIMESTAMP_SHIFT ) + epoch_ms

def decode_node_id(snowflake_id: int) -> int:
    return (snowflake_id >> SEQUENCE_ID_BITS) & NODE_ID_MAX

def decode_sequence_id(snowflake_id: int) -> int:
    return snowflake_id & SEQUENCE_ID_MAX


    # главная функция
def generate_snowflake_id(sequence_id: int, node_id:
 int = NODE_ID_DEFAULT, 
 epoch_ms: int = EPOCH_MS_DEFAULT) -> int | None:

    local_const_time = read_current_millis(epoch_ms)

    if node_id < 0 or node_id > NODE_ID_MAX:
        print(f"node_id must be in [0, {NODE_ID_MAX}]")
        return None
    if sequence_id < 0 or sequence_id > SEQUENCE_ID_MAX:
        print(f"sequence_id must be in [0, {SEQUENCE_ID_MAX}]")
        return None
    if local_const_time > TIMESTAMP_MS_MAX:
        print("overflows time")
        return None
    
    snowflake_id = (local_const_time << TIMESTAMP_SHIFT) | \
                (node_id << SEQUENCE_ID_BITS) | sequence_id
    return snowflake_id
    

    
    
    

