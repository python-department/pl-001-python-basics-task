from typing import Final

from .crud import read_product, update_product
from .storage import (
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


def add_to_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    product = read_product(storage, product_id)
    if product is None:
        return None

    for i in range(len(storage)):
        product = storage[i]
        if product_id == product[PRODUCT_ID_INDEX]:
            quantity_storage = product[QUANTITY_INDEX]
            if quantity > quantity_storage:
                print(
                    f"not enough stock for product <{product_id}>: {quantity_storage} available, {quantity} requested"
                )
                return None

            name, price = product[NAME_INDEX], product[PRICE_INDEX]
            new_product = (product_id, name, price, quantity_storage - quantity)
            storage[i] = new_product

            for j in range(len(cart)):
                cur_cart = cart[j]
                if cur_cart[LINE_PRODUCT_ID_INDEX] == product_id:
                    new_cart = (
                        cur_cart[LINE_PRODUCT_ID_INDEX],
                        cur_cart[LINE_QUANTITY_INDEX] + quantity,
                    )
                    cart[j] = new_cart
                    return new_cart

            new_cart = (product_id, quantity)
            cart.append(new_cart)
            return new_cart

    return None


def find_cart_line(
    cart: list[CartLine],
    product_id: int,
) -> CartLine | None:
    for product in cart:
        if product_id == product[LINE_PRODUCT_ID_INDEX]:
            return product

    return None


def remove_from_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    cart_line = find_cart_line(cart, product_id)

    if cart_line is None:
        print(f"product <{product_id}> is not in the cart")
        return None

    for i in range(len(cart)):
        id, quantity_cart = cart[i]
        if id == product_id:
            if quantity > quantity_cart:
                print(
                    f"cart holds only {quantity_cart} unit(s) of product <{product_id}>, cannot remove {quantity}"
                )
                return None

            product = read_product(storage, product_id)
            if product is None:
                return None

            new_product = (
                product[NAME_INDEX],
                product[PRICE_INDEX],
                product[QUANTITY_INDEX] + quantity,
            )
            update_product(storage, product_id, new_product)

            if quantity == quantity_cart:
                cart.pop(i)
                return (product_id, 0)

            cart[i] = (product_id, quantity_cart - quantity)

            return cart[i]

    return None
