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
    for c_prod in cart:
        if c_prod[LINE_PRODUCT_ID_INDEX] == product_id:
            return c_prod
    print(f"no product with id {product_id} in the cart")
    return None


def change_cart_quantity(
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> int | None:
    for ind in range(len(cart)):
        if cart[ind][LINE_PRODUCT_ID_INDEX] == product_id:
            new_c_prod: CartLine = (
                product_id,
                cart[ind][LINE_QUANTITY_INDEX] - quantity,
            )
            cart[ind] = new_c_prod
            return ind
    print(f"no product with id {product_id} in cart")
    return None


def add_to_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    prod = read_product(storage, product_id)
    if prod is None:
        return None
    if prod[QUANTITY_INDEX] < quantity:
        print(
            f"not enough stock for product {product_id}: {prod[QUANTITY_INDEX]} available, {quantity} requested"
        )
        return None
    update_product(
        storage,
        product_id,
        (prod[NAME_INDEX], prod[PRICE_INDEX], prod[QUANTITY_INDEX] - quantity),
    )
    for ind in range(len(cart)):
        if cart[ind][LINE_PRODUCT_ID_INDEX] == product_id:
            cart[ind] = (product_id, cart[ind][LINE_QUANTITY_INDEX] + quantity)
            return cart[ind]
    cart.append((product_id, quantity))
    return cart[-1]


def remove_from_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    c_prod = find_cart_line(cart, product_id)
    if c_prod is None:
        return None
    if c_prod[LINE_QUANTITY_INDEX] < quantity:
        print(
            f"cart holds only {c_prod[LINE_QUANTITY_INDEX]} unit(s) of product {product_id}, cannot remove {quantity}"
        )
        return None
    prod = read_product(storage, product_id)
    if prod is None:
        return None
    update_product(
        storage,
        product_id,
        (prod[NAME_INDEX], prod[PRICE_INDEX], prod[QUANTITY_INDEX] + quantity),
    )
    ind = change_cart_quantity(cart, product_id, quantity)
    if ind is None:
        return None
    if cart[ind][LINE_QUANTITY_INDEX] == 0:
        res = cart[ind]
        del cart[ind]
        return res
    return cart[ind]
