import uuid
from typing import Any

from .storage import (
    NAME_KEY,
    PRICE_KEY,
    QUANTITY_KEY,
    Product,
)
from .utils import normalize_price, normalize_product_name


def generate_product_id() -> str:
    return str(uuid.uuid4())


def create_product(
    storage: dict[str, Product],
    product_names: set[str],
    fields: dict[str, Any],
) -> str | None:
    name = normalize_product_name(fields[NAME_KEY])
    fields[NAME_KEY] = name

    if not name:
        print("product name must not be blank")
        return None

    if name in product_names:
        print(f"product name '{name}' is already taken")
        return None

    norm_price = normalize_price(fields[PRICE_KEY])
    fields[PRICE_KEY] = norm_price

    product_id = generate_product_id()
    storage[product_id] = {
        NAME_KEY: name,
        PRICE_KEY: norm_price,
        QUANTITY_KEY: fields[QUANTITY_KEY],
    }
    product_names.add(name)
    return product_id


def read_product(storage: dict[str, Product], product_id: str) -> Product | None:
    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None
    return storage[product_id]


def update_product(
    storage: dict[str, Product],
    product_names: set[str],
    product_id: str,
    fields: dict[str, Any],
) -> Product | None:
    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None

    if NAME_KEY in fields:
        name = normalize_product_name(fields[NAME_KEY])
        fields[NAME_KEY] = name
        if not name:
            print("product name must not be blank")
            return None
        current_name = storage[product_id][NAME_KEY]
        if name != current_name and name in product_names:
            print(f"product name '{name}' is already taken")
            return None

    if PRICE_KEY in fields:
        norm_price = normalize_price(fields[PRICE_KEY])
        fields[PRICE_KEY] = norm_price

    if NAME_KEY in fields:
        old_name = storage[product_id][NAME_KEY]
        new_name = fields[NAME_KEY]
        if new_name != old_name:
            product_names.remove(old_name)
            product_names.add(new_name)
        storage[product_id][NAME_KEY] = new_name

    if PRICE_KEY in fields:
        storage[product_id][PRICE_KEY] = fields[PRICE_KEY]

    if QUANTITY_KEY in fields:
        storage[product_id][QUANTITY_KEY] = fields[QUANTITY_KEY]

    return storage[product_id]


def delete_product(
    storage: dict[str, Product],
    product_names: set[str],
    product_id: str,
) -> str | None:
    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None

    name = storage[product_id][NAME_KEY]
    del storage[product_id]
    product_names.discard(name)
    return product_id
