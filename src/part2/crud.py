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
    if len(storage) == 0:
        return PRODUCT_ID_MIN
    return max(product[PRODUCT_ID_INDEX] for product in storage) + 1


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    name, price, quantity = fields
    if name in [product[NAME_INDEX] for product in storage]:
        return print(f"product name {name} is already taken")
    new_id = generate_product_id(storage)
    price = normalize_price(price)
    product = (new_id, name, price, quantity)
    storage.append(product)
    return new_id


def read_product(storage: list[Product], product_id: int) -> Product | None:
    for product in storage:
        if product[PRODUCT_ID_INDEX] == product_id:
            return product
    return print(f"no product with id {product_id}")


def update_product(
    storage: list[Product],
    product_id: int,
    fields: tuple[str, Decimal, int],
) -> Product | None:
    for product in storage:
        if product[PRODUCT_ID_INDEX] == product_id:
            name, price, quantity = fields
            price = normalize_price(price)
            updated_product = (product_id, name, price, quantity)
            storage[storage.index(product)] = updated_product
            return updated_product
    return print(f"no product with id {product_id}")


def delete_product(storage: list[Product], product_id: int) -> int | None:
    for product in storage:
        if product[PRODUCT_ID_INDEX] == product_id:
            storage.remove(product)
            return product_id
    return print(f"no product with id {product_id}")
