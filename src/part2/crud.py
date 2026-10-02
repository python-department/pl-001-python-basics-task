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
from typing import Any

from .storage import (
    NAME_INDEX,
    PRICE_INDEX,
    PRODUCT_ID_INDEX,
    PRODUCT_ID_MIN,
    QUANTITY_INDEX,
    Product,
)
from .utils import normalize_price


def dict_to_product(record: dict[int, Any]) -> Product:
    return tuple(x[1] for x in sorted(record.items()))


def generate_product_id(storage: list[Product]) -> int:
    """Choose the identifier for the next product added to ``storage``.

    Args:
        storage: The product store to inspect.

    Returns:
        One past the greatest identifier currently held in ``storage``, or
        :data:`~src.part2.storage.PRODUCT_ID_MIN` when ``storage`` is
        empty.
    """
    return (
        PRODUCT_ID_MIN
        if not storage
        else max(storage, key=lambda x: x[PRODUCT_ID_INDEX])[PRODUCT_ID_INDEX] + 1
    )


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
    if fields[0] in [x[NAME_INDEX] for x in storage]:
        print(f"product name {fields[0]} is already taken")
        return None
    dict_record = {
        PRODUCT_ID_INDEX: generate_product_id(storage),
        NAME_INDEX: fields[0],
        PRICE_INDEX: normalize_price(fields[1]),
        QUANTITY_INDEX: fields[2],
    }
    new_record = dict_to_product(dict_record)
    storage.append(new_record)
    storage.sort()
    return new_record[PRODUCT_ID_INDEX]


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
    record = [x for x in storage if x[PRODUCT_ID_INDEX] == product_id]
    if not record:
        print(f"no product with id {product_id}")
        return None
    return record[0]


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
        left unchanged and a message is printed).
    """
    record = read_product(storage, product_id)
    if not record:
        return None

    dict_record = {
        PRODUCT_ID_INDEX: record[PRODUCT_ID_INDEX],
        NAME_INDEX: fields[0],
        PRICE_INDEX: normalize_price(fields[1]),
        QUANTITY_INDEX: fields[2],
    }
    new_record = dict_to_product(dict_record)
    storage.remove(record)
    storage.append(new_record)
    storage.sort()

    return new_record


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
    record = read_product(storage, product_id)
    if not record:
        return None

    storage.remove(record)
    return product_id
