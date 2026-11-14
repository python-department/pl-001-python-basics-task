from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Final

from .storage import (
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
TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", NAME_KEY, PRICE_KEY, QUANTITY_KEY)


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
    return " ".join(name.split()).lower()


def get_columns_width(rows_data: list[tuple[str, ...]]) -> list[int]:
    return [
        max(
            max([len(str(row_data[i])) for row_data in rows_data] + [0]),
            len(TABLE_HEADERS[i]),
        )
        for i in range(len(TABLE_HEADERS))
    ]


def merge_in_row_data(product_id: str, fields: dict[str, Any]) -> tuple[str, ...]:
    return (product_id, *map(str, fields.values()))


def get_dividing_row(cols_width: list[int]) -> str:
    dividing_row_data = ["-" * (width + 2) for width in cols_width]
    return "|" + "|".join(dividing_row_data) + "|"


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
    rows_data = [TABLE_HEADERS] + list(
        map(merge_in_row_data, storage.keys(), storage.values())
    )
    cols_width = get_columns_width(rows_data)
    rows = []
    for row_data in rows_data:
        row = "|"
        for i, cell_data in enumerate(row_data):
            cell = cell_data.ljust(cols_width[i])
            row += " " + cell + " |"
        rows.append(row)
    dividing_row = get_dividing_row(cols_width)
    rows.insert(1, dividing_row)
    return "\n".join(rows)
