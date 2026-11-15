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

TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", NAME_KEY, PRICE_KEY, QUANTITY_KEY)
STATS_TABLE_HEADERS: Final[tuple[str, ...]] = (
    "command name",
    "success",
    "fails",
    "success rate",
)


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return " ".join(name.lower().split())


def get_storage_str_representation(storage: dict[int, Product]) -> str:
    rows = [
        [
            str(product_id),
            product[NAME_KEY],
            str(product[PRICE_KEY]),
            str(product[QUANTITY_KEY]),
        ]
        for product_id, product in storage.items()
    ]

    widths: list[int] = []
    for column, header in enumerate(TABLE_HEADERS):
        width = len(header)
        for row in rows:
            width = max(width, len(row[column]))
        widths.append(width)

    def format_row(cells: list[str] | tuple[str, ...]) -> str:
        formatted_cells = [
            " " + cell.ljust(width) + " " for cell, width in zip(cells, widths)
        ]
        return "|" + "|".join(formatted_cells) + "|"

    header_line = format_row(TABLE_HEADERS)
    separator_line = "|" + "|".join("-" * (width + 2) for width in widths) + "|"

    lines = [header_line, separator_line]
    lines.extend(format_row(row) for row in rows)
    return "\n".join(lines)


def get_stats_str_representation(registry: Registry) -> str:

    def rate(ok: int, fail: int) -> str:
        total = ok + fail
        return f"{ok / total * 100:.2f}%" if total else "0.00%"

    rows = [
        [
            name,
            str(stats[SUCCESS_KEY]),
            str(stats[FAILS_KEY]),
            rate(stats[SUCCESS_KEY], stats[FAILS_KEY]),
        ]
        for name, stats in registry.items()
    ]

    widths: list[int] = []
    for column, header in enumerate(STATS_TABLE_HEADERS):
        width = len(header)
        for row in rows:
            width = max(width, len(row[column]))
        widths.append(width)

    def format_row(cells: list[str] | tuple[str, ...]) -> str:
        formatted_cells = [
            " " + cell.ljust(width) + " " for cell, width in zip(cells, widths)
        ]
        return "|" + "|".join(formatted_cells) + "|"

    header_line = format_row(STATS_TABLE_HEADERS)
    separator_line = "|" + "|".join("-" * (width + 2) for width in widths) + "|"

    lines = [header_line, separator_line]
    lines.extend(format_row(row) for row in rows)
    return "\n".join(lines)
