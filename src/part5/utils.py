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
    correct_price = price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)

    return correct_price


def normalize_product_name(name: str) -> str:
    correct_name = [word.lower() for word in name.split()]

    return " ".join(correct_name)


# TODO: при необходимости добавьте свои вспомогательные функции


def get_storage_str_representation(storage: dict[int, Product]) -> str:
    len_headers = [
        len(TABLE_HEADERS[0]),
        len(TABLE_HEADERS[1]),
        len(TABLE_HEADERS[2]),
        len(TABLE_HEADERS[3]),
    ]

    for product_id, product_info in storage.items():
        len_id = len(str(product_id))
        len_name = len(str(product_info[NAME_KEY]))
        len_price = len(str(product_info[PRICE_KEY]))
        len_quantity = len(str(product_info[QUANTITY_KEY]))

        len_headers = [
            max(len_headers[0], len_id),
            max(len_headers[1], len_name),
            max(len_headers[2], len_price),
            max(len_headers[3], len_quantity),
        ]

    first_header = [f" {TABLE_HEADERS[i].ljust(len_headers[i])} " for i in range(4)]

    first_row = "|" + "|".join(first_header) + "|"

    sep_str = ["-" * (len_headers[i] + 2) for i in range(4)]
    sep_row = "|" + "|".join(sep_str) + "|"

    strings = [first_row, sep_row]

    for product_id, product_info in storage.items():
        current_info = [
            str(product_id),
            str(product_info[NAME_KEY]),
            str(product_info[PRICE_KEY]),
            str(product_info[QUANTITY_KEY]),
        ]

        current_string = [
            f" {current_info[i].ljust(len_headers[i])} " for i in range(4)
        ]
        current_string_with_sep = "|" + "|".join(current_string) + "|"
        strings.append(current_string_with_sep)

    return "\n".join(strings)


def get_stats_str_representation(registry: Registry) -> str:
    len_headers = [
        len(STATS_TABLE_HEADERS[0]),
        len(STATS_TABLE_HEADERS[1]),
        len(STATS_TABLE_HEADERS[2]),
        len(STATS_TABLE_HEADERS[3]),
    ]

    for command_name, stats in registry.items():
        success = stats[SUCCESS_KEY]
        fails = stats[FAILS_KEY]
        total = success + fails

        if total == 0:
            rate_str = "0.00%"
        else:
            rate_str = f"{(success / total * 100):.2f}%"

        len_cmd = len(command_name)
        len_success = len(str(success))
        len_fails = len(str(fails))
        len_rate = len(rate_str)

        len_headers = [
            max(len_headers[0], len_cmd),
            max(len_headers[1], len_success),
            max(len_headers[2], len_fails),
            max(len_headers[3], len_rate),
        ]

    first_header = [
        f" {STATS_TABLE_HEADERS[i].ljust(len_headers[i])} " for i in range(4)
    ]
    first_row = "|" + "|".join(first_header) + "|"

    sep_str = ["-" * (len_headers[i] + 2) for i in range(4)]
    sep_row = "|" + "|".join(sep_str) + "|"

    strings = [first_row, sep_row]

    for command_name, stats in registry.items():
        success = stats[SUCCESS_KEY]
        fails = stats[FAILS_KEY]
        total = success + fails

        if total == 0:
            rate_str = "0.00%"
        else:
            rate_str = f"{(success / total * 100):.2f}%"

        current_info = [
            command_name,
            str(success),
            str(fails),
            rate_str,
        ]

        current_string = [
            f" {current_info[i].ljust(len_headers[i])} " for i in range(4)
        ]
        current_string_with_sep = "|" + "|".join(current_string) + "|"
        strings.append(current_string_with_sep)

    return "\n".join(strings)
