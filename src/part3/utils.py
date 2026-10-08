from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .storage import Product


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)

TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return " ".join(name.lower().split())


def len_column(storage: list[Product], column_number: int) -> int:
    max_len = max((len(str(s[column_number])) for s in storage), default=0)
    return max(len(TABLE_HEADERS[column_number]), max_len)


def line_string_headers(max_len_column: list[int]) -> str:
    line = "|"
    for column_number, header in enumerate(TABLE_HEADERS):
        line += " " + header.ljust(max_len_column[column_number]) + " |"
    return line


def line_string(storage_i: Product, max_len_column: list[int]) -> str:
    line = "|"
    for column_number, value in enumerate(storage_i):
        str_value = str(value)
        line += " " + str_value.ljust(max_len_column[column_number]) + " |"
    return line


def line_void(max_len_column: list[int]) -> str:
    line = "|"
    for column_len in max_len_column:
        line += "-" + "-" * column_len + "-|"
    return line


def get_storage_str_representation(storage: list[Product]) -> str:
    max_len_column = [len_column(storage, i) for i in range(len(TABLE_HEADERS))]
    str_representation = ""
    str_representation += line_string_headers(max_len_column) + "\n"
    str_representation += line_void(max_len_column) + "\n"
    for storage_i in storage:
        str_representation += line_string(storage_i, max_len_column) + "\n"
    return str_representation.rstrip("\n")
