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

from decimal import ROUND_HALF_UP, Decimal  # noqa: F401
from typing import Final

from .storage import (  # noqa: F401
    NAME_KEY,
    PRICE_KEY,
    QUANTITY_KEY,
    Product,
)


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal("0.01")


TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return " ".join(name.split()).lower()


def get_storage_str_representation(storage: dict[str, Product]) -> str:
   rows: list[tuple[str, str, str, str]] = []
   for product_id, product in storage.items():
    rows.append(
       (
          product_id,
          product[NAME_KEY],
          str(product[PRICE_KEY]),
          str(product[QUANTITY_KEY]),
       )
    )

    widths = [len(header) for header in TABLE_HEADERS]
    for row in rows:
       for i, value in enumerate(row):
          if len(value) > widths[i]:
             widths[i] = len(value)

    def format_row(row: tuple[str, str, str, str]) -> str:
       return " | ".join(value.ljust(widths[i]) for i, value in enumerate(row))

    separator = "-+-".join("-" * width for width in widths)
    lines = [format_row(TABLE_HEADERS), separator]
    lines.extend(format_row(row) for row in rows)
    return "\n".join(lines)
