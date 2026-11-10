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
    name_product = normalize_product_name(fields[NAME_KEY])

    if not name_product:
        print("product name must not be blank")
        return None

    if name_product in product_names:
        print(f"product name '{name_product}' is already taken")
        return None

    new_id = generate_id()

    if new_id is None:
        return None

    price_product = normalize_price(fields[PRICE_KEY])
    quantity_product = fields[QUANTITY_KEY]

    product_names.add(name_product)
    storage[new_id] = {
        NAME_KEY: name_product,
        PRICE_KEY: price_product,
        QUANTITY_KEY: quantity_product,
    }
    return new_id


@collect_stats(READ_KEY, STATS_REGISTRY)
def read_product(storage: dict[int, Product], product_id: int) -> Product | None:
    reading = storage.get(product_id)
    if reading is None:
        print(f"no product with id {product_id}")
    return reading


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

    if fields.get(NAME_KEY) is not None:
        fields[NAME_KEY] = normalize_product_name(fields[NAME_KEY])

        if not fields[NAME_KEY]:
            print("product name must not be blank")
            return None

        if (fields[NAME_KEY] != storage[product_id][NAME_KEY]) and (
            fields[NAME_KEY] in product_names
        ):
            print(f"product name '{fields[NAME_KEY]}' is already taken")
            return None

    if fields.get(PRICE_KEY) is not None:
        fields[PRICE_KEY] = normalize_price(fields[PRICE_KEY])

    if fields.get(NAME_KEY) is not None:
        product_names.discard(storage[product_id][NAME_KEY])
        product_names.add(fields[NAME_KEY])
        storage[product_id][NAME_KEY] = fields[NAME_KEY]

    if fields.get(PRICE_KEY) is not None:
        storage[product_id][PRICE_KEY] = fields[PRICE_KEY]

    if fields.get(QUANTITY_KEY) is not None:
        storage[product_id][QUANTITY_KEY] = fields[QUANTITY_KEY]

    return storage[product_id]


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
