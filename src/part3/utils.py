"""Standalone helpers shared by the part2 storage and CRUD modules.

For now this is limited to money handling: :func:`normalize_price` rounds a
raw :class:`~decimal.Decimal` amount to the fixed number of fractional
digits (:data:`PRICE_PRECISION`) that every stored price uses, keeping
currency values free of binary floating-point error.
"""

from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .storage import Product


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
    return " ".join(name.split()).lower()


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

    widths = []
    for column, header in enumerate(TABLE_HEADERS):
        lengths = [len(str(product[column])) for product in storage]
        widths.append(max([len(header), *lengths]))

    rows: list[tuple[str, ...]] = [TABLE_HEADERS]
    for product in storage:
        rows.append(tuple(str(field) for field in product))

    result = []

    line = "|"
    for i in range(len(rows[0])):
        line += " " + rows[0][i].ljust(widths[i]) + " |"
    result.append(line)

    line = "|"
    for width in widths:
        line += "-" * (width + 2) + "|"
    result.append(line)

    for row in rows[1:]:
        line = "|"
        for i in range(len(row)):
            line += " " + row[i].ljust(widths[i]) + " |"
        result.append(line)

    return "\n".join(result)
