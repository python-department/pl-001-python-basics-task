"""Standalone helpers shared by the part5 storage and CRUD modules.

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
* :func:`get_stats_str_representation` renders the call statistics gathered
  by :func:`~src.part5.decorators.collect_stats` as a table of the same
  look, with the success rate of every command as a percentage.
"""

from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .decorators import (
    FAILS_KEY,
    SUCCESS_KEY,
    Registry,
)
from .storage import (
    NAME_KEY,
    PRICE_KEY,
    QUANTITY_KEY,
    Product,
)


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)


TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", NAME_KEY, PRICE_KEY, QUANTITY_KEY)
STATS_TABLE_HEADERS = ("command name", SUCCESS_KEY, FAILS_KEY, "success rate")


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


def get_columns_width(
    rows_data: tuple[tuple[str, ...], ...],
    headers: tuple[str, ...],
) -> tuple[int, ...]:
    if not rows_data:
        return tuple(len(header) for header in headers)
    columns = zip(headers, *rows_data)

    return tuple(max(map(len, column)) for column in columns)


def get_dividing_row(cols_width: tuple[int, ...]) -> str:
    dividing_row_data = ["-" * (width + 2) for width in cols_width]
    return "|" + "|".join(dividing_row_data) + "|"


def get_str_of_rows(
    rows_data: tuple[tuple[str, ...], ...],
    headers: tuple[str, ...],
) -> str:
    cols_width = get_columns_width(rows_data, headers)
    rows = []
    for row_data in rows_data:
        row = "|"
        for cell_num, cell_data in enumerate(row_data):
            cell = cell_data.ljust(cols_width[cell_num])
            row += " " + cell + " |"
        rows.append(row)
    dividing_row = get_dividing_row(cols_width)
    rows.insert(1, dividing_row)
    return "\n".join(rows)


def get_storage_str_representation(storage: dict[int, Product]) -> str:
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
    rows_data = (TABLE_HEADERS,) + tuple(
        (
            str(product_id),
            str(product[NAME_KEY]),
            str(product[PRICE_KEY]),
            str(product[QUANTITY_KEY]),
        )
        for product_id, product in storage.items()
    )
    return get_str_of_rows(rows_data, TABLE_HEADERS)


def get_success_rate(counter: dict[str, int]) -> str:
    denominator = counter[SUCCESS_KEY] + counter[FAILS_KEY]
    if not denominator:
        return f"{0:.2%}"
    numerator = counter[SUCCESS_KEY]
    return f"{numerator / denominator:.2%}"


def get_success_rate_data(registry: Registry) -> tuple[str, ...]:
    return tuple(get_success_rate(counter) for counter in registry.values())


def get_stats_str_representation(registry: Registry) -> str:
    """Render the call statistics as a text table with data-sized columns.

    The table has the columns named by :data:`STATS_TABLE_HEADERS` -- command
    name, number of successful calls, number of failed calls and success
    rate. It is laid out like the one from
    :func:`get_storage_str_representation`: every column is as wide as the
    longest value it carries, its header counted.

    Args:
        registry: The statistics to render, a mapping of command name to the
            counters kept by :func:`~src.part5.decorators.collect_stats`.

    Returns:
        A multi-line string: a header row, a dashed separator row, then one
        row per registry entry in insertion order. When ``registry`` is
        empty only the header and separator rows are returned, sized to the
        header labels.
    """

    rows_data = (STATS_TABLE_HEADERS,) + tuple(
        (
            str(product_id),
            str(product[SUCCESS_KEY]),
            str(product[FAILS_KEY]),
            get_success_rate(product),
        )
        for product_id, product in registry.items()
    )
    return get_str_of_rows(rows_data, STATS_TABLE_HEADERS)
