from decimal import Decimal
from typing import Any

import pytest
from src.part5 import crud
from src.part5.constants import NODE_ID_DEFAULT
from src.part5.crud import (
    CREATE_KEY,
    DELETE_KEY,
    READ_KEY,
    STATS_REGISTRY,
    UPDATE_KEY,
    create_product,
    delete_product,
    generate_snowflake_id,
    read_product,
    update_product,
)
from src.part5.snowflake import decode_node_id, decode_sequence_id
from src.part5.storage import NAME_KEY, PRICE_KEY, QUANTITY_KEY, Product


def make_fields(
    name: str = "Saw", price: str = "9.995", quantity: int = 5
) -> dict[str, Any]:
    return {NAME_KEY: name, PRICE_KEY: Decimal(price), QUANTITY_KEY: quantity}


def counters(key: str) -> tuple[int, int]:
    record = STATS_REGISTRY[key]
    return record["success"], record["fails"]


class IdSource:
    """Deterministic ``generate_id`` that counts how often it was called."""

    def __init__(self, *ids: int | None) -> None:
        self.ids = list(ids)
        self.calls = 0

    def __call__(self) -> int | None:
        self.calls += 1
        return self.ids.pop(0)


def test_stats_registry_keys_and_initial_state() -> None:
    assert (CREATE_KEY, READ_KEY, UPDATE_KEY, DELETE_KEY) == (
        "create",
        "read",
        "update",
        "delete",
    )
    assert list(STATS_REGISTRY) == ["create", "read", "update", "delete"]


def test_decorated_functions_keep_names() -> None:
    assert create_product.__name__ == "create_product"
    assert read_product.__name__ == "read_product"
    assert update_product.__name__ == "update_product"
    assert delete_product.__name__ == "delete_product"


def test_generate_snowflake_id_uses_shared_generator() -> None:
    first = generate_snowflake_id()
    second = generate_snowflake_id()

    assert first is not None and second is not None
    assert 0 < first < second < 2**63
    assert decode_node_id(first) == NODE_ID_DEFAULT
    assert decode_node_id(second) == NODE_ID_DEFAULT


def test_generate_snowflake_id_calls_generator_directly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    values: list[int | None] = [10, None, 12]
    monkeypatch.setattr(crud, "snowflake_id_generator", lambda: values.pop(0))

    assert generate_snowflake_id() == 10
    assert generate_snowflake_id() is None
    assert generate_snowflake_id() == 12


def test_generate_snowflake_id_without_generator(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(crud, "snowflake_id_generator", None)

    assert generate_snowflake_id() is None
    assert generate_snowflake_id() is None
    assert capsys.readouterr().out == ""


def test_generate_snowflake_id_does_not_touch_registry() -> None:
    before = {key: dict(value) for key, value in STATS_REGISTRY.items()}

    generate_snowflake_id()

    assert STATS_REGISTRY == before


def test_generate_snowflake_id_sequence_grows() -> None:
    ids = [generate_snowflake_id() for _ in range(50)]

    assert None not in ids
    assert len(set(ids)) == 50
    assert [i for i in ids if i is not None] == sorted(i for i in ids if i)
    assert all(decode_sequence_id(i) >= 0 for i in ids if i is not None)


def test_create_product_success() -> None:
    storage: dict[int, Product] = {}
    names: set[str] = set()
    ids = IdSource(42)
    before = counters(CREATE_KEY)

    result = create_product(storage, names, make_fields("  Saw  BIG "), ids)

    assert result == 42
    assert storage == {
        42: {NAME_KEY: "saw big", PRICE_KEY: Decimal("10.00"), QUANTITY_KEY: 5}
    }
    assert names == {"saw big"}
    assert ids.calls == 1
    assert counters(CREATE_KEY) == (before[0] + 1, before[1])


def test_create_product_blank_name(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[int, Product] = {}
    names: set[str] = set()
    ids = IdSource(1)
    before = counters(CREATE_KEY)

    assert create_product(storage, names, make_fields(" \t "), ids) is None

    assert capsys.readouterr().out == "product name must not be blank\n"
    assert storage == {} and names == set()
    assert ids.calls == 0
    assert counters(CREATE_KEY) == (before[0], before[1] + 1)


def test_create_product_duplicate_name(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[int, Product] = {}
    names: set[str] = set()
    ids = IdSource(1, 2)
    create_product(storage, names, make_fields("Saw"), ids)
    capsys.readouterr()

    assert create_product(storage, names, make_fields("  sAW "), ids) is None

    assert capsys.readouterr().out == "product name 'saw' is already taken\n"
    assert list(storage) == [1]
    assert names == {"saw"}
    assert ids.calls == 1


def test_create_product_generate_id_failure(
    capsys: pytest.CaptureFixture[str],
) -> None:
    storage: dict[int, Product] = {}
    names: set[str] = set()
    ids = IdSource(None)
    before = counters(CREATE_KEY)

    assert create_product(storage, names, make_fields(), ids) is None

    assert capsys.readouterr().out == ""
    assert storage == {} and names == set()
    assert ids.calls == 1
    assert counters(CREATE_KEY) == (before[0], before[1] + 1)


def test_create_product_with_broken_shared_generator(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(crud, "snowflake_id_generator", None)
    storage: dict[int, Product] = {}
    names: set[str] = set()

    result = create_product(storage, names, make_fields(), generate_snowflake_id)

    assert result is None
    assert storage == {} and names == set()
    assert capsys.readouterr().out == ""


def test_create_product_with_real_generator() -> None:
    storage: dict[int, Product] = {}
    names: set[str] = set()

    first = create_product(storage, names, make_fields("a"), generate_snowflake_id)
    second = create_product(storage, names, make_fields("b"), generate_snowflake_id)

    assert first is not None and second is not None
    assert first < second
    assert set(storage) == {first, second}
    assert names == {"a", "b"}


def test_read_product_success_and_missing(
    capsys: pytest.CaptureFixture[str],
) -> None:
    record = {NAME_KEY: "saw", PRICE_KEY: Decimal("1.00"), QUANTITY_KEY: 1}
    storage: dict[int, Product] = {7: record}
    before = counters(READ_KEY)

    assert read_product(storage, 7) is record
    assert counters(READ_KEY) == (before[0] + 1, before[1])
    assert capsys.readouterr().out == ""

    assert read_product(storage, 8) is None
    assert capsys.readouterr().out == "no product with id 8\n"
    assert counters(READ_KEY) == (before[0] + 1, before[1] + 1)


def make_store() -> tuple[dict[int, Product], set[str]]:
    storage: dict[int, Product] = {}
    names: set[str] = set()
    ids = IdSource(1, 2)
    create_product(storage, names, make_fields("saw", "1.00", 3), ids)
    create_product(storage, names, make_fields("axe", "2.00", 4), ids)
    return storage, names


def test_update_product_all_fields() -> None:
    storage, names = make_store()
    before = counters(UPDATE_KEY)

    result = update_product(
        storage,
        names,
        1,
        {NAME_KEY: "  Big SAW", PRICE_KEY: Decimal("3.456"), QUANTITY_KEY: 10},
    )

    expected = {NAME_KEY: "big saw", PRICE_KEY: Decimal("3.46"), QUANTITY_KEY: 10}
    assert result == expected
    assert storage[1] == expected
    assert names == {"big saw", "axe"}
    assert counters(UPDATE_KEY) == (before[0] + 1, before[1])


def test_update_product_partial_fields() -> None:
    storage, names = make_store()

    update_product(storage, names, 1, {QUANTITY_KEY: 99})
    assert storage[1] == {
        NAME_KEY: "saw",
        PRICE_KEY: Decimal("1.00"),
        QUANTITY_KEY: 99,
    }

    update_product(storage, names, 1, {PRICE_KEY: Decimal(7)})
    assert storage[1][PRICE_KEY] == Decimal("7.00")
    assert storage[1][NAME_KEY] == "saw"
    assert names == {"saw", "axe"}


def test_update_product_rename_to_own_name() -> None:
    storage, names = make_store()

    result = update_product(storage, names, 1, {NAME_KEY: "  SAW "})

    assert result is not None
    assert storage[1][NAME_KEY] == "saw"
    assert names == {"saw", "axe"}


def test_update_product_missing_id(capsys: pytest.CaptureFixture[str]) -> None:
    storage, names = make_store()
    before = counters(UPDATE_KEY)

    assert update_product(storage, names, 999, {QUANTITY_KEY: 1}) is None

    assert capsys.readouterr().out == "no product with id 999\n"
    assert counters(UPDATE_KEY) == (before[0], before[1] + 1)


def test_update_product_blank_name(capsys: pytest.CaptureFixture[str]) -> None:
    storage, names = make_store()

    assert update_product(storage, names, 1, {NAME_KEY: "   "}) is None

    assert capsys.readouterr().out == "product name must not be blank\n"
    assert storage[1][NAME_KEY] == "saw"
    assert names == {"saw", "axe"}


def test_update_product_name_taken(capsys: pytest.CaptureFixture[str]) -> None:
    storage, names = make_store()

    assert update_product(storage, names, 1, {NAME_KEY: "AXE"}) is None

    assert capsys.readouterr().out == "product name 'axe' is already taken\n"
    assert storage[1][NAME_KEY] == "saw"
    assert names == {"saw", "axe"}


def test_delete_product_success() -> None:
    storage, names = make_store()
    before = counters(DELETE_KEY)

    assert delete_product(storage, names, 1) == 1

    assert list(storage) == [2]
    assert names == {"axe"}
    assert counters(DELETE_KEY) == (before[0] + 1, before[1])


def test_delete_product_missing(capsys: pytest.CaptureFixture[str]) -> None:
    storage, names = make_store()
    before = counters(DELETE_KEY)

    assert delete_product(storage, names, 5) is None

    assert capsys.readouterr().out == "no product with id 5\n"
    assert list(storage) == [1, 2]
    assert names == {"saw", "axe"}
    assert counters(DELETE_KEY) == (before[0], before[1] + 1)


def test_names_index_matches_storage_after_operations() -> None:
    storage, names = make_store()

    update_product(storage, names, 1, {NAME_KEY: "hammer"})
    delete_product(storage, names, 2)
    create_product(storage, names, make_fields("saw"), IdSource(3))

    assert names == {record[NAME_KEY] for record in storage.values()}
