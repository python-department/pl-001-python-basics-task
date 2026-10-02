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
    else:
        return max(storage)[PRODUCT_ID_INDEX] + 1


def product_search(storage: list[Product], product_id: int) -> Product | None:
    for product in storage:
        if product[PRODUCT_ID_INDEX] == product_id:
            return product

    return None


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    name, price, quantity = fields

    for product in storage:
        if name == product[NAME_INDEX]:
            print(f"product name {name} is already taken")
            return None

    product_id = generate_product_id(storage)
    product_price = normalize_price(price)

    new_product: Product = (product_id, name, product_price, quantity)
    storage.append(new_product)

    return product_id


def read_product(storage: list[Product], product_id: int) -> Product | None:
    product = product_search(storage, product_id)
    if product is not None:
        return product

    print(f"no product with id {product_id}")
    return None


def update_product(
    storage: list[Product],
    product_id: int,
    fields: tuple[str, Decimal, int],
) -> Product | None:
    name, price, quantity = fields

    product = product_search(storage, product_id)
    if product is not None:
        new_price = normalize_price(price)
        new_product = (product_id, name, new_price, quantity)
        storage[storage.index(product)] = new_product
        return new_product

    print(f"no product with id {product_id}")
    return None


def delete_product(storage: list[Product], product_id: int) -> int | None:
    product = product_search(storage, product_id)
    if product is not None:
        storage.remove(product)
        return product_id

    print(f"no product with id {product_id}")
    return None
