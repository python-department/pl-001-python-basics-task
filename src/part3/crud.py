from decimal import Decimal

from .storage import (
    PRODUCT_ID_MIN,
    Product,
)
from .utils import normalize_price, normalize_product_name


def generate_product_id(storage: list[Product]) -> int:
    idmax = 0
    if len(storage) == 0:
        idmax = PRODUCT_ID_MIN
    else:
        for i in range(len(storage)):
            idmax = max(storage[i][0], idmax)
    return idmax + 1


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    name, price, shtyk = fields
    norm_name = normalize_product_name(name)
    if not norm_name:
        print("product name must not be blank")
        return None
    for product in storage:
        if normalize_product_name(product[1]) == norm_name:
            print(f"product name '{norm_name}' is already taken")
            return None
    norm_price = normalize_price(price)
    id_f = generate_product_id(storage)
    storage.append((id_f, norm_name, norm_price, shtyk))
    return id_f


def read_product(storage: list[Product], product_id: int) -> Product | None:
    for i in range(len(storage)):
        if product_id == storage[i][0]:
            return storage[i]
    print(f"no product with id {product_id}")
    return None


def update_product(
    storage: list[Product],
    product_id: int,
    fields: tuple[str, Decimal, int],
) -> Product | None:
    name, price, shtyk = fields
    norm_name = normalize_product_name(name)
    if not norm_name:
        print("product name must not be blank")
        return None
    found_index = None
    for i in range(len(storage)):
        if storage[i][0] == product_id:
            found_index = i
            break
    if found_index is None:
        print(f"no product with id {product_id}")
        return None
    for product in storage:
        if product[0] != product_id and normalize_product_name(product[1]) == norm_name:
            print(f"product name '{norm_name}' is already taken")
            return None
    updated = (product_id, norm_name, normalize_price(price), shtyk)
    storage[found_index] = updated
    return updated


def delete_product(storage: list[Product], product_id: int) -> int | None:
    for i in range(len(storage)):
        if product_id == storage[i][0]:
            del storage[i]
            return product_id
    print(f"no product with id {product_id}")
    return None
