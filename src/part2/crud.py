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
    mx = max(product[PRODUCT_ID_INDEX] for product in storage) + 1

    return mx


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    for product in storage:
        if product[NAME_INDEX] == fields[0]:
            print(f"product name {product[NAME_INDEX]} is already taken.")
            return None

    product_id = generate_product_id(storage)
    name, price, quantity = fields
    new_product = (product_id, name, normalize_price(price), quantity)

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
    for i in range(len(storage)):
        if storage[i][PRODUCT_ID_INDEX] == product_id:
            name, price, quality = fields
            new_product = (product_id, name, normalize_price(price), quality)
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
