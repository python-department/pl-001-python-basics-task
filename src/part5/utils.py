from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .decorators import Registry
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
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return " ".join(name.split()).lower()


def _render_table(
    headers: tuple[str, ...],
    rows: list[tuple[str, ...]],
) -> str:
    columns_lengths_sets: list[set[int]] = [{len(header)} for header in headers]

    for row in rows:
        for index, cell in enumerate(row):
            columns_lengths_sets[index].add(len(cell))

    final_widths: list[int] = [max(length_set) for length_set in columns_lengths_sets]

    header_parts = [
        headers[index].ljust(final_widths[index]) for index in range(len(headers))
    ]
    header_line = f"| {' | '.join(header_parts)} |"

    separating_parts = ["-" * (length + 2) for length in final_widths]
    separating_line = f"|{'|'.join(separating_parts)}|"

    table = [header_line, separating_line]

    for row in rows:
        row_parts = [
            row[index].ljust(final_widths[index]) for index in range(len(headers))
        ]
        table.append(f"| {' | '.join(row_parts)} |")

    return "\n".join(table)


def number_length(value: Decimal | float) -> int:
    return len(str(value))


def get_storage_str_representation(storage: dict[int, Product]) -> str:
    columns_lengths_sets: list[set[int]] = [set() for _ in range(4)]

    for index, header in enumerate(TABLE_HEADERS):
        columns_lengths_sets[index].add(len(header))

    if storage:
        for product_id, product in storage.items():
            columns_lengths_sets[0].add(number_length(product_id))
            columns_lengths_sets[1].add(len(str(product[NAME_KEY])))
            columns_lengths_sets[2].add(number_length(product[PRICE_KEY]))
            columns_lengths_sets[3].add(number_length(product[QUANTITY_KEY]))

    final_widths: list[int] = [max(length_set) for length_set in columns_lengths_sets]

    header_parts = [
        TABLE_HEADERS[index].ljust(final_widths[index])
        for index in range(len(TABLE_HEADERS))
    ]
    header_line = f"| {' | '.join(header_parts)} |"

    separating_parts = ["-" * (length + 2) for length in final_widths]
    separating_line = f"|{'|'.join(separating_parts)}|"

    table = [header_line, separating_line]

    if not storage:
        return "\n".join(table)

    for product_id, product in storage.items():
        line = (
            f"| {str(product_id).ljust(final_widths[0])} | "
            f"{str(product[NAME_KEY]).ljust(final_widths[1])} | "
            f"{str(product[PRICE_KEY]).ljust(final_widths[2])} | "
            f"{str(product[QUANTITY_KEY]).ljust(final_widths[3])} |"
        )
        table.append(line)

    return "\n".join(table)


def get_stats_str_representation(registry: Registry) -> str:
    rows: list[tuple[str, ...]] = []
    for command_name, counters in registry.items():
        success_count = counters["success"]
        fails_count = counters["fails"]
        total_calls = success_count + fails_count

        if total_calls == 0:
            rate_str = "0.00%"
        else:
            rate = (success_count / total_calls) * 100
            rate_str = f"{rate:.2f}%"

        rows.append(
            (
                command_name,
                str(success_count),
                str(fails_count),
                rate_str,
            )
        )

    return _render_table(STATS_TABLE_HEADERS, rows)
