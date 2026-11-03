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

    new_product_id = generate_product_id()
    normalized_price = normalize_price(fields[PRICE_KEY])
    product_content = {
        NAME_KEY: normalized_name,
        PRICE_KEY: normalized_price,
        QUANTITY_KEY: fields[QUANTITY_KEY],
    }

    storage[new_product_id] = product_content
    product_names.add(normalized_name)
    return new_product_id


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
    # 1. Товар должен существовать
    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None

    product = storage[product_id]
    old_name = product[NAME_KEY]

    # 2-4. Нормализация и проверки для имени
    if NAME_KEY in fields:
        normalized_name = normalize_product_name(fields[NAME_KEY])
        if not normalized_name:
            print("product name must not be blank")
            return None
        if normalized_name != old_name and normalized_name in product_names:
            print(f"product name '{normalized_name}' is already taken")
            return None
        fields[NAME_KEY] = normalized_name

    # 5. Нормализация цены
    if PRICE_KEY in fields:
        fields[PRICE_KEY] = normalize_price(fields[PRICE_KEY])

    # 6. Записываем поля в товар
    if NAME_KEY in fields:
        product[NAME_KEY] = fields[NAME_KEY]
    if PRICE_KEY in fields:
        product[PRICE_KEY] = fields[PRICE_KEY]
    if QUANTITY_KEY in fields:
        product[QUANTITY_KEY] = fields[QUANTITY_KEY]

    # 7. Обновляем индекс при переименовании
    current_name = product[NAME_KEY]
    if current_name != old_name:
        product_names.discard(old_name)
        product_names.add(current_name)

    return product


def delete_product(
    storage: dict[str, Product],
    product_names: set[str],
    product_id: str,
) -> str | None:
    if product_id in storage:
        name = storage[product_id][NAME_KEY]
        del storage[product_id]
        product_names.discard(name)
        return product_id

    print(f"no product with id {product_id}")
    return None
