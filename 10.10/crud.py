from decimal import Decimal

from .storage import (
    Product,
    PRODUCT_ID_INDEX,
    NAME_INDEX,
    PRODUCT_ID_MIN,
)
from .utils import normalize_price, normalize_product_name


def generate_product_id(storage: list[Product]) -> int:
    return max(
        (p[PRODUCT_ID_INDEX] for p in storage),
        default=PRODUCT_ID_MIN - 1,
    ) + 1


def create_product(
    storage: list[Product],
    fields: tuple[str, Decimal, int],
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


def read_product(
    storage: list[Product],
    product_id: int,
) -> Product | None:
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

    for i, product in enumerate(storage):
        if product[PRODUCT_ID_INDEX] != product_id:
            continue

        if any(
            p[PRODUCT_ID_INDEX] != product_id and p[NAME_INDEX] == name
            for p in storage
        ):
            print(f"product name '{name}' is already taken")
            return None

        updated = (product_id, name, normalize_price(price), quantity)
        storage[i] = updated
        return updated

    print(f"no product with id {product_id}")
    return None


def delete_product(
    storage: list[Product],
    product_id: int,
) -> int | None:
    for i, product in enumerate(storage):
        if product[PRODUCT_ID_INDEX] == product_id:
            del storage[i]
            return product_id

    print(f"no product with id {product_id}")
    return None