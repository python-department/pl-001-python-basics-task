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
# решение части 3)
PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)

# Column headers of the table produced by get_storage_str_representation,
# left to right. The width of each column is not fixed here -- it is
# measured per call from the data (see the function).
# TODO: задайте заголовки столбцов таблицы (используйте своё решение части 3)
TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=(ROUND_HALF_UP))


def normalize_product_name(name: str) -> str:
    return " ".join(name.split()).lower()


# TODO: при необходимости добавьте свои вспомогательные функции


def get_storage_str_representation(storage: dict[str, Product]) -> str:
    def product_to_row(product_id: str, product: Product) -> tuple[str, ...]:
        return (
            str(product_id),
            str(product[NAME_KEY]),
            str(product[PRICE_KEY]),
            str(product[QUANTITY_KEY]),
        )

    rows = [TABLE_HEADERS] + [product_to_row(cid, c) for cid, c in storage.items()]
    widths = [max(len(row[i]) for row in rows) for i in range(len(TABLE_HEADERS))]

    def format_row(row: tuple[str, ...]) -> str:
        return "| " + " | ".join(v.ljust(w) for v, w in zip(row, widths)) + " |"

    separator = "|-" + "-|-".join("-" * w for w in widths) + "-|"

    lines = [format_row(rows[0]), separator]
    lines.extend(format_row(r) for r in rows[1:])
    return "\n".join(lines)
