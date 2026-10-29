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

    normalized_price = normalize_price(fields[PRICE_KEY])
    product_id = generate_product_id()
    quantity = fields[QUANTITY_KEY]
    new_product = {
        NAME_KEY: normalized_name,
        PRICE_KEY: normalized_price,
        QUANTITY_KEY: quantity,
    }

    product_names.add(normalized_name)
    storage[product_id] = new_product

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

    product = storage[product_id]
    normalized_fields = fields.copy()

    if NAME_KEY in normalized_fields:
        normalized_name = normalize_product_name(normalized_fields[NAME_KEY])

        if not normalized_name:
            print("product name must not be blank")
            return None

        current_name = product[NAME_KEY]

        if normalized_name != current_name and normalized_name in product_names:
            print(f"product name '{normalized_name}' is already taken")
            return None

        normalized_fields[NAME_KEY] = normalized_name

    if PRICE_KEY in normalized_fields:
        normalized_fields[PRICE_KEY] = normalize_price(normalized_fields[PRICE_KEY])

    if NAME_KEY in normalized_fields:
        old_name = product[NAME_KEY]
        new_name = normalized_fields[NAME_KEY]

        if old_name != new_name:
            product_names.discard(old_name)
            product_names.add(new_name)

    fields.update(normalized_fields)
    product.update(normalized_fields)

    return product


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
