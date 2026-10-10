from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .storage import (
    Product
)


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)
TABLE_HEADERS: Final = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, ROUND_HALF_UP)

def normalize_product_name(name: str) -> str:
    return ' '.join(name.split()).lower()

def get_storage_str_representation(storage: list[Product]) -> str:
    col_width = [
        max(
            max([len(str(product[i])) for product in storage] + [0]), # + [0] во избежание
            len(TABLE_HEADERS[i])                                     # пустоты списка
        )
        for i in range(len(TABLE_HEADERS))
    ]
    rows_data = [TABLE_HEADERS] + storage
    rows = []
    for row_data in rows_data:
        row = '|'
        for i, cell_data in enumerate(row_data):
            cell = str(cell_data).ljust(col_width[i])
            row = row + ' ' + cell + ' |'
        rows.append(row)
    dividing_row_data = ['-' * (width + 2) for width in col_width]
    dividing_row = '|' + '|'.join(dividing_row_data) + '|'
    rows.insert(1, dividing_row)
    return '\n'.join(rows)