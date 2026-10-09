from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .storage import Product


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


def get_storage_str_representation(storage: list[Product]) -> str:
    rows: list[list[str]] = [list(TABLE_HEADERS)]

    for p in storage:
        rows.append(
            [
                str(p[0]),
                str(p[1]),
                str(p[2]),
                str(p[3]),
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