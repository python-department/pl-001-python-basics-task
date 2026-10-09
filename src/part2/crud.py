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
    if not storage:
        return PRODUCT_ID_MIN
    return max(product[PRODUCT_ID_INDEX] for product in storage) + 1


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    if fields[0] in (product[NAME_INDEX] for product in storage):
        print(f'The name "{fields[0]}" is already used')
        return None

    product_id = generate_product_id(storage)
    storage.append((product_id, fields[0], normalize_price(fields[1]), fields[2]))
    return product_id


def read_product(storage: list[Product], product_id: int) -> Product | None:
    for product in storage:
        if product[PRODUCT_ID_INDEX] == product_id:
            return product
    print(f"no product with id {product_id}")
    return None


def update_product(
    storage: list[Product],
    product_id: int,
    fields: tuple[str, Decimal, int],
) -> Product | None:
    id_list = [product[PRODUCT_ID_INDEX] for product in storage]

    if product_id not in id_list:
        print(f"no product with id {product_id}")
        return None

    for old_product in storage:
        if product_id == old_product[PRODUCT_ID_INDEX]:
            new_product = (product_id, fields[0], normalize_price(fields[1]), fields[2])
            storage.append(new_product)
            storage.remove(old_product)
            break
    return new_product


def delete_product(storage: list[Product], product_id: int) -> int | None:
    for product in storage:
        if product[PRODUCT_ID_INDEX] == product_id:
            storage.remove(product)
            return product[PRODUCT_ID_INDEX]

    print(f"no product with id {product_id}")
    return None
