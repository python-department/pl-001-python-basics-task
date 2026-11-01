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

    new_id = generate_product_id()
    normalized_price = normalize_price(fields[PRICE_KEY])
    quantity = fields[QUANTITY_KEY]

    storage[new_id] = {
        NAME_KEY: normalized_name,
        PRICE_KEY: normalized_price,
        QUANTITY_KEY: quantity,
    }

    product_names.add(normalized_name)

    return new_id


def read_product(storage: dict[str, Product], product_id: str) -> Product | None:
    if product_id in storage:
        return storage[product_id]
    print(f"no product with id {product_id}")
    return None


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
    if NAME_KEY in fields:
        raw_name = fields[NAME_KEY]
        norm_name = normalize_product_name(raw_name)

        if not norm_name:
            print("product name must not be blank")
            return None

        current_name = product[NAME_KEY]

        if norm_name != current_name and norm_name in product_names:
            print(f"product name '{norm_name}' is already taken")
            return None

    if PRICE_KEY in fields:
        norm_price = normalize_price(fields[PRICE_KEY])

    if NAME_KEY in fields:
        fields[NAME_KEY] = norm_name
        product[NAME_KEY] = norm_name

        if norm_name != current_name:
            product_names.remove(current_name)
            product_names.add(norm_name)

    if PRICE_KEY in fields:
        fields[PRICE_KEY] = norm_price
        product[PRICE_KEY] = norm_price

    if QUANTITY_KEY in fields:
        product[QUANTITY_KEY] = fields[QUANTITY_KEY]

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
    del storage[product_id]
    product_names.remove(name)
    return product_id
