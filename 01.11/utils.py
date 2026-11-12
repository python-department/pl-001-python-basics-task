from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .storage import NAME_KEY, PRICE_KEY, QUANTITY_KEY, Product

PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final[Decimal] = Decimal(1).scaleb(-PRICE_PRECISION)

TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return " ".join(name.split()).lower()


def get_storage_str_representation(storage: dict[str, Product]) -> str:
    rows: list[tuple[str, str, str, str]] = []
    for product_id, product in storage.items():
        rows.append((
            str(product_id),
            str(product[NAME_KEY]),
            str(product[PRICE_KEY]),
            str(product[QUANTITY_KEY]),
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