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


def get_separator_str(storage_lengths: tuple[int, ...]) -> str:
    separator = "|"
    for length in storage_lengths:
        separator += "-" + "-" * length + "-|"
    separator += "\n"
    return separator


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
    storage_lengths = []
    for i in range(len(TABLE_HEADERS)):
        max_value_length = 0
        for elem in storage:
            max_value_length = max(len(str(elem[i])), max_value_length)
        storage_lengths.append(max(len(str(TABLE_HEADERS[i])), max_value_length))

    table = ""

    table += "|"
    for i in range(len(TABLE_HEADERS)):
        table += " "
        table += str(TABLE_HEADERS[i]) + " " * (
            storage_lengths[i] - len(str(TABLE_HEADERS[i]))
        )
        table += " |"
    table += "\n"

    table += get_separator_str(tuple(storage_lengths))

    for product in storage:
        row = "|"
        for i in range(len(TABLE_HEADERS)):
            row += (
                " "
                + str(product[i])
                + " " * (storage_lengths[i] - len(str(product[i])))
                + " |"
            )
        table += row + "\n"

    table = table[:-1]

    return table
