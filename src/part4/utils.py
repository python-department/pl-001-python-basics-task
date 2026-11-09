from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .storage import NAME_KEY, PRICE_KEY, QUANTITY_KEY, Product


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)

TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")

PRODUCT_FIELDS: Final[tuple[str, ...]] = (NAME_KEY, PRICE_KEY, QUANTITY_KEY)


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return " ".join(name.lower().split())


def len_first_column(storage: dict[str, Product]) -> int:
    max_len = max((len(s) for s in storage), default=0)
    return max(max_len, len(TABLE_HEADERS[0]))


def len_other_column(storage: dict[str, Product], column_number: int) -> int:
    field_key = PRODUCT_FIELDS[column_number - 1]
    max_len = max(
        (len(str(product[field_key])) for product in storage.values()),
        default=0,
    )
    return max(max_len, len(TABLE_HEADERS[column_number]))


def line_string_headers(max_len_column: list[int]) -> str:
    line = "|"
    for column_number, header in enumerate(TABLE_HEADERS):
        line += " " + header.ljust(max_len_column[column_number]) + " |"
    return line


def line_string(product_id: str, storage_i: Product, max_len_column: list[int]) -> str:
    line = "|"
    line += " " + product_id.ljust(max_len_column[0]) + " |"
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


def max_len(storage: dict[str, Product]) -> list[int]:
    max_len_column = [len_first_column(storage)]
    max_len_column.extend(
        len_other_column(storage, i) for i in range(1, len(TABLE_HEADERS))
    )
    return max_len_column


def get_storage_str_representation(storage: dict[str, Product]) -> str:
    max_len_column = max_len(storage)
    str_representation = ""
    str_representation += line_string_headers(max_len_column) + "\n"
    str_representation += line_void(max_len_column) + "\n"
    for product_id, storage_i in storage.items():
        str_representation += line_string(product_id, storage_i, max_len_column) + "\n"
    return str_representation.rstrip("\n")
