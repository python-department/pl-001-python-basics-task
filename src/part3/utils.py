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


# Number of fractional digits every stored price is rounded to.
# Quantisation step derived from PRICE_PRECISION, e.g. Decimal("0.01").
# TODO: задайте число знаков после запятой и шаг квантования (используйте своё
# решение части 2)
PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal("0.01")

# Column headers of the table produced by get_storage_str_representation,
# left to right. The width of each column is not fixed here -- it is
# measured per call from the data (see the function).
# TODO: задайте заголовки столбцов таблицы
TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quatity")


def normalize_price(price: Decimal) -> Decimal:
    """Round a price to the precision every stored record uses.

    Args:
        price: The raw price amount.

    Returns:
        ``price`` quantised to :data:`PRICE_PRECISION` fractional digits,
        with halves rounded up.
    """
    # TODO: реализуйте функцию (используйте своё решение части 2)
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


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
    # TODO: реализуйте функцию
    return " ".join(name.split()).lower()


# TODO: при необходимости добавьте свои вспомогательные функции


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
    # TODO: реализуйте функцию
    rows_data = []
    for product in storage:
        rows_data.append(
            (
                str(product[PRODUCT_ID_INDEX]),
                str(product[NAME_INDEX]),
                str(product[PRICE_INDEX]),
                str(product[QUANTITY_INDEX]),
            )
        )
    widths = [len(header) for header in TABLE_HEADERS]
    for row in rows_data:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    header_cells = [f"{header:<{widths[i]}}" for i, header in enumerate(TABLE_HEADERS)]
    header_line = "| " + " | ".join(header_cells) + " |"
    separator_cells = ["-" * (widths[i] + 2) for i in range(len(TABLE_HEADERS))]
    separator_line = "|" + "|".join(separator_cells) + "|"
    data_lines = []
    for row in rows_data:
        cells = [f"{cell:<{widths[i]}}" for i, cell in enumerate(row)]
        data_lines.append("| " + " | ".join(cells) + " |")
    result_lines = [header_line, separator_line] + data_lines
    return "\n".join(result_lines)
