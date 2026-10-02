from typing import Final

from .crud import read_product, update_product  # noqa: F401
from .storage import (  # noqa: F401
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


def change_cart_quantity(
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    for i, cart_i in enumerate(cart):
        if cart_i[LINE_PRODUCT_ID_INDEX] == product_id:
            if cart_i[LINE_QUANTITY_INDEX] + quantity == 0:
                del cart[i]
                return (product_id, 0)
            cart[i] = (cart_i[0], cart_i[1] + quantity)
            return cart[i]
    return None


def add_to_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    product_new = read_product(storage, product_id)
    if product_new is None:
        return None
    if product_new[QUANTITY_INDEX] < quantity:
        print(
            f"not enough stock for product {product_id}: {product_new[QUANTITY_INDEX]} available, {quantity} requested"
        )
        return None
    index = next(
        (i for i, p in enumerate(storage) if p[PRODUCT_ID_INDEX] == product_id), None
    )
    if index is None:
        return None
    storage[index] = (
        product_new[0],
        product_new[1],
        product_new[2],
        product_new[3] - quantity,
    )
    change = change_cart_quantity(cart, product_id, quantity)
    if change is None:
        cart.append((product_id, quantity))
        return (product_id, quantity)
    else:
        return change


def find_cart_line(
    cart: list[CartLine],
    product_id: int,
) -> CartLine | None:
    for cart_i in cart:
        if cart_i[LINE_PRODUCT_ID_INDEX] == product_id:
            return cart_i
    return None


def remove_from_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    cart_find = find_cart_line(cart, product_id)
    if cart_find is None:
        print(f"product {product_id} is not in the cart")
        return None
    if cart_find[LINE_QUANTITY_INDEX] < quantity:
        print(
            f"cart holds only {cart_find[LINE_QUANTITY_INDEX]} unit(s) of product {product_id}, cannot remove {quantity}"
        )
        return None
    product_new = read_product(storage, product_id)
    if product_new == None:
        return None
    index = next(
        (i for i, p in enumerate(storage) if p[PRODUCT_ID_INDEX] == product_id), None
    )
    if index is None:
        return None
    storage[index] = (
        product_new[0],
        product_new[1],
        product_new[2],
        product_new[3] + quantity,
    )
    return change_cart_quantity(cart, product_id, -quantity)
