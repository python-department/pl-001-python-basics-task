"""Standalone helpers shared by the hw4 storage and CRUD modules.

For now this is limited to money handling: :func:`normalize_price` rounds a
raw :class:`~decimal.Decimal` amount to the fixed number of fractional
digits (:data:`PRICE_PRECISION`) that every stored price uses, keeping
currency values free of binary floating-point error.
"""

from decimal import ROUND_HALF_UP, Decimal
from typing import Final


# TODO: задайте число знаков после запятой и шаг квантования
PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)


def normalize_price(price: Decimal) -> Decimal:
    """Round a price to the precision every stored record uses.

    Args:
        price: The raw price amount.

    Returns:
        ``price`` quantised to :data:`PRICE_PRECISION` fractional digits,
        with halves rounded up.
    """
    ratio = price / PRICE_STEP
    steps = ratio.quantize(Decimal("1."), rounding=ROUND_HALF_UP)
    real_price = steps * PRICE_STEP
    return real_price
