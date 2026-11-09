from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from part4.cart import add_to_cart, remove_from_cart
from part4.crud import (
    create_product,
    delete_product,
    generate_product_id,
    read_product,
    update_product,
)
from part4.run_admin import PROMPT, main, run_command
from part4.storage import NAME_KEY, PRICE_KEY, QUANTITY_KEY, Product
from part4.utils import get_storage_str_representation, normalize_price


# ============================================================
# Helpers
# ============================================================


ID_1 = "3f2c9a4e-8b1d-4c7a-9e55-0d6a1b7c2f10"
ID_2 = "8c7d6e5f-4a3b-4c2d-9e1f-0a1b2c3d4e5f"


def product(name: str, price: str = "10.00", quantity: int = 10) -> Product:
    return {
        NAME_KEY: name,
        PRICE_KEY: normalize_price(Decimal(price)),
        QUANTITY_KEY: quantity,
    }


def assert_name_index(storage: dict[str, Product], names: set[str]) -> None:
    assert names == {item[NAME_KEY] for item in storage.values()}


# ============================================================
# storage and UUID generation
# ============================================================


class TestStorage:
    def test_product_is_a_dictionary_with_only_named_fields(self) -> None:
        record = product("hammer", "12.34", 5)

        assert record == {
            NAME_KEY: "hammer",
            PRICE_KEY: Decimal("12.34"),
            QUANTITY_KEY: 5,
        }
        assert set(record) == {"name", "price", "quantity"}

    def test_old_tuple_index_constants_are_gone(self) -> None:
        import part4.storage as storage_module

        for constant in (
            "PRODUCT_ID_INDEX",
            "NAME_INDEX",
            "PRICE_INDEX",
            "QUANTITY_INDEX",
            "PRODUCT_ID_MIN",
        ):
            assert not hasattr(storage_module, constant)


class TestGenerateProductId:
    def test_returns_a_string_containing_a_version_four_uuid(self) -> None:
        product_id = generate_product_id()

        assert isinstance(product_id, str)
        assert len(product_id) == 36
        assert uuid.UUID(product_id).version == 4

    def test_consecutive_calls_return_different_ids(self) -> None:
        assert generate_product_id() != generate_product_id()


# ============================================================
# CRUD
# ============================================================


class TestCreateProduct:
    def test_creates_normalized_record_and_updates_name_index(self) -> None:
        storage: dict[str, Product] = {}
        names: set[str] = set()
        data = {
            NAME_KEY: "  Cordless   Drill ",
            PRICE_KEY: Decimal("89.999"),
            QUANTITY_KEY: 12,
        }

        product_id = create_product(storage, names, data)

        assert product_id is not None
        assert uuid.UUID(product_id).version == 4
        assert storage == {
            product_id: {
                NAME_KEY: "cordless drill",
                PRICE_KEY: Decimal("90.00"),
                QUANTITY_KEY: 12,
            }
        }
        assert names == {"cordless drill"}
        assert set(storage[product_id]) == {NAME_KEY, PRICE_KEY, QUANTITY_KEY}

    @pytest.mark.parametrize(
        ("name", "message"),
        [
            (" \t\n ", "product name must not be blank\n"),
            (" CORDLESS   DRILL ", "product name 'cordless drill' is already taken\n"),
        ],
    )
    def test_rejects_blank_or_duplicate_name_without_mutation(
        self,
        name: str,
        message: str,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        storage = {ID_1: product("cordless drill")}
        names = {"cordless drill"}
        before_storage = {key: value.copy() for key, value in storage.items()}
        before_names = names.copy()

        result = create_product(
            storage,
            names,
            {NAME_KEY: name, PRICE_KEY: Decimal(20), QUANTITY_KEY: 3},
        )

        assert result is None
        assert storage == before_storage
        assert names == before_names
        assert capsys.readouterr().out == message


class TestReadProduct:
    def test_returns_the_record_stored_under_the_id(self) -> None:
        record = product("hammer")
        storage = {ID_1: record}

        assert read_product(storage, ID_1) is record

    def test_missing_id_prints_error_and_returns_none(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert read_product({}, "missing-id") is None
        assert capsys.readouterr().out == "no product with id missing-id\n"


class TestUpdateProduct:
    @pytest.mark.parametrize(
        ("changes", "expected"),
        [
            (
                {QUANTITY_KEY: 4},
                {NAME_KEY: "hammer", PRICE_KEY: Decimal("10.00"), QUANTITY_KEY: 4},
            ),
            (
                {PRICE_KEY: Decimal("12.345")},
                {NAME_KEY: "hammer", PRICE_KEY: Decimal("12.35"), QUANTITY_KEY: 10},
            ),
            (
                {NAME_KEY: "  RUBBER   MALLET "},
                {
                    NAME_KEY: "rubber mallet",
                    PRICE_KEY: Decimal("10.00"),
                    QUANTITY_KEY: 10,
                },
            ),
        ],
    )
    def test_partial_update_preserves_omitted_fields_and_record_identity(
        self,
        changes: dict[str, object],
        expected: dict[str, object],
    ) -> None:
        record = product("hammer")
        storage = {ID_1: record}
        names = {"hammer"}

        updated = update_product(storage, names, ID_1, changes)

        assert updated is record
        assert storage[ID_1] is record
        assert record == expected
        assert_name_index(storage, names)

    def test_rename_removes_old_name_and_adds_new_name(self) -> None:
        storage = {ID_1: product("hammer"), ID_2: product("saw")}
        names = {"hammer", "saw"}
        update_fields = {NAME_KEY: "  CLAW   HAMMER ", PRICE_KEY: Decimal("4.567")}

        updated = update_product(storage, names, ID_1, update_fields)

        assert updated is storage[ID_1]
        assert updated == {
            NAME_KEY: "claw hammer",
            PRICE_KEY: Decimal("4.57"),
            QUANTITY_KEY: 10,
        }
        assert update_fields[NAME_KEY] == "claw hammer"
        assert update_fields[PRICE_KEY] == Decimal("4.57")
        assert names == {"claw hammer", "saw"}
        assert_name_index(storage, names)

    def test_same_normalized_name_is_not_a_duplicate(self) -> None:
        storage = {ID_1: product("cordless drill")}
        names = {"cordless drill"}

        result = update_product(storage, names, ID_1, {NAME_KEY: " CORDLESS   DRILL "})

        assert result is storage[ID_1]
        assert names == {"cordless drill"}

    @pytest.mark.parametrize(
        ("product_id", "changes", "message"),
        [
            (ID_1, {NAME_KEY: "  "}, "product name must not be blank\n"),
            (ID_1, {NAME_KEY: "saw"}, "product name 'saw' is already taken\n"),
            ("missing-id", {NAME_KEY: "  "}, "no product with id missing-id\n"),
        ],
    )
    def test_failed_update_does_not_change_storage_or_index(
        self,
        product_id: str,
        changes: dict[str, object],
        message: str,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        storage = {ID_1: product("hammer"), ID_2: product("saw")}
        names = {"hammer", "saw"}
        before_storage = {key: value.copy() for key, value in storage.items()}

        assert update_product(storage, names, product_id, changes) is None

        assert storage == before_storage
        assert names == {"hammer", "saw"}
        assert capsys.readouterr().out == message

    def test_empty_update_is_a_no_op(self) -> None:
        record = product("hammer")
        storage = {ID_1: record}
        names = {"hammer"}

        assert update_product(storage, names, ID_1, {}) is record
        assert storage[ID_1] is record
        assert names == {"hammer"}


class TestDeleteProduct:
    def test_deletes_record_and_removes_its_name_from_index(self) -> None:
        storage = {ID_1: product("hammer"), ID_2: product("saw")}
        names = {"hammer", "saw"}

        assert delete_product(storage, names, ID_1) == ID_1
        assert ID_1 not in storage
        assert names == {"saw"}
        assert_name_index(storage, names)

    def test_missing_id_changes_nothing(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        storage = {ID_1: product("hammer")}
        names = {"hammer"}

        assert delete_product(storage, names, "missing-id") is None

        assert storage == {ID_1: product("hammer")}
        assert names == {"hammer"}
        assert capsys.readouterr().out == "no product with id missing-id\n"


# ============================================================
# Table rendering for dictionary storage
# ============================================================


class TestStorageTable:
    def test_uses_uuid_keys_and_keeps_dictionary_insertion_order(self) -> None:
        storage = {
            ID_2: product("second", "2.50", 2),
            ID_1: product("first", "1.25", 1),
        }

        table = get_storage_str_representation(storage)

        assert table.index(ID_2) < table.index(ID_1)
        assert "second" in table and "first" in table
        assert "2.50" in table and "1.25" in table
        assert not table.endswith("\n")

    def test_empty_dictionary_has_the_expected_empty_table(self) -> None:
        assert get_storage_str_representation({}) == (
            "| ID | name | price | quantity |\n|----|------|-------|----------|"
        )


# ============================================================
# Cart dictionary
# ============================================================


class TestAddToCart:
    def test_adds_to_existing_quantity_and_decreases_stock(self) -> None:
        record = product("hammer", quantity=8)
        storage = {ID_1: record}
        names = {"hammer"}
        cart = {ID_1: 2}

        result = add_to_cart(storage, names, cart, ID_1, 3)

        assert result == 5
        assert cart == {ID_1: 5}
        assert record[QUANTITY_KEY] == 5
        assert record[NAME_KEY] == "hammer"
        assert record[PRICE_KEY] == Decimal("10.00")
        assert names == {"hammer"}

    def test_exact_stock_is_allowed(self) -> None:
        storage = {ID_1: product("hammer", quantity=3)}
        cart: dict[str, int] = {}
        names = {"hammer"}

        assert add_to_cart(storage, names, cart, ID_1, 3) == 3
        assert storage[ID_1][QUANTITY_KEY] == 0
        assert cart == {ID_1: 3}
        assert ID_1 in storage

    @pytest.mark.parametrize(
        ("product_id", "quantity", "message"),
        [
            ("missing-id", 1, "no product with id missing-id\n"),
            (
                ID_1,
                4,
                f"not enough stock for product {ID_1}: 3 available, 4 requested\n",
            ),
        ],
    )
    def test_failed_add_does_not_change_stock_or_cart(
        self,
        product_id: str,
        quantity: int,
        message: str,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        storage = {ID_1: product("hammer", quantity=3)}
        names = {"hammer"}
        cart = {ID_2: 2}
        before_storage = {key: value.copy() for key, value in storage.items()}

        assert add_to_cart(storage, names, cart, product_id, quantity) is None

        assert storage == before_storage
        assert cart == {ID_2: 2}
        assert names == {"hammer"}
        assert capsys.readouterr().out == message


class TestRemoveFromCart:
    def test_partial_remove_returns_items_to_stock(self) -> None:
        record = product("hammer", quantity=2)
        storage = {ID_1: record}
        names = {"hammer"}
        cart = {ID_1: 5}

        assert remove_from_cart(storage, names, cart, ID_1, 3) == 2
        assert record[QUANTITY_KEY] == 5
        assert cart == {ID_1: 2}
        assert names == {"hammer"}

    def test_removing_all_units_deletes_cart_key(self) -> None:
        storage = {ID_1: product("hammer", quantity=2)}
        names = {"hammer"}
        cart = {ID_1: 4}

        assert remove_from_cart(storage, names, cart, ID_1, 4) == 0
        assert cart == {}
        assert storage[ID_1][QUANTITY_KEY] == 6

    @pytest.mark.parametrize(
        ("storage", "cart", "product_id", "quantity", "message"),
        [
            ({}, {}, ID_1, 1, f"product {ID_1} is not in the cart\n"),
            (
                {},
                {ID_1: 1},
                ID_1,
                2,
                f"cart holds only 1 unit(s) of product {ID_1}, cannot remove 2\n",
            ),
            ({}, {ID_1: 2}, ID_1, 1, f"no product with id {ID_1}\n"),
        ],
    )
    def test_failed_remove_does_not_change_storage_or_cart(
        self,
        storage: dict[str, Product],
        cart: dict[str, int],
        product_id: str,
        quantity: int,
        message: str,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        names: set[str] = set()
        before_cart = cart.copy()

        assert remove_from_cart(storage, names, cart, product_id, quantity) is None

        assert storage == {}
        assert cart == before_cart
        assert capsys.readouterr().out == message


class TestCartInvariants:
    def test_add_then_remove_restores_storage_and_cart(self) -> None:
        storage = {ID_1: product("hammer", "12.34", 7)}
        names = {"hammer"}
        cart: dict[str, int] = {}
        before = {key: value.copy() for key, value in storage.items()}

        assert add_to_cart(storage, names, cart, ID_1, 4) == 4
        assert remove_from_cart(storage, names, cart, ID_1, 4) == 0

        assert storage == before
        assert cart == {}
        assert names == {"hammer"}


# ============================================================
# Admin console — changed signatures and string UUIDs
# ============================================================


class TestRunCommand:
    def test_create_update_delete_keep_name_index_in_sync(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        import part4.crud as crud_module

        monkeypatch.setattr(crud_module, "generate_product_id", lambda: ID_1)
        storage: dict[str, Product] = {}
        names: set[str] = set()

        assert run_command(storage, names, "create Cordless Drill 89.99 12") is True
        assert capsys.readouterr().out == f"{ID_1}\n"
        assert names == {"cordless drill"}

        assert run_command(storage, names, f"update {ID_1} Claw Hammer 10 5") is True
        assert storage[ID_1][NAME_KEY] == "claw hammer"
        assert names == {"claw hammer"}
        capsys.readouterr()

        assert run_command(storage, names, f"delete {ID_1}") is True
        assert storage == {}
        assert names == set()
        assert capsys.readouterr().out == f"{ID_1}\n"

    def test_read_passes_uuid_argument_as_a_string(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        storage = {ID_1: product("hammer")}
        names = {"hammer"}

        assert run_command(storage, names, "read not-a-uuid") is True

        assert capsys.readouterr().out == "no product with id not-a-uuid\n"

    def test_invalid_argument_count_is_rejected(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        storage = {ID_1: product("hammer")}
        names = {"hammer"}

        assert run_command(storage, names, "read one two") is True

        assert capsys.readouterr().out == "'read one two' is not a command\n"
        assert storage == {ID_1: product("hammer")}
        assert names == {"hammer"}


class TestAdminMain:
    def test_main_keeps_storage_and_name_index_for_the_session(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        commands = iter(["create Cordless Drill 89.99 12", "show", "exit"])
        prompts: list[str] = []

        def fake_input(prompt: str = "") -> str:
            prompts.append(prompt)
            return next(commands)

        import part4.crud as crud_module

        monkeypatch.setattr("builtins.input", fake_input)
        monkeypatch.setattr(crud_module, "generate_product_id", lambda: ID_1)

        main()

        output = capsys.readouterr().out
        assert output.startswith(f"{ID_1}\n")
        assert ID_1 in output and "cordless drill" in output
        assert prompts == [PROMPT, PROMPT, PROMPT]

    def test_main_reports_invalid_numeric_arguments_and_continues(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        commands = iter(["create hammer not-a-price 4", "exit"])

        monkeypatch.setattr("builtins.input", lambda _prompt="": next(commands))
        main()

        assert capsys.readouterr().out == (
            "'create hammer not-a-price 4' names a command but its arguments are invalid\n"
        )
