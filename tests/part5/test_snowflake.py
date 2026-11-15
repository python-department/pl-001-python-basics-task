import pytest
from src.part5 import snowflake
from src.part5.constants import (
    EPOCH_MS_DEFAULT,
    NODE_ID_BITS,
    NODE_ID_DEFAULT,
    NODE_ID_MAX,
    SEQUENCE_ID_BITS,
    SEQUENCE_ID_MAX,
    TIMESTAMP_BITS,
    TIMESTAMP_MS_MAX,
)
from src.part5.snowflake import (
    decode_node_id,
    decode_sequence_id,
    decode_timestamp_ms,
    get_snowflake_id_generator,
    read_current_millis,
)


class FakeClock:
    """Replaces ``read_current_millis``: returns elapsed ms since the epoch."""

    def __init__(self, elapsed_ms: int) -> None:
        self.elapsed_ms = elapsed_ms

    def __call__(self, epoch_ms: int) -> int:
        return self.elapsed_ms


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> FakeClock:
    fake_clock = FakeClock(1_000_000)
    monkeypatch.setattr(snowflake, "read_current_millis", fake_clock)
    return fake_clock


def test_constants() -> None:
    assert EPOCH_MS_DEFAULT == 1288834974657
    assert NODE_ID_DEFAULT == 1
    assert (TIMESTAMP_BITS, NODE_ID_BITS, SEQUENCE_ID_BITS) == (41, 10, 12)
    assert TIMESTAMP_MS_MAX == 2**41 - 1
    assert NODE_ID_MAX == 1023
    assert SEQUENCE_ID_MAX == 4095


def test_read_current_millis(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(snowflake.time, "time", lambda: 1000.5)

    assert read_current_millis(0) == 1_000_500
    assert read_current_millis(500) == 1_000_000
    assert read_current_millis(1_000_500) == 0
    assert read_current_millis(1_000_600) == -100


def test_decoders() -> None:
    timestamp, node, sequence = 123_456, 77, 9
    snowflake_id = (
        (timestamp << (NODE_ID_BITS + SEQUENCE_ID_BITS))
        | (node << SEQUENCE_ID_BITS)
        | sequence
    )

    assert decode_timestamp_ms(snowflake_id, 1000) == timestamp + 1000
    assert decode_timestamp_ms(snowflake_id) == timestamp + EPOCH_MS_DEFAULT
    assert decode_node_id(snowflake_id) == node
    assert decode_sequence_id(snowflake_id) == sequence


def test_decoders_extreme_values() -> None:
    snowflake_id = (
        (TIMESTAMP_MS_MAX << (NODE_ID_BITS + SEQUENCE_ID_BITS))
        | (NODE_ID_MAX << SEQUENCE_ID_BITS)
        | SEQUENCE_ID_MAX
    )

    assert snowflake_id == 2**63 - 1
    assert decode_timestamp_ms(snowflake_id, 0) == TIMESTAMP_MS_MAX
    assert decode_node_id(snowflake_id) == NODE_ID_MAX
    assert decode_sequence_id(snowflake_id) == SEQUENCE_ID_MAX
    assert decode_timestamp_ms(0, 5) == 5
    assert decode_node_id(0) == 0
    assert decode_sequence_id(0) == 0


@pytest.mark.parametrize("node_id", [-1, NODE_ID_MAX + 1])
def test_generator_rejects_bad_node_id(
    node_id: int, clock: FakeClock, capsys: pytest.CaptureFixture[str]
) -> None:
    assert get_snowflake_id_generator(node_id=node_id) is None
    assert (
        capsys.readouterr().out
        == f"node_id must be in [0, {NODE_ID_MAX}], got {node_id}\n"
    )


@pytest.mark.parametrize("node_id", [0, 1, NODE_ID_MAX])
def test_generator_accepts_node_id_bounds(
    node_id: int, clock: FakeClock, capsys: pytest.CaptureFixture[str]
) -> None:
    generate_id = get_snowflake_id_generator(node_id=node_id)

    assert generate_id is not None
    assert capsys.readouterr().out == ""
    snowflake_id = generate_id()
    assert snowflake_id is not None
    assert decode_node_id(snowflake_id) == node_id


def test_generator_rejects_future_epoch(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(snowflake.time, "time", lambda: 1000.0)

    assert get_snowflake_id_generator(epoch_ms=1_000_001) is None
    assert (
        capsys.readouterr().out == "epoch_ms must not be in the future, got 1000001\n"
    )


def test_generator_accepts_epoch_equal_to_now(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(snowflake.time, "time", lambda: 1000.0)

    assert get_snowflake_id_generator(epoch_ms=1_000_000) is not None
    assert capsys.readouterr().out == ""


def test_node_id_is_checked_before_epoch(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(snowflake.time, "time", lambda: 1000.0)

    assert get_snowflake_id_generator(node_id=-1, epoch_ms=2_000_000) is None
    assert capsys.readouterr().out == "node_id must be in [0, 1023], got -1\n"


def test_creating_generator_issues_nothing(clock: FakeClock) -> None:
    generate_id = get_snowflake_id_generator(node_id=3)
    assert generate_id is not None

    first = generate_id()
    assert first is not None
    assert decode_sequence_id(first) == 0


def test_generator_packs_fields(clock: FakeClock) -> None:
    generate_id = get_snowflake_id_generator(node_id=5, epoch_ms=1000)
    assert generate_id is not None

    snowflake_id = generate_id()

    assert snowflake_id is not None
    assert 0 < snowflake_id < 2**63
    assert decode_timestamp_ms(snowflake_id, 1000) == 1000 + clock.elapsed_ms
    assert decode_node_id(snowflake_id) == 5
    assert decode_sequence_id(snowflake_id) == 0


def test_sequence_grows_within_millisecond(clock: FakeClock) -> None:
    generate_id = get_snowflake_id_generator()
    assert generate_id is not None

    ids = [generate_id() for _ in range(5)]

    assert None not in ids
    assert [decode_sequence_id(i) for i in ids if i is not None] == [0, 1, 2, 3, 4]
    assert len(set(ids)) == 5
    assert ids == sorted(ids, key=lambda i: i or 0)


def test_sequence_resets_in_new_millisecond(clock: FakeClock) -> None:
    generate_id = get_snowflake_id_generator()
    assert generate_id is not None

    generate_id()
    generate_id()
    clock.elapsed_ms += 1
    third = generate_id()

    assert third is not None
    assert decode_sequence_id(third) == 0
    assert decode_timestamp_ms(third) == EPOCH_MS_DEFAULT + clock.elapsed_ms


def test_generators_are_independent(clock: FakeClock) -> None:
    generate_a = get_snowflake_id_generator(node_id=1)
    generate_b = get_snowflake_id_generator(node_id=2)
    assert generate_a is not None and generate_b is not None

    generate_a()
    generate_a()
    id_a = generate_a()
    id_b = generate_b()

    assert id_a is not None and id_b is not None
    assert (decode_node_id(id_a), decode_sequence_id(id_a)) == (1, 2)
    assert (decode_node_id(id_b), decode_sequence_id(id_b)) == (2, 0)


def test_sequence_exhaustion(
    clock: FakeClock, capsys: pytest.CaptureFixture[str]
) -> None:
    generate_id = get_snowflake_id_generator()
    assert generate_id is not None

    ids = [generate_id() for _ in range(SEQUENCE_ID_MAX + 1)]
    assert None not in ids
    assert len(set(ids)) == SEQUENCE_ID_MAX + 1
    assert capsys.readouterr().out == ""

    message = f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], got "
    assert generate_id() is None
    assert capsys.readouterr().out == f"{message}{SEQUENCE_ID_MAX + 1}\n"
    assert generate_id() is None
    assert capsys.readouterr().out == f"{message}{SEQUENCE_ID_MAX + 2}\n"


def test_sequence_recovers_in_next_millisecond(
    clock: FakeClock, capsys: pytest.CaptureFixture[str]
) -> None:
    generate_id = get_snowflake_id_generator()
    assert generate_id is not None
    for _ in range(SEQUENCE_ID_MAX + 2):
        generate_id()
    capsys.readouterr()

    clock.elapsed_ms += 1
    snowflake_id = generate_id()

    assert snowflake_id is not None
    assert decode_sequence_id(snowflake_id) == 0
    assert capsys.readouterr().out == ""


def test_timestamp_overflow(
    clock: FakeClock, capsys: pytest.CaptureFixture[str]
) -> None:
    generate_id = get_snowflake_id_generator()
    assert generate_id is not None

    clock.elapsed_ms = TIMESTAMP_MS_MAX + 1

    assert generate_id() is None
    assert (
        capsys.readouterr().out
        == f"timestamp {TIMESTAMP_MS_MAX + 1} ms overflows {TIMESTAMP_MS_MAX} ms\n"
    )


def test_timestamp_max_is_still_allowed(
    clock: FakeClock, capsys: pytest.CaptureFixture[str]
) -> None:
    generate_id = get_snowflake_id_generator(epoch_ms=0)
    assert generate_id is not None

    clock.elapsed_ms = TIMESTAMP_MS_MAX
    snowflake_id = generate_id()

    assert snowflake_id is not None
    assert 0 < snowflake_id < 2**63
    assert decode_timestamp_ms(snowflake_id, 0) == TIMESTAMP_MS_MAX
    assert capsys.readouterr().out == ""


def test_real_clock_ids_are_unique_and_increasing() -> None:
    generate_id = get_snowflake_id_generator(node_id=7)
    assert generate_id is not None

    ids = [generate_id() for _ in range(SEQUENCE_ID_MAX)]
    issued = [i for i in ids if i is not None]

    assert issued == sorted(set(issued))
    assert all(decode_node_id(i) == 7 for i in issued)
