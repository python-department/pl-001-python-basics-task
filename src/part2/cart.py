"""Shopping-cart operations layered on top of the product store.

The cart is a plain list of tuples, one :data:`CartLine` --
``(product_id, quantity)`` -- per distinct product. Moving units between the
store and the cart keeps the two sides in balance: :func:`add_to_cart` takes
units out of stock, :func:`remove_from_cart` puts them back.

Like the CRUD layer, the failure path never raises -- the operation prints
an explanatory message to stdout and returns ``None``.
"""

from typing import Final, Literal

from part2.crud import read_product
from part2.storage import (
    NAME_INDEX,
    PRICE_INDEX,
    PRODUCT_ID_INDEX,
    QUANTITY_INDEX,
    Product,
)


type CartLine = tuple[int, int]

LINE_PRODUCT_ID_INDEX: Final[Literal[0]] = 0
LINE_QUANTITY_INDEX: Final[Literal[1]] = 1


def find_cart_line(cart: list[CartLine], product_id: int) -> CartLine | None:
    """Return the cart line for ``product_id``, or ``None`` if absent."""
    for line in cart:
        if line[LINE_PRODUCT_ID_INDEX] == product_id:
            return line
    return None


def add_to_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    product = read_product(storage, product_id)
    if product is None:
        return None

    available = product[QUANTITY_INDEX]
    if available < quantity:
        print(
            f"not enough stock for product {product_id}: "
            f"{available} available, {quantity} requested"
        )
        return None

    for index, item in enumerate(storage):
        if item[PRODUCT_ID_INDEX] == product_id:
            storage[index] = (
                item[PRODUCT_ID_INDEX],
                item[NAME_INDEX],
                item[PRICE_INDEX],
                available - quantity,
            )
            break

    for index, line in enumerate(cart):
        if line[LINE_PRODUCT_ID_INDEX] == product_id:
            updated = (
                product_id,
                line[LINE_QUANTITY_INDEX] + quantity,
            )
            cart[index] = updated
            return updated

    new_line = (product_id, quantity)
    cart.append(new_line)
    return new_line


def remove_from_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    line = find_cart_line(cart, product_id)
    if line is None:
        print(f"product {product_id} is not in the cart")
        return None

    cart_qty = line[LINE_QUANTITY_INDEX]
    if cart_qty < quantity:
        print(
            f"cart holds only {cart_qty} unit(s) of product {product_id}, "
            f"cannot remove {quantity}"
        )
        return None

    product = read_product(storage, product_id)
    if product is None:
        return None

    for index, item in enumerate(storage):
        if item[PRODUCT_ID_INDEX] == product_id:
            storage[index] = (
                item[PRODUCT_ID_INDEX],
                item[NAME_INDEX],
                item[PRICE_INDEX],
                item[QUANTITY_INDEX] + quantity,
            )
            break

    for index, cart_line in enumerate(cart):
        if cart_line[LINE_PRODUCT_ID_INDEX] == product_id:
            remaining = cart_qty - quantity
            if remaining == 0:
                del cart[index]
                return (product_id, 0)
            updated = (product_id, remaining)
            cart[index] = updated
            return updated
    return None
