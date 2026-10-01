"""In-memory product store for the shop CRUD exercise.

The store is deliberately primitive: a plain list of tuples, with no
persistence, no indexing and no schema enforcement. Each element is a
:data:`Product` record -- a ``(product_id, name, price, quantity)`` tuple
where:

* ``product_id`` -- unique positive integer key, assigned by the create
  operation in :mod:`src.part2.crud`;
* ``name`` -- human-readable product name, unique across the store;
* ``price`` -- price of a single unit, held as a :class:`~decimal.Decimal`
  amount rounded to a fixed number of decimal places (see
  :func:`src.part2.utils.normalize_price`) so that money is never
  subject to binary floating-point error;
* ``quantity`` -- number of units currently in stock.

Field positions are exposed as ``*_INDEX`` constants so callers never
hard-code tuple offsets.
"""

from decimal import Decimal
from typing import Final


type Product = tuple[int, str, Decimal, int]

# TODO: задайте позиции полей внутри кортежа Product
PRODUCT_ID_INDEX: Final = 0
NAME_INDEX: Final = 0
PRICE_INDEX: Final = 0
QUANTITY_INDEX: Final = 0

# TODO: задайте идентификатор первого товара в пустом хранилище
PRODUCT_ID_MIN: Final[int] = 0
