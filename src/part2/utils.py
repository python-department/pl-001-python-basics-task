from typing import Final
from decimal import Decimal, ROUND_HALF_UP


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)
def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)