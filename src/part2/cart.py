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
    item = read_product(storage, product_id)
    if item is None:
        return None

    available = item[QUANTITY_INDEX]
    if available < quantity:
        print(f"not enough stock for product {product_id}: {available} available, {quantity} requested")
        return None
    
    new_quantity = (available - quantity)
    new_fields = (item[NAME_INDEX], item[PRICE_INDEX], new_quantity)
    update_product(storage, product_id, new_fields)

    for i in range(len(cart)):
        if cart[i][LINE_PRODUCT_ID_INDEX] == product_id:
            prev_cart_quant = cart[i][LINE_QUANTITY_INDEX]
            new_cart_item = (product_id, prev_cart_quant + quantity)
            cart[i] = new_cart_item
            return cart[i]

    new_cart_item = (product_id, quantity)
    cart.append(new_cart_item)
    return new_cart_item



def find_cart_line(
    cart: list[CartLine],
    product_id: int,
) -> CartLine | None:
    for i in range(len(cart)):
        if cart[i][LINE_PRODUCT_ID_INDEX] == product_id:
            return cart[i]

    return None


def remove_from_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    line = find_cart_line(cart, product_id)
    if not line:
        print(f"product {product_id} is not in the cart")
        return None

    if quantity > line[LINE_QUANTITY_INDEX]:
        print(f"cart holds only {line[LINE_QUANTITY_INDEX]} unit(s) of product {product_id}, cannot remove {quantity}")
        return None

    product = read_product(storage, product_id)
    if not product:
        return None

    new_quantity = (product[QUANTITY_INDEX] + quantity)
    new_fields = (product[NAME_INDEX], product[PRICE_INDEX], new_quantity)
    update_product(storage, product_id, new_fields)
    for i in range(len(cart)):
        if cart[i][LINE_PRODUCT_ID_INDEX] == product_id:
            cart[i] = (product_id, line[LINE_QUANTITY_INDEX] - quantity)
            if cart[i][LINE_QUANTITY_INDEX] == 0:
                cart.pop(i)
                return (product_id, 0)
            return cart[i]
