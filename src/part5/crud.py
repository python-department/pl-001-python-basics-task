from collections.abc import Callable
from decimal import Decimal
from typing import Any, Final

from .decorators import Registry, collect_stats
from .snowflake import get_snowflake_id_generator
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


STATS_REGISTRY: Final[Registry] = {}

CREATE_KEY: Final[str] = "create"
READ_KEY: Final[str] = "read"
UPDATE_KEY: Final[str] = "update"
DELETE_KEY: Final[str] = "delete"

SNOWFLAKE_GENERATOR: Final[Callable[[], int | None] | None] = (
    get_snowflake_id_generator()
)


def generate_snowflake_id() -> int | None:
    if SNOWFLAKE_GENERATOR is None:
        return None
    return SNOWFLAKE_GENERATOR()


@collect_stats(CREATE_KEY, STATS_REGISTRY)
def create_product(
    storage: dict[int, Product],
    product_names: set[str],
    fields: dict[str, Any],
    generate_id: Callable[[], int | None],
) -> int | None:
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

    product_id = generate_id()
    if product_id is None:
        return None

    normalized_price = normalize_price(price)

    new_product: Product = {
        NAME_KEY: normalized_name,
        PRICE_KEY: normalized_price,
        QUANTITY_KEY: quantity,
    }
    storage[product_id] = new_product
    product_names.add(normalized_name)

    return product_id


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


@collect_stats(DELETE_KEY, STATS_REGISTRY)
def delete_product(
    storage: dict[int, Product],
    product_names: set[str],
    product_id: int,
) -> int | None:
    if product_id in storage:
        product = storage.pop(product_id)
        product_names.remove(product[NAME_KEY])
        return product_id

    print(f"no product with id {product_id}")
    return None
