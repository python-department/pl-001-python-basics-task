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


_snowflake_id = get_snowflake_id_generator()


def generate_snowflake_id() -> int | None:
    if _snowflake_id is None:
        return None
    return _snowflake_id()


@collect_stats(CREATE_KEY, Registry)
def create_product(
    storage: dict[int, Product],
    product_names: set[str],
    fields: dict[str, Any],
    generate_id: Callable[[], int | None],
) -> int | None:
    name = fields[NAME_KEY]
    price = fields[PRICE_KEY]
    quantity = fields[QUANTITY_KEY]
    norm_name = normalize_product_name(name)

    if not norm_name:
        print("product name must not be blank")
        return None

    if norm_name in product_names:
        print(f"product {norm_name!r}  is already taken")
        return None

    id = generate_id()
    if id is None:
        return None

    storage[id] = {
        NAME_KEY: norm_name,
        PRICE_KEY: normalize_price(price),
        QUANTITY_KEY: quantity,
    }
    product_names.add(norm_name)
    return id


@collect_stats(READ_KEY, Registry)
def read_product(storage: dict[int, Product], product_id: int) -> Product | None:
    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None
    else:
        return storage[product_id]


@collect_stats(UPDATE_KEY, Registry)
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

    if NAME_KEY in fields:
        normalized_name = normalize_product_name(fields[NAME_KEY])

        if not normalized_name:
            print("product name must not be blank")
            return None

        if normalized_name != old_name and normalized_name in product_names:
            print(f"product name '{normalized_name}' is already taken")
            return None

        fields[NAME_KEY] = normalized_name

    if PRICE_KEY in fields:
        fields[PRICE_KEY] = normalize_price(fields[PRICE_KEY])

    product.update(fields)

    if NAME_KEY in fields:
        new_name = fields[NAME_KEY]
        if new_name != old_name:
            product_names.remove(old_name)
            product_names.add(new_name)

    return product


@collect_stats(DELETE_KEY, Registry)
def delete_product(
    storage: dict[int, Product],
    product_names: set[str],
    product_id: int,
) -> int | None:
    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None

    product = storage[product_id]
    name = product[NAME_KEY]

    product_names.remove(name)
    del storage[product_id]
    return product_id
