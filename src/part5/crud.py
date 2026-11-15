from collections.abc import Callable
from typing import Any, Final

from .decorators import Registry, collect_stats
from .snowflake import get_snowflake_id_generator
from .storage import NAME_KEY, PRICE_KEY, QUANTITY_KEY, Product
from .utils import normalize_price, normalize_product_name


STATS_REGISTRY: Final[Registry] = {}

CREATE_KEY: Final[str] = "create"
READ_KEY: Final[str] = "read"
UPDATE_KEY: Final[str] = "update"
DELETE_KEY: Final[str] = "delete"


_SNOWFLAKE_GENERATOR = get_snowflake_id_generator()


def generate_snowflake_id() -> int | None:
    if _SNOWFLAKE_GENERATOR is None:
        return None

    return _SNOWFLAKE_GENERATOR()


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
def read_product(
    storage: dict[int, Product],
    product_id: int,
) -> Product | None:

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


@collect_stats(DELETE_KEY, STATS_REGISTRY)
def delete_product(
    storage: dict[int, Product],
    product_names: set[str],
    product_id: int,
) -> int | None:

    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None

    product = storage.pop(product_id)
    product_names.remove(product[NAME_KEY])

    return product_id
