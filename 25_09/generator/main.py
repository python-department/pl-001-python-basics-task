from constants import *
from snowflake import * 

test = generate_snowflake_id(sequence_id=5, node_id=1)
print(test)
print(decode_sequence_id(test))   # 5
print(decode_node_id(test))       # 1
print(decode_timestamp_ms(test))  # близко к текущему времени
