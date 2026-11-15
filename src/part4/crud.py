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
    product_name = normalize_product_name(fields[NAME_KEY])
    if not product_name:
        print("product name must not be blank")
        return None
    if product_name in product_names:
        print(f"product name '{product_name}' is already taken")
        return None

    new_id = generate_product_id()
    storage[new_id] = {
        NAME_KEY: product_name,
        PRICE_KEY: normalize_price(fields[PRICE_KEY]),
        QUANTITY_KEY: fields[QUANTITY_KEY],
    }
    product_names.add(product_name)
    return new_id


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
    if read_product(storage, product_id) is None:
        return None

    if NAME_KEY in fields:
        product_name = normalize_product_name(fields[NAME_KEY])
        if not product_name:
            print("product name must not be blank")
            return None
        if product_name != storage[product_id][NAME_KEY]:
            if product_name in product_names:
                print(f"product name '{product_name}' is already taken")
                return None
            product_names.remove(storage[product_id][NAME_KEY])
            product_names.add(product_name)
        fields[NAME_KEY] = product_name

    if PRICE_KEY in fields:
        fields[PRICE_KEY] = normalize_price(fields[PRICE_KEY])

    storage[product_id].update(fields)
    return storage[product_id]


def delete_product(
    storage: dict[str, Product],
    product_names: set[str],
    product_id: str,
) -> str | None:
    if read_product(storage, product_id) is None:
        return None
    product_names.remove(storage[product_id][NAME_KEY])
    del storage[product_id]
    return product_id
