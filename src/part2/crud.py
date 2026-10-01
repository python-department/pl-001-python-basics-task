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

from .storage import (  # noqa: F401
    NAME_INDEX,
    PRODUCT_ID_INDEX,
    PRODUCT_ID_MIN,
    Product,
)
from .utils import normalize_price  # noqa: F401


def generate_product_id(storage: list[Product]) -> int:
    if not storage:
        return PRODUCT_ID_MIN
    
    max_storage = max(product[PRODUCT_ID_INDEX] for product in storage) + 1
    return max_storage


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    name, price, quantity = fields
    for item in storage:
        if name == item[NAME_INDEX]:
            print(f"product name '{name}' is already taken")
            return None
    
    new_id = generate_product_id(storage)
    new_price = normalize_price(price)
    new_product = (new_id, name, new_price, quantity)
    storage.append(new_product)
    return new_id


def read_product(storage: list[Product], product_id: int) -> Product | None:
    for i in range(len(storage)):
        if storage[i][PRODUCT_ID_INDEX] == product_id:
            return storage[i]

    print(f"no product with id {product_id}")
    return None


def update_product(
    storage: list[Product],
    product_id: int,
    fields: tuple[str, Decimal, int],
) -> Product | None:
    name, price, quantity = fields
    for i in range(len(storage)):
        if product_id == storage[i][PRODUCT_ID_INDEX]:
            new_price = normalize_price(price)
            new_item = (product_id, name, new_price, quantity)
            storage[i] = new_item
            return new_item

    print(f"no product with id '{product_id}'")
    return None

    
def delete_product(storage: list[Product], product_id: int) -> int | None:
    for item in storage:
        if item[PRODUCT_ID_INDEX] == product_id:
            storage.remove(item)
            return product_id
    
    print(f"no product with id '{product_id}'")
    return None

