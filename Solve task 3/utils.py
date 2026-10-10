from decimal import ROUND_HALF_UP, Decimal
from typing import Final
from storage import Product

PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)
TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return (" ".join(name.split())).lower()


def size_check(storage: list[Product]):#находит нужные размеры столбцов
    column_size = [[2], [4], [5], [8]]
    for prod in storage:
        for ind in range (4):
            column_size[ind].append(len(str(prod[ind])))
    return [max(column_size[i]) for i in range(4)]

def output_line(values: str|Product, size: list[int]):#выводит строку таблицы
    if values == "-":
        line = ("|" + "-" * (2 + size[0]) + "|" + "-" * (2 + size[1]) + 
                "|" + "-" * (2 + size[2]) + "|" + "-" * (2 + size[3]) + "|")
    else:
        line = "|"
        for ind in range(4):
            value = str(values[ind])
            line += f" {value} " + " " * (size[ind] - len(value)) + "|"
    print (line)

def get_storage_str_representation(storage: list[Product]) -> str:
    final_size = size_check(storage)
    output_line(TABLE_HEADERS, final_size)
    output_line("-", final_size)
    for prod in storage:
        output_line(prod, final_size)