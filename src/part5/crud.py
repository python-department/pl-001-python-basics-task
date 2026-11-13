from collections.abc import Callable
from typing import Any, Final

from .decorators import Registry, collect_stats
from .snowflake import get_snowflake_id_generator
from .storage import (
    NAME_KEY,
    PRICE_KEY,
    Product,
)
from .utils import normalize_price, normalize_product_name


STATS_REGISTRY: Final[Registry] = {}


CREATE_KEY: Final[str] = "create"
READ_KEY: Final[str] = "read"
UPDATE_KEY: Final[str] = "update"
DELETE_KEY: Final[str] = "delete"


general_generator = get_snowflake_id_generator()


def generate_snowflake_id() -> int | None:
    if general_generator is None:
        return None
    result = general_generator()
    return result


def name_check(name: str, product_names: set[str]) -> bool | str:
    name = normalize_product_name(name)
    if name == "":
        print("product name must not be blank")
        return False
    if name in product_names:
        print(f"product name {name} is already taken")
        return False
    return name


@collect_stats(CREATE_KEY, STATS_REGISTRY)
def create_product(
    storage: dict[int, Product],
    product_names: set[str],
    fields: dict[str, Any],
    generate_id: Callable[[], int | None],
) -> int | None:

    check = name_check(fields[NAME_KEY], product_names)
    if not check:
        return None

    new_id = generate_id()
    if new_id is None:
        return None

    fields[NAME_KEY] = check
    product_names.add(fields[NAME_KEY])
    fields[PRICE_KEY] = normalize_price(fields[PRICE_KEY])

    storage[new_id] = fields
    return new_id


def id_check(num_id: int, storage: dict[int, Product]) -> bool:
    if num_id not in storage:
        print(f"no product with id {num_id}")
        return False
    return True


@collect_stats(READ_KEY, STATS_REGISTRY)
def read_product(storage: dict[int, Product], product_id: int) -> Product | None:
    if not id_check(product_id, storage):
        return None
    return storage[product_id]


@collect_stats(UPDATE_KEY, STATS_REGISTRY)
def update_product(
    storage: dict[int, Product],
    product_names: set[str],
    product_id: int,
    fields: dict[str, Any],
) -> Product | None:
    if not id_check(product_id, storage):
        return None

    if NAME_KEY in fields:
        fields[NAME_KEY] = normalize_product_name(fields[NAME_KEY])
        name = fields[NAME_KEY]
        if name == "":
            print("product name must not be blank")
            return None
        if name in product_names and storage[product_id][NAME_KEY] != name:
            print(f"product name {name} is already taken")
            return None
        if storage[product_id][NAME_KEY] != name:
            product_names.add(name)
            product_names.remove(storage[product_id][NAME_KEY])

    if PRICE_KEY in fields:
        fields[PRICE_KEY] = normalize_price(fields[PRICE_KEY])

    for nkey, value in fields.items():
        storage[product_id][nkey] = value
    return storage[product_id]


@collect_stats(DELETE_KEY, STATS_REGISTRY)
def delete_product(
    storage: dict[int, Product],
    product_names: set[str],
    product_id: int,
) -> int | None:

    if not id_check(product_id, storage):
        return None
    product_names.remove(storage[product_id][NAME_KEY])
    del storage[product_id]
    return product_id
