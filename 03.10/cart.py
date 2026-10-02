from typing import Final

from crud import read_product, update_product
from storage import (
    Product,
    NAME_INDEX,
    PRICE_INDEX,
    QUANTITY_INDEX,
)

CartLine = tuple[int, int]

LINE_PRODUCT_ID_INDEX: Final[int] = 0
LINE_QUANTITY_INDEX: Final[int] = 1


def find_cart_line(cart: list[CartLine], product_id: int) -> CartLine:
    for line in cart:
        if line[LINE_PRODUCT_ID_INDEX] == product_id:
            return line
    raise ValueError(f"product {product_id} is not in the cart")


def change_cart_quantity(
    cart: list[CartLine],
    product_id: int,
    quantity_delta: int,
) -> CartLine:
    for index in range(len(cart)):
        if cart[index][LINE_PRODUCT_ID_INDEX] == product_id:
            new_quantity = cart[index][LINE_QUANTITY_INDEX] + quantity_delta
            if new_quantity < 0:
                raise ValueError("cart quantity cannot be negative")
            if new_quantity == 0:
                del cart[index]
                return (product_id, 0)
            cart[index] = (product_id, new_quantity)
            return cart[index]
    raise ValueError(f"product {product_id} is not in the cart")


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

    in_cart = False
    for line in cart:
        if line[LINE_PRODUCT_ID_INDEX] == product_id:
            in_cart = True
            break

    if in_cart:
        new_line = change_cart_quantity(cart, product_id, quantity)
    else:
        new_line = (product_id, quantity)
        cart.append(new_line)

    update_product(
        storage,
        product_id,
        (product[NAME_INDEX], product[PRICE_INDEX], available - quantity),
    )
    return new_line


def remove_from_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    in_cart = -1
    for line in cart:
        if line[LINE_PRODUCT_ID_INDEX] == product_id:
            in_cart = line[LINE_QUANTITY_INDEX]
            break

    if in_cart == -1:
        print(f"product {product_id} is not in the cart")
        return None

    if in_cart < quantity:
        print(
            f"cart holds only {in_cart} unit(s) of product {product_id}, "
            f"cannot remove {quantity}"
        )
        return None

    product = read_product(storage, product_id)
    if product is None:
        return None

    new_line = change_cart_quantity(cart, product_id, -quantity)

    update_product(
        storage,
        product_id,
        (product[NAME_INDEX], product[PRICE_INDEX], product[QUANTITY_INDEX] + quantity),
    )
    return new_line