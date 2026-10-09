from decimal import Decimal

from .storage import (
    NAME_INDEX,
    PRODUCT_ID_INDEX,
    PRODUCT_ID_MIN,
    Product,
)
from .utils import normalize_price, normalize_product_name


def check_product(storage: list[Product], product_name: str) -> bool | None:
    if not (product_name):
        print("product name must not be blank")
        return None

    for product in storage:
        if product_name == product[NAME_INDEX]:
            print(f"product name '{product_name}' is already taken")
            return None
    return True


def generate_product_id(storage: list[Product]) -> int:
    if not storage:
        return PRODUCT_ID_MIN

    max_id = max(product[PRODUCT_ID_INDEX] for product in storage)

    return max_id + 1


def create_product(
    storage: list[Product],
    fields: tuple[str, Decimal, int],
) -> int | None:
    product_name, product_price, product_quantity = fields

    normalized_name = normalize_product_name(product_name)
    if (status := check_product(storage, normalized_name)) is None:
        return status

    product_id = generate_product_id(storage)
    normalized_price = normalize_price(product_price)

    storage.append(
        (
            product_id,
            normalized_name,
            normalized_price,
            product_quantity,
        )
    )

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
    product_name, product_price, product_quantity = fields
    normalized_name = normalize_product_name(product_name)

    if not normalized_name:
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
        if (
            product[PRODUCT_ID_INDEX] != product_id
            and product[NAME_INDEX] == normalized_name
        ):
            print(f"product name '{normalized_name}' is already taken")
            return None

    new_product: Product = (
        product_id,
        normalized_name,
        normalize_price(product_price),
        product_quantity,
    )

    storage[product_index] = new_product
    return new_product


def delete_product(storage: list[Product], product_id: int) -> int | None:
    for index, product in enumerate(storage):
        if product[PRODUCT_ID_INDEX] == product_id:
            storage.pop(index)
            return product_id

    print(f"no product with id {product_id}")
    return None