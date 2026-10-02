"""Standalone helpers shared by the hw4 storage and CRUD modules.

For now this is limited to money handling: :func:`normalize_price` rounds a
raw :class:`~decimal.Decimal` amount to the fixed number of fractional
digits (:data:`PRICE_PRECISION`) that every stored price uses, keeping
currency values free of binary floating-point error.
"""

from decimal import ROUND_HALF_UP, Decimal
from typing import Final


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, ROUND_HALF_UP)
