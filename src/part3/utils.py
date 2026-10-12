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
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return " ".join(name.split()).lower()


def number_length(value: Decimal | float) -> int:
    return len(str(value))


def get_storage_str_representation(storage: list[Product]) -> str:
    coloumns_lengths_sets: list[set[int]] = [set(), set(), set(), set()]
    coloumns_lengths_numbers: list[int] = [0, 0, 0, 0]

    for index in range(len(TABLE_HEADERS)):
        coloumns_lengths_sets[index].add(len(TABLE_HEADERS[index]))

    if storage:
        for product in storage:
            coloumns_lengths_sets[PRODUCT_ID_INDEX].add(
                number_length(product[PRODUCT_ID_INDEX])
            )
            coloumns_lengths_sets[NAME_INDEX].add(len(product[NAME_INDEX]))
            coloumns_lengths_sets[PRICE_INDEX].add(number_length(product[PRICE_INDEX]))
            coloumns_lengths_sets[QUANTITY_INDEX].add(
                number_length(product[QUANTITY_INDEX])
            )

    for coloumn_index in range(len(coloumns_lengths_numbers)):
        coloumns_lengths_numbers[coloumn_index] = max(
            coloumns_lengths_sets[coloumn_index]
        )

    header_parts = [
        TABLE_HEADERS[index].ljust(coloumns_lengths_numbers[index])
        for index in range(len(TABLE_HEADERS))
    ]
    header_line = f"| {' | '.join(header_parts)} |"

    separating_parts = ["-" * (length + 2) for length in coloumns_lengths_numbers]
    separating_line = f"|{'|'.join(separating_parts)}|"

    table = [header_line, separating_line]

    if not storage:
        return "\n".join(table)

    for product in storage:
        line = f"| {' | '.join([str(product[index]).ljust(coloumns_lengths_numbers[index]) for index in range(len(product))])} |"
        table.append(line)

    return "\n".join(table)
