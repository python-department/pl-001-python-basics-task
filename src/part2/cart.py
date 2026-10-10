"""Shopping-cart operations layered on top of the product store.

The cart is a plain list of tuples, one :data:`CartLine` --
``(product_id, quantity)`` -- per distinct product. Moving units between the
store and the cart keeps the two sides in balance: :func:`add_to_cart` takes
units out of stock, :func:`remove_from_cart` puts them back.

Like the CRUD layer, the failure path never raises -- the operation prints
an explanatory message to stdout and returns ``None``.
"""

from typing import Final

from .crud import read_product, update_product  # noqa: F401
from .storage import (  # noqa: F401
    NAME_INDEX,
    PRICE_INDEX,
    QUANTITY_INDEX,
    Product,
)


type CartLine = tuple[int, int]

LINE_PRODUCT_ID_INDEX: Final = 0
LINE_QUANTITY_INDEX: Final = 1


def find_cart_line(
    cart: list[CartLine],
    product_id: int,
) -> CartLine | None:
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
    if product[QUANTITY_INDEX] < quantity:
        return print(
            f"not enough stock for product {product_id}: {product[QUANTITY_INDEX]} available, {quantity} requested"
        )
    id, name, price, stock_quantity = product
    updated_product = (id, name, price, stock_quantity - quantity)
    storage[storage.index(product)] = updated_product
    for line in cart:
        if line[LINE_PRODUCT_ID_INDEX] == product_id:
            updated_line = (product_id, line[LINE_QUANTITY_INDEX] + quantity)
            cart[cart.index(line)] = updated_line
            return updated_line
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
    if line == None:
        return print(f"product {product_id} is not in the cart")
    if line[LINE_QUANTITY_INDEX] < quantity:
        return print(
            f"cart holds only {line[LINE_QUANTITY_INDEX]} unit(s) of product {product_id}, cannot remove {quantity}"
        )
    product = read_product(storage, product_id)
    if product is None:
        return None
    id, name, price, storage_quantity = product
    updated_product = (id, name, price, storage_quantity + quantity)
    storage[storage.index(product)] = updated_product
    id, cart_quantity = line
    updated_line = (id, cart_quantity - quantity)
    if cart_quantity - quantity == 0:
        cart.remove(line)
    else:
        cart[cart.index(line)] = updated_line
    return updated_line
