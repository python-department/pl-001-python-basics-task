from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .storage import (
    NAME_KEY,
    PRICE_KEY,
    QUANTITY_KEY,
    Product,
)


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)

TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return " ".join(name.split()).lower()


def get_storage_str_representation(storage: dict[str, Product]) -> str:
    rows = [
        [
            product_id,
            product[NAME_KEY],
            str(product[PRICE_KEY]),
            str(product[QUANTITY_KEY]),
        ]
        for product_id, product in storage.items()
    ]

    widths = [
        max(len(TABLE_HEADERS[i]), *(len(row[i]) for row in rows))
        if rows
        else len(TABLE_HEADERS[i])
        for i in range(len(TABLE_HEADERS))
    ]

    header = (
        "| "
        + " | ".join(
            TABLE_HEADERS[i].ljust(widths[i]) for i in range(len(TABLE_HEADERS))
        )
        + " |"
    )

    separator = "|" + "|".join("-" * (width + 2) for width in widths) + "|"

    data_rows = [
        "| "
        + " | ".join(row[i].ljust(widths[i]) for i in range(len(TABLE_HEADERS)))
        + " |"
        for row in rows
    ]

    return "\n".join([header, separator, *data_rows])
