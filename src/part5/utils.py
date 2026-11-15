from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .decorators import FAILS_KEY, SUCCESS_KEY, Registry
from .storage import NAME_KEY, PRICE_KEY, QUANTITY_KEY, Product


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)


TABLE_HEADERS: Final[tuple[str, ...]] = (
    "ID",
    "name",
    "price",
    "quantity",
)
STATS_TABLE_HEADERS: Final[tuple[str, ...]] = (
    "command name",
    "success",
    "fails",
    "success rate",
)


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return " ".join(name.lower().split())


def get_storage_str_representation(storage: dict[int, Product]) -> str:
    rows: list[tuple[str, ...]] = [
        (
            str(product_id),
            product[NAME_KEY],
            str(product[PRICE_KEY]),
            str(product[QUANTITY_KEY]),
        )
        for product_id, product in storage.items()
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


def get_stats_str_representation(registry: Registry) -> str:
    rows: list[tuple[str, ...]] = []
    for command, stats in registry.items():
        success = stats[SUCCESS_KEY]
        fails = stats[FAILS_KEY]
        total = success + fails
        if total == 0:
            rate = "0.00%"
        else:
            rate = f"{success / total * 100:.2f}%"
        rows.append((command, str(success), str(fails), rate))

    widths = [len(header) for header in STATS_TABLE_HEADERS]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))

    def format_row(cells: tuple[str, ...]) -> str:
        return (
            "| "
            + " | ".join(cell.ljust(widths[index]) for index, cell in enumerate(cells))
            + " |"
        )

    header_line = format_row(STATS_TABLE_HEADERS)
    separator_line = "|" + "|".join("-" * (width + 2) for width in widths) + "|"

    lines = [header_line, separator_line]
    lines.extend(format_row(row) for row in rows)
    return "\n".join(lines)
