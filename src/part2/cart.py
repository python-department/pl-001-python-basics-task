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

# TODO: задайте позиции полей внутри кортежа CartLine
LINE_PRODUCT_ID_INDEX: Final = 0
LINE_QUANTITY_INDEX: Final = 1


def find_cart_line(
    cart: list[CartLine],
    product_id: int,
) -> CartLine | None:
    for line in cart:
        if line[LINE_PRODUCT_ID_INDEX] == product_id:
            return line
    return None


def add_to_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
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
    # TODO: реализуйте функцию

    product = read_product(storage, product_id)
    if product is None:
        return None

    stock_quantity = product[QUANTITY_INDEX]
    if stock_quantity < quantity:
        print(
            f"not enough stock for product {product_id}: {stock_quantity} available, {quantity} requested"
        )
        return None

    new_stock_quantity = stock_quantity - quantity
    update_product(
        storage,
        product_id,
        (product[NAME_INDEX], product[PRICE_INDEX], new_stock_quantity),
    )

    index = 0
    for line in cart:
        if line[LINE_PRODUCT_ID_INDEX] == product_id:
            updated_product = (product_id, line[LINE_PRODUCT_ID_INDEX] + quantity)
            cart[index] = updated_product
            return updated_product

    new_line = (product_id, quantity)
    cart.append(new_line)

    return new_line


def remove_from_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
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
    # TODO: реализуйте функцию
    line = find_cart_line(cart, product_id)
    if line is None:
        print(f"product {product_id} is not in the cart")
        return None

    cart_quantity = line[LINE_QUANTITY_INDEX]
    if cart_quantity < quantity:
        print(
            f"cart holds only {cart_quantity} unit(s) of product <{product_id}, cannot remove {quantity}"
        )
        return None
    product = read_product(storage, product_id)
    if product is None:
        return None
    update_product(
        storage,
        product_id,
        (product[NAME_INDEX], product[PRICE_INDEX], product[QUANTITY_INDEX] + quantity),
    )

    new_quantity = cart_quantity - quantity
    for index in range(len(cart)):
        if cart[index][LINE_PRODUCT_ID_INDEX] == product_id:
            if new_quantity == 0:
                del cart[index]
                return (product_id, 0)
            updated_product = (product_id, new_quantity)
            cart[index] = updated_product
            return updated_product
    return None
