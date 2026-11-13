from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .decorators import (
    FAILS_KEY,
    SUCCESS_KEY,
    Registry,
)
from .storage import (
    NAME_KEY,
    PRICE_KEY,
    QUANTITY_KEY,
    Product,
)


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final[Decimal] = Decimal(1).scaleb(-PRICE_PRECISION)

TABLE_HEADERS: Final[tuple[str, str, str, str]] = (
    "ID",
    "name",
    "price",
    "quantity",
)
STATS_TABLE_HEADERS: Final[tuple[str, ...]] = (
    "command name",
    "success",
    "fails",
    "success rate",
)


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return " ".join(name.split()).lower()


def get_storage_str_representation(storage: dict[int, Product]) -> str:
    rows: list[list[str]] = [list(TABLE_HEADERS)]

    for product_id, product in storage.items():
        rows.append(
            [
                str(product_id),
                product[NAME_KEY],
                str(product[PRICE_KEY]),
                str(product[QUANTITY_KEY]),
            ]
        )

    col_widths = [max(len(row[i]) for row in rows) for i in range(len(TABLE_HEADERS))]

    formatted_rows = []
    for row in rows:
        padded_cells = [
            f" {row[i].ljust(col_widths[i])} " for i in range(len(TABLE_HEADERS))
        ]
        formatted_rows.append(f"|{'|'.join(padded_cells)}|")

    dash_cells = ["-" * (w + 2) for w in col_widths]
    separator_line = f"|{'|'.join(dash_cells)}|"
    formatted_rows.insert(1, separator_line)

    return "\n".join(formatted_rows)


def get_stats_str_representation(registry: Registry) -> str:
    rows: list[list[str]] = [list(STATS_TABLE_HEADERS)]

    for command_name, stats in registry.items():
        success = stats[SUCCESS_KEY]
        fails = stats[FAILS_KEY]
        total = success + fails
        rate = (success / total * 100) if total > 0 else 0.0

        rows.append(
            [
                command_name,
                str(success),
                str(fails),
                f"{rate:.2f}%",
            ]
        )

    col_widths = [
        max(len(row[i]) for row in rows) for i in range(len(STATS_TABLE_HEADERS))
    ]

    formatted_rows = []
    for row in rows:
        padded_cells = [
            f" {row[i].ljust(col_widths[i])} " for i in range(len(STATS_TABLE_HEADERS))
        ]
        formatted_rows.append(f"|{'|'.join(padded_cells)}|")

    dash_cells = ["-" * (w + 2) for w in col_widths]
    separator_line = f"|{'|'.join(dash_cells)}|"
    formatted_rows.insert(1, separator_line)

    return "\n".join(formatted_rows)
