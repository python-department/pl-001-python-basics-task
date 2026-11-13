"""Standalone helpers shared by the part4 storage and CRUD modules.

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
    NAME_KEY,
    PRICE_KEY,
    QUANTITY_KEY,
    Product,
)


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)


TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    res = [word.lower() for word in name.split()]
    return " ".join(res)


def get_storage_str_representation(storage: dict[str, Product]) -> str:
    rows = [
        [
            str(product_id),
            product[NAME_KEY],
            str(product[PRICE_KEY]),
            str(product[QUANTITY_KEY]),
        ]
        for product_id, product in storage.items()
    ]
    widths = [
        max(len(TABLE_HEADERS[i]), *(len(row[i]) for row in rows))
        if rows
        else len(TABLE_HEADERS[i])
        for i in range(len(TABLE_HEADERS))
    ]

    header_line = (
        "| "
        + " | ".join(
            TABLE_HEADERS[i].ljust(widths[i]) for i in range(len(TABLE_HEADERS))
        )
        + " |"
    )
    sep_line = "|" + "|".join("-" * (w + 2) for w in widths) + "|"
    data_lines = [
        "| "
        + " | ".join(row[i].ljust(widths[i]) for i in range(len(TABLE_HEADERS)))
        + " |"
        for row in rows
    ]
    return "\n".join([header_line, sep_line, *data_lines])
