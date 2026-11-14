from .storage import (  # noqa: F401
    NAME_KEY,
    PRICE_KEY,
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
    """Move ``quantity`` units of ``product_id`` from the store into ``cart``.

    The product is looked up in ``storage``. If it is missing, a message is
    printed and nothing changes. If the store holds fewer units than
    requested, an explanatory message is printed and nothing changes.
    Otherwise the store record is decremented by ``quantity`` and the cart
    gains ``quantity`` units of ``product_id`` -- the product is added when
    the cart had none of it.

    Args:
        storage: The product store to draw stock from; modified in place on
            success.
        product_names: The normalised names in ``storage``; a
            quantity-only change never renames a product, so it is left
            unchanged here.
        cart: The cart to add the units to; modified in place on success.
        product_id: The identifier of the product to add.
        quantity: Number of units to move into the cart.

    Returns:
        The quantity of ``product_id`` in the cart after the addition, or
        ``None`` when the product is unknown or the store cannot cover the
        request.
    """
    if not product_id in storage:
        print(f"no product with id {product_id}")
        return None
    if (storage_quantity := storage[product_id][QUANTITY_KEY]) < quantity:
        print(
            f"not enough stock for product {product_id}: "
            f"{storage_quantity} available, "
            f"{quantity} requested"
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
    """Move ``quantity`` units of ``product_id`` from ``cart`` back to the store.

    If the cart holds no units of ``product_id``, a message is printed and
    nothing changes. If it holds fewer units than requested, an explanatory
    message is printed and nothing changes. If the product is missing from
    ``storage``, a message is printed and nothing changes. Otherwise the cart loses
    ``quantity`` units of the product -- the product is dropped from the
    cart when its quantity reaches zero -- and the store record gains
    ``quantity`` units back.

    Args:
        storage: The product store to return stock to; modified in place on
            success.
        product_names: The normalised names in ``storage``; a
            quantity-only change never renames a product, so it is left
            unchanged here.
        cart: The cart to take the units from; modified in place on
            success.
        product_id: The identifier of the product to remove.
        quantity: Number of units to move back into the store.

    Returns:
        The quantity of ``product_id`` left in the cart after the removal
        (zero means the product was dropped from the cart), or ``None`` when
        the cart does not hold the product or holds too few units.
    """
    if not product_id in cart:
        print(f"product {product_id} is not in the cart")
        return None
    if cart[product_id] < quantity:
        print(
            f"cart holds only {cart[product_id]} "
            f"unit(s) of product {product_id}, "
            f"cannot remove {quantity}"
        )
        return None
    if not product_id in storage:
        print(f"no product with id {product_id}")
        return None
    storage[product_id][QUANTITY_KEY] += quantity
    cart[product_id] -= quantity
    if cart[product_id] == 0:
        return cart.pop(product_id)
    return cart[product_id]
