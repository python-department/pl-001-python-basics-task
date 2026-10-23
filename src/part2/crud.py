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

    max_id = 0
    for product in storage:
        current_id = int(product[PRODUCT_ID_INDEX])
        max_id = max(current_id, max_id)
    return max_id + 1


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    name, price, quantity = fields
    for product in storage:
        if product[NAME_INDEX] == name:
            print(f"Product name '{name}' is already taken")
            return None

    new_id = generate_product_id(storage)
    normalized_price = normalize_price(price)
    storage.append((new_id, name, normalized_price, quantity))
    return new_id


def read_product(storage: list[Product], product_id: int) -> Product | None:
    for product in storage:
        if product[PRODUCT_ID_INDEX] == product_id:
            return product
    print(f"No product with id {product_id}")
    return None


def update_product(
    storage: list[Product],
    product_id: int,
    fields: tuple[str, Decimal, int],
) -> Product | None:
    name, price, quantity = fields
    normalized_price = normalize_price(price)
    for i in range(len(storage)):
        if storage[i][PRODUCT_ID_INDEX] == product_id:
            updated_product = (product_id, name, normalized_price, quantity)
            storage[i] = updated_product
            return updated_product
    print(f"No product with id {product_id}")
    return None


def delete_product(storage: list[Product], product_id: int) -> int | None:
    for i in range(len(storage)):
        if storage[i][PRODUCT_ID_INDEX] == product_id:
            del storage[i]
            return product_id
    print(f"No product with id {product_id}")
    return None
