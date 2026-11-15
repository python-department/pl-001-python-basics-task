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

from collections.abc import Sequence
from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .decorators import FAILS_KEY, SUCCESS_KEY, Registry
from .storage import NAME_KEY, PRICE_KEY, QUANTITY_KEY, Product


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)
RATE_QUANT: Final[Decimal] = Decimal("0.01")

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


def format_row(values: tuple[str, ...], widths: list[int]) -> str:
    cells = [f" {value.ljust(width)} " for value, width in zip(values, widths)]
    return "|" + "|".join(cells) + "|"


def render_table(headers: tuple[str, ...], rows: Sequence[tuple[str, ...]]) -> str:
    all_rows: list[tuple[str, ...]] = [headers, *rows]

    col_widths = []
    for col_ind in range(len(headers)):
        max_width = max(len(row[col_ind]) for row in all_rows)
        col_widths.append(max_width)

    result_lines = [
        format_row(headers, col_widths),
        "|" + "|".join("-" * (width + 2) for width in col_widths) + "|",
    ]

    for row in rows:
        result_lines.append(format_row(row, col_widths))

    return "\n".join(result_lines)


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

    rows = []
    for product_id, product in storage.items():
        rows.append(
            (
                str(product_id),
                product[NAME_KEY],
                str(product[PRICE_KEY]),
                str(product[QUANTITY_KEY]),
            )
        )
    return render_table(TABLE_HEADERS, rows)


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

    rows = []
    for command, stats in registry.items():
        success = stats[SUCCESS_KEY]
        fails = stats[FAILS_KEY]
        total = success + fails
        if total > 0:
            rate = (Decimal(success * 100) / Decimal(total)).quantize(
                RATE_QUANT, rounding=ROUND_HALF_UP
            )
        else:
            rate = Decimal("0.00")

        rows.append(
            (
                command,
                str(success),
                str(fails),
                f"{rate}%",
            )
        )
    return render_table(STATS_TABLE_HEADERS, rows)
