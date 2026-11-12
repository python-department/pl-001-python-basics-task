"""Create/read/update/delete operations over the in-memory product store.

Every operation takes the store -- a dictionary mapping product id to its
:data:`~src.part5.storage.Product` record -- as its first argument and
works on it in place. ``create_product``, ``update_product`` and
``delete_product`` additionally take ``product_names``, the ``set[str]``
of normalised names currently in ``storage`` (see
:mod:`src.part5.storage`), and keep it in sync with ``storage`` on
every successful call. The failure path never raises: the operation
prints an explanatory message to stdout and returns ``None``.

The identifier of a new product is not chosen by :func:`create_product`
itself: the caller hands in a zero-argument ``generate_id`` function that
returns the next identifier (or ``None`` when it cannot issue one), so the
identifier scheme can be swapped without touching the CRUD code. The module
supplies :func:`generate_snowflake_id`, backed by a Twitter Snowflake
generator (see :mod:`src.part5.snowflake`); the identifiers it issues
grow with creation time, so they are roughly ordered by insertion.

Every product name that reaches the store is passed through
:func:`~src.part5.utils.normalize_product_name` first. A name that
normalises to an empty string is rejected -- the operation prints a
message and changes nothing. Names are also kept unique --
:func:`create_product` refuses a normalised name that is already taken,
and :func:`update_product` refuses one that is already taken by another
product -- via an O(1) membership test against ``product_names`` rather
than a scan over ``storage.values()``.

The four store operations (everything except :func:`generate_snowflake_id`)
should be decorated with :func:`~src.part5.decorators.collect_stats`, which
counts their successful calls and their failed ones (those returning
``None``) in the module-level :data:`STATS_REGISTRY`, filed under
:data:`CREATE_KEY`, :data:`READ_KEY`, :data:`UPDATE_KEY` and
:data:`DELETE_KEY`. The counters live for the lifetime of the process and
are shared by every store.
"""

from collections.abc import Callable
from typing import Any, Final

from .decorators import Registry, collect_stats
from .snowflake import get_snowflake_id_generator
from .storage import NAME_KEY, PRICE_KEY, QUANTITY_KEY, Product
from .utils import normalize_price, normalize_product_name


STATS_REGISTRY: Final[Registry] = {}

# TODO: задайте ключи операций в реестре, см. TASK.md
CREATE_KEY: Final[str] = "create"
READ_KEY: Final[str] = "read"
UPDATE_KEY: Final[str] = "update"
DELETE_KEY: Final[str] = "delete"

# TODO: при необходимости заведите здесь общий генератор Snowflake-идентификаторов
# для generate_snowflake_id (см. TASK.md)
global_generator = get_snowflake_id_generator()


def generate_snowflake_id() -> int | None:
    if global_generator is None:
        return None

    return global_generator()


@collect_stats(CREATE_KEY, STATS_REGISTRY)
def create_product(
    storage: dict[int, Product],
    product_names: set[str],
    fields: dict[str, Any],
    generate_id: Callable[[], int | None],
) -> int | None:

    form_name = normalize_product_name(fields[NAME_KEY])
    if not form_name:
        print("product name must not be blank")
        return None

    if form_name in product_names:
        print(f"product name {form_name!r} is already taken")
        return None

    new_id = generate_id()
    if new_id is None:
        return None

    form_price = normalize_price(fields[PRICE_KEY])
    new_fields = {
        NAME_KEY: form_name,
        PRICE_KEY: form_price,
        QUANTITY_KEY: fields[QUANTITY_KEY],
    }
    storage[new_id] = new_fields
    product_names.add(form_name)

    return new_id


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
    curr_product = storage[product_id]
    curr_name = curr_product[NAME_KEY]

    if NAME_KEY in fields:
        form_name = normalize_product_name(fields[NAME_KEY])
        if not form_name:
            print("product name must not be blank")
            return None

        if form_name != curr_name and form_name in product_names:
            print(f"product name {form_name!r} is already taken")
            return None

        fields[NAME_KEY] = form_name

    if PRICE_KEY in fields:
        form_price = normalize_price(fields[PRICE_KEY])
        fields[PRICE_KEY] = form_price

    if NAME_KEY in fields and fields[NAME_KEY] != curr_name:
        product_names.remove(curr_name)
        product_names.add(fields[NAME_KEY])

    curr_product.update(fields)
    return curr_product


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
