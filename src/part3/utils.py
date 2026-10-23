from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .storage import Product


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final[Decimal] = Decimal(1).scaleb(-PRICE_PRECISION)
TABLE_HEADERS: Final[tuple[str, str, str, str]] = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return " ".join(name.split()).lower()


def get_storage_str_representation(storage: list[Product]) -> str:
    rows: list[tuple[str, str, str, str]] = [
        (str(product[0]), product[1], str(product[2]), str(product[3]))
        for product in storage
    ]
    widths: list[int] = [
        max(len(header), *(len(row[i]) for row in rows)) if rows else len(header)
        for i, header in enumerate(TABLE_HEADERS)
    ]
    header_line = (
        "|"
        + "|".join(f" {cell:<{width}} " for cell, width in zip(TABLE_HEADERS, widths))
        + "|"
    )
    dop_line = "|" + "|".join("-" * (width + 2) for width in widths) + "|"
    data_lines = [
        "|" + "|".join(f" {cell:<{width}} " for cell, width in zip(row, widths)) + "|"
        for row in rows
    ]
    return "\n".join([header_line, dop_line, *data_lines])
