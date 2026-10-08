from typing import Final

from .crud import read_product
from .storage import (
    NAME_INDEX,
    PRICE_INDEX,
    PRODUCT_ID_INDEX,
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

    if quantity <= 0:
        print(f"quantity must be positive, got {quantity}")
        return None

    if product[QUANTITY_INDEX] < quantity:
        print(
            f"not enough stock for product {product_id}: "
            f"{product[QUANTITY_INDEX]} available, {quantity} requested"
        )
        return None

    for i in range(len(storage)):
        if storage[i][PRODUCT_ID_INDEX] == product_id:
            storage[i] = (
                storage[i][PRODUCT_ID_INDEX],
                storage[i][NAME_INDEX],
                storage[i][PRICE_INDEX],
                storage[i][QUANTITY_INDEX] - quantity,
            )
            break

    line = find_cart_line(cart, product_id)
    if line is None:
        cart.append((product_id, quantity))
        return cart[-1]

    idx = cart.index(line)
    cart[idx] = (product_id, line[LINE_QUANTITY_INDEX] + quantity)
    return cart[idx]


def remove_from_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:

    if quantity <= 0:
        print(f"quantity must be positive, got {quantity}")
        return None

    line = find_cart_line(cart, product_id)
    if line is None:
        print(f"product {product_id} is not in the cart")
        return None

    if line[LINE_QUANTITY_INDEX] < quantity:
        print(
            f"cart holds only {line[LINE_QUANTITY_INDEX]} unit(s) of "
            f"product {product_id}, cannot remove {quantity}"
        )
        return None

    product = read_product(storage, product_id)
    if product is None:
        return None

    for i in range(len(storage)):
        if storage[i][PRODUCT_ID_INDEX] == product_id:
            storage[i] = (
                storage[i][PRODUCT_ID_INDEX],
                storage[i][NAME_INDEX],
                storage[i][PRICE_INDEX],
                storage[i][QUANTITY_INDEX] + quantity,
            )
            break

    new_quantity = line[LINE_QUANTITY_INDEX] - quantity
    idx = cart.index(line)
    if new_quantity == 0:
        del cart[idx]
        return (product_id, 0)
    cart[idx] = (product_id, new_quantity)
    return cart[idx]
