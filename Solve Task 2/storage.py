from decimal import Decimal
from typing import Final

Product = tuple[int, str, Decimal, int]

PRODUCT_ID_INDEX: Final[int] = 0
NAME_INDEX: Final[int] = 1
PRICE_INDEX: Final[int] = 2
QUANTITY_INDEX: Final[int] = 3

PRODUCT_ID_MIN: Final[int] = 1
