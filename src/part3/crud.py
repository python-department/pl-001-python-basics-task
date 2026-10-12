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


def product_in_storage(storage: list[Product], product_id: int) -> int | None:
    for product in storage:
        if product[PRODUCT_ID_INDEX] == product_id:
            return storage.index(product)
    return None


def generate_product_id(storage: list[Product]) -> int:
    if not storage:
        return PRODUCT_ID_MIN
    return max(product[PRODUCT_ID_INDEX] for product in storage) + 1


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    name, price, quantity = fields

    product_name = normalize_product_name(name)
    if not product_name:
        print("product name must not be blank")
        return None
    for product in storage:
        if product[NAME_INDEX] == product_name:
            print(f"product name '{product_name}' is already taken")
            return None

    product_id = generate_product_id(storage)
    product_price = normalize_price(price)
    new_product = (product_id, product_name, product_price, quantity)
    storage.append(new_product)
    return product_id


def read_product(storage: list[Product], product_id: int) -> Product | None:
    product_index = product_in_storage(storage, product_id)
    if product_index is not None:
        return storage[product_index]

    print(f"no product with id {product_id}")
    return None


def update_product(
    storage: list[Product],
    product_id: int,
    fields: tuple[str, Decimal, int],
) -> Product | None:
    name, price, quantity = fields
    normalize_name = normalize_product_name(name)
    if not normalize_name:
        print("product name must not be blank")
        return None

    product_index = product_in_storage(storage, product_id)
    if product_index is None:
        print(f"no product with id {product_id}")
        return None

    for product in storage:
        if (product[NAME_INDEX] == normalize_name) and (
            product_id != product[PRODUCT_ID_INDEX]
        ):
            print(f"product name '{normalize_name}' is already taken")
            return None

    new_price = normalize_price(price)
    updated_product = (product_id, normalize_name, new_price, quantity)
    storage[product_index] = updated_product
    return updated_product


def delete_product(storage: list[Product], product_id: int) -> int | None:
    product_index = product_in_storage(storage, product_id)
    if product_index is not None:
        del storage[product_index]
        return product_id

    print(f"no product with id {product_id}")
    return None
