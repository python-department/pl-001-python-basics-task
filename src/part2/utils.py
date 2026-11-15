from decimal import ROUND_HALF_UP, Decimal
from typing import Final


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)


def normalize_price(price: Decimal) -> Decimal:
    """Для себя: метод number.quantize(step, rounding=round) округляет число
    до состояния number.step знаков после запятой с точностью округления round
    """
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)
