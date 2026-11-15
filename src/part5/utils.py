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


# TODO: задайте число знаков после запятой и шаг квантования (используйте своё
# решение части 4)
PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final[Decimal] = Decimal(1).scaleb(-PRICE_PRECISION)
PERCENT_MULTIPLIER: Final[int] = 100

TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")


# TODO: задайте заголовки столбцов таблицы статистики, см. TASK.md
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
    list_of_words = name.split()
    name = " ".join(list_of_words)
    name = name.lower()
    return name


# TODO: при необходимости добавьте свои вспомогательные функции


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
    # TODO: реализуйте функцию (используйте своё решение части 3)
    rows: list[tuple[str, ...]] = []
    for item_id, characteristics in storage.items():
        name = characteristics[NAME_KEY]
        price = characteristics[PRICE_KEY]
        quantity = characteristics[QUANTITY_KEY]
        rows.append((str(item_id), str(name), str(price), str(quantity)))
    return make_table(TABLE_HEADERS, rows)


def make_table(headers: tuple[str, ...], data: list[tuple[str, ...]]) -> str:
    col_length = [len(h) for h in headers]
    for row in data:
        for index, element in enumerate(row):
            col_length[index] = max(col_length[index], len(element))
    string_headers = "|"
    for header, length in zip(headers, col_length, strict=True):
        string_headers = f"{string_headers} {header.ljust(length)} |"
    separator = "|"
    for length in col_length:
        separator = f"{separator}{'-' * (length + 2)}|"
    table = [string_headers, separator]
    for row in data:
        line = "|"
        for cell, length_c in zip(row, col_length, strict=True):
            line = f"{line} {cell.ljust(length_c)} |"
        table.append(line)
    return "\n".join(table)


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
    # TODO: реализуйте функцию
    rows: list[tuple[str, ...]] = []
    for command, command_stats in registry.items():
        success = command_stats[SUCCESS_KEY]
        fails = command_stats[FAILS_KEY]
        total = success + fails

        if total > 0:
            percentage = (success / total) * PERCENT_MULTIPLIER
        else:
            percentage = 0
        rows.append((command, str(success), str(fails), f"{percentage:.2f}%"))
    return make_table(STATS_TABLE_HEADERS, rows)
