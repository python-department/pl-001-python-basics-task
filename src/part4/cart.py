"""Shopping-cart operations layered on top of the product store.

The cart is a plain dictionary mapping each product identifier to the
number of units of that product in the cart. Moving units between the
store and the cart keeps the two sides in balance: :func:`add_to_cart` takes
units out of stock, :func:`remove_from_cart` puts them back.

Like the CRUD layer, the failure path never raises -- the operation prints
an explanatory message to stdout and returns ``None``.
"""

from .storage import QUANTITY_KEY, Product


# TODO: при необходимости добавьте свои вспомогательные функции


def add_to_cart(
    storage: dict[str, Product],
    product_names: set[str],
    cart: dict[str, int],
    product_id: str,
    quantity: int,
) -> int | None:
    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None

    stock: int = storage[product_id][QUANTITY_KEY]
    if stock < quantity:
        print(
            f"not enough stock for product {product_id}: {stock} available, {quantity} requested"
        )
        return None

    storage[product_id][QUANTITY_KEY] -= quantity
    cart[product_id] = cart.get(product_id, 0) + quantity

    return cart[product_id]


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

    cart_quantity: int = cart[product_id]
    if cart_quantity < quantity:
        print(
            f"cart holds only {cart_quantity} unit(s) of product {product_id}, cannot remove {quantity}"
        )
        return None

    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None

    storage[product_id][QUANTITY_KEY] += quantity
    cart[product_id] -= quantity

    if cart[product_id] == 0:
        del cart[product_id]

    return cart.get(product_id, 0)
