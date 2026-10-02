from decimal import ROUND_HALF_UP, Decimal
from typing import Final


# TODO: задайте число знаков после запятой и шаг квантования
PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)
