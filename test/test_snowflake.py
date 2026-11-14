from part1.constants import EPOCH_MS_DEFAULT, NODE_ID_MAX, SEQUENCE_ID_MAX
from part1.snowflake import (
    decode_node_id,
    decode_sequence_id,
    decode_timestamp_ms,
    generate_snowflake_id,
)


def test_roundtrip_node_and_sequence():
    for node in [0, 1, 42, 500, NODE_ID_MAX]:
        for seq in [0, 1, 100, 4000, SEQUENCE_ID_MAX]:
            sid = generate_snowflake_id(seq, node)
            assert sid is not None
            assert decode_node_id(sid) == node
            assert decode_sequence_id(sid) == seq


def test_timestamp_close_to_now():
    import time
    before = time.time_ns() // 1_000_000
    sid = generate_snowflake_id(0, 1)
    after = time.time_ns() // 1_000_000

    ts = decode_timestamp_ms(sid)
    assert before <= ts <= after


def test_positive_64bit():
    sid = generate_snowflake_id(SEQUENCE_ID_MAX, NODE_ID_MAX)
    assert 0 < sid < 2**63


def test_invalid_node():
    assert generate_snowflake_id(0, NODE_ID_MAX + 1) is None
    assert generate_snowflake_id(0, -1) is None


def test_invalid_sequence():
    assert generate_snowflake_id(SEQUENCE_ID_MAX + 1, 1) is None
    assert generate_snowflake_id(-1, 1) is None
