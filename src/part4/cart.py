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
    storage: dict[str, Product],
    product_names: set[str],
    cart: dict[str, int],
    product_id: str,
    quantity: int,
) -> int | None:
    """Move ``quantity`` units of ``product_id`` from the store into ``cart``.

    The product is looked up in ``storage``. If it is missing, a message is
    printed (by :func:`~src.part2.crud.read_product`) and nothing
    changes. If the store holds fewer units than requested, an explanatory
    message is printed and nothing changes. Otherwise the store record is
    decremented by ``quantity`` and the cart line for ``product_id`` gains
    ``quantity`` units -- a new line is created when the cart had none.

    Args:
        storage: The product store to draw stock from; modified in place on
            success.
        cart: The cart to add the units to; modified in place on success.
        product_id: The identifier of the product to add.
        quantity: Number of units to move into the cart.

    Returns:
        The cart line for ``product_id`` after the addition, or ``None``
        when the product is unknown or the store cannot cover the request.
    """
    product = read_product(storage, product_id)
    if product is None:
        return None

    in_stock = product[QUANTITY_KEY]
    if in_stock < quantity:
        print(
            f"not enough stock for product {product_id}: "
            f"{in_stock} available, {quantity} requested"
        )
        return None

    update_product(
        storage, product_names, product_id, {QUANTITY_KEY: in_stock - quantity}
    )

    cart[product_id] = cart.get(product_id, 0) + quantity
    return cart[product_id]


def remove_from_cart(
    storage: dict[str, Product],
    product_names: set[str],
    cart: dict[str, int],
    product_id: str,
    quantity: int,
) -> int | None:
    """Move ``quantity`` units of ``product_id`` from ``cart`` back to the store.

    The cart line for ``product_id`` is looked up. If there is none, a
    message is printed and nothing changes. If the line holds fewer units
    than requested, an explanatory message is printed and nothing changes.
    Otherwise the cart line loses ``quantity`` units -- the line is dropped
    when it reaches zero -- and the store record gains ``quantity`` units
    back.

    Args:
        storage: The product store to return stock to; modified in place on
            success.
        cart: The cart to take the units from; modified in place on
            success.
        product_id: The identifier of the product to remove.
        quantity: Number of units to move back into the store.

    Returns:
        The cart line for ``product_id`` after the removal (a quantity of
        zero means the line was dropped), or ``None`` when the cart has no
        line for the product or holds too few units.
    """

    in_cart = cart.get(product_id)
    if in_cart is None:
        print(f"product {product_id} is not in the cart")
        return None

    if in_cart < quantity:
        print(
            f"cart holds only {in_cart} unit(s) of product {product_id}, "
            f"cannot remove {quantity}"
        )
        return None

    product = read_product(storage, product_id)
    if product is None:
        return None

    product = read_product(storage, product_id)
    if product is None:
        return None

    update_product(
        storage,
        product_names,
        product_id,
        {QUANTITY_KEY: product[QUANTITY_KEY] + quantity},
    )

    left_in_cart = in_cart - quantity
    if left_in_cart:
        cart[product_id] = left_in_cart
    else:
        del cart[product_id]
    return left_in_cart
