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
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    res = [word.lower() for word in name.split()]
    return " ".join(res)


def _render_table(headers: tuple[str, ...], rows: list[list[str]]) -> str:
    widths = [
        max(len(headers[i]), *(len(row[i]) for row in rows))
        if rows
        else len(headers[i])
        for i in range(len(headers))
    ]
    header_line = (
        "| "
        + " | ".join(headers[i].ljust(widths[i]) for i in range(len(headers)))
        + " |"
    )
    sep_line = "|" + "|".join("-" * (w + 2) for w in widths) + "|"
    data_lines = [
        "| " + " | ".join(row[i].ljust(widths[i]) for i in range(len(headers))) + " |"
        for row in rows
    ]
    return "\n".join([header_line, sep_line, *data_lines])


def get_storage_str_representation(storage: dict[int, Product]) -> str:
    rows = [
        [str(pid), p[NAME_KEY], str(p[PRICE_KEY]), str(p[QUANTITY_KEY])]
        for pid, p in storage.items()
    ]
    return _render_table(TABLE_HEADERS, rows)


def get_stats_str_representation(registry: Registry) -> str:
    rows = []
    for command, stats in registry.items():
        success = stats[SUCCESS_KEY]
        fails = stats[FAILS_KEY]
        total = success + fails
        rate = f"{success / total * 100:.2f}%" if total else "0.00%"
        rows.append([command, str(success), str(fails), rate])
    return _render_table(STATS_TABLE_HEADERS, rows)
