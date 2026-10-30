import time
from constants import (
    EPOCH_MS_DEFAULT,
    NODE_ID_DEFAULT,
    TIMESTAMP_BITS,
    NODE_ID_BITS,
    SEQUENCE_ID_BITS,
    TIMESTAMP_MS_MAX,
    NODE_ID_MAX,
    SEQUENCE_ID_MAX
)

def read_current_millis(epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    return int(time.time() * 1000) - epoch_ms

def generate_snowflake_id(sequence_id: int, node_id: int = NODE_ID_DEFAULT, epoch_ms: int = EPOCH_MS_DEFAULT) -> int | None:
    if not 0 <= node_id <= NODE_ID_MAX:
        print(f"node_id must be in range 0..{NODE_ID_MAX}, got {node_id}")
        return None
    if not 0 <= sequence_id <= SEQUENCE_ID_MAX:
        print(f"sequence_id must be in range 0..{SEQUENCE_ID_MAX}, got {sequence_id}")
        return None
    timestamp_ms = read_current_millis(epoch_ms)
    if timestamp_ms < 0 or timestamp_ms > TIMESTAMP_MS_MAX:
        print(f"timestamp out of range: {timestamp_ms}")
        return None
    return(timestamp_ms << (NODE_ID_BITS + SEQUENCE_ID_BITS)) | (node_id << SEQUENCE_ID_BITS) | sequence_id

def decode_timestamp_ms(snowflake_id: int, epoch_ms: int = EPOCH_MS_DEFAULT) -> int:
    return (snowflake_id >> (NODE_ID_BITS + SEQUENCE_ID_BITS)) + epoch_ms

def decode_node_id(snowflake_id: int) -> int:
    return (snowflake_id >> SEQUENCE_ID_BITS) & NODE_ID_MAX

def decode_sequence_id(snowflake_id: int) -> int:
    return snowflake_id & SEQUENCE_ID_MAX

def main() -> None:
    s = int(input("sequence_id: "))
    n = int(input("node_id: "))
    e = int(input("epoch_ms: "))

    id = generate_snowflake_id(s, n, e)

    if id is None:
        print("Error")
        return

    print("snowflake_id =", id)
    print("timestamp_ms =", decode_timestamp_ms(id, e))
    print("node_id      =", decode_node_id(id))
    print("sequence_id  =", decode_sequence_id(id))

if __name__ == "__main__":
    main()