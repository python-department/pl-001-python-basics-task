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
ID_KEY: Final[str] = TABLE_HEADERS[0]


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    normalized_name = " ".join(name.split()).lower()
    return normalized_name


# TODO: при необходимости добавьте свои вспомогательные функции


def get_storage_str_representation(storage: dict[str, Product]) -> str:
    lens = {
        key: [len(h)]
        for key, h in zip((ID_KEY, NAME_KEY, PRICE_KEY, QUANTITY_KEY), TABLE_HEADERS)
    }

    for product_id, product in storage.items():
        lens[ID_KEY].append(len(product_id))
        for key in (NAME_KEY, PRICE_KEY, QUANTITY_KEY):
            lens[key].append(len(str(product[key])))

    maxlens = list(map(max, lens.values()))

    header_str = "|"
    separating_str = "|"
    for header, length in zip(TABLE_HEADERS, maxlens):
        header_str += f" {header.ljust(length)} |"
        separating_str += "-" + "-" * length + "-|"

    table = header_str + "\n" + separating_str

    for product_id, product in storage.items():
        table += "\n|"
        elems = (
            product_id,
            product[NAME_KEY],
            product[PRICE_KEY],
            product[QUANTITY_KEY],
        )
        for elem, length in zip(elems, maxlens):
            table += f" {str(elem).ljust(length)} |"

    return table
