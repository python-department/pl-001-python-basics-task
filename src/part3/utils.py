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
    return price.quantize(PRICE_STEP, rounding=(ROUND_HALF_UP))


def normalize_product_name(name: str) -> str:
    return " ".join(name.split()).lower()


def get_storage_str_representation(storage: list[Product]) -> str:
    def product_to_row(point: Product) -> tuple[str, ...]:
        return (
            str(point[PRODUCT_ID_INDEX]),
            point[NAME_INDEX],
            str(point[PRICE_INDEX]),
            str(point[QUANTITY_INDEX]),
        )

    rows = [TABLE_HEADERS] + [product_to_row(p) for p in storage]

    widths = [max(len(row[i]) for row in rows) for i in range(len(TABLE_HEADERS))]

    def format_row(row: tuple[str, ...]) -> str:
        return "| " + " | ".join(v.ljust(w) for v, w in zip(row, widths)) + " |"

    separator = "|-" + "-|-".join("-" * w for w in widths) + "-|"

    lines = [format_row(rows[0]), separator]
    lines.extend(format_row(r) for r in rows[1:])
    return "\n".join(lines)
