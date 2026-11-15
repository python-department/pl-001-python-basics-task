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


def _find_index(storage: list[Product], product_id: int) -> int | None:
    for i, product in enumerate(storage):
        if product[PRODUCT_ID_INDEX] == product_id:
            return i
    return None


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:

    name, price, quantity = fields
    if any(product[NAME_INDEX] == name for product in storage):
        print(f"product name '{name}' is already taken")
        return None

    new_id = generate_product_id(storage)
    storage.append((new_id, name, normalize_price(price), quantity))
    return new_id


def read_product(storage: list[Product], product_id: int) -> Product | None:

    idx = _find_index(storage, product_id)
    if idx is None:
        print(f"no product with id {product_id}")
        return None
    return storage[idx]


def update_product(
    storage: list[Product],
    product_id: int,
    fields: tuple[str, Decimal, int],
) -> Product | None:

    idx = _find_index(storage, product_id)
    if idx is None:
        print(f"no product with id {product_id}")
        return None

    name, price, quantity = fields
    storage[idx] = (product_id, name, normalize_price(price), quantity)
    return storage[idx]


def delete_product(storage: list[Product], product_id: int) -> int | None:

    idx = _find_index(storage, product_id)
    if idx is None:
        print(f"no product with id {product_id}")
        return None

    del storage[idx]
    return product_id
