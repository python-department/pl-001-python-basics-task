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

    if not name:
        print("product name must not be blank")
        return None

    if name in product_names:
        print(f"product name '{name}' is already taken")
        return None

    product_id = generate_product_id()

    product = {
        NAME_KEY: name,
        PRICE_KEY: normalize_price(fields[PRICE_KEY]),
        QUANTITY_KEY: fields[QUANTITY_KEY],
    }

    storage[product_id] = product

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

    product = storage[product_id]

    if NAME_KEY in fields:
        name = normalize_product_name(fields[NAME_KEY])

        if not name:
            print("product name must not be blank")
            return None

        if name != product[NAME_KEY] and name in product_names:
            print(f"product name '{name}' is already taken")
            return None

        fields[NAME_KEY] = name

    if PRICE_KEY in fields:
        fields[PRICE_KEY] = normalize_price(fields[PRICE_KEY])

    if NAME_KEY in fields:
        old_name = product[NAME_KEY]
        new_name = fields[NAME_KEY]

        if old_name != new_name:
            product_names.remove(old_name)
            product_names.add(new_name)

    product.update(fields)

    return product


def delete_product(
    storage: dict[str, Product],
    product_names: set[str],
    product_id: str,
) -> str | None:

    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None

    product = storage.pop(product_id)
    product_names.remove(product[NAME_KEY])

    return product_id
