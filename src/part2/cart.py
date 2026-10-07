"""Shopping-cart operations layered on top of the product store.

The cart is a plain list of tuples, one :data:`CartLine` --
``(product_id, quantity)`` -- per distinct product. Moving units between the
store and the cart keeps the two sides in balance: :func:`add_to_cart` takes
units out of stock, :func:`remove_from_cart` puts them back.

Like the CRUD layer, the failure path never raises -- the operation prints
an explanatory message to stdout and returns ``None``.
"""

from typing import Final

from .crud import read_product
from .storage import (
    NAME_INDEX,
    PRICE_INDEX,
    PRODUCT_ID_INDEX,
    QUANTITY_INDEX,
    Product,
)


type CartLine = tuple[int, int]

# TODO: задайте позиции полей внутри кортежа CartLine
LINE_PRODUCT_ID_INDEX: Final = 0
LINE_QUANTITY_INDEX: Final = 1


def find_cart_line(cart: list[CartLine], product_id: int) -> CartLine | None:
    """Return the cart line stored under ``product_id``.

    Args:
        cart: The store of cart line.
        product_id: The identifier to look up.

    Returns:
        The matching ``(product_id, line_quantity)`` record,
        ``None`` when no cart line carries that identifier (a message is
        printed in that case).
    """
    for cart_line in cart:
        if cart_line[LINE_PRODUCT_ID_INDEX] == product_id:
            return cart_line
    return None


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
    product = read_product(storage, product_id)
    if product is None:
        return None
    if product[QUANTITY_INDEX] < quantity:
        print(
            f"not enough stock for product {product_id}: "
            f"{product[QUANTITY_INDEX]} available, {quantity} requested"
        )
        return None

    for index_product, cell in enumerate(storage):
        if cell[PRODUCT_ID_INDEX] == product_id:
            storage[index_product] = (
                cell[PRODUCT_ID_INDEX],
                cell[NAME_INDEX],
                cell[PRICE_INDEX],
                cell[QUANTITY_INDEX] - quantity,
            )
            break
    else:
        return None

    for index_line, purchase in enumerate(cart):
        if purchase[LINE_PRODUCT_ID_INDEX] == product_id:
            new_line: CartLine = (
                purchase[LINE_PRODUCT_ID_INDEX],
                purchase[LINE_QUANTITY_INDEX] + quantity,
            )
            cart[index_line] = new_line
            return new_line

    new_line = (product_id, quantity)
    cart.append(new_line)
    return new_line


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
    our_line = find_cart_line(cart, product_id)
    if our_line is None:
        print(f"product {product_id} is not in the cart")
        return None
    if our_line[LINE_QUANTITY_INDEX] < quantity:
        print(
            f"cart holds only {our_line[LINE_QUANTITY_INDEX]} unit(s) "
            f"of product {product_id}, cannot remove {quantity}"
        )
        return None

    product = read_product(storage, product_id)
    if product is None:
        return None

    for index_product, stored_product in enumerate(storage):
        if stored_product[PRODUCT_ID_INDEX] == product_id:
            storage[index_product] = (
                stored_product[PRODUCT_ID_INDEX],
                stored_product[NAME_INDEX],
                stored_product[PRICE_INDEX],
                stored_product[QUANTITY_INDEX] + quantity,
            )
            break
    else:
        return None

    for index_cart_line, cart_line in enumerate(cart):
        if cart_line[LINE_PRODUCT_ID_INDEX] == product_id:
            new_quantity = cart_line[LINE_QUANTITY_INDEX] - quantity
            if new_quantity == 0:
                del cart[index_cart_line]
                return (product_id, 0)
            updated_line: CartLine = (product_id, new_quantity)
            cart[index_cart_line] = updated_line
            return updated_line

    return None
