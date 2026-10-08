from decimal import Decimal

from .storage import (
    NAME_INDEX,
    PRODUCT_ID_INDEX,
    PRODUCT_ID_MIN,
    Product,
)
from .utils import normalize_price, normalize_product_name


def generate_product_id(storage: list[Product]) -> int:
    if len(storage) == 0:
        return PRODUCT_ID_MIN
    return max(p[PRODUCT_ID_INDEX] for p in storage) + 1


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    name = normalize_product_name(fields[0])
    price = normalize_price(fields[1])
    quantity = fields[2]
    if not name:
        print("product name must not be blank")
        return None
    for cor in storage:
        if cor[NAME_INDEX] == name:
            print(f"product name '{name}' is already taken")
            return None
    new_id = generate_product_id(storage)
    storage.append((new_id, name, price, quantity))
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
    name = normalize_product_name(fields[0])
    price = normalize_price(fields[1])
    quantity = fields[2]
    if not name:
        print("product name must not be blank")
        return None
    index_id = next(
        (i for i, p in enumerate(storage) if p[PRODUCT_ID_INDEX] == product_id), None
    )
    if index_id is None:
        print(f"no product with id {product_id}")
        return None
    index_name = next(
        (
            i
            for i, p in enumerate(storage)
            if (p[NAME_INDEX] == name) and (p[PRODUCT_ID_INDEX] != product_id)
        ),
        None,
    )
    if index_name is not None:
        print(f"product name '{name}' is already taken")
        return None
    fields_new = (product_id, name, price, quantity)
    storage[index_id] = fields_new
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
