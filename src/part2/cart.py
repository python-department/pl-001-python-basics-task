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


def find_cart_line(cart: list[CartLine], product_id: int) -> CartLine | None:
    for cartline in cart:
        if cartline[LINE_PRODUCT_ID_INDEX] == product_id:
            return cartline
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

    storage_quantity = product[QUANTITY_INDEX]
    if quantity > storage_quantity:
        print(
            f"not enough stock for product <{product_id}>: <{product[QUANTITY_INDEX]}> avaiable, <{quantity}> requested"
        )
        return None
    fields = (
        product[NAME_INDEX],
        product[PRICE_INDEX],
        product[QUANTITY_INDEX] - quantity,
    )
    update_product(storage, product_id, fields)

    existing_line = find_cart_line(cart, product_id)
    if existing_line is not None:
        new_cart_quantity = existing_line[LINE_QUANTITY_INDEX] + quantity
        new_line = (product_id, new_cart_quantity)
        for index, line in enumerate(cart):
            if line[LINE_PRODUCT_ID_INDEX] == product_id:
                cart[index] = new_line
                break
    else:
        new_line = (product_id, quantity)
        cart.append(new_line)
        return new_line

    return new_line


def remove_from_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    cart_line = find_cart_line(cart, product_id)
    if cart_line is None:
        print(f"product <{product_id}> is not in the cart")
        return None

    cart_quantity = cart_line[LINE_QUANTITY_INDEX]
    if cart_quantity < quantity:
        print(
            f"cart holds only {cart_quantity} unit(s) of product <{product_id}>, "
            f"cannot remove {quantity}"
        )
        return None

    product = read_product(storage, product_id)
    if product is None:
        return None

    new_stock_quantity = product[QUANTITY_INDEX] + quantity
    update_product(
        storage,
        product_id,
        (product[NAME_INDEX], product[PRICE_INDEX], new_stock_quantity),
    )

    new_cart_quantity = cart_quantity - quantity
    if new_cart_quantity == 0:
        for index, line in enumerate(cart):
            if line[LINE_PRODUCT_ID_INDEX] == product_id:
                cart.pop(index)
                break
        return (product_id, 0)

    new_line = (product_id, new_cart_quantity)
    for index, line in enumerate(cart):
        if line[LINE_PRODUCT_ID_INDEX] == product_id:
            cart[index] = new_line
            break

    return new_line
