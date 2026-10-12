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


def find_cart_line(cart: list[CartLine], product_id: int) -> int | None:
    for cartline in cart:
        if cartline[LINE_PRODUCT_ID_INDEX] == product_id:
            return cart.index(cartline)

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
            f"not enough stock for product {product_id}: {product[QUANTITY_INDEX]} available, {quantity} requested"
        )
        return None

    fields = (
        product[NAME_INDEX],
        product[PRICE_INDEX],
        product[QUANTITY_INDEX] - quantity,
    )

    update_product(storage, product_id, fields)

    line_index = find_cart_line(cart, product_id)
    if line_index is not None:
        line: CartLine = (product_id, cart[line_index][LINE_QUANTITY_INDEX] + quantity)
        return cart[line_index]

    line = (product_id, quantity)
    cart.append(line)

    return line


def remove_from_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    line_index = find_cart_line(cart, product_id)
    if line_index is None:
        print(f"{product_id} is not in the cart")
        return None

    line = cart[line_index]
    if line[LINE_QUANTITY_INDEX] < quantity:
        print(
            f"cart holds only {line[LINE_QUANTITY_INDEX]} unit(s) of product {product_id}, cannot remove {quantity}"
        )
        return None

    product = read_product(storage, product_id)
    if product is None:
        return None

    fields = (
        product[NAME_INDEX],
        product[PRICE_INDEX],
        product[QUANTITY_INDEX] + quantity,
    )

    update_product(storage, product_id, fields)

    line_index = find_cart_line(cart, product_id)

    if line_index is not None:
        new_quantity = cart[line_index][LINE_QUANTITY_INDEX] - quantity

    new_line = (product_id, new_quantity)

    if new_quantity == 0 and line_index is not None:
        del cart[line_index]

    return new_line
