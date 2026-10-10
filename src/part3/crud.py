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
    name_norm = normalize_product_name(fields[0])
    if name_norm == "":
        print("product name must not be blank")
        return None
    else:
        _, price, quantity = fields
        if any(product[NAME_INDEX] == name_norm for product in storage):
            print(f"product name '{name_norm}' is already taken")
            return None

        new_id = generate_product_id(storage)
        storage.append((new_id, name_norm, normalize_price(price), quantity))
        return new_id


def _find_index(storage: list[Product], product_id: int) -> int | None:
    for i, product in enumerate(storage):
        if product[PRODUCT_ID_INDEX] == product_id:
            return i
    return None


def read_product(storage: list[Product], product_id: int) -> Product | None:
    idx = _find_index(storage, product_id)
    if idx is None:
        print(f"no product with id {product_id}")
        return None
    return storage[idx]


def find_product(storage: list[Product], product_id: int) -> int | None:
    for i, product in enumerate(storage):
        if product[PRODUCT_ID_INDEX] == product_id:
            return i
    return None


def update_product(
    storage: list[Product],
    product_id: int,
    fields: tuple[str, Decimal, int],
) -> Product | None:
    name_norm = normalize_product_name(fields[0])
    if name_norm == "":
        print("product name must not be blank")
        return None
    if not (product_id in [product[PRODUCT_ID_INDEX] for product in storage]):
        print(f"no product with id {product_id}")
        return None

    _, price, quantity = fields

    if any(
        product[NAME_INDEX] == name_norm and product[PRODUCT_ID_INDEX] != product_id
        for product in storage
    ):
        print(f"product name '{name_norm}' is already taken")
        return None

    idx = find_product(storage, product_id)

    if idx is None:
        print(f"no product with id {product_id}")
        return None

    storage[idx] = (
        product_id,
        name_norm,
        normalize_price(price),
        quantity,
    )
    return storage[idx]


def delete_product(storage: list[Product], product_id: int) -> int | None:

    idx = _find_index(storage, product_id)
    if idx is None:
        print(f"no product with id {product_id}")
        return None

    del storage[idx]
    return product_id
