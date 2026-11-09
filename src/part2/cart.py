from typing import Final

from .crud import read_product
from .storage import Product


type CartLine = tuple[int, int]

LINE_PRODUCT_ID_INDEX: Final = 0
LINE_QUANTITY_INDEX: Final = 1


def find_cart_line(cart: list[CartLine], product_id: int) -> CartLine | None:
    for i in range(len(cart)):
        if cart[i][0] == product_id:
            return cart[i]
    print(f"product {product_id} is not in the cart")
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
    else:
        if product[3] < quantity:
            print(
                f"not enough stock for product {product_id}: {product[3]} available, {quantity} requested"
            )
            return None
        else:
            indp = storage.index(product)
            storage[indp] = (
                storage[indp][0],
                storage[indp][1],
                storage[indp][2],
                storage[indp][3] - quantity,
            )
            for i in range(len(cart)):
                if cart[i][0] == product_id:
                    idn, quantit1 = cart[i]
                    cart[i] = (idn, quantit1 + quantity)
                    return cart[i]
            cart1 = (product_id, quantity)
            cart.append(cart1)
            return cart1


def remove_from_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    cart1 = find_cart_line(cart, product_id)
    product = read_product(storage, product_id)
    if cart1 is None:
        return None
    else:
        if cart1[1] < quantity:
            print(
                f"cart holds only {cart1[1]} unit(s) of product {product_id}, cannot remove {quantity}"
            )
            return None
        else:
            if product is None:
                return None
            else:
                indp = storage.index(product)
                jdnc = cart.index(cart1)
                storage[indp] = (
                    storage[indp][0],
                    storage[indp][1],
                    storage[indp][2],
                    storage[indp][3] + quantity,
                )
                cart[jdnc] = (cart[jdnc][0], cart[jdnc][1] - quantity)
                idn = cart[jdnc][0]
                if (cart[jdnc][1]) == 0:
                    del cart[jdnc]
                    return (idn, 0)
                else:
                    return cart[jdnc]
