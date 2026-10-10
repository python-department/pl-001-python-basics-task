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
    if not product:
        return None

    if product[QUANTITY_INDEX] < quantity:
        print(
            f"not enough stock for product {product_id}: "
            f"{product[QUANTITY_INDEX]} available, {quantity} requested"
        )
        return None

    update_product(
        storage,
        product_id,
        (product[NAME_INDEX], product[PRICE_INDEX], product[QUANTITY_INDEX] - quantity),
    )

    existing_line = find_cart_line(cart, product_id)
    if existing_line:
        cart.remove(existing_line)
        updated_line = (product_id, existing_line[LINE_QUANTITY_INDEX] + quantity)
        cart.append(updated_line)
        return updated_line
    else:
        new_line = (product_id, quantity)
        cart.append(new_line)
        return new_line


def remove_from_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    cartline = find_cart_line(cart, product_id)
    if not cartline:
        print(f"product {product_id} is not in the cart")
        return None

    if cartline[LINE_QUANTITY_INDEX] < quantity:
        print(
            f"cart holds only {cartline[LINE_QUANTITY_INDEX]} "
            f"unit(s) of product {product_id}, "
            f"cannot remove {quantity}"
        )
        return None

    product = read_product(storage, product_id)
    if not product:
        return None

    update_product(
        storage,
        product_id,
        (product[NAME_INDEX], product[PRICE_INDEX], product[QUANTITY_INDEX] + quantity),
    )

    new_quantity = cartline[LINE_QUANTITY_INDEX] - quantity
    cart.remove(cartline)
    if new_quantity == 0:
        return (product_id, 0)
    updated_line = (product_id, new_quantity)
    cart.append(updated_line)
    return updated_line
