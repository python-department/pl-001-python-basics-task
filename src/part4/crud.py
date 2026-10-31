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
    form_name = normalize_product_name(fields[NAME_KEY])
    if not form_name:
        print("product name must not be blank")
        return None

    if form_name in product_names:
        print(f"product name {form_name!r} is already taken")
        return None

    new_id = generate_product_id()
    form_price = normalize_price(fields[PRICE_KEY])
    normalized_fields = {
        NAME_KEY: form_name,
        PRICE_KEY: form_price,
        QUANTITY_KEY: fields[QUANTITY_KEY],
    }
    storage[new_id] = normalized_fields
    product_names.add(form_name)
    return new_id


def read_product(storage: dict[str, Product], product_id: str) -> Product | None:
    if product_id in storage:
        return storage[product_id]

    print(f"no product with id {product_id}")
    return None


def update_product(
    storage: dict[str, Product],
    product_names: set[str],
    product_id: str,
    fields: dict[str, Any],
) -> Product | None:
    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None
    curr_product = storage[product_id]
    curr_name = curr_product[NAME_KEY]

    if NAME_KEY in fields:
        form_name = normalize_product_name(fields[NAME_KEY])
        if not form_name:
            print("product name must not be blank")
            return None

        if form_name != curr_name and form_name in product_names:
            print(f"product name {form_name!r} is already taken")
            return None

        fields[NAME_KEY] = form_name

    if PRICE_KEY in fields:
        form_price = normalize_price(fields[PRICE_KEY])
        fields[PRICE_KEY] = form_price

    if NAME_KEY in fields and fields[NAME_KEY] != curr_name:
        product_names.remove(curr_name)
        product_names.add(fields[NAME_KEY])

    curr_product.update(fields)
    return curr_product


def delete_product(
    storage: dict[str, Product],
    product_names: set[str],
    product_id: str,
) -> str | None:
    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None

    product = storage.pop(product_id)
    product_names.remove(product[NAME_KEY])
    return product_id
