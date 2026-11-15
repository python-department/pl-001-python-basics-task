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
from .storage import NAME_KEY, PRICE_KEY, QUANTITY_KEY, Product


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)

TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")

STATS_TABLE_HEADERS: Final[tuple[str, ...]] = (
    "command name",
    "success",
    "fails",
    "success rate",
)

CELL_PADDING: Final[int] = 1

COLUMN_BORDER: Final[str] = "|"
SEPARATOR_FILL: Final[str] = "-"

PERCENT_STEP: Final = Decimal("0.01")
PERCENT_FACTOR: Final[int] = 100


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


def format_row(cells: list[str], widths: list[int]) -> str:
    """Render one table row, padding each cell to its column width.

    Args:
        cells: The text of each cell, left to right.
        widths: The width of each column, left to right.

    Returns:
        The row as ``| a | b | c | d |`` with every cell padded on the
        right to its column width.
    """
    padded_cells = [cell.ljust(width) for cell, width in zip(cells, widths)]
    padding = " " * CELL_PADDING
    joiner = f"{padding}{COLUMN_BORDER}{padding}"
    row = joiner.join(padded_cells)
    return f"{COLUMN_BORDER}{padding}{row}{padding}{COLUMN_BORDER}"


def format_table(headers: tuple[str, ...], rows: list[list[str]]) -> str:
    """Render a header row, a dashed separator and ``rows`` as a text table.

    Args:
        headers: The column headers, left to right.
        rows: The cell texts of each row; every row has one cell per header.

    Returns:
        A multi-line string without a trailing newline. Each column is as
        wide as the longest value it carries, its header counted, so with
        no rows only the header and separator rows are returned.
    """
    widths = [
        max([len(header)] + [len(row[i]) for row in rows])
        for i, header in enumerate(headers)
    ]

    dashes = [SEPARATOR_FILL * (width + 2 * CELL_PADDING) for width in widths]
    separator = f"{COLUMN_BORDER}{COLUMN_BORDER.join(dashes)}{COLUMN_BORDER}"

    lines = [format_row(list(headers), widths), separator]
    lines.extend(format_row(row, widths) for row in rows)

    return "\n".join(lines)


def format_success_rate(success: int, fails: int) -> str:
    """Format the share of successful calls as a percentage.

    Args:
        success: Number of successful calls.
        fails: Number of failed calls.

    Returns:
        ``success / (success + fails)`` in percent with two fractional digits
        and a ``%`` sign, halves rounded up; ``"0.00%"`` when there were no
        calls at all.
    """
    total = success + fails
    if total == 0:
        return f"{Decimal(0):.2f}%"

    rate = (Decimal(success) * PERCENT_FACTOR / total).quantize(
        PERCENT_STEP, ROUND_HALF_UP
    )
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
    rows = [
        [
            str(product_id),
            record[NAME_KEY],
            str(record[PRICE_KEY]),
            str(record[QUANTITY_KEY]),
        ]
        for product_id, record in storage.items()
    ]

    return format_table(TABLE_HEADERS, rows)


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
    rows = [
        [
            command,
            str(stats[SUCCESS_KEY]),
            str(stats[FAILS_KEY]),
            format_success_rate(stats[SUCCESS_KEY], stats[FAILS_KEY]),
        ]
        for command, stats in registry.items()
    ]

    return format_table(STATS_TABLE_HEADERS, rows)
