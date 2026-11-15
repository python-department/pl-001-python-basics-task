from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal, InvalidOperation

import pytest

from part5 import crud as crud_module
from part5 import run_admin as admin
from part5 import snowflake as sf
from part5.cart import add_to_cart, remove_from_cart
from part5.constants import (
    NODE_ID_DEFAULT,
    NODE_ID_MAX,
    SEQUENCE_ID_MAX,
    TIMESTAMP_MS_MAX,
)
from part5.decorators import FAILS_KEY, SUCCESS_KEY, collect_stats
from part5.storage import NAME_KEY, PRICE_KEY, QUANTITY_KEY, Product
from part5.utils import (
    get_stats_str_representation,
    get_storage_str_representation,
)


ID_1 = 1_288_834_974_657_000_001  # 19-digit Snowflake ID from the task
ID_2 = ID_1 + 1


def product(name: str = "hammer", quantity: int = 10) -> Product:
    return {
        NAME_KEY: name,
        PRICE_KEY: Decimal("10.00"),
        QUANTITY_KEY: quantity,
    }


@pytest.fixture(autouse=True)
def reset_stats() -> Iterator[None]:
    """Keep the process-wide registry isolated between tests."""
    registry = crud_module.STATS_REGISTRY
    previous = {key: value.copy() for key, value in registry.items()}
    registry.clear()
    registry.update(
        {
            key: {SUCCESS_KEY: 0, FAILS_KEY: 0}
            for key in ("create", "read", "update", "delete")
        }
    )
    yield
    registry.clear()
    registry.update(previous)


# ---------------------------------------------------------------------------
# snowflake.py — stateful generator; old part-1 helpers are not retested
# ---------------------------------------------------------------------------


class TestSnowflakeGenerator:
    def test_task_example_node_five_sequence_and_millisecond_rollover(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        now = [123_456]
        monkeypatch.setattr(sf, "read_current_millis", lambda _epoch: now[0])

        generate_id = sf.get_snowflake_id_generator(node_id=5, epoch_ms=0)
        assert generate_id is not None  # сужает тип до Callable[[], int | None]
        assert capsys.readouterr().out == ""  # creating it does not issue an ID

        first = generate_id()
        second = generate_id()
        now[0] += 1
        third = generate_id()
        assert first is not None
        assert second is not None
        assert third is not None

        assert [sf.decode_node_id(value) for value in (first, second, third)] == [
            5,
            5,
            5,
        ]
        assert [
            sf.decode_timestamp_ms(value, 0) for value in (first, second, third)
        ] == [
            123_456,
            123_456,
            123_457,
        ]
        assert [sf.decode_sequence_id(value) for value in (first, second, third)] == [
            0,
            1,
            0,
        ]
        assert first < second < third
        assert all(0 < value < 2**63 for value in (first, second, third))
        assert capsys.readouterr().out == ""

    @pytest.mark.parametrize("node_id", [-1, NODE_ID_MAX + 1])
    def test_rejects_node_outside_inclusive_bounds(
        self,
        node_id: int,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        monkeypatch.setattr(sf, "read_current_millis", lambda _epoch: 0)

        assert sf.get_snowflake_id_generator(node_id=node_id, epoch_ms=0) is None
        assert capsys.readouterr().out == (
            f"node_id must be in [0, {NODE_ID_MAX}], got {node_id}\n"
        )

    def test_accepts_max_node_and_epoch_equal_to_now(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(sf, "read_current_millis", lambda _epoch: 0)
        generate_id = sf.get_snowflake_id_generator(node_id=NODE_ID_MAX, epoch_ms=0)

        assert generate_id is not None
        value = generate_id()
        assert value is not None
        assert sf.decode_node_id(value) == NODE_ID_MAX
        assert capsys.readouterr().out == ""

    def test_rejects_future_epoch_at_creation(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(sf, "read_current_millis", lambda _epoch: -1)

        assert sf.get_snowflake_id_generator(node_id=0, epoch_ms=123) is None
        assert (
            capsys.readouterr().out == "epoch_ms must not be in the future, got 123\n"
        )

    def test_counter_exhaustion_recovers_on_next_millisecond(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        now = [50]
        monkeypatch.setattr(sf, "read_current_millis", lambda _epoch: now[0])
        generate_id = sf.get_snowflake_id_generator(epoch_ms=0)
        assert generate_id is not None

        last: int | None = None
        for _ in range(SEQUENCE_ID_MAX + 1):
            last = generate_id()
        assert last is not None
        assert sf.decode_sequence_id(last) == SEQUENCE_ID_MAX

        assert generate_id() is None
        assert capsys.readouterr().out == (
            f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], "
            f"got {SEQUENCE_ID_MAX + 1}\n"
        )

        now[0] += 1
        recovered = generate_id()
        assert recovered is not None
        assert sf.decode_timestamp_ms(recovered, 0) == 51
        assert sf.decode_sequence_id(recovered) == 0

    def test_timestamp_limit_is_inclusive(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        now = [TIMESTAMP_MS_MAX]
        monkeypatch.setattr(sf, "read_current_millis", lambda _epoch: now[0])
        generate_id = sf.get_snowflake_id_generator(epoch_ms=0)
        assert generate_id is not None

        last_valid = generate_id()
        assert last_valid is not None
        assert sf.decode_timestamp_ms(last_valid, 0) == TIMESTAMP_MS_MAX

        now[0] += 1
        assert generate_id() is None
        assert capsys.readouterr().out == (
            f"timestamp {TIMESTAMP_MS_MAX + 1} ms overflows {TIMESTAMP_MS_MAX} ms\n"
        )

    def test_generators_keep_independent_counters(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(sf, "read_current_millis", lambda _epoch: 100)
        generate_a = sf.get_snowflake_id_generator(node_id=1, epoch_ms=0)
        generate_b = sf.get_snowflake_id_generator(node_id=2, epoch_ms=0)
        assert generate_a is not None
        assert generate_b is not None

        a_first = generate_a()
        a_second = generate_a()
        b_first = generate_b()
        assert a_first is not None
        assert a_second is not None
        assert b_first is not None

        assert (sf.decode_node_id(a_first), sf.decode_sequence_id(a_first)) == (1, 0)
        assert (sf.decode_node_id(a_second), sf.decode_sequence_id(a_second)) == (1, 1)
        assert (sf.decode_node_id(b_first), sf.decode_sequence_id(b_first)) == (2, 0)


# ---------------------------------------------------------------------------
# decorators.py — generic statistics decorator
# ---------------------------------------------------------------------------


class TestCollectStats:
    def test_task_divide_example_counts_zero_as_success_and_none_as_failure(
        self,
    ) -> None:
        registry: dict[str, dict[str, int]] = {}

        @collect_stats("divide", registry)
        def divide(a: int, b: int) -> float | None:
            "Divide two numbers."
            if b == 0:
                print("division by zero")
                return None
            return a / b

        assert registry == {"divide": {SUCCESS_KEY: 0, FAILS_KEY: 0}}
        assert divide(a=10, b=4) == 2.5
        assert divide(0, 5) == 0.0
        assert divide(1, 0) is None
        assert registry["divide"] == {SUCCESS_KEY: 2, FAILS_KEY: 1}
        assert divide.__name__ == "divide"
        assert divide.__doc__ == "Divide two numbers."

    def test_duplicate_key_returns_original_function_and_preserves_registry(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        old_stats: dict[str, int] = {SUCCESS_KEY: 7, FAILS_KEY: 3}
        registry: dict[str, dict[str, int]] = {"create": old_stats}

        def operation(value: int) -> int:
            return value * 2

        decorated = collect_stats("create", registry)(operation)
        assert decorated is operation
        assert decorated(4) == 8
        assert registry == {"create": old_stats}
        assert registry["create"] is old_stats
        assert capsys.readouterr().out == "stats key 'create' is already registered\n"

    def test_different_keys_have_independent_counters(self) -> None:
        registry: dict[str, dict[str, int]] = {}

        @collect_stats("first", registry)
        def first() -> bool:
            return False

        @collect_stats("second", registry)
        def second() -> None:
            return None

        assert first() is False
        assert second() is None
        assert registry == {
            "first": {SUCCESS_KEY: 1, FAILS_KEY: 0},
            "second": {SUCCESS_KEY: 0, FAILS_KEY: 1},
        }


# ---------------------------------------------------------------------------
# crud.py — injected ID factory, integer IDs and CRUD statistics
# ---------------------------------------------------------------------------


class TestChangedCrud:
    def test_generate_snowflake_id_uses_one_increasing_global_generator(self) -> None:
        before = {
            key: value.copy() for key, value in crud_module.STATS_REGISTRY.items()
        }

        first = crud_module.generate_snowflake_id()
        second = crud_module.generate_snowflake_id()

        assert isinstance(first, int) and isinstance(second, int)
        assert 0 < first < second < 2**63
        assert sf.decode_node_id(first) == NODE_ID_DEFAULT
        assert crud_module.STATS_REGISTRY == before  # ID generation is not counted
        assert not hasattr(crud_module, "generate_product_id")

    def test_create_passes_generated_id_into_integer_keyed_storage(self) -> None:
        storage: dict[int, Product] = {}
        names: set[str] = set()
        calls: list[None] = []

        def generate_id() -> int:
            calls.append(None)
            return ID_1

        result = crud_module.create_product(
            storage,
            names,
            {
                NAME_KEY: "  Cordless   Drill ",
                PRICE_KEY: Decimal("89.999"),
                QUANTITY_KEY: 12,
            },
            generate_id,
        )

        assert result == ID_1
        assert calls == [None]
        assert storage == {
            ID_1: {
                NAME_KEY: "cordless drill",
                PRICE_KEY: Decimal("90.00"),
                QUANTITY_KEY: 12,
            }
        }
        assert names == {"cordless drill"}
        assert crud_module.STATS_REGISTRY["create"] == {
            SUCCESS_KEY: 1,
            FAILS_KEY: 0,
        }

    @pytest.mark.parametrize(
        ("name", "initial_names", "message"),
        [
            (" \t\n ", set(), "product name must not be blank\n"),
            (
                " CORDLESS   DRILL ",
                {"cordless drill"},
                "product name 'cordless drill' is already taken\n",
            ),
        ],
    )
    def test_invalid_name_does_not_call_id_factory_or_mutate_state(
        self,
        name: str,
        initial_names: set[str],
        message: str,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        storage: dict[int, Product] = {ID_1: product("cordless drill")}
        names: set[str] = set(initial_names)
        before_storage: dict[int, Product] = {
            key: value.copy() for key, value in storage.items()
        }
        calls: list[None] = []

        result = crud_module.create_product(
            storage,
            names,
            {NAME_KEY: name, PRICE_KEY: Decimal(5), QUANTITY_KEY: 1},
            lambda: calls.append(None),
        )

        assert result is None
        assert calls == []
        assert storage == before_storage
        assert names == initial_names
        assert capsys.readouterr().out == message
        assert crud_module.STATS_REGISTRY["create"] == {
            SUCCESS_KEY: 0,
            FAILS_KEY: 1,
        }

    def test_none_from_id_factory_is_failure_without_extra_output(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        storage: dict[int, Product] = {}
        names: set[str] = set()

        def unavailable_id() -> None:
            print("sequence exhausted")

        assert (
            crud_module.create_product(
                storage,
                names,
                {NAME_KEY: "hammer", PRICE_KEY: Decimal(10), QUANTITY_KEY: 2},
                unavailable_id,
            )
            is None
        )
        assert storage == {} and names == set()
        assert capsys.readouterr().out == "sequence exhausted\n"
        assert crud_module.STATS_REGISTRY["create"] == {
            SUCCESS_KEY: 0,
            FAILS_KEY: 1,
        }

    def test_all_four_crud_operations_count_success_and_none(self) -> None:
        storage = {ID_1: product()}
        names = {"hammer"}

        assert crud_module.read_product(storage, ID_1) is storage[ID_1]
        assert crud_module.read_product(storage, ID_2) is None
        assert (
            crud_module.update_product(storage, names, ID_1, {QUANTITY_KEY: 3})
            is storage[ID_1]
        )
        assert (
            crud_module.update_product(storage, names, ID_2, {QUANTITY_KEY: 4}) is None
        )
        assert crud_module.delete_product(storage, names, ID_1) == ID_1
        assert crud_module.delete_product(storage, names, ID_1) is None

        assert crud_module.STATS_REGISTRY == {
            "create": {SUCCESS_KEY: 0, FAILS_KEY: 0},
            "read": {SUCCESS_KEY: 1, FAILS_KEY: 1},
            "update": {SUCCESS_KEY: 1, FAILS_KEY: 1},
            "delete": {SUCCESS_KEY: 1, FAILS_KEY: 1},
        }


# ---------------------------------------------------------------------------
# cart.py and storage table — only the changed integer-ID representation
# ---------------------------------------------------------------------------


class TestIntegerIdsOutsideCrud:
    def test_cart_accepts_integer_ids_without_changing_name_index_or_stats(
        self,
    ) -> None:
        storage: dict[int, Product] = {ID_1: product(quantity=7)}
        names: set[str] = {"hammer"}
        cart: dict[int, int] = {}
        stats_before: dict[str, dict[str, int]] = {
            key: value.copy() for key, value in crud_module.STATS_REGISTRY.items()
        }

        assert add_to_cart(storage, names, cart, ID_1, 4) == 4
        assert remove_from_cart(storage, names, cart, ID_1, 4) == 0
        assert storage[ID_1][QUANTITY_KEY] == 7
        assert cart == {}
        assert names == {"hammer"}
        assert crud_module.STATS_REGISTRY == stats_before  # cart is not instrumented

    def test_storage_table_displays_full_19_digit_integer_id(self) -> None:
        table = get_storage_str_representation({ID_1: product("hammer", 3)})

        assert str(ID_1) in table

        assert f"{ID_1:e}" not in table
        assert f"{ID_1:g}" not in table

        assert "hammer" in table
        assert "10.00" in table

        last_row = table.splitlines()[-1]
        assert last_row.startswith("|") and last_row.endswith("|")
        quantity_cell = last_row.split("|")[-2].strip()
        assert quantity_cell == "3"


# ---------------------------------------------------------------------------
# utils.py — new statistics table
# ---------------------------------------------------------------------------


class TestStatsTable:
    def test_task_example_percentages_and_zero_calls(self) -> None:
        registry = {
            "create": {SUCCESS_KEY: 2, FAILS_KEY: 1},
            "read": {SUCCESS_KEY: 0, FAILS_KEY: 0},
            "delete": {SUCCESS_KEY: 5, FAILS_KEY: 0},
        }

        assert get_stats_str_representation(registry) == (
            "| command name | success | fails | success rate |\n"
            "|--------------|---------|-------|--------------|\n"
            "| create       | 2       | 1     | 66.67%       |\n"
            "| read         | 0       | 0     | 0.00%        |\n"
            "| delete       | 5       | 0     | 100.00%      |"
        )

    def test_long_command_name_expands_column_and_rounds_rate(self) -> None:
        table = get_stats_str_representation(
            {"update-everything-twice": {SUCCESS_KEY: 1, FAILS_KEY: 30}}
        )

        assert "update-everything-twice" in table
        assert "3.23%" in table
        assert not table.endswith("\n")
        assert len(table.splitlines()[0]) == len(table.splitlines()[2])

    def test_empty_registry_contains_only_header_and_separator(self) -> None:
        assert get_stats_str_representation({}) == (
            "| command name | success | fails | success rate |\n"
            "|--------------|---------|-------|--------------|"
        )


# ---------------------------------------------------------------------------
# run_admin.py — integer parsing and the new stats command
# ---------------------------------------------------------------------------


class TestAdminChanges:
    def test_create_command_uses_snowflake_adapter(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        storage: dict[int, Product] = {}
        names: set[str] = set()

        assert (
            admin.run_command(storage, names, "create Gibson SG Junior 89.99 12")
            is True
        )
        output = capsys.readouterr().out
        created_id = int(output.strip())
        assert 0 < created_id < 2**63
        assert created_id in storage
        assert storage[created_id][NAME_KEY] == "gibson sg junior"
        assert names == {"gibson sg junior"}

    def test_numeric_ids_are_converted_for_read_update_and_delete(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        storage: dict[int, Product] = {ID_1: product()}
        names: set[str] = {"hammer"}

        assert admin.run_command(storage, names, f"read {ID_1}") is True
        assert "hammer" in capsys.readouterr().out
        assert (
            admin.run_command(storage, names, f"update {ID_1} Claw Hammer 12.34 5")
            is True
        )
        assert storage[ID_1][NAME_KEY] == "claw hammer"
        assert names == {"claw hammer"}
        capsys.readouterr()
        assert admin.run_command(storage, names, f"delete {ID_1}") is True
        assert storage == {} and names == set()
        assert capsys.readouterr().out == f"{ID_1}\n"

    def test_non_integer_id_raises_value_error(self) -> None:
        """Bad ids surface as ValueError; the REPL layer is what reports them."""
        storage: dict[int, Product] = {}
        names: set[str] = set()
        with pytest.raises(ValueError):
            admin.run_command(storage, names, "read not-an-int")

    def test_non_decimal_price_raises_invalid_operation(self) -> None:
        """Bad prices surface as decimal.InvalidOperation, not ValueError."""
        storage: dict[int, Product] = {}
        names: set[str] = set()
        with pytest.raises(InvalidOperation):
            admin.run_command(storage, names, "create x abc 5")

    def test_main_reports_bad_arguments_and_keeps_running(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        inputs: Iterator[str] = iter(["read not-an-int", "exit"])
        monkeypatch.setattr("builtins.input", lambda _prompt="": next(inputs))

        admin.main()

        out = capsys.readouterr().out
        assert "'read not-an-int' names a command but its arguments are invalid" in out

    def test_stats_command_prints_registry_without_mutating_store(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        storage: dict[int, Product] = {ID_1: product()}
        names: set[str] = {"hammer"}
        before_storage: dict[int, Product] = {
            key: value.copy() for key, value in storage.items()
        }
        before_names: set[str] = names.copy()
        crud_module.STATS_REGISTRY["create"][SUCCESS_KEY] = 2

        assert admin.run_command(storage, names, "stats") is True
        output = capsys.readouterr().out
        assert "command name" in output and "success rate" in output
        assert "create" in output and "2" in output
        assert storage == before_storage
        assert names == before_names

    def test_stats_with_extra_arguments_is_not_a_command(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        storage: dict[int, Product] = {}
        names: set[str] = set()
        assert admin.run_command(storage, names, "stats create") is True
        assert capsys.readouterr().out == "'stats create' is not a command\n"

    def test_help_lists_stats_after_delete(self) -> None:
        help_text: str = admin.HELP_TEXT
        assert help_text.index("delete <id>") < help_text.index("stats")
        assert "print call statistics of the CRUD commands" in help_text
