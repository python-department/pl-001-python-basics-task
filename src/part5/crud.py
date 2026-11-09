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

from .decorators import Registry
from .storage import Product


STATS_REGISTRY: Final[Registry] = {}

# TODO: задайте ключи операций в реестре, см. TASK.md
CREATE_KEY: Final[str] = ""
READ_KEY: Final[str] = ""
UPDATE_KEY: Final[str] = ""
DELETE_KEY: Final[str] = ""

# TODO: при необходимости заведите здесь общий генератор Snowflake-идентификаторов
# для generate_snowflake_id (см. TASK.md)


def generate_snowflake_id() -> int | None:
    """Issue the next product identifier from the shared Snowflake generator.

    This is the identifier source callers pass to :func:`create_product`.

    Returns:
        A positive 63-bit Snowflake integer, or ``None`` (after a message
        has been printed) when no identifier can be issued right now -- see
        :func:`~src.part5.snowflake.get_snowflake_id_generator` for the
        cases.
    """
    # TODO: реализуйте функцию
    return 0


# TODO: оберните операцию декоратором collect_stats
def create_product(
    storage: dict[int, Product],
    product_names: set[str],
    fields: dict[str, Any],
    generate_id: Callable[[], int | None],
) -> int | None:
    """Add a new product to ``storage`` and return its new identifier.

    Args:
        storage: The product store to add to; modified in place on
            success.
        product_names: The normalised names already in ``storage``; the
            new name is added to it in place on success.
        fields: A dictionary with the ``name``, ``price`` and ``quantity``
            keys (see :data:`~src.part5.storage.NAME_KEY`,
            :data:`~src.part5.storage.PRICE_KEY` and
            :data:`~src.part5.storage.QUANTITY_KEY`) describing the
            product. ``name`` is normalised (surrounding whitespace
            stripped, lower-cased) before it is stored or compared.
            ``price`` is a :class:`~decimal.Decimal` amount and is rounded
            to the stored money precision before it is saved.
        generate_id: A zero-argument function returning the identifier for
            the new product, or ``None`` if it cannot issue one (for
            example :func:`generate_snowflake_id`). It is only expected to
            return an identifier that is not yet a key of ``storage``.

    Returns:
        The identifier returned by ``generate_id`` for the new product, or
        ``None`` when ``name`` is blank once normalised, a product with
        the same normalised name already exists, or ``generate_id``
        returned ``None``. In the ``None`` case ``storage`` and
        ``product_names`` are left unchanged and an explanatory message is
        printed (for the last case, by ``generate_id`` itself).
    """
    # TODO: реализуйте функцию
    return 0


# TODO: оберните операцию декоратором collect_stats
def read_product(storage: dict[int, Product], product_id: int) -> Product | None:
    """Return the product stored under ``product_id``.

    Args:
        storage: The product store to search.
        product_id: The identifier to look up.

    Returns:
        The matching product record, or ``None`` when no product carries
        that identifier (a message is printed in that case).
    """
    # TODO: реализуйте функцию (используйте своё решение части 4)
    return {}


# TODO: оберните операцию декоратором collect_stats
def update_product(
    storage: dict[int, Product],
    product_names: set[str],
    product_id: int,
    fields: dict[str, Any],
) -> Product | None:
    """Overwrite the fields of the product stored under ``product_id``.

    The identifier itself is preserved. ``fields`` may carry any subset of
    ``name``, ``price`` and ``quantity``; a key that is missing keeps the
    value the product already has, so a caller can update a single field
    without repeating the other two.

    Args:
        storage: The product store to modify; the matching record is
            updated in place on success.
        product_names: The normalised names already in ``storage``; on a
            successful rename the old name is removed from it and the new
            one added.
        product_id: The identifier of the product to change.
        fields: A dictionary with any of the ``name``, ``price`` and
            ``quantity`` keys (see :data:`~src.part5.storage.NAME_KEY`,
            :data:`~src.part5.storage.PRICE_KEY` and
            :data:`~src.part5.storage.QUANTITY_KEY`) holding the new
            values. ``price`` is a :class:`~decimal.Decimal` amount and is
            rounded to the stored money precision before it is saved.
            Mutated in place: a ``name`` or ``price`` value present in
            ``fields`` is overwritten with its normalised form.

    Returns:
        The updated product record, or ``None`` when ``name`` is present
        and blank once normalised, no product carries that identifier, or
        the normalised name is already taken by another product. In every
        ``None`` case ``storage`` and ``product_names`` are left unchanged
        and an explanatory message is printed. Renaming a product to its
        own current name is allowed.
    """
    # TODO: реализуйте функцию (используйте своё решение части 4)
    return {}


# TODO: оберните операцию декоратором collect_stats
def delete_product(
    storage: dict[int, Product],
    product_names: set[str],
    product_id: int,
) -> int | None:
    """Remove the product stored under ``product_id`` from ``storage``.

    Args:
        storage: The product store to remove from; modified in place on
            success.
        product_names: The normalised names already in ``storage``; the
            departing product's name is removed from it in place on
            success.
        product_id: The identifier of the product to remove.

    Returns:
        ``product_id`` when a product was removed, or ``None`` when no
        product carried that identifier (``storage`` and ``product_names``
        are left unchanged and a message is printed).
    """
    # TODO: реализуйте функцию (используйте своё решение части 4)
    return 0
