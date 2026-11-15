"""Shopping-cart operations layered on top of the product store.

The cart is a plain dictionary mapping each product identifier to the
number of units of that product in the cart. Moving units between the
store and the cart keeps the two sides in balance: :func:`add_to_cart` takes
units out of stock, :func:`remove_from_cart` puts them back.

Like the CRUD layer, the failure path never raises -- the operation prints
an explanatory message to stdout and returns ``None``.
"""

from .crud import read_product, update_product
from .storage import QUANTITY_KEY, Product


def add_to_cart(
    storage: dict[int, Product],
    product_names: set[str],
    cart: dict[int, int],
    product_id: int,
    quantity: int,
) -> int | None:
    product = read_product(storage, product_id)
    if product is None:
        return None
    if product[QUANTITY_KEY] < quantity:
        print(f"not enough units of product with id {product_id} in store")
        return None

    update_product(
        storage,
        product_names,
        product_id,
        {QUANTITY_KEY: product[QUANTITY_KEY] - quantity},
    )
    cart[product_id] = cart.get(product_id, 0) + quantity
    return cart[product_id]


def remove_from_cart(
    storage: dict[int, Product],
    product_names: set[str],
    cart: dict[int, int],
    product_id: int,
    quantity: int,
) -> int | None:
    if product_id not in cart:
        print(f"no product with id {product_id} in cart")
        return None
    if cart[product_id] < quantity:
        print(f"not enough units of product with id {product_id} in cart")
        return None

    product = storage[product_id]
    update_product(
        storage,
        product_names,
        product_id,
        {QUANTITY_KEY: product[QUANTITY_KEY] + quantity},
    )
    cart[product_id] -= quantity
    if cart[product_id] == 0:
        del cart[product_id]
    return cart.get(product_id, 0)
