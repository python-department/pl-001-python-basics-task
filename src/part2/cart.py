"""Shopping-cart operations layered on top of the product store.

The cart is a plain list of tuples, one :data:`CartLine` --
``(product_id, quantity)`` -- per distinct product. Moving units between the
store and the cart keeps the two sides in balance: :func:`add_to_cart` takes
units out of stock, :func:`remove_from_cart` puts them back.

Like the CRUD layer, the failure path never raises -- the operation prints
an explanatory message to stdout and returns ``None``.
"""

from typing import Final

from .crud import read_product, update_product
from .storage import (
    NAME_INDEX,
    PRICE_INDEX,
    QUANTITY_INDEX,
    Product,
)


type CartLine = tuple[int, int]

LINE_PRODUCT_ID_INDEX: Final = 0
LINE_QUANTITY_INDEX: Final = 1


def add_to_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    """Move ``quantity`` units of ``product_id`` from the store into ``cart``.

    The product is looked up in ``storage``. If it is missing, a message is
    printed (by :func:`~src.part2.crud.read_product`) and nothing
    changes. If the store holds fewer units than requested, an explanatory
    message is printed and nothing changes. Otherwise the store record is
    decremented by ``quantity`` and the cart line for ``product_id`` gains
    ``quantity`` units -- a new line is created when the cart had none.

    Args:
        storage: The product store to draw stock from; modified in place on
            success.
        cart: The cart to add the units to; modified in place on success.
        product_id: The identifier of the product to add.
        quantity: Number of units to move into the cart.

    Returns:
        The cart line for ``product_id`` after the addition, or ``None``
        when the product is unknown or the store cannot cover the request.
    """
    storage_product = read_product(storage, product_id)

    if storage_product is None:
        return None

    if storage_product[QUANTITY_INDEX] < quantity:
        print(
            f"not enough stock for product {product_id}: "
            f"{storage_product[QUANTITY_INDEX]} available, {quantity} requested"
        )
        return None

    product_fields = (
        storage_product[NAME_INDEX],
        storage_product[PRICE_INDEX],
        storage_product[QUANTITY_INDEX] - quantity,
    )
    update_product(storage, product_id, product_fields)

    return change_cart_quantity(cart, product_id, quantity)


def remove_from_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    """Move ``quantity`` units of ``product_id`` from ``cart`` back to the store.

    The cart line for ``product_id`` is looked up. If there is none, a
    message is printed and nothing changes. If the line holds fewer units
    than requested, an explanatory message is printed and nothing changes.
    Otherwise the cart line loses ``quantity`` units -- the line is dropped
    when it reaches zero -- and the store record gains ``quantity`` units
    back.

    Args:
        storage: The product store to return stock to; modified in place on
            success.
        cart: The cart to take the units from; modified in place on
            success.
        product_id: The identifier of the product to remove.
        quantity: Number of units to move back into the store.

    Returns:
        The cart line for ``product_id`` after the removal (a quantity of
        zero means the line was dropped), or ``None`` when the cart has no
        line for the product or holds too few units.
    """
    if not find_cart_line(cart, product_id):
        print(f"product {product_id} is not in the cart")
        return None

    cart_line = read_cart_line(cart, product_id)
    if cart_line is not None and cart_line[LINE_QUANTITY_INDEX] < quantity:
        print(
            f"cart holds only {cart_line[LINE_QUANTITY_INDEX]} unit(s) "
            f"of product {product_id}, cannot remove {quantity}"
        )
        return None

    storage_product = read_product(storage, product_id)
    if storage_product is None:
        return None

    storage_fields = (
        storage_product[NAME_INDEX],
        storage_product[PRICE_INDEX],
        storage_product[QUANTITY_INDEX] + quantity,
    )
    update_product(storage, product_id, storage_fields)

    new_line = change_cart_quantity(cart, product_id, -quantity)
    if new_line[LINE_QUANTITY_INDEX] != 0:
        return new_line

    cart.remove(new_line)
    return (product_id, 0)


def find_cart_line(cart: list[CartLine], product_id: int) -> bool:
    for line in cart:
        if line[LINE_PRODUCT_ID_INDEX] == product_id:
            return True
    return False


def read_cart_line(cart: list[CartLine], product_id: int) -> CartLine | None:
    for line in cart:
        if line[LINE_PRODUCT_ID_INDEX] == product_id:
            return line
    return None


def change_cart_quantity(
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine:
    """Change the quantity of the cart line for ``product_id`` by ``quantity``.

    Creates the line when the cart has none for the product.

    Args:
        cart: The cart to modify; modified in place.
        product_id: The identifier of the product whose line changes.
        quantity: The delta applied to the line quantity.

    Returns:
        The cart line for ``product_id`` after the change.
    """
    cart_line = read_cart_line(cart, product_id)
    if cart_line is not None:
        new_line = (product_id, cart_line[LINE_QUANTITY_INDEX] + quantity)
        cart[cart.index(cart_line)] = new_line
        return new_line

    new_line = (product_id, quantity)
    cart.append(new_line)
    return new_line
