import time

from constants import *

def read_current_millis(epoch_ms: int) -> int: 
    return int(time.time()*1000) - epoch_ms

def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int: 
    return int(bin(snowflake_id)[3:44], 2) + epoch_ms

def decode_node_id(snowflake_id: int) -> int:
    return int(bin(snowflake_id)[44:54], 2)

def decode_sequence_id(snowflake_id: int) -> int:
    return int(bin(snowflake_id)[54:], 2)

def generate_snowflake_id(
    sequence_id: int,
    node_id: int = NODE_ID_DEFAULT,
    epoch_ms: int = EPOCH_MS_DEFAULT) -> int | None:
    if node_id < 0 or node_id > NODE_ID_MAX:
        print (f"node_id must be in [0, {NODE_ID_MAX}]")
        return None
    elif sequence_id < 0 or sequence_id > SEQUENCE_ID_MAX:
        print (f"sequence_id be in [0, {SEQUENCE_ID_MAX}]")
        return None 
    else:
        timestamp = time.time()
        if timestamp > TIMESTAMP_MS_MAX:
            print ("overflows")
            return None
    return int('0' + bin(int(time.time()*1000) + epoch_ms)[2:].zfill(41) + bin(node_id)[2:].zfill(10) + bin(sequence_id)[2:].zfill(12), 2)
