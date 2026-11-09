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
    raw_name, price, qty = fields
    name = normalize_product_name(raw_name)
    if not name:
        print("product name must not be blank")
        return None
    for p in storage:
        if p[NAME_INDEX] == name:
            print(f"product name '{name}' is already taken")
            return None
    new_id = generate_product_id(storage)
    norm_price = normalize_price(price)
    storage.append((new_id, name, norm_price, qty))
    return new_id


def read_product(storage: list[Product], product_id: int) -> Product | None:
    for p in storage:
        if p[PRODUCT_ID_INDEX] == product_id:
            return p
    print(f"no product with id {product_id}")
    return None


def update_product(
    storage: list[Product],
    product_id: int,
    fields: tuple[str, Decimal, int],
) -> Product | None:
    raw_name, price, qty = fields
    name = normalize_product_name(raw_name)
    if not name:
        print("product name must not be blank")
        return None
    target_idx = -1

    for i, p in enumerate(storage):
        if p[PRODUCT_ID_INDEX] == product_id:
            target_idx = i
            break
    if target_idx == -1:
        print(f"no product with id {product_id}")
        return None

    for p in storage:
        if p[NAME_INDEX] == name and p[PRODUCT_ID_INDEX] != product_id:
            print(f"product name '{name}' is already taken")
            return None
    norm_price = normalize_price(price)
    update_tuple = (product_id, name, norm_price, qty)
    storage[target_idx] = update_tuple
    return update_tuple


def delete_product(storage: list[Product], product_id: int) -> int | None:
    for i, p in enumerate(storage):
        if p[PRODUCT_ID_INDEX] == product_id:
            storage.pop(i)
            return product_id
    return None
