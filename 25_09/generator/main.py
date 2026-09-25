from constants import *
from snowflake import * 

test = generate_snowflake_id(sequence_id=5, node_id=1)
print(test)
print(decode_sequence_id(test))   # 5
print(decode_node_id(test))       # 1
print(decode_timestamp_ms(test))  # близко к текущему времени

# сквозная проверка: соберём обратно из частей
ts   = decode_timestamp_ms(test) - EPOCH_MS_DEFAULT
node = decode_node_id(test)
seq  = decode_sequence_id(test)

rebuilt = (ts << TIMESTAMP_SHIFT) | (node << SEQUENCE_ID_BITS) | seq
print(rebuilt == test)   # True