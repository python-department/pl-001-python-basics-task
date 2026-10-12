"""Create/read/update/delete operations over the in-memory product store.

Every operation takes the store -- a list of
:data:`~src.part3.storage.Product` tuples -- as its first argument and
works on it in place. The failure path never raises: the operation prints
an explanatory message to stdout and returns ``None``.

The identifier of a new product is derived from the store itself
(:func:`generate_product_id`): one past the greatest identifier in use, or
:data:`~src.part3.storage.PRODUCT_ID_MIN` when the store is empty.

Every product name that reaches the store is passed through
:func:`~src.part3.utils.normalize_product_name` first. A name that
normalises to an empty string is rejected -- the operation prints a
message and changes nothing. Names are also kept unique --
:func:`create_product` refuses a normalised name that is already taken,
and :func:`update_product` refuses one that is already taken by another
product.
"""

from decimal import Decimal

from .storage import (
    NAME_INDEX,
    PRODUCT_ID_INDEX,
    PRODUCT_ID_MIN,
    Product,
)
from .utils import normalize_price, normalize_product_name


def generate_product_id(storage: list[Product]) -> int:
    if not storage:
        return PRODUCT_ID_MIN
    return max(p[PRODUCT_ID_INDEX] for p in storage) + 1


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    name = normalize_product_name(fields[0])
    if not name:
        print("product name must not be blank")
        return None
    if _name_taken(storage, name):
        print(f"product name '{name}' is already taken")
        return None

    product_id = generate_product_id(storage)
    storage.append((product_id, name, normalize_price(fields[1]), fields[2]))
    return product_id


def read_product(storage: list[Product], product_id: int) -> Product | None:
    for product in storage:
        if product[PRODUCT_ID_INDEX] == product_id:
            return product
    print(f"no product with id {product_id}")
    return None


def _find_index(storage: list[Product], product_id: int) -> int | None:
    return next(
        (
            i
            for i, product in enumerate(storage)
            if product[PRODUCT_ID_INDEX] == product_id
        ),
        None,
    )


def _name_taken(
    storage: list[Product], name: str, except_id: int | None = None
) -> bool:
    return any(
        product[NAME_INDEX] == name and product[PRODUCT_ID_INDEX] != except_id
        for product in storage
    )


def update_product(
    storage: list[Product],
    product_id: int,
    fields: tuple[str, Decimal, int],
) -> Product | None:
    name = normalize_product_name(fields[0])
    if not name:
        print("product name must not be blank")
        return None

    index = _find_index(storage, product_id)
    if index is None:
        print(f"no product with id {product_id}")
        return None

    if _name_taken(storage, name, except_id=product_id):
        print(f"product name '{name}' is already taken")
        return None

    updated = (product_id, name, normalize_price(fields[1]), fields[2])
    storage[index] = updated
    return updated


def delete_product(storage: list[Product], product_id: int) -> int | None:
    index = _find_index(storage, product_id)
    if index is None:
        print(f"no product with id {product_id}")
        return None
    del storage[index]
    return product_id
