import time

from part5 import snowflake as sf
from part5.constants import (
    EPOCH_MS_DEFAULT,
    NODE_ID_BITS,
    NODE_ID_DEFAULT,
    NODE_ID_MAX,
    SEQUENCE_ID_BITS,
    SEQUENCE_ID_MAX,
    TIMESTAMP_BITS,
    TIMESTAMP_MS_MAX,
)


# ============================================================
# CONSTANTS — границы и согласованность
# ============================================================


class TestConstants:
    def test_bit_widths(self) -> None:
        assert (TIMESTAMP_BITS, NODE_ID_BITS, SEQUENCE_ID_BITS) == (41, 10, 12)

    def test_total_width_is_63(self) -> None:
        # 1 (sign) + 41 + 10 + 12 = 64; знаковый разряд не используется -> 63
        assert TIMESTAMP_BITS + NODE_ID_BITS + SEQUENCE_ID_BITS == 63

    def test_max_are_derived(self) -> None:
        assert TIMESTAMP_MS_MAX == 2**41 - 1
        assert NODE_ID_MAX == 2**10 - 1 == 1023
        assert SEQUENCE_ID_MAX == 2**12 - 1 == 4095

    def test_epoch_and_default(self) -> None:
        assert EPOCH_MS_DEFAULT == 1288834974657
        assert NODE_ID_DEFAULT == 1


# ============================================================
# read_current_millis
# ============================================================


class TestReadCurrentMillis:
    def test_is_in_milliseconds(self) -> None:
        before = int(time.time() * 1000)
        got = sf.read_current_millis(0)
        after = int(time.time() * 1000)
        assert before <= got <= after

    def test_epoch_zero_equals_unix_ms(self) -> None:
        assert abs(sf.read_current_millis(0) - int(time.time() * 1000)) < 5

    def test_future_epoch_negative(self) -> None:
        future = int(time.time() * 1000) + 10_000_000
        assert sf.read_current_millis(future) < 0

    def test_default_epoch_yields_positive(self) -> None:
        assert sf.read_current_millis(EPOCH_MS_DEFAULT) > 0

    def test_tiny_negative_epoch(self) -> None:
        assert sf.read_current_millis(-1) > 0


# ============================================================
# decode_*
# ============================================================


class TestDecodeNodeId:
    def test_zero(self) -> None:
        assert sf.decode_node_id(0) == 0

    def test_max(self) -> None:
        sid = NODE_ID_MAX << SEQUENCE_ID_BITS
        assert sf.decode_node_id(sid) == NODE_ID_MAX

    def test_isolated_from_sequence(self) -> None:
        sid = (NODE_ID_MAX << SEQUENCE_ID_BITS) | SEQUENCE_ID_MAX
        assert sf.decode_node_id(sid) == NODE_ID_MAX

    def test_isolated_from_timestamp(self) -> None:
        sid = (12345 << (NODE_ID_BITS + SEQUENCE_ID_BITS)) | (5 << SEQUENCE_ID_BITS) | 3
        assert sf.decode_node_id(sid) == 5


class TestDecodeSequenceId:
    def test_zero(self) -> None:
        assert sf.decode_sequence_id(0) == 0

    def test_max(self) -> None:
        assert sf.decode_sequence_id(SEQUENCE_ID_MAX) == SEQUENCE_ID_MAX

    def test_only_low_12_bits(self) -> None:
        assert sf.decode_sequence_id(0xFFFF_FFFF) == SEQUENCE_ID_MAX

    def test_isolated_from_node_and_timestamp(self) -> None:
        sid = (999 << 22) | (7 << 12) | 42
        assert sf.decode_sequence_id(sid) == 42


class TestDecodeTimestampMs:
    def test_zero_with_epoch(self) -> None:
        assert sf.decode_timestamp_ms(0, epoch_ms=EPOCH_MS_DEFAULT) == EPOCH_MS_DEFAULT

    def test_zero_with_zero_epoch(self) -> None:
        assert sf.decode_timestamp_ms(0, epoch_ms=0) == 0

    def test_max_timestamp_roundtrip(self) -> None:
        sid = TIMESTAMP_MS_MAX << (NODE_ID_BITS + SEQUENCE_ID_BITS)
        assert sf.decode_timestamp_ms(sid, epoch_ms=0) == TIMESTAMP_MS_MAX

    def test_isolated_from_lower_fields(self) -> None:
        ts = 123_456_789
        sid = (ts << 22) | (NODE_ID_MAX << 12) | SEQUENCE_ID_MAX
        assert sf.decode_timestamp_ms(sid, epoch_ms=0) == ts

    def test_default_epoch_is_used(self) -> None:
        ts = 1000
        sid = ts << 22
        assert sf.decode_timestamp_ms(sid) == ts + EPOCH_MS_DEFAULT

