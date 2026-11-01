from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, cast

import pytest

from part3.crud import create_product, delete_product, read_product, update_product
from part3.run_admin import (
    HELP_TEXT,
    PROMPT,
    main,
    print_result,
    run_command,
    show_help,
)
from part3.storage import (
    NAME_INDEX,
    PRICE_INDEX,
    PRODUCT_ID_INDEX,
    PRODUCT_ID_MIN,
    QUANTITY_INDEX,
    Product,
)
from part3.utils import (
    TABLE_HEADERS,
    get_storage_str_representation,
    normalize_price,
    normalize_product_name,
)


# ============================================================
# Helpers
# ============================================================


def product(
    product_id: int,
    name: str,
    price: str = "10.00",
    quantity: int = 10,
) -> Product:
    """Build a Product using the public index constants, not fixed positions."""
    fields: list[Any] = [None] * 4
    fields[PRODUCT_ID_INDEX] = product_id
    fields[NAME_INDEX] = name
    fields[PRICE_INDEX] = normalize_price(Decimal(price))
    fields[QUANTITY_INDEX] = quantity
    return cast(Product, tuple(fields))


def product_id(record: Product) -> int:
    return record[PRODUCT_ID_INDEX]


def product_name(record: Product) -> str:
    return record[NAME_INDEX]


def product_price(record: Product) -> Decimal:
    return record[PRICE_INDEX]


def product_quantity(record: Product) -> int:
    return record[QUANTITY_INDEX]


EXPECTED_HELP_TEXT = """Available commands:
  help                                       show this message
  exit                                       leave the console
  show                                       print the whole store as a table
  create <name...> <price> <quantity>        add a product, print its new id
  read <id>                                  print the product with that id
  update <id> <name...> <price> <quantity>   overwrite that product's fields
  delete <id>                                remove the product with that id

For create and update the price and quantity are the last two words of the
line; everything before them is the product name, so it may contain spaces
(for example "Gibson SG Junior") and needs no quoting."""


# ============================================================
# utils — TABLE_HEADERS and normalize_product_name
# ============================================================


class TestTableHeaders:
    def test_table_headers_have_the_required_order(self) -> None:
        assert TABLE_HEADERS == ("ID", "name", "price", "quantity")


class TestNormalizeProductName:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("  Cordless Drill  ", "cordless drill"),
            ("abc    def\tghi\tjkl", "abc def ghi jkl"),
            (" \t\n ", ""),
            ("claw hammer", "claw hammer"),
            ("  RUBBER\t\tMALLET  ", "rubber mallet"),
            ("one\ntwo\r\nthree", "one two three"),
            ("\v  A\fB  ", "a b"),
            ("123   ABC", "123 abc"),
            ("", ""),
        ],
    )
    def test_normalizes_name(self, raw: str, expected: str) -> None:
        assert normalize_product_name(raw) == expected

    def test_normalization_is_idempotent(self) -> None:
        normalized = normalize_product_name("  Cordless\t  DRILL \n")
        assert normalize_product_name(normalized) == normalized


# ============================================================
# utils — get_storage_str_representation
# ============================================================


class TestGetStorageStringRepresentation:
    def test_empty_storage_has_only_header_and_separator(self) -> None:
        assert get_storage_str_representation([]) == (
            "| ID | name | price | quantity |\n|----|------|-------|----------|"
        )

    def test_simple_storage_matches_exact_table(self) -> None:
        storage = [
            product(1, "saw", "9.90", 5),
            product(2, "axe", "12.00", 8),
        ]

        assert get_storage_str_representation(storage) == (
            "| ID | name | price | quantity |\n"
            "|----|------|-------|----------|\n"
            "| 1  | saw  | 9.90  | 5        |\n"
            "| 2  | axe  | 12.00 | 8        |"
        )

    def test_column_widths_expand_to_fit_values(self) -> None:
        storage = [
            product(10, "compressor", "1299.99", 3),
            product(2, "nail", "2.50", 500),
        ]

        assert get_storage_str_representation(storage) == (
            "| ID | name       | price   | quantity |\n"
            "|----|------------|---------|----------|\n"
            "| 10 | compressor | 1299.99 | 3        |\n"
            "| 2  | nail       | 2.50    | 500      |"
        )

    def test_table_preserves_storage_order(self) -> None:
        storage = [
            product(8, "last alphabetically", "1.00", 1),
            product(2, "first alphabetically", "2.00", 2),
        ]

        table = get_storage_str_representation(storage)
        assert table.index("last alphabetically") < table.index("first alphabetically")

    def test_all_rows_have_the_same_width_and_aligned_separators(self) -> None:
        storage = [
            product(100, "a much longer product name", "123456.78", 1000),
            product(2, "x", "0.01", 1),
            product(30, "medium name", "10.00", 99999),
        ]
        lines = get_storage_str_representation(storage).split("\n")

        assert len({len(line) for line in lines}) == 1
        bar_positions = [
            [i for i, char in enumerate(line) if char == "|"] for line in lines
        ]
        assert all(positions == bar_positions[0] for positions in bar_positions)

    def test_table_has_no_trailing_newline(self) -> None:
        table = get_storage_str_representation([product(1, "saw")])
        assert not table.endswith("\n")

    def test_data_values_are_not_reordered_or_truncated(self) -> None:
        storage = [product(17, "A very long name", "12345.67", 123456)]
        table = get_storage_str_representation(storage)

        assert "A very long name" in table
        assert "12345.67" in table
        assert "123456" in table
        assert table.index("17") < table.index("A very long name")


# ============================================================
# crud — create_product with normalized names
# ============================================================


class TestCreateProductPart3:
    def test_success_normalizes_name_and_price(self) -> None:
        storage: list[Product] = []

        created_id = create_product(
            storage,
            ("  Cordless   Drill ", Decimal("89.999"), 12),
        )

        assert created_id == PRODUCT_ID_MIN
        assert len(storage) == 1
        saved = storage[0]
        assert product_id(saved) == created_id
        assert product_name(saved) == "cordless drill"
        assert product_price(saved) == Decimal("90.00")
        assert product_quantity(saved) == 12

    def test_successive_products_receive_successive_ids(self) -> None:
        storage: list[Product] = []
        first_id = create_product(storage, ("Cordless Drill", Decimal(10), 1))
        second_id = create_product(storage, ("Claw Hammer", Decimal(20), 2))

        assert first_id == PRODUCT_ID_MIN
        assert second_id == PRODUCT_ID_MIN + 1
        assert [product_id(item) for item in storage] == [first_id, second_id]

    def test_duplicate_after_normalization_is_rejected_without_mutation(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        storage = [product(1, "cordless drill", "50.00", 3)]
        before = list(storage)

        result = create_product(
            storage,
            ("  CORDLESS   DRILL  ", Decimal(75), 1),
        )

        assert result is None
        assert storage == before
        assert (
            capsys.readouterr().out
            == "product name 'cordless drill' is already taken\n"
        )

    @pytest.mark.parametrize("blank_name", ["", "   ", "\t \n"])
    def test_blank_name_is_rejected_without_mutation(
        self, blank_name: str, capsys: pytest.CaptureFixture[str]
    ) -> None:
        storage = [product(1, "hammer")]
        before = list(storage)

        result = create_product(storage, (blank_name, Decimal(10), 3))

        assert result is None
        assert storage == before
        assert capsys.readouterr().out == "product name must not be blank\n"

    def test_successfully_created_product_can_be_read(self) -> None:
        storage: list[Product] = []
        created_id = create_product(
            storage, ("  RUBBER  MALLET ", Decimal("7.505"), 25)
        )

        assert created_id is not None
        saved = read_product(storage, created_id)
        assert saved is not None
        assert product_name(saved) == "rubber mallet"
        assert product_price(saved) == Decimal("7.51")
        assert product_quantity(saved) == 25


# ============================================================
# crud — update_product with normalized names
# ============================================================


class TestUpdateProductPart3:
    def test_success_normalizes_name_and_price_and_keeps_id(self) -> None:
        storage = [
            product(1, "cordless drill", "90.00", 12),
            product(2, "claw hammer", "9.90", 40),
        ]

        updated = update_product(
            storage,
            2,
            ("  Rubber   Mallet ", Decimal("7.505"), 25),
        )

        assert updated is not None
        assert product_id(updated) == 2
        assert product_name(updated) == "rubber mallet"
        assert product_price(updated) == Decimal("7.51")
        assert product_quantity(updated) == 25
        assert storage == [product(1, "cordless drill", "90.00", 12), updated]

    def test_update_to_same_name_in_different_form_is_allowed(self) -> None:
        storage = [product(1, "cordless drill", "90.00", 12)]

        updated = update_product(
            storage,
            1,
            (" CORDLESS   Drill ", Decimal(85), 10),
        )

        assert updated is not None
        assert product_id(updated) == 1
        assert product_name(updated) == "cordless drill"
        assert product_price(updated) == Decimal("85.00")
        assert product_quantity(updated) == 10
        assert storage == [updated]

    def test_duplicate_name_owned_by_another_product_is_rejected(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        storage = [
            product(1, "cordless drill", "90.00", 12),
            product(2, "claw hammer", "9.90", 40),
        ]
        before = list(storage)

        result = update_product(
            storage,
            1,
            ("  CLAW   HAMMER ", Decimal(85), 10),
        )

        assert result is None
        assert storage == before
        assert (
            capsys.readouterr().out == "product name 'claw hammer' is already taken\n"
        )

    @pytest.mark.parametrize("blank_name", ["", "    ", "\t\n"])
    def test_blank_name_is_rejected_without_mutation(
        self, blank_name: str, capsys: pytest.CaptureFixture[str]
    ) -> None:
        storage = [product(1, "cordless drill", "90.00", 12)]
        before = list(storage)

        result = update_product(storage, 1, (blank_name, Decimal(85), 10))

        assert result is None
        assert storage == before
        assert capsys.readouterr().out == "product name must not be blank\n"

    def test_blank_name_is_checked_before_missing_product_id(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        storage = [product(1, "cordless drill")]

        result = update_product(storage, 99, ("   ", Decimal(20), 5))

        assert result is None
        assert capsys.readouterr().out == "product name must not be blank\n"
        assert storage == [product(1, "cordless drill")]

    def test_missing_product_id_does_not_change_storage(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        storage = [product(1, "cordless drill", "90.00", 12)]
        before = list(storage)

        result = update_product(storage, 99, ("saw", Decimal(20), 5))

        assert result is None
        assert storage == before
        assert capsys.readouterr().out == "no product with id 99\n"

    def test_normalized_name_can_be_reused_after_old_product_is_deleted(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        storage = [
            product(PRODUCT_ID_MIN, "cordless drill"),
            product(PRODUCT_ID_MIN + 1, "claw hammer"),
            product(PRODUCT_ID_MIN + 2, "saw"),
        ]
        assert delete_product(storage, PRODUCT_ID_MIN + 1) == PRODUCT_ID_MIN + 1
        capsys.readouterr()

        created_id = create_product(storage, (" CLAW   HAMMER ", Decimal(11), 3))

        assert created_id == PRODUCT_ID_MIN + 3
        assert product_name(storage[-1]) == "claw hammer"


# ============================================================
# run_admin — show_help and print_result
# ============================================================


class TestAdminOutputHelpers:
    def test_help_text_matches_the_task(self) -> None:
        assert HELP_TEXT == EXPECTED_HELP_TEXT

    def test_show_help_prints_the_help_text(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        show_help()
        assert capsys.readouterr().out == EXPECTED_HELP_TEXT + "\n"

    @pytest.mark.parametrize("result", [1, "created", (1, "hammer")])
    def test_print_result_prints_non_none_values(
        self, result: object, capsys: pytest.CaptureFixture[str]
    ) -> None:
        print_result(result)
        assert capsys.readouterr().out == f"{result}\n"

    def test_print_result_does_not_print_none(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        print_result(None)
        assert capsys.readouterr().out == ""


# ============================================================
# run_admin — run_command
# ============================================================


class TestRunCommand:
    def test_help_prints_exact_help_text_and_continues(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert run_command([], "help") is True
        assert capsys.readouterr().out == EXPECTED_HELP_TEXT + "\n"

    def test_exit_returns_false_without_output(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert run_command([], "exit") is False
        assert capsys.readouterr().out == ""

    def test_show_prints_empty_storage_table(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert run_command([], "show") is True
        assert capsys.readouterr().out == (
            "| ID | name | price | quantity |\n|----|------|-------|----------|\n"
        )

    def test_create_parses_multiword_name_and_prints_id(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        storage: list[Product] = []

        assert run_command(storage, "create  Cordless   Drill  89.999 12") is True

        assert capsys.readouterr().out == f"{PRODUCT_ID_MIN}\n"
        assert len(storage) == 1
        assert product_id(storage[0]) == PRODUCT_ID_MIN
        assert product_name(storage[0]) == "cordless drill"
        assert product_price(storage[0]) == Decimal("90.00")
        assert product_quantity(storage[0]) == 12

    def test_create_duplicate_does_not_print_none(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        storage = [product(1, "cordless drill")]

        assert run_command(storage, "create CORDLESS DRILL 20 4") is True

        assert (
            capsys.readouterr().out
            == "product name 'cordless drill' is already taken\n"
        )
        assert storage == [product(1, "cordless drill")]

    def test_read_prints_the_product(self, capsys: pytest.CaptureFixture[str]) -> None:
        storage = [product(7, "hammer", "9.90", 3)]

        assert run_command(storage, "read 7") is True

        assert capsys.readouterr().out == "(7, 'hammer', Decimal('9.90'), 3)\n"

    def test_read_missing_product_prints_only_error(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        storage = [product(7, "hammer")]

        assert run_command(storage, "read 99") is True

        assert capsys.readouterr().out == "no product with id 99\n"

    def test_update_parses_multiword_name_and_prints_updated_product(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        storage = [product(1, "cordless drill", "90.00", 12)]

        assert run_command(storage, "update 1  Rubber   Mallet  7.505 25") is True

        assert capsys.readouterr().out == "(1, 'rubber mallet', Decimal('7.51'), 25)\n"
        assert storage == [product(1, "rubber mallet", "7.51", 25)]

    def test_update_duplicate_name_does_not_change_storage(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        storage = [product(1, "cordless drill"), product(2, "claw hammer")]
        before = list(storage)

        assert run_command(storage, "update 1 Claw Hammer 20 5") is True

        assert (
            capsys.readouterr().out == "product name 'claw hammer' is already taken\n"
        )
        assert storage == before

    def test_delete_removes_product_and_prints_id(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        storage = [product(1, "hammer"), product(2, "saw")]

        assert run_command(storage, "delete 1") is True

        assert capsys.readouterr().out == "1\n"
        assert storage == [product(2, "saw")]

    @pytest.mark.parametrize(
        "line",
        [
            "frobnicate",
            "read 1 2 3",
            "delete",
            "show extra",
            "help now",
            "exit now",
            "create 89.90 12",
            "update 1 89.90 12",
            "",
        ],
    )
    def test_unknown_command_or_wrong_argument_count_is_rejected(
        self,
        line: str,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        storage = [product(1, "hammer")]
        before = list(storage)

        assert run_command(storage, line) is True

        assert capsys.readouterr().out == f"'{line}' is not a command\n"
        assert storage == before

    def test_invalid_integer_argument_propagates_value_error(self) -> None:
        with pytest.raises(ValueError):
            run_command([], "read not-an-id")

    def test_invalid_decimal_argument_propagates_invalid_operation(self) -> None:
        with pytest.raises(InvalidOperation):
            run_command([], "create hammer not-a-price 4")

    def test_invalid_update_id_propagates_value_error(self) -> None:
        with pytest.raises(ValueError):
            run_command([], "update not-an-id hammer 10 4")


# ============================================================
# run_admin — main loop and invalid arguments
# ============================================================


class TestAdminMain:
    def test_main_keeps_one_storage_for_the_whole_session(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        commands = iter(
            [
                "create Cordless Drill 89.99 12",
                "create Claw Hammer 9.9 40",
                "show",
                "exit",
            ]
        )
        prompts: list[str] = []

        def fake_input(prompt: str = "") -> str:
            prompts.append(prompt)
            return next(commands)

        monkeypatch.setattr("builtins.input", fake_input)
        main()

        output = capsys.readouterr().out
        expected_storage = [
            product(PRODUCT_ID_MIN, "cordless drill", "89.99", 12),
            product(PRODUCT_ID_MIN + 1, "claw hammer", "9.90", 40),
        ]
        expected_table = get_storage_str_representation(expected_storage)
        assert output == (f"{PRODUCT_ID_MIN}\n{PRODUCT_ID_MIN + 1}\n{expected_table}\n")
        assert prompts == [PROMPT, PROMPT, PROMPT, PROMPT]

    @pytest.mark.parametrize(
        ("bad_command", "expected_error"),
        [
            (
                "read not-an-id",
                "'read not-an-id' names a command but its arguments are invalid\n",
            ),
            (
                "create hammer not-a-price 4",
                "'create hammer not-a-price 4' names a command but its arguments are invalid\n",
            ),
            (
                "update bad-id hammer 10 4",
                "'update bad-id hammer 10 4' names a command but its arguments are invalid\n",
            ),
        ],
    )
    def test_main_handles_invalid_arguments_and_continues(
        self,
        bad_command: str,
        expected_error: str,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        commands = iter([bad_command, "exit"])
        prompts: list[str] = []

        def fake_input(prompt: str = "") -> str:
            prompts.append(prompt)
            return next(commands)

        monkeypatch.setattr("builtins.input", fake_input)
        main()

        assert capsys.readouterr().out == expected_error
        assert prompts == [PROMPT, PROMPT]
