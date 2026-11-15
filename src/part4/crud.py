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
    normalized_name = normalize_product_name(fields[NAME_KEY])

    if not normalized_name:
        print("product name must not be blank")
        return None

    if normalized_name in product_names:
        print(f"product name '{normalized_name}' is already taken")
        return None

    product_id = generate_product_id()

    storage[product_id] = {
        NAME_KEY: normalized_name,
        PRICE_KEY: normalize_price(fields[PRICE_KEY]),
        QUANTITY_KEY: fields[QUANTITY_KEY],
    }

    product_names.add(normalized_name)

    return product_id


def read_product(storage: dict[str, Product], product_id: str) -> Product | None:
    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None
    else:
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

    product = storage[product_id]
    old_name = product[NAME_KEY]

    if NAME_KEY in fields:
        normalized_name = normalize_product_name(fields[NAME_KEY])

        if not normalized_name:
            print("product name must not be blank")
            return None

        if normalized_name != old_name and normalized_name in product_names:
            print(f"product name '{normalized_name}' is already taken")
            return None

        fields[NAME_KEY] = normalized_name

    if PRICE_KEY in fields:
        fields[PRICE_KEY] = normalize_price(fields[PRICE_KEY])

    product.update(fields)

    if NAME_KEY in fields:
        new_name = fields[NAME_KEY]
        if new_name != old_name:
            product_names.remove(old_name)
            product_names.add(new_name)

    return product


def delete_product(
    storage: dict[str, Product],
    product_names: set[str],
    product_id: str,
) -> str | None:

    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None

    product = storage[product_id]
    name = product[NAME_KEY]

    product_names.remove(name)
    del storage[product_id]
    return product_id
