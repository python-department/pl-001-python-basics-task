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
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)


# TODO: задайте заголовки столбцов таблицы (используйте своё решение части 4)
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
    ratio = price / PRICE_STEP
    steps = ratio.quantize(Decimal("1."), rounding=ROUND_HALF_UP)
    real_price = steps * PRICE_STEP
    return real_price


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
    pars_name = name.split()
    norm_list = [norm_word.lower() for word in pars_name if (norm_word := word.strip())]
    norm_name = " ".join(norm_list)
    return norm_name


def make_list_from_product(product: Product) -> list[str]:
    return [
        product[NAME_KEY],
        str(product[PRICE_KEY]),
        str(product[QUANTITY_KEY]),
    ]


def render_row(cells: list[str], widths: list[int]) -> str:
    parts = ["|"]
    for cell, width in zip(cells, widths):
        parts.append(" " + str(cell).ljust(width) + " ")
        parts.append("|")
    return "".join(parts)


def calculate_of_width(storage: dict[int, Product]) -> list[int]:
    widths = [len(word) for word in TABLE_HEADERS]
    ID_PLACE = 0
    SHIFT = 1

    for key in storage:
        widths[ID_PLACE] = max(widths[ID_PLACE], len(str(key)))  # str!

    for product in storage.values():
        for i, value in enumerate(make_list_from_product(product)):
            idx = i + SHIFT
            widths[idx] = max(widths[idx], len(value))

    return widths


def render_sep(widths: list[int]) -> str:
    return "|" + "|".join("-" * (w + 2) for w in widths) + "|"


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
    widths = calculate_of_width(storage)

    lines = [
        render_row(list(TABLE_HEADERS), widths),
        render_sep(widths),
    ]
    for key, product in storage.items():
        lines.append(render_row([str(key)] + make_list_from_product(product), widths))

    return "\n".join(lines)


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
    rows: list[list[str]] = []
    for name, stats in registry.items():
        success = stats[SUCCESS_KEY]
        fails = stats[FAILS_KEY]
        total = success + fails
        if total == 0:
            rate = "0.00%"
        else:
            pct = (Decimal(success) * Decimal(100) / Decimal(total)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            rate = f"{pct}%"
        rows.append([name, str(success), str(fails), rate])

    widths = [len(h) for h in STATS_TABLE_HEADERS]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    lines = [
        render_row(list(STATS_TABLE_HEADERS), widths),
        render_sep(widths),
    ]
    for row in rows:
        lines.append(render_row(row, widths))

    return "\n".join(lines)
