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
    return max(product[PRODUCT_ID_INDEX] for product in storage) + 1


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:

    name, price, quantity = fields

    if any(product[NAME_INDEX] == name for product in storage):
        print(f"product name {name} is already taken.")
        return None

    new_product_id = generate_product_id(storage)

    normalized_price = normalize_price(price)

    new_product = (new_product_id, name, normalized_price, quantity)
    storage.append(new_product)
    return new_product_id


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
    normalized_price = normalize_price(price)

    for i, product in enumerate(storage):
        if product[PRODUCT_ID_INDEX] == product_id:
            updated = (product_id, name, normalized_price, quantity)
            storage[i] = updated
            return updated

    print(f"no product with id {product_id}")
    return None


def delete_product(storage: list[Product], product_id: int) -> int | None:

    for product in storage:
        if product[PRODUCT_ID_INDEX] == product_id:
            storage.remove(product)
            return product_id

    print(f"no product with id {product_id}")
    return None
