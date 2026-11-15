from collections.abc import Sequence
from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .decorators import FAILS_KEY, SUCCESS_KEY, Registry
from .storage import NAME_KEY, PRICE_KEY, QUANTITY_KEY, Product


PRICE_PRECISION: Final = 2
PRICE_STEP: Final = Decimal("0.01")

TABLE_HEADERS: Final = ("ID", "name", "price", "quantity")
STATS_TABLE_HEADERS: Final = ("command name", "success", "fails", "success rate")


def normalize_product_name(name: str) -> str:
    return " ".join(name.split()).lower()


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def _format_table(headers: tuple[str, ...], rows: Sequence[tuple[str, ...]]) -> str:
    widths = [
        max(len(header), *(len(row[i]) for row in rows))
        for i, header in enumerate(headers)
    ]
    header_line = (
        "| "
        + " | ".join(header.ljust(widths[i]) for i, header in enumerate(headers))
        + " |"
    )
    separator_line = "|" + "|".join("-" * (width + 2) for width in widths) + "|"

    if not rows:
        return f"{header_line}\n{separator_line}"

    data_lines = [
        "| " + " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)) + " |"
        for row in rows
    ]
    return "\n".join([header_line, separator_line, *data_lines])


def get_storage_str_representation(storage: dict[int, Product]) -> str:
    rows = [
        (
            str(product_id),
            str(product[NAME_KEY]),
            str(product[PRICE_KEY]),
            str(product[QUANTITY_KEY]),
        )
        for product_id, product in storage.items()
    ]
    return _format_table(TABLE_HEADERS, rows)


def get_stats_str_representation(registry: Registry) -> str:
    rows: list[tuple[str, ...]] = []
    for command_name, stats in registry.items():
        success = stats[SUCCESS_KEY]
        fails = stats[FAILS_KEY]
        total = success + fails
        success_rate = (success / total * 100) if total > 0 else 0.0
        rows.append((command_name, str(success), str(fails), f"{success_rate:.2f}%"))
    return _format_table(STATS_TABLE_HEADERS, rows)
