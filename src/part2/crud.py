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
    res = (max(storage, key=lambda prod: prod[PRODUCT_ID_INDEX]))[PRODUCT_ID_INDEX] + 1
    return res


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    if any(prod[NAME_INDEX] == fields[0] for prod in storage):
        print(f"product name {fields[0]} is already taken")
        return None
    cur_id = generate_product_id(storage)
    result: Product = (cur_id, fields[0], normalize_price(fields[1]), fields[2])
    storage.append(result)
    return cur_id


def read_product(storage: list[Product], product_id: int) -> Product | None:
    for prod in storage:
        if prod[PRODUCT_ID_INDEX] == product_id:
            return prod
    print(f"no product with id {product_id}")
    return None


def update_product(
    storage: list[Product],
    product_id: int,
    fields: tuple[str, Decimal, int],
) -> Product | None:
    for ind in range(len(storage)):
        if storage[ind][PRODUCT_ID_INDEX] == product_id:
            new_product: Product = (
                product_id,
                fields[0],
                normalize_price(fields[1]),
                fields[2],
            )
            storage[ind] = new_product
            return storage[ind]
    print(f"no product with id {product_id}")
    return None


def delete_product(storage: list[Product], product_id: int) -> int | None:
    for ind in range(len(storage)):
        if storage[ind][PRODUCT_ID_INDEX] == product_id:
            del storage[ind]
            return product_id
    print(f"no product with id {product_id}")
    return None
