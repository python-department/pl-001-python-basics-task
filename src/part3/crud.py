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
    if not len(storage):
        return PRODUCT_ID_MIN
    mid = 0
    for i in range(len(storage)):
        mid = max(mid, storage[i][PRODUCT_ID_INDEX])

    return mid + 1


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    fields = (normalize_product_name(fields[0]), fields[1], fields[2])

    if not len(fields[0]):
        print("product name must not be blank")
        return None

    for i in range(len(storage)):
        if fields[0] == storage[i][NAME_INDEX]:
            print(f"product name '{fields[0]}' is already taken")
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
    fields = (normalize_product_name(fields[0]), fields[1], fields[2])

    if not len(fields[0]):
        print("product name must not be blank")
        return None

    product_index = None
    for index, product in enumerate(storage):
        if product[PRODUCT_ID_INDEX] == product_id:
            product_index = index
            break

    if product_index is None:
        print(f"no product with id {product_id}")
        return None

    for i in range(len(storage)):
        if i != product_index and fields[0] == storage[i][NAME_INDEX]:
            print(f"product name '{fields[0]}' is already taken")
            return None

    obnow_product = (product_id, fields[0], normalize_price(fields[1]), fields[2])
    storage[product_index] = obnow_product
    return obnow_product


def delete_product(storage: list[Product], product_id: int) -> int | None:
    for i in range(len(storage)):
        if product_id == storage[i][PRODUCT_ID_INDEX]:
            storage.remove(storage[i])
            return product_id
    print(f"no product with id {product_id}")
    return None
