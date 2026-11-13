from collections.abc import Callable
from typing import Any, Final

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


generator = get_snowflake_id_generator()


def generate_snowflake_id() -> int | None:
    if generator is None:
        return None
    return generator()


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

    product_id = generate_id()

    if product_id is None:
        return None

    product = {
        NAME_KEY: normalized_name,
        PRICE_KEY: normalize_price(fields[PRICE_KEY]),
        QUANTITY_KEY: fields[QUANTITY_KEY],
    }

    storage[product_id] = product
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


@collect_stats(DELETE_KEY, STATS_REGISTRY)
def delete_product(
    storage: dict[int, Product],
    product_names: set[str],
    product_id: int,
) -> int | None:
    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None

    product_names.discard(storage[product_id][NAME_KEY])
    del storage[product_id]

    return product_id
