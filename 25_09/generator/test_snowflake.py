# test_snowflake.py
from snowflake import generate_snowflake_id, decode_sequence_id, decode_node_id
from constants import EPOCH_MS_DEFAULT, NODE_ID_DEFAULT, SEQUENCE_ID_MAX, NODE_ID_MAX

def test_generate_and_decode_cycle():
    """Проверяет, что генерация и декодирование работают согласованно."""
    test_seq = 5
    test_node = 1
    
    # Генерируем ID
    sid = generate_snowflake_id(sequence_id=test_seq, node_id=test_node)
    
    # Проверяем, что ID сгенерирован (не None)
    assert sid is not None
    
    # Проверяем, что части декодируются обратно в исходные значения
    assert decode_sequence_id(sid) == test_seq
    assert decode_node_id(sid) == test_node

def test_invalid_input_returns_none():
    """Проверяет, что при неверных данных возвращается None."""
    # sequence_id вне диапазона
    assert generate_snowflake_id(sequence_id=SEQUENCE_ID_MAX + 1) is None
    # node_id вне диапазона
    assert generate_snowflake_id(sequence_id=0, node_id=NODE_ID_MAX + 1) is None
