from decimal import Decimal

from .storage import (
    NAME_INDEX,
    PRODUCT_ID_INDEX,
    PRODUCT_ID_MIN,
    Product,
)
from .utils import normalize_price


def generate_product_id(storage: list[Product]) -> int:
    if len(storage) == 0:
        return PRODUCT_ID_MIN
    return max(p[PRODUCT_ID_INDEX] for p in storage) + 1


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    for cor in storage:
        if cor[NAME_INDEX] == fields[0]:
            print(f"product name '{fields[0]}' is already taken.")
            return None
    new_id = generate_product_id(storage)
    storage.append((new_id, fields[0], normalize_price(fields[1]), fields[2]))
    return new_id


def read_product(storage: list[Product], product_id: int) -> Product | None:
    for cor in storage:
        if cor[PRODUCT_ID_INDEX] == product_id:
            return cor
    print(f"no product with id {product_id}")
    return None


def update_product(
    storage: list[Product],
    product_id: int,
    fields: tuple[str, Decimal, int],
) -> Product | None:
    index = next(
        (i for i, p in enumerate(storage) if p[PRODUCT_ID_INDEX] == product_id), None
    )
    if index is None:
        print(f"no product with id {product_id}")
        return None
    fields_new = (product_id, fields[0], normalize_price(fields[1]), fields[2])
    storage[index] = fields_new
    return fields_new


def delete_product(storage: list[Product], product_id: int) -> int | None:
    index = next(
        (i for i, p in enumerate(storage) if p[PRODUCT_ID_INDEX] == product_id), None
    )
    if index is None:
        print(f"no product with id {product_id}")
        return None
    storage.pop(index)
    return product_id
