from collections.abc import Callable
from typing import Any, Final

from .decorators import Registry, collect_stats
from .snowflake import *
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

gen = get_snowflake_id_generator()


def generate_snowflake_id() -> int | None:
    if gen is None:
        return None
    return gen()


@collect_stats(CREATE_KEY, STATS_REGISTRY)
def create_product(
    storage: dict[int, Product],
    product_names: set[str],
    fields: dict[str, Any],
    generate_id: Callable[[], int | None],
) -> int | None:
    normalized_name = normalize_product_name(fields[NAME_KEY])
    normalized_price = normalize_price(fields[PRICE_KEY])

    if not normalized_name:
        print("product name must not be blank")
        return None
    elif normalized_name in product_names:
        print(f"product name '{normalized_name}' is already taken")
        return None

    if (product_id := generate_id()) is None:
        return None

    storage[product_id] = {
        NAME_KEY: normalized_name,
        PRICE_KEY: normalized_price,
        QUANTITY_KEY: fields[QUANTITY_KEY],
    }
    product_names.add(normalized_name)

    return product_id


@collect_stats(READ_KEY, STATS_REGISTRY)
def read_product(storage: dict[int, Product], product_id: int) -> Product | None:
    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None
    return storage[product_id]


@collect_stats(UPDATE_KEY, STATS_REGISTRY)
def update_product(
    storage: dict[int, Product],
    product_names: set[str],
    product_id: int,
    fields: dict[str, Any],
) -> Product | None:
    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None

    current_name = storage[product_id][NAME_KEY]

    if NAME_KEY in fields:
        normalized_name = normalize_product_name(fields[NAME_KEY])
        fields[NAME_KEY] = normalized_name
        if not normalized_name:
            print("product name must not be blank")
            return None
        elif (normalized_name != current_name) and (normalized_name in product_names):
            print(f"product name '{normalized_name}' is already taken")
            return None

        if normalized_name != current_name:
            product_names.discard(current_name)
            product_names.add(normalized_name)

    if PRICE_KEY in fields:
        normalized_price = normalize_price(fields[PRICE_KEY])
        fields[PRICE_KEY] = normalized_price

    storage[product_id].update(fields)

    return storage[product_id]


@collect_stats(DELETE_KEY, STATS_REGISTRY)
def delete_product(
    storage: dict[int, Product],
    product_names: set[str],
    product_id: int,
) -> int | None:
    deleted = storage.pop(product_id, None)

    if deleted is None:
        print(f"no product with id {product_id}")
        return None

    product_names.remove(deleted[NAME_KEY])
    return product_id
