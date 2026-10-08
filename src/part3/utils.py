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
from re import sub
from typing import Final

from .storage import NAME_INDEX, PRICE_INDEX, PRODUCT_ID_INDEX, QUANTITY_INDEX, Product


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)

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
    return sub(r"\s+", " ", name.strip()).lower()


def format_row(values: list[str] | tuple[str, ...], widths: list[int]) -> str:
    cells = [values[i].ljust(widths[i]) for i in range(len(widths))]
    return "| " + " | ".join(cells) + " |"


def separator(widths: list[int]) -> str:
    return "|" + "|".join(["-" * (w + 2) for w in widths]) + "|"


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
    rows: list[list[str]] = []
    for product in storage:
        rows.append(
            [
                str(product[PRODUCT_ID_INDEX]),
                str(product[NAME_INDEX]),
                str(product[PRICE_INDEX]),
                str(product[QUANTITY_INDEX]),
            ]
        )

    widths = [len(h) for h in TABLE_HEADERS]
    for row in rows:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(value))

    lines = [format_row(TABLE_HEADERS, widths), separator(widths)]
    for row in rows:
        lines.append(format_row(row, widths))

    return "\n".join(lines)
