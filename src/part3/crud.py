from decimal import Decimal

from .storage import (
    NAME_INDEX,
    PRODUCT_ID_INDEX,
    PRODUCT_ID_MIN,
    Product,
)
from .utils import normalize_price, normalize_product_name


def generate_product_id(storage: list[Product]) -> int:
    if not storage:
        return PRODUCT_ID_MIN
    return max(p[PRODUCT_ID_INDEX] for p in storage) + 1


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    name, price, quantity = fields
    name = normalize_product_name(name)
    if not name:
        print("product name must not be blank")
        return None
    if any(p[NAME_INDEX] == name for p in storage):
        print(f"product name '{name}' is already taken")
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
    name = normalize_product_name(name)
    if not name:
        print("product name must not be blank")
        return None

    index = None
    for i, product in enumerate(storage):
        if product[PRODUCT_ID_INDEX] == product_id:
            index = i
            break

    if index is None:
        print(f"no product with id {product_id}")
        return None

    for product in storage:
        if product[NAME_INDEX] == name and product[PRODUCT_ID_INDEX] != product_id:
            print(f"product name '{name}' is already taken")
            return None
    updated = (product_id, name, normalize_price(price), quantity)
    storage[index] = updated
    return updated


def delete_product(storage: list[Product], product_id: int) -> int | None:
    for index, product in enumerate(storage):
        if product[PRODUCT_ID_INDEX] == product_id:
            del storage[index]
            return product_id

    print(f"no product with id {product_id}")
    return None
