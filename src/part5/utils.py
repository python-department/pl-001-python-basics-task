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

from .decorators import FAILS_KEY, SUCCESS_KEY, Registry
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

RATE_PRECISION: Final[int] = 2
RATE_STEP: Final = Decimal(1).scaleb(-RATE_PRECISION)
PERCENT: Final[int] = 100

# Column headers of the table produced by get_storage_str_representation,
# left to right. The width of each column is not fixed here -- it is
# measured per call from the data (see the function).
TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")
STATS_TABLE_HEADERS: Final[tuple[str, ...]] = (
    "command name",
    "success",
    "fails",
    "success rate",
)


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
    words = name.split()

    return " ".join(words).lower()


def get_row_str(cells: list[str], widths: list[int]) -> str:
    cells_with_spaces = []

    for cell, width in zip(cells, widths):
        cells_with_spaces.append(cell.ljust(width))

    middle = " | ".join(cells_with_spaces)

    return f"| {middle} |"


def get_separator_str(widths: list[int]) -> str:
    dashes = []

    for width in widths:
        dashes.append("-" * (width + 2))

    middle = "|".join(dashes)

    return f"|{middle}|"


def get_table_str(table: list[list[str]]) -> str:
    widths = []

    for column in range(len(table[0])):
        widths.append(max(len(values[column]) for values in table))

    lines = [get_row_str(table[0], widths), get_separator_str(widths)]

    for values in table[1:]:
        lines.append(get_row_str(values, widths))

    return "\n".join(lines)


def get_success_rate_str(success: int, fails: int) -> str:
    calls = success + fails

    if calls == 0:
        rate = Decimal(0)
    else:
        rate = Decimal(success * PERCENT) / calls

    rate = rate.quantize(RATE_STEP, rounding=ROUND_HALF_UP)

    return f"{rate}%"


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
    table = [list(TABLE_HEADERS)]

    for product_id, product in storage.items():
        price = str(product[PRICE_KEY])
        quantity = str(product[QUANTITY_KEY])
        table.append([str(product_id), product[NAME_KEY], price, quantity])

    return get_table_str(table)


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
    table = [list(STATS_TABLE_HEADERS)]

    for command_name, stats in registry.items():
        success = stats[SUCCESS_KEY]
        fails = stats[FAILS_KEY]
        rate = get_success_rate_str(success, fails)
        table.append([command_name, str(success), str(fails), rate])

    return get_table_str(table)
