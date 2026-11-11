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

# Column headers of the table produced by get_storage_str_representation,
# left to right. The width of each column is not fixed here -- it is
# measured per call from the data (see the function).
TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")

# Column headers of the table produced by get_stats_str_representation,
# left to right; measured per call the same way as TABLE_HEADERS.
STATS_TABLE_HEADERS: Final[tuple[str, ...]] = (
    "command name",
    "success",
    "fails",
    "success rate",
)

# Step the success rate percentage is rounded to, e.g. Decimal("0.01").
_STATS_RATE_STEP: Final = Decimal(1).scaleb(-2)


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


def _render_table(headers: tuple[str, ...], rows: tuple[tuple[str, ...], ...]) -> str:
    """Lay out a header row, a dashed separator and ``rows`` as a table.

    Every column is made exactly as wide as the longest value it carries
    in this call, its header counted, and each cell is padded with one
    space on both sides.

    Args:
        headers: The labels of the columns, left to right.
        rows: One tuple of cell values per data row; each as wide as
            ``headers``.

    Returns:
        The rendered multi-line string without a trailing newline. When
        ``rows`` is empty only the header and separator lines remain,
        sized to the header labels.
    """
    table = (headers, *rows)
    widths = tuple(
        max(len(row[index]) for row in table) for index in range(len(headers))
    )

    def format_row(row: tuple[str, ...]) -> str:
        return (
            "|"
            + "|".join(
                f" {value:<{width}} " for value, width in zip(row, widths, strict=True)
            )
            + "|"
        )

    separator = "|" + "|".join("-" * (width + 2) for width in widths) + "|"
    return "\n".join(
        (format_row(headers), separator, *(format_row(row) for row in rows))
    )


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
    rows = tuple(
        (
            str(product_id),
            product[NAME_KEY],
            str(product[PRICE_KEY]),
            str(product[QUANTITY_KEY]),
        )
        for product_id, product in storage.items()
    )
    return _render_table(TABLE_HEADERS, rows)


def _format_success_rate(success: int, fails: int) -> str:
    """Format the share of successful calls as a percentage.

    Args:
        success: The number of successful calls.
        fails: The number of failed calls.

    Returns:
        ``success`` out of all calls as a percentage with exactly two
        fractional digits and a ``%`` sign, halves rounded up. A function
        that was never called yields ``0.00%`` rather than an error.
    """
    total = success + fails
    if not total:
        return "0.00%"
    rate = Decimal(success * 100) / Decimal(total)
    return f"{rate.quantize(_STATS_RATE_STEP, rounding=ROUND_HALF_UP)}%"


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
    rows = tuple(
        (
            key,
            str(stats[SUCCESS_KEY]),
            str(stats[FAILS_KEY]),
            _format_success_rate(stats[SUCCESS_KEY], stats[FAILS_KEY]),
        )
        for key, stats in registry.items()
    )
    return _render_table(STATS_TABLE_HEADERS, rows)
