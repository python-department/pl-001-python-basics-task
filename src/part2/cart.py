"""Shopping-cart operations layered on top of the product store.

The cart is a plain list of tuples, one :data:`CartLine` --
``(product_id, quantity)`` -- per distinct product. Moving units between the
store and the cart keeps the two sides in balance: :func:`add_to_cart` takes
units out of stock, :func:`remove_from_cart` puts them back.

Like the CRUD layer, the failure path never raises -- the operation prints
an explanatory message to stdout and returns ``None``.
"""

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


def change_cart_quantity(
    cart: list[CartLine], cartline: CartLine, quantity: int
) -> None:
    cart.append(
        (cartline[LINE_PRODUCT_ID_INDEX], cartline[LINE_QUANTITY_INDEX] + quantity)
    )
    cart.remove(cartline)


def add_to_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    requested_product = read_product(storage, product_id)
    if requested_product is None:
        return None
    product_name = requested_product[NAME_INDEX]
    product_price = requested_product[PRICE_INDEX]
    product_amount = requested_product[QUANTITY_INDEX]

    if product_amount < quantity:
        print(
            f"not enough stock for product {product_id}: {product_amount} available, {quantity} requested"
        )
        return None

    update_product(
        storage, product_id, (product_name, product_price, product_amount - quantity)
    )

    old_cartline = find_cart_line(cart, product_id)

    if old_cartline is not None:
        change_cart_quantity(cart, old_cartline, quantity)
    else:
        cart.append((product_id, quantity))

    return find_cart_line(cart, product_id)


def remove_from_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    changable_cartline = find_cart_line(cart, product_id)

    if changable_cartline is None:
        print(f"product {product_id} is not in the cart")
        return None
    if changable_cartline[LINE_QUANTITY_INDEX] < quantity:
        print(
            f"cart holds only {changable_cartline[LINE_QUANTITY_INDEX]} unit(s) of product {product_id}, cannot remove {quantity}"
        )
        return None

    storage_product = read_product(storage, product_id)
    if storage_product is None:
        return None

    update_product(
        storage,
        product_id,
        (
            storage_product[NAME_INDEX],
            storage_product[PRICE_INDEX],
            storage_product[QUANTITY_INDEX] + quantity,
        ),
    )
    change_cart_quantity(cart, changable_cartline, -quantity)
    updated_cartline = find_cart_line(cart, product_id)

    if updated_cartline is None:  # проверка, чтобы mypy не ругался
        return None

    if updated_cartline[LINE_QUANTITY_INDEX] == 0:
        cart.remove(updated_cartline)
        return (product_id, 0)

    return updated_cartline
