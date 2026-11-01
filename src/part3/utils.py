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

TABLE_HEADERS: Final[tuple[str, ...]] = (
    "ID",
    "name",
    "price",
    "quantity",
)


def normalize_price(price: Decimal) -> Decimal:

    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:

    return " ".join(name.lower().split())


def get_storage_str_representation(storage: list[Product]) -> str:
    rows: list[tuple[str, ...]] = [
        (
            str(product[PRODUCT_ID_INDEX]),
            product[NAME_INDEX],
            str(product[PRICE_INDEX]),
            str(product[QUANTITY_INDEX]),
        )
        for product in storage
    ]

    widths = [len(header) for header in TABLE_HEADERS]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))

    def format_row(cells: tuple[str, ...]) -> str:
        return (
            "| "
            + " | ".join(cell.ljust(widths[index]) for index, cell in enumerate(cells))
            + " |"
        )

    header_line = format_row(TABLE_HEADERS)
    separator_line = "|" + "|".join("-" * (width + 2) for width in widths) + "|"

    lines = [header_line, separator_line]
    lines.extend(format_row(row) for row in rows)
    return "\n".join(lines)
