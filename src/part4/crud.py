"""Create/read/update/delete operations over the in-memory product store.

Every operation takes the store -- a dictionary mapping product id to its
:data:`~src.part4.storage.Product` record -- as its first argument and
works on it in place. ``create_product``, ``update_product`` and
``delete_product`` additionally take ``product_names``, the ``set[str]``
of normalised names currently in ``storage`` (see
:mod:`src.part4.storage`), and keep it in sync with ``storage`` on
every successful call. The failure path never raises: the operation
prints an explanatory message to stdout and returns ``None``.

The identifier of a new product is a freshly generated UUID string
(:func:`generate_product_id`), independent of insertion order or of any
identifier already in ``storage``.

Every product name that reaches the store is passed through
:func:`~src.part4.utils.normalize_product_name` first. A name that
normalises to an empty string is rejected -- the operation prints a
message and changes nothing. Names are also kept unique --
:func:`create_product` refuses a normalised name that is already taken,
and :func:`update_product` refuses one that is already taken by another
product -- via an O(1) membership test against ``product_names`` rather
than a scan over ``storage.values()``.
"""

import uuid
from typing import Any

from .storage import (
    NAME_KEY,
    PRICE_KEY,
    QUANTITY_KEY,
    Product,
)
from .utils import normalize_price, normalize_product_name


def generate_product_id() -> str:
    """Generate an identifier for a new product.

    Returns:
        A freshly generated UUID, stringified.
    """
    return str(uuid.uuid4())


def create_product(
    storage: dict[str, Product],
    product_names: set[str],
    fields: dict[str, Any],
) -> str | None:
    """Add a new product to ``storage`` and return its new identifier.

    Args:
        storage: The product store to add to; modified in place on
            success.
        product_names: The normalised names already in ``storage``; the
            new name is added to it in place on success.
        fields: A dictionary with the ``name``, ``price`` and ``quantity``
            keys (see :data:`~src.part4.storage.NAME_KEY`,
            :data:`~src.part4.storage.PRICE_KEY` and
            :data:`~src.part4.storage.QUANTITY_KEY`) describing the
            product. ``name`` is normalised (surrounding whitespace
            stripped, lower-cased) before it is stored or compared.
            ``price`` is a :class:`~decimal.Decimal` amount and is rounded
            to the stored money precision before it is saved.

    Returns:
        The identifier generated for the new product, or ``None`` when
        ``name`` is blank once normalised or a product with the same
        normalised name already exists. In the ``None`` case ``storage``
        and ``product_names`` are left unchanged and an explanatory
        message is printed.
    """
    name, price, quantity = fields.values()

    name = normalize_product_name(name)

    if not name:
        print("product name must not be blank")
        return None

    if name in product_names:
        print(f"product name {name} is already taken")
        return None

    product_id = generate_product_id()

    storage[product_id] = {
        NAME_KEY: name,
        PRICE_KEY: normalize_price(price),
        QUANTITY_KEY: quantity,
    }

    product_names.add(name)

    return product_id


def read_product(storage: dict[str, Product], product_id: str) -> Product | None:
    """Return the product stored under ``product_id``.

    Args:
        storage: The product store to search.
        product_id: The identifier to look up.

    Returns:
        The matching product record, or ``None`` when no product carries
        that identifier (a message is printed in that case).
    """
    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None
    return storage[product_id]


def update_product(
    storage: dict[str, Product],
    product_names: set[str],
    product_id: str,
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
            ``quantity`` keys (see :data:`~src.part4.storage.NAME_KEY`,
            :data:`~src.part4.storage.PRICE_KEY` and
            :data:`~src.part4.storage.QUANTITY_KEY`) holding the new
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
    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None

    product = storage[product_id]

    if NAME_KEY in fields:
        name = normalize_product_name(fields[NAME_KEY])
        if not name:
            print("product name must not be blank")
            return None

        old_name = product[NAME_KEY]

        if name != old_name and name in product_names:
            print(f"product name {name} is already taken")
            return None

        fields[NAME_KEY] = name

        if old_name != name:
            product_names.remove(old_name)
            product_names.add(name)

    if PRICE_KEY in fields:
        fields[PRICE_KEY] = normalize_price(fields[PRICE_KEY])

    product.update(fields)

    return product


def delete_product(
    storage: dict[str, Product],
    product_names: set[str],
    product_id: str,
) -> str | None:
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
    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None

    product_names.remove(storage[product_id][NAME_KEY])
    del storage[product_id]

    return product_id
