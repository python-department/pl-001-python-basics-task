"""In-memory product store for the shop CRUD exercise.

The store is deliberately primitive: a plain dictionary, with no
persistence and no schema enforcement. It maps a product's ``id`` -- a
UUID string assigned by the create operation in :mod:`src.part4.crud`
-- to its :data:`Product` record -- a dictionary with the keys ``name``,
``price`` and ``quantity`` -- where:

* the ``storage`` key itself -- unique string identifier, assigned by the
  create operation in :mod:`src.part4.crud`; it is not duplicated
  inside the record;
* ``name`` -- human-readable product name, unique across the store, held
  in normalised form (see
  :func:`src.part4.utils.normalize_product_name`);
* ``price`` -- price of a single unit, held as a :class:`~decimal.Decimal`
  amount rounded to a fixed number of decimal places (see
  :func:`src.part4.utils.normalize_price`) so that money is never
  subject to binary floating-point error;
* ``quantity`` -- number of units currently in stock.

Field names are exposed as ``*_KEY`` constants so callers never hard-code
the dictionary keys.

Every caller that mutates the store also threads along a second
structure, a ``set[str]`` of the normalised names currently in use --
see, for example, the ``product_names`` parameter of
:func:`src.part4.crud.create_product`. Keeping that name index as a
plain set passed next to ``storage``, rather than bundling the two into
an object, lets a name-uniqueness check become an O(1) membership test
against the set instead of a linear scan over ``storage.values()``. The
set must always mirror the normalised names present in ``storage``; the
functions in :mod:`src.part4.crud` keep the two in sync on every
successful create, update and delete.
"""

from typing import Any, Final


type Product = dict[str, Any]

# Name of each field inside a Product record.
# TODO: задайте имена полей записи
NAME_KEY: Final = ""
PRICE_KEY: Final = ""
QUANTITY_KEY: Final = ""
