"""Create/read/update/delete operations over the in-memory product store.

Every operation takes the store -- a list of
:data:`~src.part3.storage.Product` tuples -- as its first argument and
works on it in place. The failure path never raises: the operation prints
an explanatory message to stdout and returns ``None``.

The identifier of a new product is derived from the store itself
(:func:`generate_product_id`): one past the greatest identifier in use, or
:data:`~src.part3.storage.PRODUCT_ID_MIN` when the store is empty.

Every product name that reaches the store is passed through
:func:`~src.part3.utils.normalize_product_name` first. A name that
normalises to an empty string is rejected -- the operation prints a
message and changes nothing. Names are also kept unique --
:func:`create_product` refuses a normalised name that is already taken,
and :func:`update_product` refuses one that is already taken by another
product.
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
from .utils import normalize_price, normalize_product_name


def make(
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
        :data:`~src.part3.storage.PRODUCT_ID_MIN` when ``storage`` is
        empty.
    """
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
            ``name`` is normalised (surrounding whitespace stripped,
            lower-cased) before it is stored or compared. ``price`` is a
            :class:`~decimal.Decimal` amount and is rounded to the stored
            money precision before it is saved.

    Returns:
        The identifier generated for the new product, or ``None`` when
        ``name`` is blank once normalised or a product with the same
        normalised name already exists. In the ``None`` case ``storage``
        is left unchanged and an explanatory message is printed.
    """
    name, price, quantity = fields
    name = normalize_product_name(name)
    if name == "":
        print("product name must not be blank")
        return None
    for product in storage:
        if product[NAME_INDEX] == name:
            print(f"product name '{name}' is already taken")
            return None
    new_id = generate_product_id(storage)
    fixed_price = normalize_price(price)
    storage.append(make(new_id, name, fixed_price, quantity))
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
        ``None`` when ``name`` is blank once normalised, no product
        carries that identifier, or the normalised name is already taken
        by another product. In every ``None`` case ``storage`` is left
        unchanged and an explanatory message is printed. Renaming a
        product to its own current name is allowed.
    """
    name, price, quantity = fields
    name = normalize_product_name(name)
    if name == "":
        print("product name must not be blank")
        return None
    index = -1
    for i in range(len(storage)):
        if storage[i][PRODUCT_ID_INDEX] == product_id:
            index = i
            break
    if index == -1:
        print(f"no product with id {product_id}")
        return None
    for product in storage:
        if product[NAME_INDEX] == name and product[PRODUCT_ID_INDEX] != product_id:
            print(f"product name '{name}' is already taken")
            return None
    fixed_price = normalize_price(price)
    new_record = make(product_id, name, fixed_price, quantity)
    storage[index] = new_record
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
    for product in storage:
        if product[PRODUCT_ID_INDEX] == product_id:
            storage.remove(product)
            return product_id
    print(f"no product with id {product_id}")
    return None
