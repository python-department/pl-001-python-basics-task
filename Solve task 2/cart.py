from typing import Final
from crud import read_product, update_product
from storage import (  
    NAME_INDEX,
    PRICE_INDEX,
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
    prod = read_product(storage, product_id)
    if prod is None:
        return None
    if prod[QUANTITY_INDEX] < quantity:
        print (f"not enough stock for product {product_id}: {prod[QUANTITY_INDEX]} available, {quantity} requested")
        return None
    storage[storage.index(prod)] = update_product(storage, product_id, (prod[NAME_INDEX], prod[PRICE_INDEX], prod[QUANTITY_INDEX] - quantity))
    for i in range(len(cart)):
        if cart[i][LINE_PRODUCT_ID_INDEX] is product_id:
            cart[i] = (product_id, cart[i][LINE_QUANTITY_INDEX] + quantity)
            return cart[i]
    cart.append(product_id, quantity)
    return cart[-1]    


def find_cart_line(cart: list[CartLine], product_id: int) -> CartLine | None:
    for line in cart:
        if line[LINE_PRODUCT_ID_INDEX] is product_id:
            return line
    return None


def remove_from_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    prod_cart = find_cart_line(cart, product_id)
    if prod_cart is None:
        print (f"product {product_id} is not in the cart")
        return None
    if prod_cart[LINE_QUANTITY_INDEX] < quantity:
        print (f"cart holds only {prod_cart[LINE_QUANTITY_INDEX]} unit(s) of product {product_id}, cannot remove {quantity}")
        return None
    prod = read_product(storage, product_id)
    if prod is None:
        return None
    storage[storage.index(prod)] = update_product(storage, product_id, (prod[NAME_INDEX], prod[PRICE_INDEX], prod[QUANTITY_INDEX] + quantity))
    if prod_cart[LINE_QUANTITY_INDEX] - quantity is 0:
        cart.remove(prod_cart)
        return 0
    
    cart [cart.index(prod_cart)] = CartLine(product_id, prod_cart[LINE_QUANTITY_INDEX] - quantity)
    return cart [cart.index(prod_cart)]