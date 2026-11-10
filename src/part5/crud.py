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


SNOWFLAKE_GENERATOR = get_snowflake_id_generator()


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
    good_name = normalize_product_name(fields[NAME_KEY])

    if not good_name:
        print("product name must not be blank")
        return None

    if good_name in product_names:
        print(f"product name '{good_name}' is already taken")
        return None

    product_id = generate_id()
    if product_id is None:
        return None

    storage[product_id] = {
        NAME_KEY: good_name,
        PRICE_KEY: normalize_price(fields[PRICE_KEY]),
        QUANTITY_KEY: fields[QUANTITY_KEY],
    }
    product_names.add(good_name)
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
    if NAME_KEY in fields:
        fields[NAME_KEY] = normalize_product_name(fields[NAME_KEY])
        if not fields[NAME_KEY]:
            print("product name must not be blank")
            return None
        if (
            storage[product_id][NAME_KEY] != fields[NAME_KEY]
            and fields[NAME_KEY] in product_names
        ):
            print(f"product name '{fields[NAME_KEY]}' is already taken")
            return None
    if PRICE_KEY in fields:
        fields[PRICE_KEY] = normalize_price(fields[PRICE_KEY])

    if NAME_KEY in fields and fields[NAME_KEY] != storage[product_id][NAME_KEY]:
        product_names.remove(storage[product_id][NAME_KEY])
        product_names.add(fields[NAME_KEY])

    storage[product_id].update(fields)

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

    product_names.remove(storage[product_id][NAME_KEY])
    del storage[product_id]

    return product_id
