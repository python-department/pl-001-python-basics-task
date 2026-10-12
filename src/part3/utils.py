"""Standalone helpers shared by the part3 storage and CRUD modules.

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
"""

import re
from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .storage import Product


# Number of fractional digits every stored price is rounded to.
# Quantisation step derived from PRICE_PRECISION, e.g. Decimal("0.01").
# TODO: задайте число знаков после запятой и шаг квантования (используйте своё
# решение части 2)
PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)
_WHITESPACE_RUN: Final = re.compile(r"\s+")
_CELL_PADDING: Final = 2

# Column headers of the table produced by get_storage_str_representation,
# left to right. The width of each column is not fixed here -- it is
# measured per call from the data (see the function).
# TODO: задайте заголовки столбцов таблицы
TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return _WHITESPACE_RUN.sub(" ", name.strip()).lower()


def _measure_widths(rows: list[tuple[str, ...]]) -> list[int]:
    return [
        max(len(header), *(len(row[i]) for row in rows))
        for i, header in enumerate(TABLE_HEADERS)
    ]


def _render_row(cells: tuple[str, ...], widths: list[int]) -> str:
    padded = (cell.ljust(width) for cell, width in zip(cells, widths))
    return "| " + " | ".join(padded) + " |"


def _render_separator(widths: list[int]) -> str:
    runs = ("-" * (width + _CELL_PADDING) for width in widths)
    return "|" + "|".join(runs) + "|"


def get_storage_str_representation(storage: list[Product]) -> str:
    rows = [tuple(str(value) for value in product) for product in storage]
    widths = _measure_widths(rows)

    lines = [_render_row(TABLE_HEADERS, widths), _render_separator(widths)]
    lines.extend(_render_row(row, widths) for row in rows)
    return "\n".join(lines)
