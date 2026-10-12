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


def add_to_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    product = read_product(storage, product_id)

    if product is None:
        return None

    stock_quantity = product[QUANTITY_INDEX]

    if stock_quantity < quantity:
        print(
            f"not enough stock for product {product_id}: "
            f"{stock_quantity} available, {quantity} requested"
        )
        return None

    new_stock_quantity = stock_quantity - quantity

    updated_product = (
        product[PRODUCT_ID_INDEX],
        product[NAME_INDEX],
        product[PRICE_INDEX],
        new_stock_quantity,
    )

    storage_index = storage.index(product)
    storage[storage_index] = updated_product

    for index, line in enumerate(cart):
        if line[LINE_PRODUCT_ID_INDEX] == product_id:
            new_line = (
                product_id,
                line[LINE_QUANTITY_INDEX] + quantity,
            )
            cart[index] = new_line
            return new_line

    new_line = (product_id, quantity)
    cart.append(new_line)
    return new_line


def remove_from_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    """Move ``quantity`` units of ``product_id`` from ``cart`` back to the store."""
    cart_line = find_cart_line(cart, product_id)

    if cart_line is None:
        print(f"product {product_id} is not in the cart")
        return None

    cart_quantity = cart_line[LINE_QUANTITY_INDEX]

    if cart_quantity < quantity:
        print(
            f"cart holds only {cart_quantity} unit(s) of product "
            f"{product_id}, cannot remove {quantity}"
        )
        return None

    product = read_product(storage, product_id)

    if product is None:
        return None

    new_stock_quantity = product[QUANTITY_INDEX] + quantity

    updated_product = (
        product[PRODUCT_ID_INDEX],
        product[NAME_INDEX],
        product[PRICE_INDEX],
        new_stock_quantity,
    )

    storage_index = storage.index(product)
    storage[storage_index] = updated_product

    new_cart_quantity = cart_quantity - quantity

    for index, line in enumerate(cart):
        if line[LINE_PRODUCT_ID_INDEX] == product_id:
            if new_cart_quantity == 0:
                cart.pop(index)
                return (product_id, 0)

            new_line = (product_id, new_cart_quantity)
            cart[index] = new_line
            return new_line

    return None


def find_cart_line(
    cart: list[CartLine],
    product_id: int,
) -> CartLine | None:
    for line in cart:
        if line[LINE_PRODUCT_ID_INDEX] == product_id:
            return line

    return None
