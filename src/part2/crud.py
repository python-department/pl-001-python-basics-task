from decimal import Decimal

from .storage import (
    PRODUCT_ID_MIN,
    Product,
)
from .utils import normalize_price


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
    for i in range(len(storage)):
        if fields[0] == storage[i][1]:
            print(f"product name {fields[0]} is already taken")
            return None

    name, price, quantity = fields
    id_f = generate_product_id(storage)
    fields_1 = (id_f, name, normalize_price(price), quantity)
    storage.append(fields_1)
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
    for i in range(len(storage)):
        if product_id == storage[i][0]:
            storage[i] = (product_id, fields[0], normalize_price(fields[1]), fields[2])
            return storage[i]
    print(f"no product with id {product_id}")
    return None


def delete_product(storage: list[Product], product_id: int) -> int | None:
    for i in range(len(storage)):
        if product_id == storage[i][0]:
            del storage[i]
            return product_id
    print(f"no product with id {product_id}")
    return None
