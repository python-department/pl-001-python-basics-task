"""Standalone helpers shared by the hw4 storage and CRUD modules.

from decimal import ROUND_HALF_UP, Decimal
from typing import Final


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)


def normalize_price(price: Decimal) -> Decimal:
    # Round a price to the precision every stored record uses.
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)
