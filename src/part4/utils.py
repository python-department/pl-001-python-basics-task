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
from typing import Any, Final

from .storage import (
    ID_KEY,
    NAME_KEY,
    PRICE_KEY,
    QUANTITY_KEY,
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
    name_words = name.split()
    normalized_name = " ".join(name_words).lower()

    return normalized_name


def get_max_column_length(storage: dict[str, Product], key: str) -> int:
    """Measure the widest table cell a record can hold for one field.

    Args:
        storage: The product store to measure.
        key: The name of the record field to measure.

    Returns:
        The character length of the longest of the column header ``key``
        and ``str`` of every value stored under ``key`` in ``storage``, so
        the result is never shorter than the header itself.
    """
    values = [len(key)]
    for record in storage.values():
        values.append(len(str(record[key])))

    return max(values)


def get_line_separator(column_lengths: dict[str, int]) -> str:
    """Build the dashed separator row of the store table.

    Args:
        column_lengths: The table column names and their widths.

    Returns:
        A string of the form ``|----|------|`` where each dash run is
        exactly two characters (the surrounding padding spaces) wider
        than the column it belongs to.
    """
    dashes = [f"{'-' * (length + 2)}" for length in column_lengths.values()]

    return f"|{'|'.join(dashes)}|"


def format_row(cells: dict[str, Any], column_lengths: dict[str, int]) -> str:
    """Render one store-table row with each cell padded to its column width.

    Args:
        cells: The row cells keyed by column name, in the exact column
            order the row must be printed in.
        column_lengths: The table column names and their widths.

    Returns:
        The row as a string: every cell is left-justified and padded to
        its column width, wrapped in a single space and separated by
        ``|``, with ``|`` at both ends of the row.
    """
    return f"|{'|'.join(f' {cell!s:<{column_lengths[header]}} ' for header, cell in cells.items())}|"


def get_storage_str_representation(storage: dict[str, Product]) -> str:
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
        one row per product in ``storage``, in insertion order. When
        ``storage`` is empty only the header and separator rows are
        returned, sized to the header labels.
    """
    column_lengths = {
        ID_KEY: max([len(ID_KEY)] + [len(product_id) for product_id in storage]),
        NAME_KEY: get_max_column_length(storage, NAME_KEY),
        PRICE_KEY: get_max_column_length(storage, PRICE_KEY),
        QUANTITY_KEY: get_max_column_length(storage, QUANTITY_KEY),
    }
    lines = [
        format_row({header: header for header in TABLE_HEADERS}, column_lengths),
        get_line_separator(column_lengths),
    ]

    for product_id, record in storage.items():
        lines.append(
            format_row(
                {
                    ID_KEY: product_id,
                    NAME_KEY: record[NAME_KEY],
                    PRICE_KEY: record[PRICE_KEY],
                    QUANTITY_KEY: record[QUANTITY_KEY],
                },
                column_lengths,
            )
        )

    return "\n".join(lines)
