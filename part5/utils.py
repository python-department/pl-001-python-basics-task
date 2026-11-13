from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .decorators import Registry
from .storage import (
    NAME_KEY,
    PRICE_KEY,
    QUANTITY_KEY,
    Product,
)


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final[Decimal] = Decimal(1).scaleb(-PRICE_PRECISION)
TABLE_HEADERS: Final[tuple[str, str, str, str]] = ("ID", "name", "price", "quantity")
STATS_TABLE_HEADERS: Final[tuple[str, str, str, str]] = (
    "command name",
    "success",
    "fails",
    "success rate",
)


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return " ".join(name.split()).lower()


def _compute_column_widths(
    headers: tuple[str, ...], rows: list[list[str]]
) -> list[int]:
    widths = [len(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))
    return widths


def _format_row(cells: list[str], widths: list[int]) -> str:
    return (
        "| "
        + " | ".join(cell.ljust(widths[index]) for index, cell in enumerate(cells))
        + " |"
    )


def _format_table(headers: tuple[str, ...], rows: list[list[str]]) -> str:
    widths = _compute_column_widths(headers, rows)
    header_line = _format_row(list(headers), widths)
    separator_line = "|" + "|".join("-" * (width + 2) for width in widths) + "|"
    row_lines = [_format_row(row, widths) for row in rows]
    return "\n".join([header_line, separator_line, *row_lines])


def _format_success_rate(success: int, fails: int) -> str:
    total = success + fails
    rate = (success / total * 100) if total else 0.0
    return f"{rate:.2f}%"


def get_storage_str_representation(storage: dict[int, Product]) -> str:
    return _format_table(
        TABLE_HEADERS,
        [
            [
                str(product_id),
                product[NAME_KEY],
                str(product[PRICE_KEY]),
                str(product[QUANTITY_KEY]),
            ]
            for product_id, product in storage.items()
        ],
    )


def get_stats_str_representation(registry: Registry) -> str:
    return _format_table(
        STATS_TABLE_HEADERS,
        [
            [
                command_name,
                str(stats["success"]),
                str(stats["fails"]),
                _format_success_rate(stats["success"], stats["fails"]),
            ]
            for command_name, stats in registry.items()
        ],
    )
