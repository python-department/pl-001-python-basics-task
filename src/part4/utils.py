from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .storage import (
    NAME_KEY,
    PRICE_KEY,
    QUANTITY_KEY,
    Product,
)


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final[Decimal] = Decimal(1).scaleb(-PRICE_PRECISION)

TABLE_HEADERS: Final[tuple[str, str, str, str]] = (
    "ID",
    "name",
    "price",
    "quantity",
)


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return " ".join(name.split()).lower()


def get_storage_str_representation(storage: dict[str, Product]) -> str:
    rows: list[list[str]] = [list(TABLE_HEADERS)]

    for product_id, product in storage.items():
        rows.append(
            [
                product_id,
                product[NAME_KEY],
                str(product[PRICE_KEY]),
                str(product[QUANTITY_KEY]),
            ]
        )

    col_widths = [max(len(row[i]) for row in rows) for i in range(len(TABLE_HEADERS))]

    formatted_rows = []
    for row in rows:
        padded_cells = [
            f" {row[i].ljust(col_widths[i])} " for i in range(len(TABLE_HEADERS))
        ]
        formatted_rows.append(f"|{'|'.join(padded_cells)}|")

    dash_cells = ["-" * (w + 2) for w in col_widths]
    separator_line = f"|{'|'.join(dash_cells)}|"
    formatted_rows.insert(1, separator_line)

    return "\n".join(formatted_rows)
