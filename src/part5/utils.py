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
    true_price = price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)

    return true_price


def normalize_product_name(name: str) -> str:
    new_name = " ".join(name.split()).lower()

    return new_name


# TODO: при необходимости добавьте свои вспомогательные функции


def get_storage_str_representation(storage: dict[int, Product]) -> str:
    mx_len_id = len(TABLE_HEADERS[0])
    mx_len_name = len(TABLE_HEADERS[1])
    mx_len_price = len(TABLE_HEADERS[2])
    mx_len_quantity = len(TABLE_HEADERS[3])

    for key, prod in storage.items():
        mx_len_id = max(mx_len_id, len(str(key)))
        mx_len_name = max(mx_len_name, len(prod[NAME_KEY]))
        mx_len_price = max(mx_len_price, len(str(prod[PRICE_KEY])))
        mx_len_quantity = max(mx_len_quantity, len(str(prod[QUANTITY_KEY])))

    s = (
        f"| {TABLE_HEADERS[0]:<{mx_len_id}} "
        f"| {TABLE_HEADERS[1]:<{mx_len_name}} "
        f"| {TABLE_HEADERS[2]:<{mx_len_price}} "
        f"| {TABLE_HEADERS[3]:<{mx_len_quantity}} |\n"
        f"|{'-' * (mx_len_id + 2)}"
        f"|{'-' * (mx_len_name + 2)}"
        f"|{'-' * (mx_len_price + 2)}"
        f"|{'-' * (mx_len_quantity + 2)}|"
    )

    for key, prod in storage.items():
        s_new = (
            f"\n| {key:<{mx_len_id}} "
            f"| {prod[NAME_KEY]:<{mx_len_name}} "
            f"| {prod[PRICE_KEY]!s:<{mx_len_price}} "
            f"| {prod[QUANTITY_KEY]!s:<{mx_len_quantity}} |"
        )
        s += s_new
    return s


def get_stats_str_representation(registry: Registry) -> str:
    mx_len_com_name = len(STATS_TABLE_HEADERS[0])
    len_second_col = len(STATS_TABLE_HEADERS[1])
    len_third_col = len(STATS_TABLE_HEADERS[2])
    len_fourth_col = len(STATS_TABLE_HEADERS[3])
    for command in registry:
        mx_len_com_name = max(mx_len_com_name, len(command))

    s = (
        f"| {STATS_TABLE_HEADERS[0]:<{mx_len_com_name}} "
        f"| {STATS_TABLE_HEADERS[1]:<{len_second_col}} "
        f"| {STATS_TABLE_HEADERS[2]:<{len_third_col}} "
        f"| {STATS_TABLE_HEADERS[3]:<{len_fourth_col}} |\n"
        f"|{'-' * (mx_len_com_name + 2)}"
        f"|{'-' * (len_second_col + 2)}"
        f"|{'-' * (len_third_col + 2)}"
        f"|{'-' * (len_fourth_col + 2)}|"
    )

    for command, stats in registry.items():
        success = stats[SUCCESS_KEY]
        fails = stats[FAILS_KEY]
        total = success + fails
        if total > 0:
            perc = f"{(success / total * 100):.2f}%"
        else:
            perc = "0.00%"

        s += (
            f"\n| {command:<{mx_len_com_name}} "
            f"| {success:<{len_second_col}} "
            f"| {fails:<{len_third_col}} "
            f"| {perc:<{len_fourth_col}} |"
        )

    return s
