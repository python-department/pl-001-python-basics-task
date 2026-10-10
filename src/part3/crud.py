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
    if len(storage) == 0:
        return PRODUCT_ID_MIN
    return max(product[PRODUCT_ID_INDEX] for product in storage) + 1


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    name, price, quantity = fields
    name = normalize_product_name(name)
    if name == "":
        return print("product name must not be blank")
    if name in [product[NAME_INDEX] for product in storage]:
        return print(f"product name '{name}' is already taken")
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

    name, price, quantity = fields
    name = normalize_product_name(name)
    if name == "":
        return print("product name must not be blank")

    for index, product in enumerate(storage):
        if product[PRODUCT_ID_INDEX] == product_id:
            for other_product in storage:
                if (
                    other_product[NAME_INDEX] == name
                    and other_product[PRODUCT_ID_INDEX] != product_id
                ):
                    return print(f"product name '{name}' is already taken")

            price = normalize_price(price)
            updated_product = (product_id, name, price, quantity)
            storage[index] = updated_product
            return updated_product
    return print(f"no product with id {product_id}")


def delete_product(storage: list[Product], product_id: int) -> int | None:
    for product in storage:
        if product[PRODUCT_ID_INDEX] == product_id:
            storage.remove(product)
            return product_id
    return print(f"no product with id {product_id}")
