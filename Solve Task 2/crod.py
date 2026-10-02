from decimal import Decimal
from storage import (
    PRODUCT_ID_MIN,
    PRODUCT_ID_INDEX,
    NAME_INDEX,
    Product,
)
from utils import normalize_price


def create_product(storage: list[Product],
                   fields: tuple[str, Decimal, int]) -> int | None:
    product_name, product_price, product_quantity = fields
    for product in storage:
        if product_name == product[NAME_INDEX]:
            print(f"Product name {product_name} is already taken.")
            return None
    product_id = generate_product_id(storage)
    storage.append((
        product_id,
        product_name,
        normalize_price(product_price),
        product_quantity
    ))
    return product_id


def generate_product_id(storage: list[Product]) -> int:
    if not storage:
        return PRODUCT_ID_MIN
    MAX_INDEX = max(product[PRODUCT_ID_INDEX] for product in storage)
    return MAX_INDEX + 1


def read_product(storage: list[Product], product_id: int) -> Product | None:
    for product in storage:
        if product[PRODUCT_ID_INDEX] == product_id:
            return product
    print(f"No product with id {product_id}")
    return None


def update_product(
    storage: list[Product],
    product_id: int,
    fields: tuple[str, Decimal, int],
) -> Product | None:
    for index, product in enumerate(storage):
        if product[PRODUCT_ID_INDEX] == product_id:
            new_name, new_price, new_quantity = fields
            norm_price = normalize_price(new_price)
            NEW_PRODUCT = (product_id, new_name, norm_price, new_quantity)
            storage[index] = NEW_PRODUCT
            return NEW_PRODUCT
    print(f"No product with id {product_id}")
    return None


def delete_product(storage: list[Product], product_id: int) -> int | None:
    for index, product in enumerate(storage):
        if product[PRODUCT_ID_INDEX] == product_id:
            storage.pop(index)
            return product_id
    print(f"No product with id {product_id}.")
    return None
