from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .storage import (
    NAME_KEY,
    PRICE_KEY,
    QUANTITY_KEY,
    Product,
)

PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal("0.01")
TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    if not isinstance(price, Decimal):
        price = Decimal(str(price))
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return " ".join(name.strip().split()).lower()


def get_storage_str_representation(storage: dict[str, Product]) -> str:
    rows: list[list[str]] = []
    for product_id, product in storage.items():
        rows.append(
            [
                product_id,
                str(product[NAME_KEY]),
                str(product[PRICE_KEY]),
                str(product[QUANTITY_KEY]),
            ]
        )

    col_widths = [
        max(len(header), max((len(row[i]) for row in rows), default=0))
        for i, header in enumerate(TABLE_HEADERS)
    ]

    header_line = (
        "| "
        + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(TABLE_HEADERS))
        + " |"
    )
    separator_line = (
        "|-" + "-|-".join("-" * col_widths[i] for i in range(len(TABLE_HEADERS))) + "-|"
    )

    lines = [header_line, separator_line]
    for row in rows:
        row_line = (
            "| "
            + " | ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(row))
            + " |"
        )
        lines.append(row_line)

    return "\n".join(lines)
