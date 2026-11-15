"""Standalone helpers shared by the part5 storage and CRUD modules.

Normalisation:

* :func:`normalize_price` rounds a raw :class:`~decimal.Decimal` amount to
  the fixed number of fractional digits (:data:`PRICE_PRECISION`) that
  every stored price uses, keeping currency values free of binary
  floating-point error.
* :func:`normalize_product_name` strips surrounding whitespace from a
  product name, collapses every internal run of whitespace to a single
  space and lower-cases it, giving every stored name a single canonical
  form.

Presentation:

* :func:`get_storage_str_representation` renders the whole store as a
  text table meant to be printed to a terminal; each column is sized to
  the longest value it holds in that particular call.
* :func:`get_stats_str_representation` renders the call statistics gathered
  by :func:`~src.part5.decorators.collect_stats` as a table of the same
  look, with the success rate of every command as a percentage.
"""

from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .decorators import FAILS_KEY, SUCCESS_KEY, Registry
from .storage import (
    NAME_KEY,
    PRICE_KEY,
    QUANTITY_KEY,
    Product,
)


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)


TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")

STATS_TABLE_HEADERS: Final[tuple[str, ...]] = (
    "command name",
    "success",
    "fails",
    "success rate",
)


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=(ROUND_HALF_UP))


def normalize_product_name(name: str) -> str:
    return " ".join(name.split()).lower()


def _format_table(
    headers: tuple[str, ...],
    rows: list[tuple[str, ...]],
) -> str:
    all_rows = [headers] + rows
    widths = [max(len(row[i]) for row in all_rows) for i in range(len(headers))]

    def format_row(row: tuple[str, ...]) -> str:
        return (
            "| "
            + " | ".join(value.ljust(width) for value, width in zip(row, widths))
            + " |"
        )

    separator = "|-" + "-|-".join("-" * width for width in widths) + "-|"

    lines = [format_row(headers), separator]
    lines.extend(format_row(row) for row in rows)
    return "\n".join(lines)


def get_storage_str_representation(storage: dict[int, Product]) -> str:
    rows: list[tuple[str, ...]] = [
        (
            str(product_id),
            str(product[NAME_KEY]),
            str(product[PRICE_KEY]),
            str(product[QUANTITY_KEY]),
        )
        for product_id, product in storage.items()
    ]
    return _format_table(TABLE_HEADERS, rows)


def get_stats_str_representation(registry: Registry) -> str:
    rows: list[tuple[str, ...]] = []

    for command_name, stats in registry.items():
        success = stats[SUCCESS_KEY]
        fails = stats[FAILS_KEY]
        total = success + fails

        if total == 0:
            rate = Decimal("0.00")
        else:
            rate = (Decimal(success) / Decimal(total) * 100).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

        rows.append(
            (
                command_name,
                str(success),
                str(fails),
                f"{rate}%",
            )
        )

    return _format_table(STATS_TABLE_HEADERS, rows)
