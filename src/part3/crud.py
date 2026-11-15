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

    max_storage = max(product[PRODUCT_ID_INDEX] for product in storage) + 1
    return max_storage


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    name, price, quantity = fields
    new_name = normalize_product_name(name)
    if not new_name:
        print("product name must not be blank")
        return None

    for item in storage:
        if new_name == item[NAME_INDEX]:
            print(f"product name '{new_name}' is already taken")
            return None

    new_id = generate_product_id(storage)
    new_price = normalize_price(price)
    new_product = (new_id, new_name, new_price, quantity)
    storage.append(new_product)
    return new_id


def read_product(storage: list[Product], product_id: int) -> Product | None:
    for i in range(len(storage)):
        if storage[i][PRODUCT_ID_INDEX] == product_id:
            return storage[i]

    print(f"no product with id '{product_id}'")
    return None


def update_product(
    storage: list[Product],
    product_id: int,
    fields: tuple[str, Decimal, int],
) -> Product | None:
    name, price, quantity = fields
    new_name = normalize_product_name(name)
    if not new_name:
        print("product name must not be blank")
        return None

    f = False
    for i in range(len(storage)):
        if product_id == storage[i][PRODUCT_ID_INDEX]:
            f = True
            break
    if f == False:
        print(f"no product with id {product_id}")
        return None

    for i in range(len(storage)):
        if (
            new_name == storage[i][NAME_INDEX]
            and product_id != storage[i][PRODUCT_ID_INDEX]
        ):
            print(f"product name '{new_name}' is already taken")
            return None

    for i in range(len(storage)):
        if product_id == storage[i][PRODUCT_ID_INDEX]:
            new_price = normalize_price(price)
            new_item = (product_id, new_name, new_price, quantity)
            storage[i] = new_item
            return new_item

    return None


def delete_product(storage: list[Product], product_id: int) -> int | None:
    for item in storage:
        if item[PRODUCT_ID_INDEX] == product_id:
            storage.remove(item)
            return product_id

    print(f"no product with id '{product_id}'")
    return None
