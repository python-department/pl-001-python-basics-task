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

import re
from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .storage import (
    NAME_INDEX,
    PRICE_INDEX,
    PRODUCT_ID_INDEX,
    QUANTITY_INDEX,
    Product,
)


# Number of fractional digits every stored price is rounded to.
# Quantisation step derived from PRICE_PRECISION, e.g. Decimal("0.01").
PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)

# Column headers of the table produced by get_storage_str_representation,
# left to right. The width of each column is not fixed here -- it is
# measured per call from the data (see the function).
TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    """Round a price to the precision every stored record uses.

    Args:
        price: The raw price amount.

    Returns:
        ``price`` quantised to :data:`PRICE_PRECISION` fractional digits,
        with halves rounded up.
    """
    return price.quantize(PRICE_STEP, ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    """Reduce a product name to the canonical form the store keeps.

    Args:
        name: The raw product name.

    Returns:
        ``name`` with every leading and trailing whitespace character
        removed, every internal run of whitespace (spaces, tabs and the
        like) collapsed to a single space, and the rest lower-cased. For
        example ``"abc    def\tghi\tjkl"`` becomes ``"abc def ghi jkl"``.
        The result is an empty string when ``name`` holds nothing but
        whitespace.
    """

    return re.sub(r"\s+", " ", name.strip().lower())


def get_row_str_representation(
    values: list[list[str]], row_index: int, lengths_columns: list[int]
) -> str:
    """Render the row of table by index.

    Args:
        values (list[list[Product]]): values
        row_index (int): index of row
        lengths_columns (list[int]): list of lengths of columns

    Returns:
        str: string of the row of table by index
    """
    return (
        f"| {f'{values[PRODUCT_ID_INDEX][row_index]}':<{lengths_columns[PRODUCT_ID_INDEX]}} |"
        + f" {f'{values[NAME_INDEX][row_index]}':<{lengths_columns[NAME_INDEX]}} |"
        + f" {f'{values[PRICE_INDEX][row_index]}':<{lengths_columns[PRICE_INDEX]}} |"
        + f" {f'{values[QUANTITY_INDEX][row_index]}':<{lengths_columns[QUANTITY_INDEX]}} |"
        + "\n"
    )


def get_horizonal_line_str(lengths_columns: list[int]) -> str:
    """Render the dashed separator row.

    Args:
        lengths_columns (list[int]): list of lengths of columns

    Returns:
        str: string of the dashed separator row
    """

    return (
        f"|{'-' * (lengths_columns[PRODUCT_ID_INDEX] + 2)}|"
        + f"{'-' * (lengths_columns[NAME_INDEX] + 2)}|"
        + f"{'-' * (lengths_columns[PRICE_INDEX] + 2)}|"
        + f"{'-' * (lengths_columns[QUANTITY_INDEX] + 2)}|"
        + "\n"
    )


def get_storage_str_representation(storage: list[Product]) -> str:
    """Render the product store as a text table with data-sized columns.

    The table has the columns named by :data:`TABLE_HEADERS` -- id, name,
    price and quantity. Each column is made exactly as wide as the longest
    value it carries in this call (its header counted), so the columns
    line up when the string is printed to a terminal and no value is ever
    truncated.

    Args:
        storage: The product store to render.

    Returns:
        A multi-line string: a header row, a dashed separator row, then
        one row per product in ``storage`` in list order. When ``storage``
        is empty only the header and separator rows are returned, sized to
        the header labels.
    """
    values_columns: list[list[str]] = [
        [TABLE_HEADERS[PRODUCT_ID_INDEX]],
        [TABLE_HEADERS[NAME_INDEX]],
        [TABLE_HEADERS[PRICE_INDEX]],
        [TABLE_HEADERS[QUANTITY_INDEX]],
    ]
    for product in storage:
        values_columns[PRODUCT_ID_INDEX].append(str(product[PRODUCT_ID_INDEX]))
        values_columns[NAME_INDEX].append(product[NAME_INDEX])
        values_columns[PRICE_INDEX].append(str(product[PRICE_INDEX]))
        values_columns[QUANTITY_INDEX].append(str(product[QUANTITY_INDEX]))

    lengths_colums: list[int] = [
        len(max(values_columns[PRODUCT_ID_INDEX], key=len)),
        len(max(values_columns[NAME_INDEX], key=len)),
        len(max(values_columns[PRICE_INDEX], key=len)),
        len(max(values_columns[QUANTITY_INDEX], key=len)),
    ]

    output_string: str = get_row_str_representation(
        values_columns, 0, lengths_colums
    ) + get_horizonal_line_str(lengths_colums)
    for i in range(1, len(values_columns[0])):
        output_string += get_row_str_representation(values_columns, i, lengths_colums)

    return output_string.removesuffix("\n")
