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

from .decorators import Registry
from .storage import (
    NAME_KEY,
    PRICE_KEY,
    QUANTITY_KEY,
    Product,
)


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
    # TODO: реализуйте функцию (используйте своё решение части 4)
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
    # TODO: реализуйте функцию (используйте своё решение части 4)
    return " ".join(name.split()).lower()


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
    # TODO: реализуйте функцию (используйте своё решение части 4)
    ids = []
    names = []
    prices = []
    quantitys = []

    for str_prod, product in storage.items():
        ids.append(str(str_prod))
        names.append(product[NAME_KEY])
        prices.append(str(product[PRICE_KEY]))
        quantitys.append(str(product[QUANTITY_KEY]))

    w_id = max(len(TABLE_HEADERS[0]), max((len(x) for x in ids), default=0))
    w_name = max(len(TABLE_HEADERS[1]), max((len(x) for x in names), default=0))
    w_pr = max(len(TABLE_HEADERS[2]), max((len(x) for x in prices), default=0))
    w_qty = max(len(TABLE_HEADERS[3]), max((len(x) for x in quantitys), default=0))

    change_str_main = (
        f"| {TABLE_HEADERS[0].ljust(w_id)} "
        f"| {TABLE_HEADERS[1].ljust(w_name)} "
        f"| {TABLE_HEADERS[2].ljust(w_pr)} "
        f"| {TABLE_HEADERS[3].ljust(w_qty)} |"
    )

    change_str_dif = (
        f"|{'-' * (w_id + 2)}"
        f"|{'-' * (w_name + 2)}"
        f"|{'-' * (w_pr + 2)}"
        f"|{'-' * (w_qty + 2)}|"
    )

    rows = []
    for i in range(len(storage)):
        row = (
            f"| {ids[i].ljust(w_id)} "
            f"| {names[i].ljust(w_name)} "
            f"| {prices[i].ljust(w_pr)} "
            f"| {quantitys[i].ljust(w_qty)} |"
        )
        rows.append(row)

    res = "\n".join([change_str_main, change_str_dif, *rows])

    return res


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
    commands = []
    successes = []
    fails = []
    ratios = []

    for cmd, stats in registry.items():
        s = stats["success"]
        f = stats["fails"]
        total = s + f

        if total > 0:
            ratio = f"{s / total * 100:.2f}%"
        else:
            ratio = "0.00%"

        commands.append(cmd)
        successes.append(str(s))
        fails.append(str(f))
        ratios.append(ratio)

    w_cmd = max(len(STATS_TABLE_HEADERS[0]), max((len(x) for x in commands), default=0))
    w_suc = max(
        len(STATS_TABLE_HEADERS[1]), max((len(x) for x in successes), default=0)
    )
    w_fai = max(len(STATS_TABLE_HEADERS[2]), max((len(x) for x in fails), default=0))
    w_rat = max(len(STATS_TABLE_HEADERS[3]), max((len(x) for x in ratios), default=0))

    change_str_main = (
        f"| {STATS_TABLE_HEADERS[0].ljust(w_cmd)} "
        f"| {STATS_TABLE_HEADERS[1].ljust(w_suc)} "
        f"| {STATS_TABLE_HEADERS[2].ljust(w_fai)} "
        f"| {STATS_TABLE_HEADERS[3].ljust(w_rat)} |"
    )

    change_str_dif = (
        f"|{'-' * (w_cmd + 2)}"
        f"|{'-' * (w_suc + 2)}"
        f"|{'-' * (w_fai + 2)}"
        f"|{'-' * (w_rat + 2)}|"
    )

    rows = []
    for i in range(len(registry)):
        row = (
            f"| {commands[i].ljust(w_cmd)} "
            f"| {successes[i].ljust(w_suc)} "
            f"| {fails[i].ljust(w_fai)} "
            f"| {ratios[i].ljust(w_rat)} |"
        )
        rows.append(row)

    return "\n".join([change_str_main, change_str_dif, *rows])
