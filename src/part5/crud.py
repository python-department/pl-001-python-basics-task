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

_snowflake_id_generator = get_snowflake_id_generator()


def generate_snowflake_id() -> int | None:
    if _snowflake_id_generator is None:
        return None
    return _snowflake_id_generator()


@collect_stats(CREATE_KEY, STATS_REGISTRY)
def create_product(
    storage: dict[int, Product],
    product_names: set[str],
    fields: dict[str, Any],
    generate_id: Callable[[], int | None],
) -> int | None:
    name = normalize_product_name(fields[NAME_KEY])
    if not name:
        print("product name must not be blank")
        return None
    if name in product_names:
        print(f"product name '{name}' is already taken")
        return None
    product_id = generate_id()
    if product_id is None:
        return None
    storage[product_id] = {
        NAME_KEY: name,
        PRICE_KEY: normalize_price(fields[PRICE_KEY]),
        QUANTITY_KEY: fields[QUANTITY_KEY],
    }
    product_names.add(name)
    return product_id


@collect_stats(READ_KEY, STATS_REGISTRY)
def read_product(storage: dict[int, Product], product_id: int) -> Product | None:
    product = storage.get(product_id)
    if product is not None:
        return product

    print(f"no product with id {product_id}")
    return None


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
    old_name = product[NAME_KEY]
    new_name: str | None = None

    if NAME_KEY in fields:
        name = normalize_product_name(fields[NAME_KEY])
        if not name:
            print("product name must not be blank")
            return None
        if name != old_name and name in product_names:
            print(f"product name '{name}' is already taken")
            return None
        new_name = name
        fields[NAME_KEY] = name

    if PRICE_KEY in fields:
        fields[PRICE_KEY] = normalize_price(fields[PRICE_KEY])

    for key in (NAME_KEY, PRICE_KEY, QUANTITY_KEY):
        if key in fields:
            product[key] = fields[key]

    if new_name is not None and new_name != old_name:
        product_names.discard(old_name)
        product_names.add(new_name)

    return product


@collect_stats(DELETE_KEY, STATS_REGISTRY)
def delete_product(
    storage: dict[int, Product],
    product_names: set[str],
    product_id: int,
) -> int | None:
    if product_id in storage:
        product_names.discard(storage[product_id][NAME_KEY])
        del storage[product_id]
        return product_id

    print(f"no product with id {product_id}")
    return None
