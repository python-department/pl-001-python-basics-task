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

from .storage import (
    NAME_INDEX,
    PRODUCT_ID_INDEX,
    PRODUCT_ID_MIN,
    Product,
)
from .utils import normalize_price, normalize_product_name


def generate_product_id(storage: list[Product]) -> int:
    """Choose the identifier for the next product added to ``storage``.

    Args:
        storage: The product store to inspect.

    Returns:
        One past the greatest identifier currently held in ``storage``, or
        :data:`~src.part3.storage.PRODUCT_ID_MIN` when ``storage`` is
        empty.
    """
    # TODO: реализуйте функцию (используйте своё решение части 2)
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
    # TODO: реализуйте функцию
    name, price, quantity = fields
    name = normalize_product_name(name)
    if not name:
        print("product name must not be blank")
        return None
    for product in storage:
        if product[NAME_INDEX] == name:
            print(f"product name '{name}' is already taken")
            return None
    product_id = generate_product_id(storage)
    price = normalize_price(price)
    new_product = (product_id, name, price, quantity)
    storage.append(new_product)
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
    # TODO: реализуйте функцию (используйте своё решение части 2)
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
    # TODO: реализуйте функцию
    name, price, quantity = fields
    name = normalize_product_name(name)
    if not name:
        print("product name must not be blank")
        return None
    target_index = None
    for i, product in enumerate(storage):
        if product[PRODUCT_ID_INDEX] == product_id:
            target_index = i
            break
    if target_index is None:
        print(f"no product with id {product_id}")
        return None
    for product in storage:
        if product[NAME_INDEX] == name and product[PRODUCT_ID_INDEX] != product_id:
            print(f"product name '{name}' is already taken")
            return None
    price = normalize_price(price)
    updated_product = (product_id, name, price, quantity)
    storage[target_index] = updated_product
    return updated_product


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
    # TODO: реализуйте функцию (используйте своё решение части 2)
    for i, product in enumerate(storage):
        if product[PRODUCT_ID_INDEX] == product_id:
            del storage[i]
            return product_id
    print(f"no product with id {product_id}")
    return None
