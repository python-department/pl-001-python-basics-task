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

from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .storage import (
    NAME_INDEX,
    PRICE_INDEX,
    PRODUCT_ID_INDEX,
    QUANTITY_INDEX,
    Product,
)


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)

TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    name = name.lower()
    list_name = name.split()
    list_name2 = [word.strip() for word in list_name if word.strip() != ""]
    if not len(list_name2):
        return ""
    return " ".join(list_name2)


def get_storage_str_representation(storage: list[Product]) -> str:
    rows = [
        [
            str(product[PRODUCT_ID_INDEX]),
            product[NAME_INDEX],
            str(product[PRICE_INDEX]),
            str(product[QUANTITY_INDEX]),
        ]
        for product in storage
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
