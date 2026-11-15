from collections.abc import Callable
from typing import Any, Final

from .constants import EPOCH_MS_DEFAULT, NODE_ID_DEFAULT
from .decorators import Registry, collect_stats
from .snowflake import get_snowflake_id_generator
from .storage import (
    NAME_KEY,
    PRICE_KEY,
    QUANTITY_KEY,
    Product,
)
from .utils import normalize_price, normalize_product_name


STATS_REGISTRY: Final[Registry] = {}

CREATE_KEY: Final[str] = "create"
READ_KEY: Final[str] = "read"
UPDATE_KEY: Final[str] = "update"
DELETE_KEY: Final[str] = "delete"

GENERATE_ID = get_snowflake_id_generator(NODE_ID_DEFAULT, EPOCH_MS_DEFAULT)


def generate_snowflake_id() -> int | None:
    if GENERATE_ID is None:
        return None
    return GENERATE_ID()


@collect_stats(CREATE_KEY, STATS_REGISTRY)
def create_product(
    storage: dict[int, Product],
    product_names: set[str],
    fields: dict[str, Any],
    generate_id: Callable[[], int | None],
) -> int | None:

    normalized_name = normalize_product_name(fields[NAME_KEY])

    if not normalized_name:
        print("product name must not be blank")
        return None

    if normalized_name in product_names:
        print(f"product name '{normalized_name}' is already taken")
        return None

    new_product_id = generate_id()
    if new_product_id is None:
        return None

    normalized_price = normalize_price(fields[PRICE_KEY])

    product_content = {
        NAME_KEY: normalized_name,
        PRICE_KEY: normalized_price,
        QUANTITY_KEY: fields[QUANTITY_KEY],
    }

    storage[new_product_id] = product_content
    product_names.add(normalized_name)

    return new_product_id


@collect_stats(READ_KEY, STATS_REGISTRY)
def read_product(storage: dict[int, Product], product_id: int) -> Product | None:
    if product_id in storage:
        return storage[product_id]
    print(f"no product with id {product_id}")
    return None


@collect_stats(UPDATE_KEY, STATS_REGISTRY)
def update_product(
    storage: dict[int, Product],
    product_names: set[str],
    product_id: int,
    fields: dict[str, Any],
) -> Product | None:
    # 1. Товар должен существовать
    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None

    product = storage[product_id]
    old_name = product[NAME_KEY]

    # 2. Нормализация и проверки для имени
    if NAME_KEY in fields:
        normalized_name = normalize_product_name(fields[NAME_KEY])
        if not normalized_name:
            print("product name must not be blank")
            return None
        if normalized_name != old_name and normalized_name in product_names:
            print(f"product name '{normalized_name}' is already taken")
            return None
        fields[NAME_KEY] = normalized_name

    # 3. Нормализация цены
    if PRICE_KEY in fields:
        fields[PRICE_KEY] = normalize_price(fields[PRICE_KEY])

    # 4. Записываем поля в товар
    if NAME_KEY in fields:
        product[NAME_KEY] = fields[NAME_KEY]
    if PRICE_KEY in fields:
        product[PRICE_KEY] = fields[PRICE_KEY]
    if QUANTITY_KEY in fields:
        product[QUANTITY_KEY] = fields[QUANTITY_KEY]

    # 5. Обновляем индекс при переименовании
    current_name = product[NAME_KEY]
    if current_name != old_name:
        product_names.discard(old_name)
        product_names.add(current_name)

    return product


@collect_stats(DELETE_KEY, STATS_REGISTRY)
def delete_product(
    storage: dict[int, Product],
    product_names: set[str],
    product_id: int,
) -> int | None:
    if product_id in storage:
        name = storage[product_id][NAME_KEY]
        del storage[product_id]
        product_names.discard(name)
        return product_id

    print(f"no product with id {product_id}")
    return None
