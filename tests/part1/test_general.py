import pytest
import uuid

from src.part1.snowflake import (
    generate_snowflake_id,
    decode_node_id,
    decode_sequence_id,
    decode_timestamp_ms,
)

def test_generate_snowflake_id():
    print(f"{generate_snowflake_id(1, 1023):b}")

def test_decode_timestamp_ms():
    print(decode_timestamp_ms(generate_snowflake_id(1, 1023)))

def test_decode_node_id():
    print(decode_node_id(generate_snowflake_id(1, 1023)))

def test_decode_sequence_id():
    print(decode_sequence_id(generate_snowflake_id(1, 1023)))
