from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .storage import (
    NAME_INDEX,
    PRICE_INDEX,
    PRODUCT_ID_INDEX,
    QUANTITY_INDEX,
    Product,
)


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)


TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    res = [word.lower() for word in name.split()]
    return " ".join(res)


# TODO: при необходимости добавьте свои вспомогательные функции


def get_storage_str_representation(storage: list[Product]) -> str:
    rows = [
        [
            str(product[PRODUCT_ID_INDEX]),
            product[NAME_INDEX],
            str(product[PRICE_INDEX]),
            str(product[QUANTITY_INDEX]),
        ]
        for product in storage
    ]
    widths = [
        max(len(TABLE_HEADERS[i]), *(len(row[i]) for row in rows))
        if rows
        else len(TABLE_HEADERS[i])
        for i in range(len(TABLE_HEADERS))
    ]

    header_line = (
        "| "
        + " | ".join(
            TABLE_HEADERS[i].ljust(widths[i]) for i in range(len(TABLE_HEADERS))
        )
        + " |"
    )
    sep_line = "|" + "|".join("-" * (w + 2) for w in widths) + "|"
    data_lines = [
        "| "
        + " | ".join(row[i].ljust(widths[i]) for i in range(len(TABLE_HEADERS)))
        + " |"
        for row in rows
    ]
    return "\n".join([header_line, sep_line, *data_lines])
