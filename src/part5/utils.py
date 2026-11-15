from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .decorators import (
    FAILS_KEY,
    SUCCESS_KEY,
    Registry,
)
from .storage import NAME_KEY, PRICE_KEY, QUANTITY_KEY, Product


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final[Decimal] = Decimal(1).scaleb(-PRICE_PRECISION)

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
    return " ".join(name.split()).lower()


def _format_table(
    headers: tuple[str, ...],
    rows: list[list[str]],
) -> str:

    widths = [
        max(len(headers[i]), *(len(row[i]) for row in rows))
        if rows
        else len(headers[i])
        for i in range(len(headers))
    ]

    header = (
        "| "
        + " | ".join(headers[i].ljust(widths[i]) for i in range(len(headers)))
        + " |"
    )

    separator = "|" + "|".join("-" * (width + 2) for width in widths) + "|"

    data_rows = [
        "| " + " | ".join(row[i].ljust(widths[i]) for i in range(len(headers))) + " |"
        for row in rows
    ]

    return "\n".join([header, separator, *data_rows])


def get_storage_str_representation(
    storage: dict[int, Product],
) -> str:

    rows = [
        [
            str(product_id),
            product[NAME_KEY],
            str(product[PRICE_KEY]),
            str(product[QUANTITY_KEY]),
        ]
        for product_id, product in storage.items()
    ]

    return _format_table(TABLE_HEADERS, rows)


def get_stats_str_representation(registry: Registry) -> str:

    rows = []

    for command, stats in registry.items():
        success = stats[SUCCESS_KEY]
        fails = stats[FAILS_KEY]
        total = success + fails

        if total == 0:
            success_rate = "0.00%"
        else:
            success_rate = f"{success / total * 100:.2f}%"

        rows.append(
            [
                command,
                str(success),
                str(fails),
                success_rate,
            ]
        )

    return _format_table(STATS_TABLE_HEADERS, rows)
