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
    true_price = price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)

    return true_price


def normalize_product_name(name: str) -> str:
    new_name = " ".join(name.split()).lower()

    return new_name


def get_storage_str_representation(storage: list[Product]) -> str:
    mx_len_id = len(TABLE_HEADERS[0]) + 2
    mx_len_name = len(TABLE_HEADERS[1]) + 2
    mx_len_price = len(TABLE_HEADERS[2]) + 2
    mx_len_quantity = len(TABLE_HEADERS[3]) + 2
    for item in storage:
        mx_len_id = max(mx_len_id, len(str(item[PRODUCT_ID_INDEX])) + 2)
        mx_len_name = max(mx_len_name, len(item[NAME_INDEX]) + 2)
        mx_len_price = max(mx_len_price, len(str(item[PRICE_INDEX])) + 2)
        mx_len_quantity = max(mx_len_quantity, len(str(item[QUANTITY_INDEX])) + 2)

    s = (
        f"| {TABLE_HEADERS[0]}{' ' * (mx_len_id - 3)}| {TABLE_HEADERS[1]}{' ' * (mx_len_name - 5)}| {TABLE_HEADERS[2]}{' ' * (mx_len_price - 6)}| {TABLE_HEADERS[3]}{' ' * (mx_len_quantity - 9)}|\n"
        f"|{'-' * mx_len_id}|{'-' * mx_len_name}|{'-' * mx_len_price}|{'-' * mx_len_quantity}|"
    )

    for item in storage:
        s_new = (
            f"\n| {item[PRODUCT_ID_INDEX]}{' ' * (mx_len_id - len(str(item[PRODUCT_ID_INDEX])) - 1)}"
            f"| {item[NAME_INDEX]}{' ' * (mx_len_name - len(str(item[NAME_INDEX])) - 1)}"
            f"| {item[PRICE_INDEX]}{' ' * (mx_len_price - len(str(item[PRICE_INDEX])) - 1)}"
            f"| {item[QUANTITY_INDEX]}{' ' * (mx_len_quantity - len(str(item[QUANTITY_INDEX])) - 1)}|"
        )
        s += s_new
    return s
