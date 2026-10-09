from decimal import Decimal
from typing import Final


type Product = tuple[int, str, Decimal, int]

# TODO: задайте позиции полей внутри кортежа Product
PRODUCT_ID_INDEX: Final = 0
NAME_INDEX: Final = 1
PRICE_INDEX: Final = 2
QUANTITY_INDEX: Final = 3

# TODO: задайте идентификатор первого товара в пустом хранилище
PRODUCT_ID_MIN: Final[int] = 1
