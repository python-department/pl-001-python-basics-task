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


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return " ".join(name.split()).lower()


def get_storage_str_representation(storage: list[Product]) -> str:
    column_width = [len(header) for header in TABLE_HEADERS]
    for product in storage:
        column_width[0] = max(column_width[0], len(str(product[0])))
        column_width[1] = max(column_width[1], len(str(product[1])))
        column_width[2] = max(column_width[2], len(str(product[2])))
        column_width[3] = max(column_width[3], len(str(product[3])))

    id, name, price, quantity = TABLE_HEADERS
    header_row_mas = [
        f" {id.ljust(column_width[0])} ",
        f" {name.ljust(column_width[1])} ",
        f" {price.ljust(column_width[2])} ",
        f" {quantity.ljust(column_width[3])} ",
    ]
    header_row = f"|{'|'.join(header_row_mas)}|"

    delimiter_row_mas = [
        "".ljust(column_width[0] + 2, "-"),
        "".ljust(column_width[1] + 2, "-"),
        "".ljust(column_width[2] + 2, "-"),
        "".ljust(column_width[3] + 2, "-"),
    ]
    delimiter_row = f"|{'|'.join(delimiter_row_mas)}|"

    table_rows = [header_row, delimiter_row]
    for product in storage:
        id, name, price, quantity = map(str, product)
        row_mas = [
            f" {id.ljust(column_width[0])} ",
            f" {name.ljust(column_width[1])} ",
            f" {price.ljust(column_width[2])} ",
            f" {quantity.ljust(column_width[3])} ",
        ]
        row = f"|{'|'.join(row_mas)}|"
        table_rows.append(row)
    return "\n".join(table_rows)


storage: list[tuple[int, str, Decimal, int]] = []
