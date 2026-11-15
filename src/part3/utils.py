from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .storage import NAME_INDEX, PRICE_INDEX, PRODUCT_ID_INDEX, QUANTITY_INDEX, Product


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)

TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    return Decimal(price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP))


def normalize_product_name(name: str) -> str:
    return " ".join(name.lower().split())


def rowing_product(product: Product) -> tuple[str, ...]:
    return (
        str(product[PRODUCT_ID_INDEX]),
        product[NAME_INDEX],
        str(product[PRICE_INDEX]),
        str(product[QUANTITY_INDEX]),
    )


def drawing_row(cells: tuple[str, ...], widths: tuple[int, ...]) -> str:
    new_row = tuple(cell.ljust(width) for cell, width in zip(cells, widths))
    return "| " + " | ".join(new_row) + " |"


def get_storage_str_representation(storage: list[Product]) -> str:
    rows = [TABLE_HEADERS] + [rowing_product(product) for product in storage]

    widths_of_string = tuple(
        max(len(row[i]) for row in rows) for i in range(len(TABLE_HEADERS))
    )

    header = drawing_row(TABLE_HEADERS, widths_of_string)
    sep_line = "|" + "|".join("-" * (width + 2) for width in widths_of_string) + "|"

    lines = [drawing_row(row, widths_of_string) for row in rows[1:]]
    table = "\n".join([header, sep_line] + lines)

    return table
