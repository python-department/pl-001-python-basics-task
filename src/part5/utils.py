from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .decorators import FAILS_KEY, SUCCESS_KEY, Registry
from .storage import (
    NAME_KEY,
    PRICE_KEY,
    QUANTITY_KEY,
    Product,
)


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)

TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")
STATS_TABLE_HEADERS: Final[tuple[str, ...]] = (
    "command name",
    "success",
    "fails",
    "success rate",
)


def normalize_price(price: Decimal) -> Decimal:
    return Decimal(price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP))


def normalize_product_name(name: str) -> str:
    return " ".join(name.lower().split())


def product_row(product_id: int, product: Product) -> tuple[str, ...]:
    return (
        str(product_id),
        product[NAME_KEY],
        str(product[PRICE_KEY]),
        str(product[QUANTITY_KEY]),
    )


def drawing_row(cells: tuple[str, ...], widths: tuple[int, ...]) -> str:
    new_row = tuple(cell.ljust(width) for cell, width in zip(cells, widths))
    return "| " + " | ".join(new_row) + " |"


def stats_row(
    command_name: str,
    success: int,
    fails: int,
) -> tuple[str, ...]:
    total = success + fails
    if total == 0:
        rate = "0.00%"
    else:
        percent = (Decimal(success) * 100 / Decimal(total)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        rate = f"{percent}%"
    return (command_name, str(success), str(fails), rate)


def drawing_table(rows: list[tuple[str, ...]]) -> str:
    headers = rows[0]
    widths = tuple(max(len(row[i]) for row in rows) for i in range(len(headers)))

    header = drawing_row(headers, widths)
    sep_line = "|" + "|".join("-" * (width + 2) for width in widths) + "|"

    lines = [drawing_row(row, widths) for row in rows[1:]]
    return "\n".join([header, sep_line] + lines)


def get_storage_str_representation(storage: dict[int, Product]) -> str:
    rows = [TABLE_HEADERS] + [
        product_row(product_id, product) for product_id, product in storage.items()
    ]
    return drawing_table(rows)


def get_stats_str_representation(registry: Registry) -> str:
    rows = [STATS_TABLE_HEADERS] + [
        stats_row(name, stats[SUCCESS_KEY], stats[FAILS_KEY])
        for name, stats in registry.items()
    ]
    return drawing_table(rows)
