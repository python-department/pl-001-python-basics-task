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

from .storage import Product


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)

# Column headers of the table produced by get_storage_str_representation,
# left to right. The width of each column is not fixed here -- it is
# measured per call from the data (see the function).
TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")

storage: list[tuple[int, str, Decimal, int]] = []


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return " ".join(name.split()).lower()


def get_storage_str_representation(storage: list[Product]) -> str:
    column_width = [len(header) for header in TABLE_HEADERS]
    for product in storage:
        for i, value in enumerate(product):
            column_width[i] = max(column_width[i], len(str(value)))
    header_row = (
        "|"
        + "|".join(
            f" {header.ljust(width)} "
            for header, width in zip(TABLE_HEADERS, column_width)
        )
        + "|"
    )
    delimiter_row = "|" + "|".join("-" * (width + 2) for width in column_width) + "|"

    table_rows = [header_row, delimiter_row]

    for product in storage:
        row = (
            "|"
            + "|".join(
                f" {str(value).ljust(width)} "
                for value, width in zip(product, column_width)
            )
            + "|"
        )
        table_rows.append(row)

    return "\n".join(table_rows)
