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
    mx = max(product[PRODUCT_ID_INDEX] for product in storage) + 1

    return mx


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    correct_name = normalize_product_name(fields[0])

    if correct_name == "":
        print("product name must not be blank")
        return None

    for product in storage:
        if product[NAME_INDEX] == correct_name:
            print(f"product name '{correct_name}' is already taken")
            return None

    product_id = generate_product_id(storage)
    _, price, quantity = fields
    new_product = (product_id, correct_name, normalize_price(price), quantity)

    storage.append(new_product)

    return product_id


def read_product(storage: list[Product], product_id: int) -> Product | None:
    for product in storage:
        if product[PRODUCT_ID_INDEX] == product_id:
            return product

    print(f"no product with id <{product_id}>")
    return None


def update_product(
    storage: list[Product],
    product_id: int,
    fields: tuple[str, Decimal, int],
) -> Product | None:
    correct_name = normalize_product_name(fields[0])
    flag = False
    if correct_name == "":
        print("product name must not be blank")
        return None

    for i in range(len(storage)):
        product = storage[i]
        if product_id == product[PRODUCT_ID_INDEX]:
            flag = True

    if not flag:
        print(f"no product with id <{product_id}>")
        return None

    for product in storage:
        if (
            product[NAME_INDEX] == correct_name
            and product_id != product[PRODUCT_ID_INDEX]
        ):
            print(f"product name '{correct_name}' is already taken")
            return None

    for i in range(len(storage)):
        product = storage[i]
        if product_id == product[PRODUCT_ID_INDEX]:
            new_product = (
                product_id,
                correct_name,
                normalize_price(fields[1]),
                fields[2],
            )
            storage[i] = new_product

            return new_product

    print(f"no product with id <{product_id}>")
    return None


def delete_product(storage: list[Product], product_id: int) -> int | None:
    for product in storage:
        if product[PRODUCT_ID_INDEX] == product_id:
            storage.remove(product)
            return product_id

    print(f"no product with id <{product_id}>")
    return None
