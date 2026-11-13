from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Final

from .storage import (
    NAME_KEY,
    PRICE_KEY,
    QUANTITY_KEY,
    Product,
)


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)
TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", NAME_KEY, PRICE_KEY, QUANTITY_KEY)


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return (" ".join(name.split())).lower()


def size_check(
    storage: dict[str, Product],
) -> dict[str, int]:  # находит нужные размеры столбцов
    column_size = {"ID": [2], NAME_KEY: [4], PRICE_KEY: [5], QUANTITY_KEY: [8]}
    for num, value in storage.items():
        column_size["ID"].append(len(str(num)))
        for prod in value:
            column_size[prod].append(len(str(value[prod])))
    return {name: max(column_size[name]) for name in column_size}


def output_line(
    values: tuple[Any, ...], size: dict[str, int]
) -> str:  # выводит строку таблицы
    if values[0] == "-":
        line = (
            "|"
            + "-" * (2 + size["ID"])
            + "|"
            + "-" * (2 + size[NAME_KEY])
            + "|"
            + "-" * (2 + size[PRICE_KEY])
            + "|"
            + "-" * (2 + size[QUANTITY_KEY])
            + "|"
        )
    else:
        line = "|"
        for ind in range(4):
            value = str(values[ind])
            line += f" {value} " + " " * (size[TABLE_HEADERS[ind]] - len(value)) + "|"
    print(line)
    return line


def tuple_with_dict(
    object: tuple[Any, dict[str, Any]],
) -> tuple[Any, ...]:  # Объект в корзине -> tuple
    rez = []
    for part in object:
        if isinstance(part, dict):
            for name in TABLE_HEADERS[1:]:
                rez.append(part[name])
        else:
            rez.append(part)
    return tuple(rez)


def get_storage_str_representation(storage: dict[str, Product]) -> str:
    final_size = size_check(storage)
    result = ""
    result += output_line(TABLE_HEADERS, final_size)
    result += output_line(tuple("-"), final_size)
    for prod in storage.items():
        result += output_line(tuple_with_dict(prod), final_size)
    return result
