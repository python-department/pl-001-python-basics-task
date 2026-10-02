from typing import Final
from crud import (
    read_product,
    update_product,
)
from storage import (
    QUANTITY_INDEX,
    NAME_INDEX,
    PRICE_INDEX,
    Product)

CartLine = tuple[int, int]
LINE_PRODUCT_ID_INDEX: Final = 0
LINE_QUANTITY_INDEX: Final = 1


def find_cart_line(cart: list[CartLine],
                   product_id: int,) -> CartLine | None:
    for line in cart:
        if line[LINE_PRODUCT_ID_INDEX] == product_id:
            return line
    print(f"Product {product_id} is not in the cart/")
    return None


def add_to_cart(storage: list[Product],
                cart: list[CartLine],
                product_id: int,
                quantity: int) -> CartLine | None:
    product = read_product(storage, product_id)
    if product is None:
        return product
    storage_quantity = product[QUANTITY_INDEX]
    if storage_quantity < quantity:
        print(f"Not enough stock for product {product_id}: "
              f"{storage_quantity} available, "
              f"{quantity} requested.")
        return None

    new_field = (
        product[NAME_INDEX],
        product[PRICE_INDEX],
        storage_quantity - quantity
    )
    update_product(storage, product_id, new_field)

    for index, line in enumerate(cart):
        if line[LINE_PRODUCT_ID_INDEX] == product_id:
            new_line: CartLine = (
                product_id,
                line[LINE_QUANTITY_INDEX] + quantity
            )
            cart[index] = new_line
            return new_line
    new_line: CartLine = (product_id, quantity)
    cart.append(new_line)
    return new_line


def remove_from_cart(storage: list[Product],
                     cart: list[CartLine],
                     product_id: int,
                     quantity: int) -> CartLine | None:
    cart_line = find_cart_line(cart, product_id)
    product = read_product(storage, product_id)
    if cart_line is None:
        return cart_line
    if cart_line[LINE_QUANTITY_INDEX] < quantity:
        print(f"Cart holds only {cart_line[LINE_QUANTITY_INDEX]} "
              f"unit(s) of product {product_id}, cannot remove {quantity}.")
        return None
    if product is None:
        return None
    new_quantity = product[QUANTITY_INDEX] + quantity
    new_fields = (
        product[NAME_INDEX],
        product[PRICE_INDEX],
        new_quantity,
        )
    update_product(
        storage,
        product_id,
        new_fields,
    )
    new_line: CartLine = (
        product_id,
        cart_line[LINE_QUANTITY_INDEX] - quantity,
    )
    new_line: CartLine = (
            product_id,
            cart_line[LINE_QUANTITY_INDEX]-quantity
        )
    if new_line[LINE_QUANTITY_INDEX] == 0:
        cart.remove(cart_line)
        return new_line
    for index, line in enumerate(cart):
        if line == cart_line:
            cart[index] = new_line
            return new_line
