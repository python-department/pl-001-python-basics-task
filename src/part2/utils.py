from decimal import ROUND_HALF_UP, Decimal
from typing import Final


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)


def normalize_price(price: Decimal) -> Decimal:
    correct_price = price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)

    return correct_price
