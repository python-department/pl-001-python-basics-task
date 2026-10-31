"""Create/read/update/delete operations over the in-memory product store.

Every operation takes the store -- a list of
:data:`~src.part2.storage.Product` tuples -- as its first argument and
works on it in place. The failure path never raises: the operation prints
an explanatory message to stdout and returns ``None``.

The identifier of a new product is derived from the store itself
(:func:`generate_product_id`): one past the greatest identifier in use, or
:data:`~src.part2.storage.PRODUCT_ID_MIN` when the store is empty.
Product names are kept unique -- :func:`create_product` refuses a name that
is already taken.
"""

from decimal import Decimal

from .storage import (
    FIELDS_NAME_INDEX,
    FIELDS_PRICE_INDEX,
    FIELDS_QUANTITY_INDEX,
    NAME_INDEX,
    PRODUCT_ID_INDEX,
    PRODUCT_ID_MIN,
    Product,
)
from .utils import normalize_price


def generate_product_id(storage: list[Product]) -> int:
    """Choose the identifier for the next product added to ``storage``.

    Args:
        storage: The product store to inspect.

    Returns:
        One past the greatest identifier currently held in ``storage``, or
        :data:`~src.part2.storage.PRODUCT_ID_MIN` when ``storage`` is
        empty.
    """
    if not storage:
        return PRODUCT_ID_MIN

    return max(product[PRODUCT_ID_INDEX] for product in storage) + 1


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    """Append a new product to ``storage`` and return its new identifier.

    Args:
        storage: The product store to append to; modified in place on
            success.
        fields: A ``(name, price, quantity)`` tuple describing the product.
            ``price`` is a :class:`~decimal.Decimal` amount and is rounded
            to the stored money precision before it is saved.

    Returns:
        The identifier generated for the new product, or ``None`` when a
        product with the same name already exists. In the ``None`` case
        ``storage`` is left unchanged and a message naming the clashing
        name is printed.
    """
    if any(fields[FIELDS_NAME_INDEX] == product[NAME_INDEX] for product in storage):
        print(f"product name {fields[FIELDS_NAME_INDEX]} is already taken")
        return None

    new_id = generate_product_id(storage)
    new_price = normalize_price(fields[FIELDS_PRICE_INDEX])

    storage.append(
        (new_id, fields[FIELDS_NAME_INDEX], new_price, fields[FIELDS_QUANTITY_INDEX])
    )

    return new_id


def read_product(storage: list[Product], product_id: int) -> Product | None:
    """Return the product stored under ``product_id``.

    Args:
        storage: The product store to search.
        product_id: The identifier to look up.

    Returns:
        The matching ``(product_id, name, price, quantity)`` record, or
        ``None`` when no product carries that identifier (a message is
        printed in that case).
    """
    for product in storage:
        if product[PRODUCT_ID_INDEX] == product_id:
            return product

    print(f"no product with id {product_id}")
    return None


def update_product(
    storage: list[Product],
    product_id: int,
    fields: tuple[str, Decimal, int],
) -> Product | None:
    """Overwrite the fields of the product stored under ``product_id``.

    The identifier itself is preserved; only ``name``, ``price`` and
    ``quantity`` are replaced.

    Args:
        storage: The product store to modify; the matching record is
            replaced in place on success.
        product_id: The identifier of the product to change.
        fields: A ``(name, price, quantity)`` tuple with the new values.
            ``price`` is a :class:`~decimal.Decimal` amount and is rounded
            to the stored money precision before it is saved.

    Returns:
        The updated ``(product_id, name, price, quantity)`` record, or
        ``None`` when no product carries that identifier (``storage`` is
        left unchanged and a message is printed). Also ``None`` when
        product name is already taken.
    """
    index_modifiable_product = -1

    for index in range(len(storage)):
        if storage[index][NAME_INDEX] == fields[FIELDS_NAME_INDEX]:
            print(f"product name {fields[FIELDS_NAME_INDEX]} is already taken")
            return None

        if storage[index][PRODUCT_ID_INDEX] == product_id:
            index_modifiable_product = index

    if index_modifiable_product == -1:
        print(f"no product with id {product_id}")
        return None

    new_price = normalize_price(fields[FIELDS_PRICE_INDEX])

    storage[index_modifiable_product] = (
        product_id,
        fields[FIELDS_NAME_INDEX],
        new_price,
        fields[FIELDS_QUANTITY_INDEX],
    )

    return storage[index_modifiable_product]


def delete_product(storage: list[Product], product_id: int) -> int | None:
    """Remove the product stored under ``product_id`` from ``storage``.

    Args:
        storage: The product store to remove from; modified in place on
            success.
        product_id: The identifier of the product to remove.

    Returns:
        ``product_id`` when a product was removed, or ``None`` when no
        product carried that identifier (``storage`` is left unchanged and
        a message is printed).
    """
    for i, product in enumerate(storage):
        if product[PRODUCT_ID_INDEX] == product_id:
            del storage[i]
            return product_id

    print(f"no product with id {product_id}")
    return None
