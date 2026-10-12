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

    in_stock = product[QUANTITY_INDEX]
    if in_stock < quantity:
        print(
            f"not enough stock for product {product_id}: "
            f"{in_stock} available, {quantity} requested"
        )
        return None

    update_product(
        storage,
        product_id,
        (product[NAME_INDEX], product[PRICE_INDEX], in_stock - quantity),
    )

    line = find_cart_line(cart, product_id)
    if line is None:
        new_line = (product_id, quantity)
        cart.append(new_line)
        return new_line

    new_line = (product_id, line[LINE_QUANTITY_INDEX] + quantity)
    cart[cart.index(line)] = new_line
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

    in_cart = line[LINE_QUANTITY_INDEX]
    if in_cart < quantity:
        print(
            f"cart holds only {in_cart} unit(s) of product {product_id}, "
            f"cannot remove {quantity}"
        )
        return None

    product = read_product(storage, product_id)
    if product is None:
        return None

    update_product(
        storage,
        product_id,
        (product[NAME_INDEX], product[PRICE_INDEX], product[QUANTITY_INDEX] + quantity),
    )

    remaining = in_cart - quantity
    if remaining == 0:
        cart.remove(line)
        return (product_id, 0)

    new_line = (product_id, remaining)
    cart[cart.index(line)] = new_line
    return new_line
