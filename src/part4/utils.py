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


# Number of fractional digits every stored price is rounded to.
# Quantisation step derived from PRICE_PRECISION, e.g. Decimal("0.01").
# TODO: задайте число знаков после запятой и шаг квантования (используйте своё
# решение части 3)
PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)

# Column headers of the table produced by get_storage_str_representation,
# left to right. The width of each column is not fixed here -- it is
# measured per call from the data (see the function).
# TODO: задайте заголовки столбцов таблицы (используйте своё решение части 3)
TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    true_price = price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)

    return true_price



def normalize_product_name(name: str) -> str:
    new_name = " ".join(name.split()).lower()

    return new_name



def get_storage_str_representation(storage: dict[str, Product]) -> str:
    mx_len_id = len(TABLE_HEADERS[0])
    mx_len_name = len(TABLE_HEADERS[1])
    mx_len_price = len(TABLE_HEADERS[2])
    mx_len_quantity = len(TABLE_HEADERS[3])

    for key, prod in storage.items():
        mx_len_id = max(mx_len_id, len(key))
        mx_len_name = max(mx_len_name, len(prod[NAME_KEY]))
        mx_len_price = max(mx_len_price, len(str(prod[PRICE_KEY])))
        mx_len_quantity = max(mx_len_quantity, len(str(prod[QUANTITY_KEY])))

    s = (
        f"| {TABLE_HEADERS[0]:<{mx_len_id}} "
        f"| {TABLE_HEADERS[1]:<{mx_len_name}} "
        f"| {TABLE_HEADERS[2]:<{mx_len_price}} "
        f"| {TABLE_HEADERS[3]:<{mx_len_quantity}} |\n"
        f"|{'-' * (mx_len_id + 2)}"
        f"|{'-' * (mx_len_name + 2)}"
        f"|{'-' * (mx_len_price + 2)}"
        f"|{'-' * (mx_len_quantity + 2)}|"
    )

    for key, prod in storage.items():
        s_new = (
            f"\n| {key:<{mx_len_id}} "
            f"| {prod[NAME_KEY]:<{mx_len_name}} "
            f"| {str(prod[PRICE_KEY]):<{mx_len_price}} "
            f"| {str(prod[QUANTITY_KEY]):<{mx_len_quantity}} |"
        )
        s += s_new
    return s
