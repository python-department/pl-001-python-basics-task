from decimal import Decimal

from storage import (
    Product,
    PRODUCT_ID_INDEX,
    NAME_INDEX,
    PRICE_INDEX,
    QUANTITY_INDEX,
    PRODUCT_ID_MIN,
)
from utils import normalize_price


def generate_product_id(storage: list[Product]) -> int:
    if not storage:
        return PRODUCT_ID_MIN
    max_id = storage[0][PRODUCT_ID_INDEX]
    for product in storage:
        if product[PRODUCT_ID_INDEX] > max_id:
            max_id = product[PRODUCT_ID_INDEX]
    return max_id + 1


def create_product(
    storage: list[Product],
    fields: tuple[str, Decimal, int],
) -> int | None:
    name, price, quantity = fields
    for product in storage:
        if product[NAME_INDEX] == name:
            print(f"product name '{name}' is already taken.")
            return None
    product_id = generate_product_id(storage)
    storage.append((product_id, name, normalize_price(price), quantity))
    return product_id


def read_product(storage: list[Product], product_id: int) -> Product | None:
    for product in storage:
        if product[PRODUCT_ID_INDEX] == product_id:
            return product
    print(f"no product with id {product_id}")
    return None


def update_product(
    storage: list[Product],
    product_id: int,
    fields: tuple[str, Decimal, int],
) -> Product | None:
    name, price, quantity = fields
    for index in range(len(storage)):
        if storage[index][PRODUCT_ID_INDEX] == product_id:
            storage[index] = (product_id, name, normalize_price(price), quantity)
            return storage[index]
    print(f"no product with id {product_id}")
    return None


def delete_product(storage: list[Product], product_id: int) -> int | None:
    for index in range(len(storage)):
        if storage[index][PRODUCT_ID_INDEX] == product_id:
            del storage[index]
            return product_id
    print(f"no product with id {product_id}")
    return None