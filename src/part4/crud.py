"""Create/read/update/delete operations over the in-memory product store.

Every operation takes the store -- a dictionary mapping product id to its
:data:`~src.part4.storage.Product` record -- as its first argument and
works on it in place. ``create_product``, ``update_product`` and
``delete_product`` additionally take ``product_names``, the ``set[str]``
of normalised names currently in ``storage`` (see
:mod:`src.part4.storage`), and keep it in sync with ``storage`` on
every successful call. The failure path never raises: the operation
prints an explanatory message to stdout and returns ``None``.

The identifier of a new product is a freshly generated UUID string
(:func:`generate_product_id`), independent of insertion order or of any
identifier already in ``storage``.

Every product name that reaches the store is passed through
:func:`~src.part4.utils.normalize_product_name` first. A name that
normalises to an empty string is rejected -- the operation prints a
message and changes nothing. Names are also kept unique --
:func:`create_product` refuses a normalised name that is already taken,
and :func:`update_product` refuses one that is already taken by another
product -- via an O(1) membership test against ``product_names`` rather
than a scan over ``storage.values()``.
"""

import uuid
from typing import Any

from .storage import (
    NAME_KEY,
    PRICE_KEY,
    QUANTITY_KEY,
    Product,
)
from .utils import normalize_price, normalize_product_name


def generate_product_id() -> str:
    return str(uuid.uuid4())


def create_product(
    storage: dict[str, Product],
    product_names: set[str],
    fields: dict[str, Any],
) -> str | None:
    name = normalize_product_name(fields[NAME_KEY])

    if not name:
        print("product name must not be blank")
        return None

    if name in product_names:
        print(f"product name '{name}' is already taken")
        return None

    product_id = generate_product_id()
    storage[product_id] = {
        NAME_KEY: name,
        PRICE_KEY: normalize_price(fields[PRICE_KEY]),
        QUANTITY_KEY: fields[QUANTITY_KEY],
    }
    product_names.add(name)
    return product_id


def read_product(
    storage: dict[str, Product],
    product_id: str,
) -> Product | None:
    product = storage.get(product_id)
    if product is None:
        print(f"no product with id {product_id}")
    return product


def update_product(
    storage: dict[str, Product],
    product_names: set[str],
    product_id: str,
    fields: dict[str, Any],
) -> Product | None:
    product = read_product(storage, product_id)
    if product is None:
        return None

    if NAME_KEY in fields:
        new_name = normalize_product_name(fields[NAME_KEY])
        fields[NAME_KEY] = new_name

        if not new_name:
            print("product name must not be blank")
            return None

        if new_name != product[NAME_KEY] and new_name in product_names:
            print(f"product name '{new_name}' is already taken")
            return None

    if PRICE_KEY in fields:
        fields[PRICE_KEY] = normalize_price(fields[PRICE_KEY])

    if NAME_KEY in fields:
        old_name = product[NAME_KEY]
        new_name = fields[NAME_KEY]
        if new_name != old_name:
            product_names.remove(old_name)
            product_names.add(new_name)
        product[NAME_KEY] = new_name

    if PRICE_KEY in fields:
        product[PRICE_KEY] = fields[PRICE_KEY]

    if QUANTITY_KEY in fields:
        product[QUANTITY_KEY] = fields[QUANTITY_KEY]

    return product


def delete_product(
    storage: dict[str, Product],
    product_names: set[str],
    product_id: str,
) -> str | None:
    product = read_product(storage, product_id)
    if product is None:
        return None

    del storage[product_id]
    product_names.remove(product[NAME_KEY])
    return product_id
