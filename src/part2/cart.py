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
    for i in cart:
        if i[0] == product_id:
            return i
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
        print(
            f"not enough stock for product {product_id}: {product[QUANTITY_INDEX]} available, {quantity} requested"
        )
        return None
    update_product(
        storage,
        product_id,
        (product[NAME_INDEX], product[PRICE_INDEX], product[QUANTITY_INDEX] - quantity),
    )
    tovar = find_cart_line(cart, product_id)
    if tovar is not None:
        new_tovar = (product_id, tovar[1] + quantity)
        for i in range(len(cart)):
            if cart[i][0] == product_id:
                cart[i] = new_tovar
        return new_tovar
    new_tovar = (product_id, quantity)
    cart.append(new_tovar)
    return new_tovar


def remove_from_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    tovar = find_cart_line(cart, product_id)
    if tovar is None:
        print(f"product {product_id} is not in the cart")
        return None
    if tovar[1] < quantity:
        print(
            f"cart holds only {tovar[1]} unit(s) of product {product_id}, cannot remove {quantity}"
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
    new_k = tovar[1] - quantity
    if new_k == 0:
        cart.remove(tovar)
        return (product_id, 0)
    new_tovar = (product_id, new_k)
    for i in range(len(cart)):
        if cart[i][0] == product_id:
            cart[i] = new_tovar
    return new_tovar
