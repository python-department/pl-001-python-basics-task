from decimal import Decimal

from src.part5.storage import Product
from src.part5.utils import (
    PRICE_PRECISION,
    PRICE_STEP,
    STATS_TABLE_HEADERS,
    TABLE_HEADERS,
    get_stats_str_representation,
    get_storage_str_representation,
    normalize_price,
    normalize_product_name,
)


def test_constants() -> None:
    assert PRICE_PRECISION == 2
    assert PRICE_STEP == Decimal("0.01")
    assert TABLE_HEADERS == ("ID", "name", "price", "quantity")
    assert STATS_TABLE_HEADERS == (
        "command name",
        "success",
        "fails",
        "success rate",
    )


def test_normalize_price() -> None:
    assert normalize_price(Decimal("9.9")) == Decimal("9.90")
    assert str(normalize_price(Decimal(10))) == "10.00"
    assert normalize_price(Decimal("0.005")) == Decimal("0.01")
    assert normalize_price(Decimal("0.004")) == Decimal("0.00")
    assert normalize_price(Decimal("2.675")) == Decimal("2.68")


def test_normalize_product_name() -> None:
    assert normalize_product_name("  Cordless Drill  ") == "cordless drill"
    assert normalize_product_name("abc    def\tghi\tjkl") == "abc def ghi jkl"
    assert normalize_product_name(" \t\n ") == ""
    assert normalize_product_name("") == ""


def test_storage_table_empty() -> None:
    assert get_storage_str_representation({}) == (
        "| ID | name | price | quantity |\n|----|------|-------|----------|"
    )


def test_storage_table_with_products() -> None:
    storage: dict[int, Product] = {
        1: {"name": "saw", "price": Decimal("9.90"), "quantity": 5},
        22: {"name": "cordless drill", "price": Decimal("120.00"), "quantity": 8},
    }

    assert get_storage_str_representation(storage) == (
        "| ID | name           | price  | quantity |\n"
        "|----|----------------|--------|----------|\n"
        "| 1  | saw            | 9.90   | 5        |\n"
        "| 22 | cordless drill | 120.00 | 8        |"
    )


def test_storage_table_snowflake_ids() -> None:
    storage: dict[int, Product] = {
        1288834974657000001: {"name": "a", "price": Decimal("1.00"), "quantity": 1}
    }

    assert get_storage_str_representation(storage) == (
        "| ID                  | name | price | quantity |\n"
        "|---------------------|------|-------|----------|\n"
        "| 1288834974657000001 | a    | 1.00  | 1        |"
    )


def test_stats_table_empty() -> None:
    assert get_stats_str_representation({}) == (
        "| command name | success | fails | success rate |\n"
        "|--------------|---------|-------|--------------|"
    )


def test_stats_table_rows() -> None:
    registry = {
        "create": {"success": 2, "fails": 1},
        "read": {"success": 0, "fails": 0},
        "delete": {"success": 5, "fails": 0},
    }

    assert get_stats_str_representation(registry) == (
        "| command name | success | fails | success rate |\n"
        "|--------------|---------|-------|--------------|\n"
        "| create       | 2       | 1     | 66.67%       |\n"
        "| read         | 0       | 0     | 0.00%        |\n"
        "| delete       | 5       | 0     | 100.00%      |"
    )


def test_stats_table_long_name_widens_column() -> None:
    registry = {"update-everything-twice": {"success": 1, "fails": 30}}

    assert get_stats_str_representation(registry) == (
        "| command name            | success | fails | success rate |\n"
        "|-------------------------|---------|-------|--------------|\n"
        "| update-everything-twice | 1       | 30    | 3.23%        |"
    )


def test_stats_table_wide_numbers_widen_columns() -> None:
    registry = {"a": {"success": 1234567, "fails": 7654321}}

    assert get_stats_str_representation(registry) == (
        "| command name | success | fails   | success rate |\n"
        "|--------------|---------|---------|--------------|\n"
        "| a            | 1234567 | 7654321 | 13.89%       |"
    )


def test_stats_table_only_fails_and_rounding() -> None:
    registry = {
        "x": {"success": 0, "fails": 4},
        "y": {"success": 1, "fails": 2},
    }
    lines = get_stats_str_representation(registry).split("\n")

    assert lines[2].endswith("| 0.00%        |")
    assert lines[3].endswith("| 33.33%       |")
