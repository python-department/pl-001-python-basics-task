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

    return max(product[PRODUCT_ID_INDEX] for product in storage) + 1


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    name, price, quantity = fields
    name = normalize_product_name(name)

    if not name:
        print("product name must not be blank")
        return None

    for product in storage:
        if product[NAME_INDEX] == name:
            print(f"product name '{name}' is already taken")
            return None

    product_id = generate_product_id(storage)
    new_product = (
        product_id,
        name,
        normalize_price(price),
        quantity,
    )

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
    name = normalize_product_name(name)

    if not name:
        print("product name must not be blank")
        return None

    product_index = None

    for index, product in enumerate(storage):
        if product[PRODUCT_ID_INDEX] == product_id:
            product_index = index
            break

    if product_index is None:
        print(f"no product with id {product_id}")
        return None

    for product in storage:
        if product[PRODUCT_ID_INDEX] != product_id and product[NAME_INDEX] == name:
            print(f"product name '{name}' is already taken")
            return None

    updated_product = (
        product_id,
        name,
        normalize_price(price),
        quantity,
    )

    storage[product_index] = updated_product
    return updated_product


def delete_product(storage: list[Product], product_id: int) -> int | None:

    for index, product in enumerate(storage):
        if product[PRODUCT_ID_INDEX] == product_id:
            storage.pop(index)
            return product_id

    print(f"no product with id {product_id}")
    return None
