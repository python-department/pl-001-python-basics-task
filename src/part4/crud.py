import uuid
from typing import Any

from .storage import (
    NAME_KEY,
    PRICE_KEY,
    Product,
)
from .utils import normalize_price, normalize_product_name


def generate_product_id() -> str:
    return str(uuid.uuid4())


def name_check(name: str, product_names: set[str]) -> bool | str:
    name = normalize_product_name(name)
    if name == "":
        print("product name must not be blank")
        return False
    if name in product_names:
        print(f"product name {name} is already taken")
        return False
    return name


def id_check(num_id: str, storage: dict[str, Product]) -> bool:
    if num_id not in storage:
        print(f"no product with id {num_id}")
        return False
    return True


def create_product(
    storage: dict[str, Product],
    product_names: set[str],
    fields: dict[str, Any],
) -> str | None:

    check1 = name_check(fields[NAME_KEY], product_names)
    if not check1:
        return None
    fields[NAME_KEY] = check1
    product_names.add(fields[NAME_KEY])
    fields[PRICE_KEY] = normalize_price(fields[PRICE_KEY])
    new_id = generate_product_id()
    storage[new_id] = fields
    return new_id


def read_product(storage: dict[str, Product], product_id: str) -> Product | None:
    if not id_check(product_id, storage):
        return None
    return storage[product_id]


def update_product(
    storage: dict[str, Product],
    product_names: set[str],
    product_id: str,
    fields: dict[str, Any],
) -> Product | None:

    if not id_check(product_id, storage):
        return None

    if NAME_KEY in fields:
        fields[NAME_KEY] = normalize_product_name(fields[NAME_KEY])
        name = fields[NAME_KEY]
        if name == "":
            print("product name must not be blank")
            return None
        if name in product_names and storage[product_id][NAME_KEY] != name:
            print(f"product name {name} is already taken")
            return None
        if storage[product_id][NAME_KEY] != name:
            product_names.add(name)
            product_names.remove(storage[product_id][NAME_KEY])

    if PRICE_KEY in fields:
        fields[PRICE_KEY] = normalize_price(fields[PRICE_KEY])

    for nkey, value in fields.items():
        storage[product_id][nkey] = value
    return storage[product_id]


def delete_product(
    storage: dict[str, Product],
    product_names: set[str],
    product_id: str,
) -> str | None:

    if not id_check(product_id, storage):
        return None
    product_names.remove(storage[product_id][NAME_KEY])
    del storage[product_id]
    return product_id
