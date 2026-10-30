from decimal import Decimal, ROUND_HALF_UP
from typing import Final

from .storage import (
    Product,
    PRODUCT_ID_INDEX,
    NAME_INDEX,
    PRICE_INDEX,
    QUANTITY_INDEX,
)

PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final[Decimal] = Decimal(1).scaleb(-PRICE_PRECISION)

TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return " ".join(name.split()).lower()


def get_storage_str_representation(storage: list[Product]) -> str:
    rows: list[tuple[str, str, str, str]] = []
    for product in storage:
        rows.append((
            str(product[PRODUCT_ID_INDEX]),
            str(product[NAME_INDEX]),
            str(product[PRICE_INDEX]),
            str(product[QUANTITY_INDEX]),
        ))

    widths: list[int] = [len(header) for header in TABLE_HEADERS]
    for row in rows:
        for i, cell in enumerate(row):
            if len(cell) > widths[i]:
                widths[i] = len(cell)

    def format_row(cells: tuple[str, ...]) -> str:
        parts = [f" {cell.ljust(widths[i])} " for i, cell in enumerate(cells)]
        return "|" + "|".join(parts) + "|"

    lines = [format_row(TABLE_HEADERS)]
    lines.append("|" + "|".join("-" * (width + 2) for width in widths) + "|")
    for row in rows:
        lines.append(format_row(row))

    return "\n".join(lines)