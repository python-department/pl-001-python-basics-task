"""Create/read/update/delete operations over the in-memory product store.

Every operation takes the store -- a list of
:data:`~src.part2.storage.Product` tuples -- as its first argument and
works on it in place. The failure path never raises: the operation prints
an explanatory message to stdout and returns ``None``.

The identifier of a new product is derived from the store itself
(:func:`generate_product_id`): one past the greatest identifier in use, or
:data:`~src.part2.storage.PRODUCT_ID_MIN` when the store is empty.
Product names are kept unique -- :func:`create_product` refuses a name that
is already taken.
"""

from decimal import Decimal

from .storage import (
    NAME_INDEX,
    PRODUCT_ID_INDEX,
    PRODUCT_ID_MIN,
    Product,
)
from .utils import normalize_price


def generate_product_id(storage: list[Product]) -> int:
    if not len(storage):
        return PRODUCT_ID_MIN
    mid = 0
    for i in range(len(storage)):
        mid = max(mid, storage[i][PRODUCT_ID_INDEX])

    return mid + 1


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    for i in range(len(storage)):
        if fields[0] == storage[i][NAME_INDEX]:
            print(f"product name {fields[0]} is already taken")
            return None
    id = generate_product_id(storage)
    cena = normalize_price(fields[1])
    product = (id, fields[0], cena, fields[2])
    storage.append(product)
    return id


def read_product(storage: list[Product], product_id: int) -> Product | None:
    for i in range(len(storage)):
        if product_id == storage[i][PRODUCT_ID_INDEX]:
            return storage[i]
    print(f"no product with id {product_id}")
    return None


def update_product(
    storage: list[Product],
    product_id: int,
    fields: tuple[str, Decimal, int],
) -> Product | None:
    for i in range(len(storage)):
        if product_id == storage[i][PRODUCT_ID_INDEX]:
            storage[i] = (
                product_id,
                fields[0],
                normalize_price(fields[1]),
                fields[2],
            )
            return storage[i]
    print(f"no product with id {product_id}")
    return None


def delete_product(storage: list[Product], product_id: int) -> int | None:
    for i in range(len(storage)):
        if product_id == storage[i][PRODUCT_ID_INDEX]:
            storage.remove(storage[i])
            return product_id
    print(f"no product with id {product_id}")
    return None
