from snowflake import *
from constants import *

def test_generate_and_decode_cycle():
    test_seq = 5
    test_node = 1
    

    sid = generate_snowflake_id(sequence_id=test_seq, node_id=test_node)
    
    assert sid is not None
    
    assert decode_sequence_id(sid) == test_seq
    assert decode_node_id(sid) == test_node

def test_invalid_input_returns_none():
    assert generate_snowflake_id(sequence_id=SEQUENCE_ID_MAX + 1) is None

    assert generate_snowflake_id(sequence_id=0, node_id=NODE_ID_MAX + 1) is None
