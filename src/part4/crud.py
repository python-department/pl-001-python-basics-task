import uuid
from decimal import Decimal
from typing import Any

from .storage import (
    NAME_KEY,
    PRICE_KEY,
    QUANTITY_KEY,
    Product,
)
from .utils import (
    normalize_price,
    normalize_product_name,
)


def generate_product_id() -> str:
    return str(uuid.uuid4())


def create_product(
    storage: dict[str, Product],
    product_names: set[str],
    fields: dict[str, Any],
) -> str | None:
    name: str = fields[NAME_KEY]
    price: Decimal = fields[PRICE_KEY]
    quantity: int = fields[QUANTITY_KEY]

    normalized_name = normalize_product_name(name)

    if not normalized_name:
        print("product name must not be blank")
        return None

    if normalized_name in product_names:
        print(f"product name '{normalized_name}' is already taken")
        return None

    product_id = generate_product_id()
    normalized_price = normalize_price(price)

    new_product: Product = {
        NAME_KEY: normalized_name,
        PRICE_KEY: normalized_price,
        QUANTITY_KEY: quantity,
    }
    storage[product_id] = new_product

    return product_id


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

    current_product = storage[product_id]

    if NAME_KEY in fields:
        normalized_name = normalize_product_name(fields[NAME_KEY])
        if not normalized_name:
            print("product name must not be blank")
            return None
        if (
            normalized_name != current_product[NAME_KEY]
            and normalized_name in product_names
        ):
            print(f"product name '{normalized_name}' is already taken")
            return None
        fields[NAME_KEY] = normalized_name

    if PRICE_KEY in fields:
        fields[PRICE_KEY] = normalize_price(fields[PRICE_KEY])

    if NAME_KEY in fields and fields[NAME_KEY] != current_product[NAME_KEY]:
        product_names.remove(current_product[NAME_KEY])
        product_names.add(fields[NAME_KEY])

    current_product.update(fields)
    return current_product


def delete_product(
    storage: dict[str, Product],
    product_names: set[str],
    product_id: str,
) -> str | None:
    if product_id in storage:
        product = storage.pop(product_id)
        product_names.remove(product[NAME_KEY])
        return product_id

    print(f"no product with id {product_id}")
    return None
