from decimal import Decimal

from .storage import (
    NAME_INDEX,
    PRODUCT_ID_INDEX,
    Product,
)
from .utils import normalize_price, normalize_product_name


def generate_product_id(storage: list[Product]) -> int:
    if not storage:
        return 1
    return max(product[PRODUCT_ID_INDEX] for product in storage) + 1


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    name, price, quantity = fields
    normalize_name = " ".join(name.lower().split())

    if not normalize_name:
        print("product name must not be blank")
        return None

    for product in storage:
        if product[NAME_INDEX] == normalize_name:
            print(f"product name '{normalize_name}' is already taken")
            return None
    product_id = generate_product_id(storage)
    product_price = normalize_price(price)
    new_product = (product_id, normalize_name, product_price, quantity)
    storage.append(new_product)
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
    normalize_name = normalize_product_name(name)

    if not normalize_name:
        print("product name must not be blank")
        return None

    found_index: int | None = None

    for index, product in enumerate(storage):
        if product[PRODUCT_ID_INDEX] == product_id:
            found_index = index
            break

    if found_index is None:
        print(f"no product with id {product_id}")
        return None

    for index, product in enumerate(storage):
        if index != found_index and product[NAME_INDEX] == normalize_name:
            print(f"product name '{normalize_name}' is already taken")
            return None

    new_product = (
        product_id,
        normalize_name,
        normalize_price(price),
        quantity,
    )
    storage[found_index] = new_product
    return new_product


def delete_product(storage: list[Product], product_id: int) -> int | None:
    for product_index in storage:
        if product_index[PRODUCT_ID_INDEX] == product_id:
            storage.remove(product_index)
            return product_id

    print(f"no product with id {product_id}")
    return None
