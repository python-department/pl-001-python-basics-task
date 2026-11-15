"""Shopping-cart operations layered on top of the product store.

The cart is a plain dictionary mapping each product identifier to the
number of units of that product in the cart. Moving units between the
store and the cart keeps the two sides in balance: :func:`add_to_cart` takes
units out of stock, :func:`remove_from_cart` puts them back.

Like the CRUD layer, the failure path never raises -- the operation prints
an explanatory message to stdout and returns ``None``.
"""

from .crud import read_product
from .storage import (
    QUANTITY_KEY,
    Product,
)


def add_to_cart(
    storage: dict[str, Product],
    product_names: set[str],
    cart: dict[str, int],
    product_id: str,
    quantity: int,
) -> int | None:
    product = read_product(storage, product_id)
    if product is None:
        return None

    if product[QUANTITY_KEY] < quantity:
        print(
            f"not enough stock for product {product_id}: "
            f"{product[QUANTITY_KEY]} available, {quantity} requested"
        )
        return None

    product[QUANTITY_KEY] -= quantity

    new_quantity = cart.get(product_id, 0) + quantity
    if new_quantity == 0:
        cart.pop(product_id, None)
    else:
        cart[product_id] = new_quantity

    return new_quantity


def remove_from_cart(
    storage: dict[str, Product],
    product_names: set[str],
    cart: dict[str, int],
    product_id: str,
    quantity: int,
) -> int | None:
    if product_id not in cart:
        print(f"product {product_id} is not in the cart")
        return None

    cart_quantity = cart[product_id]
    if cart_quantity < quantity:
        print(
            f"cart holds only {cart_quantity} unit(s) of product {product_id}, "
            f"cannot remove {quantity}"
        )
        return None

    product = read_product(storage, product_id)
    if product is None:
        return None

    product[QUANTITY_KEY] += quantity

    remaining = cart_quantity - quantity
    if remaining == 0:
        del cart[product_id]
    else:
        cart[product_id] = remaining

    return remaining
