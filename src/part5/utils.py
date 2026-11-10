from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .decorators import FAILS_KEY, SUCCESS_KEY, Registry
from .storage import NAME_KEY, PRICE_KEY, QUANTITY_KEY, Product


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)

TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")
PRODUCT_FIELDS: Final[tuple[str, ...]] = (NAME_KEY, PRICE_KEY, QUANTITY_KEY)

STATS_TABLE_HEADERS: Final[tuple[str, ...]] = (
    "command name",
    "success",
    "fails",
    "success rate",
)


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return " ".join(name.lower().split())


def len_first_column(storage: dict[int, Product]) -> int:
    max_len = max((len(str(s)) for s in storage), default=0)
    return max(max_len, len(TABLE_HEADERS[0]))


def len_other_column(storage: dict[int, Product], column_number: int) -> int:
    field_key = PRODUCT_FIELDS[column_number - 1]
    max_len = max(
        (len(str(product[field_key])) for product in storage.values()),
        default=0,
    )
    return max(max_len, len(TABLE_HEADERS[column_number]))


def line_string_headers(
    max_len_column: list[int],
    headers: tuple[str, ...] = TABLE_HEADERS,
) -> str:
    line = "|"
    for column_number, header in enumerate(headers):
        line += " " + header.ljust(max_len_column[column_number]) + " |"
    return line


def line_string(product_id: int, storage_i: Product, max_len_column: list[int]) -> str:
    line = "|"
    line += " " + str(product_id).ljust(max_len_column[0]) + " |"
    for column_number, field_key in enumerate(PRODUCT_FIELDS, start=1):
        line += (
            " " + str(storage_i[field_key]).ljust(max_len_column[column_number]) + " |"
        )
    return line


def line_void(max_len_column: list[int]) -> str:
    line = "|"
    for column_len in max_len_column:
        line += "-" + "-" * column_len + "-|"
    return line


def max_len(storage: dict[int, Product]) -> list[int]:
    max_len_column = [len_first_column(storage)]
    max_len_column.extend(
        len_other_column(storage, i) for i in range(1, len(TABLE_HEADERS))
    )
    return max_len_column


def get_storage_str_representation(storage: dict[int, Product]) -> str:
    max_len_column = max_len(storage)
    str_representation = ""
    str_representation += line_string_headers(max_len_column) + "\n"
    str_representation += line_void(max_len_column) + "\n"
    for product_id, storage_i in storage.items():
        str_representation += line_string(product_id, storage_i, max_len_column) + "\n"
    return str_representation.rstrip("\n")


def get_stats_str_representation(registry: Registry) -> str:
    max_len_column = [len(header) for header in STATS_TABLE_HEADERS]
    rows = []

    for command_name, stats in registry.items():
        success = stats[SUCCESS_KEY]
        fails = stats[FAILS_KEY]
        total = success + fails

        if total == 0:
            rate = 0.0
        else:
            rate = success / total * 100

        row = [command_name, str(success), str(fails), f"{rate:.2f}%"]
        rows.append(row)

        for column_number, value in enumerate(row):
            max_len_column[column_number] = max(
                max_len_column[column_number], len(value)
            )

    str_representation = ""
    str_representation += (
        line_string_headers(max_len_column, STATS_TABLE_HEADERS) + "\n"
    )
    str_representation += line_void(max_len_column) + "\n"

    for row in rows:
        line = "|"
        for column_number, value in enumerate(row):
            line += " " + value.ljust(max_len_column[column_number]) + " |"
        str_representation += line + "\n"

    return str_representation.rstrip("\n")
