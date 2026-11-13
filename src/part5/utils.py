from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Final

from .decorators import Registry
from .storage import (
    NAME_KEY,
    PRICE_KEY,
    QUANTITY_KEY,
    Product,
)


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)

TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", NAME_KEY, PRICE_KEY, QUANTITY_KEY)
STATS_TABLE_HEADERS: Final[tuple[str, ...]] = (
    "command name",
    "success",
    "fails",
    "success rate",
)


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return (" ".join(name.split())).lower()


def size_check(
    storage: dict[Any, dict[str, Any]], headers: tuple[str, ...]
) -> dict[str, int]:  # находит нужные размеры столбцов

    column_size = {}
    for item in headers:
        column_size[item] = [len(item)]

    for name, values in storage.items():
        column_size[headers[0]].append(len(str(name)))
        for prod in values:
            column_size[prod].append(len(str(values[prod])))

    return {name: max(column_size[name]) for name in column_size}


def output_line(
    values: tuple[Any, ...], size: dict[Any, int], headers: tuple[str, ...]
) -> str:  # выводит строку таблицы
    if values[0] == "-":
        line = (
            "|"
            + "-" * (2 + size[headers[0]])
            + "|"
            + "-" * (2 + size[headers[1]])
            + "|"
            + "-" * (2 + size[headers[2]])
            + "|"
            + "-" * (2 + size[headers[3]])
            + "|"
        )
    else:
        line = "|"
        for ind in range(len(values)):
            value = str(values[ind])
            line += f" {value} " + " " * (size[headers[ind]] - len(value)) + "|"

        if len(values) == 3:
            if values[1] + values[2] == 0:
                line += " 0.00% " + " " * (size[headers[ind]] - len(value)) + "|"
            else:
                value = round(values[1] / (values[1] + values[2]), 4)
                line += (
                    f" {f'{value:.2%}'} "
                    + " " * (size[headers[ind]] - len(f"{value:.2%}"))
                    + "|"
                )

    print(line)
    return line + "\n"


def tuple_with_dict(
    object: tuple[Any, dict[str, Any]],
    headers: tuple[str, ...],
) -> tuple[Any, ...]:  # Объект в корзине -> tuple
    rez = []
    for part in object:
        if isinstance(part, dict):
            if headers is STATS_TABLE_HEADERS:
                for name in headers[1:-1]:
                    rez.append(part[name])
            else:
                for name in headers[1:]:
                    rez.append(part[name])
        else:
            rez.append(part)
    return tuple(rez)


def get_storage_str_representation(storage: dict[int, Product]) -> str:
    result = ""
    final_size = size_check(storage, TABLE_HEADERS)
    result += output_line(TABLE_HEADERS, final_size, TABLE_HEADERS)
    result += output_line(tuple("-"), final_size, TABLE_HEADERS)
    for prod in storage.items():
        result += output_line(
            tuple_with_dict(prod, TABLE_HEADERS), final_size, TABLE_HEADERS
        )
    return result


def get_stats_str_representation(registry: Registry) -> str:
    result = ""
    final_size = size_check(registry, STATS_TABLE_HEADERS)
    result += output_line(STATS_TABLE_HEADERS, final_size, STATS_TABLE_HEADERS)
    result += output_line(tuple("-"), final_size, STATS_TABLE_HEADERS)
    for line in registry.items():
        result += output_line(
            tuple_with_dict(line, STATS_TABLE_HEADERS), final_size, STATS_TABLE_HEADERS
        )

    return result
