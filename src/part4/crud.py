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
    price_product = normalize_price(fields[PRICE_KEY])
    quantity_product = fields[QUANTITY_KEY]
    name_product = normalize_product_name(fields[NAME_KEY])
    if not name_product:
        print("product name must not be blank")
        return None
    if name_product in product_names:
        print(f"product name '{name_product}' is already taken")
        return None
    product_names.add(name_product)
    new_id = generate_product_id()
    storage[new_id] = {
        NAME_KEY: name_product,
        PRICE_KEY: price_product,
        QUANTITY_KEY: quantity_product,
    }
    return new_id


def read_product(storage: dict[str, Product], product_id: str) -> Product | None:
    reading = storage.get(product_id)
    if reading is None:
        print(f"no product with id {product_id}")
    return reading


def update_product(
    storage: dict[str, Product],
    product_names: set[str],
    product_id: str,
    fields: dict[str, Any],
) -> Product | None:
    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None
    if fields.get(NAME_KEY) is not None:
        fields[NAME_KEY] = normalize_product_name(fields[NAME_KEY])
        if not fields[NAME_KEY]:
            print("product name must not be blank")
            return None
        if (fields[NAME_KEY] != storage[product_id][NAME_KEY]) and (
            fields[NAME_KEY] in product_names
        ):
            print(f"product name '{fields[NAME_KEY]}' is already taken")
            return None
    if fields.get(PRICE_KEY) is not None:
        fields[PRICE_KEY] = normalize_price(fields[PRICE_KEY])
    if fields.get(NAME_KEY) is not None:
        product_names.discard(storage[product_id][NAME_KEY])
        product_names.add(fields[NAME_KEY])
        storage[product_id][NAME_KEY] = fields[NAME_KEY]
    if fields.get(PRICE_KEY) is not None:
        storage[product_id][PRICE_KEY] = fields[PRICE_KEY]
    if fields.get(QUANTITY_KEY) is not None:
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
    product_names.discard(storage[product_id][NAME_KEY])
    del storage[product_id]
    return product_id
