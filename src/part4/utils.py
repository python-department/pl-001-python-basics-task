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


# Number of fractional digits every stored price is rounded to.
# Quantisation step derived from PRICE_PRECISION, e.g. Decimal("0.01").
# TODO: задайте число знаков после запятой и шаг квантования (используйте своё
# решение части 2)
PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)

# Column headers of the table produced by get_storage_str_representation,
# left to right. The width of each column is not fixed here -- it is
# measured per call from the data (see the function).
# TODO: задайте заголовки столбцов таблицы
TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    correct_price = price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)

    return correct_price


def normalize_product_name(name: str) -> str:
    correct_name = [word.lower() for word in name.split()]

    return " ".join(correct_name)


# TODO: при необходимости добавьте свои вспомогательные функции


def get_storage_str_representation(storage: dict[str, Product]) -> str:
    len_headers = [
        len(TABLE_HEADERS[0]),
        len(TABLE_HEADERS[1]),
        len(TABLE_HEADERS[2]),
        len(TABLE_HEADERS[3]),
    ]

    for product_id, product_info in storage.items():
        len_id = len(str(product_id))
        len_name = len(str(product_info[NAME_KEY]))
        len_price = len(str(product_info[PRICE_KEY]))
        len_quantity = len(str(product_info[QUANTITY_KEY]))

        len_headers = [
            max(len_headers[0], len_id),
            max(len_headers[1], len_name),
            max(len_headers[2], len_price),
            max(len_headers[3], len_quantity),
        ]

    s = (
        f"| ID {' ' * (len_headers[0] - 2)}| name {' ' * (len_headers[1] - 4)}| price {' ' * (len_headers[2] - 5)}| quantity {' ' * (len_headers[3] - 8)}|\n"
        f"|{'-' * (len_headers[0] + 2)}|{'-' * (len_headers[1] + 2)}|{'-' * (len_headers[2] + 2)}|{'-' * (len_headers[3] + 2)}|"
    )

    for product_id, product_info in storage.items():
        s += "\n"

        len_id = len(str(product_id))
        len_name = len(str(product_info[NAME_KEY]))
        len_price = len(str(product_info[PRICE_KEY]))
        len_quantity = len(str(product_info[QUANTITY_KEY]))

        s += f"| {product_id} {' ' * (len_headers[0] - len_id)}| {product_info[NAME_KEY]} {' ' * (len_headers[1] - len_name)}| {product_info[PRICE_KEY]} {' ' * (len_headers[2] - len_price)}| {product_info[QUANTITY_KEY]} {' ' * (len_headers[3] - len_quantity)}|"

    return s
