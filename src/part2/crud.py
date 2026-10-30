# Create/read/update/delete operations over the in-memory product store.

import sys
from decimal import Decimal

from .storage import (
    NAME_INDEX,
    PRODUCT_ID_INDEX,
    PRODUCT_ID_MIN,
    Product,
)
from .utils import normalize_price


def generate_product_id(storage: list[Product]) -> int:
    # Choose the identifier for the next product added to ``storage``.
    if not storage:
        return PRODUCT_ID_MIN
    return max(p[PRODUCT_ID_INDEX] for p in storage) + 1


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    # Append a new product to ``storage`` and return its new identifier.
    name, price, quantity = fields

    # Проверка уникальности имени
    for product in storage:
        if product[NAME_INDEX] == name:
            print(f"product name '{name}' is already taken", file=sys.stdout)
            return None

    product_id = generate_product_id(storage)
    norm_price = normalize_price(price)

    new_product: Product = (product_id, name, norm_price, quantity)
    storage.append(new_product)
    return product_id


def read_product(storage: list[Product], product_id: int) -> Product | None:
    # Return the product stored under ``product_id``.
    for product in storage:
        if product[PRODUCT_ID_INDEX] == product_id:
            return product

    print(f"no product with id {product_id}", file=sys.stdout)
    return None


def update_product(
    storage: list[Product],
    product_id: int,
    fields: tuple[str, Decimal, int],
) -> Product | None:
    # Overwrite the fields of the product stored under ``product_id``.
    name, price, quantity = fields

    for i, product in enumerate(storage):
        if product[PRODUCT_ID_INDEX] == product_id:
            norm_price = normalize_price(price)
            updated_product: Product = (product_id, name, norm_price, quantity)
            storage[i] = updated_product
            return updated_product

    print(f"no product with id {product_id}", file=sys.stdout)
    return None


def delete_product(storage: list[Product], product_id: int) -> int | None:
    # Remove the product stored under ``product_id`` from ``storage``.
    for i, product in enumerate(storage):
        if product[PRODUCT_ID_INDEX] == product_id:
            storage.pop(i)
            return product_id

    print(f"no product with id {product_id}", file=sys.stdout)
    return None
