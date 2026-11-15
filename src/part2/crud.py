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
from typing import cast

from .storage import (
    NAME_INDEX,
    PRICE_INDEX,
    PRODUCT_ID_INDEX,
    PRODUCT_ID_MIN,
    QUANTITY_INDEX,
    Product,
)
from .utils import normalize_price


def make(  # чтобы можно было переставлять
    product_id: int,
    name: str,
    price: Decimal,
    quantity: int,
) -> Product:
    fields: list[int | str | Decimal] = [0] * 4
    fields[PRODUCT_ID_INDEX] = product_id
    fields[NAME_INDEX] = name
    fields[PRICE_INDEX] = price
    fields[QUANTITY_INDEX] = quantity
    return cast(Product, tuple(fields))


def generate_product_id(storage: list[Product]) -> int:
    """Choose the identifier for the next product added to ``storage``.

    Args:
        storage: The product store to inspect.

    Returns:
        One past the greatest identifier currently held in ``storage``, or
        :data:`~src.part2.storage.PRODUCT_ID_MIN` when ``storage`` is
        empty.
    """
    # TODO: реализуйте функцию
    if not storage:
        return PRODUCT_ID_MIN
    max_id = 0
    for product in storage:
        max_id = max(max_id, product[PRODUCT_ID_INDEX])
    return max_id + 1


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
    # TODO: реализуйте функцию
    name, price, quantity = fields
    for product in storage:
        if product[NAME_INDEX] == name:
            print(f"product name '{name}' is already taken")
            return None
    product_id = generate_product_id(storage)
    normalized_price = normalize_price(price)
    storage.append(make(product_id, name, normalized_price, quantity))
    return product_id


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
    # TODO: реализуйте функцию
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
        left unchanged and a message is printed).
    """
    # TODO: реализуйте функцию
    name, price, quantity = fields
    price = normalize_price(price)
    for i in range(len(storage)):
        product = storage[i]
        if product[PRODUCT_ID_INDEX] == product_id:
            updated_product = make(product_id, name, price, quantity)
            storage[i] = updated_product
            return updated_product
    print(f"no product with id {product_id}")
    return None


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
    # TODO: реализуйте функцию
    for product in storage:
        if product[PRODUCT_ID_INDEX] == product_id:
            storage.remove(product)
            return product_id
    print(f"no product with id {product_id}")
    return None
