"""Shopping-cart operations layered on top of the product store.

The cart is a plain list of tuples, one :data:`CartLine` --
``(product_id, quantity)`` -- per distinct product. Moving units between the
store and the cart keeps the two sides in balance: :func:`add_to_cart` takes
units out of stock, :func:`remove_from_cart` puts them back.

Like the CRUD layer, the failure path never raises -- the operation prints
an explanatory message to stdout and returns ``None``.
"""

from typing import Any, Final

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


def dict_to_cart_line(line: dict[int, Any]) -> CartLine:
    return tuple(x[1] for x in sorted(line.items()))


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
    product = read_product(storage, product_id)
    if not product:
        return None

    if product[QUANTITY_INDEX] < quantity:
        print(
            f"not enough stock for product {product_id}: \
            {product[QUANTITY_INDEX]} available, {quantity} requested"
        )
        return None

    new_quantity = product[QUANTITY_INDEX] - quantity
    update_product(
        storage, product_id, (product[NAME_INDEX], product[PRICE_INDEX], new_quantity)
    )

    line = find_cart_line(cart, product_id)
    dict_line = {
        LINE_PRODUCT_ID_INDEX: product_id,
        LINE_QUANTITY_INDEX: quantity + (line[LINE_QUANTITY_INDEX] if line else 0),
    }
    new_line = dict_to_cart_line(dict_line)

    if line:
        cart.remove(line)
    cart.append(new_line)

    return new_line


def find_cart_line(cart: list[CartLine], product_id: int) -> CartLine | None:
    line = [x for x in cart if x[LINE_PRODUCT_ID_INDEX] == product_id]
    return line[0] if line else None


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
    line = find_cart_line(cart, product_id)
    if not line:
        print(f"product {product_id} is not in the cart")
        return None

    if line[LINE_QUANTITY_INDEX] < quantity:
        print(
            f"cart holds only {line[LINE_QUANTITY_INDEX]} unit(s) \
                of product {product_id}, cannot remove {quantity}"
        )
        return None

    product = read_product(storage, product_id)
    if not product:
        return None

    new_quantity = product[QUANTITY_INDEX] + quantity
    update_product(
        storage, product_id, (product[NAME_INDEX], product[PRICE_INDEX], new_quantity)
    )

    dict_line = {
        LINE_PRODUCT_ID_INDEX: product_id,
        LINE_QUANTITY_INDEX: line[LINE_QUANTITY_INDEX] - quantity,
    }
    new_line = dict_to_cart_line(dict_line)

    if line:
        cart.remove(line)
    if new_line[LINE_QUANTITY_INDEX] != 0:
        cart.append(new_line)

    return new_line
