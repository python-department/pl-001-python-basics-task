from snowflake import *

snowflake_id = generate_snowflake_id(123, 5)
print(snowflake_id)
print(decode_sequence_id(snowflake_id))  
print(decode_node_id(snowflake_id))      
print(decode_timestamp_ms(snowflake_id))

