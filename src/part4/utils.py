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
    return Decimal(price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP))


def normalize_product_name(name: str) -> str:
    return " ".join(name.lower().split())


def product_row(product_id: str, product: Product) -> tuple[str, ...]:
    return (
        product_id,
        product[NAME_KEY],
        str(product[PRICE_KEY]),
        str(product[QUANTITY_KEY]),
    )


def drawing_row(cells: tuple[str, ...], widths: tuple[int, ...]) -> str:
    new_row = tuple(cell.ljust(width) for cell, width in zip(cells, widths))
    return "| " + " | ".join(new_row) + " |"


def get_storage_str_representation(storage: dict[str, Product]) -> str:
    rows = [TABLE_HEADERS] + [
        product_row(product_id, product) for product_id, product in storage.items()
    ]

    widths_of_string = tuple(
        max(len(row[i]) for row in rows) for i in range(len(TABLE_HEADERS))
    )

    header = drawing_row(TABLE_HEADERS, widths_of_string)
    sep_line = "|" + "|".join("-" * (width + 2) for width in widths_of_string) + "|"

    lines = [drawing_row(row, widths_of_string) for row in rows[1:]]
    return "\n".join([header, sep_line] + lines)
