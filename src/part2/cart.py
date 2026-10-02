"""Shopping-cart operations layered on top of the product store.

The cart is a plain list of tuples, one :data:`CartLine` --
``(product_id, quantity)`` -- per distinct product. Moving units between the
store and the cart keeps the two sides in balance: :func:`add_to_cart` takes
units out of stock, :func:`remove_from_cart` puts them back.

Like the CRUD layer, the failure path never raises -- the operation prints
an explanatory message to stdout and returns ``None``.
"""

from typing import Final

from .crud import read_product
from .storage import (  # noqa: F401
    NAME_INDEX,
    PRICE_INDEX,
    QUANTITY_INDEX,
    Product,
    PRODUCT_ID_INDEX
)


type CartLine = tuple[int, int]

# TODO: задайте позиции полей внутри кортежа CartLine
LINE_PRODUCT_ID_INDEX: Final = 0
LINE_QUANTITY_INDEX: Final = 1

def find_cart_line(cart: list[CartLine], product_id: int) -> CartLine|None:
    """Return the cart line stored under ``product_id``.
    
    Args:
        cart: The store of cart line.
        product_id: The identifier to look up.

    Returns:
        The matching ``(product_id, line_quantity)`` record,
        ``None`` when no cart line carries that identifier (a message is
        printed in that case).
    """
    for cart_line in cart:
        if cart_line[LINE_PRODUCT_ID_INDEX] == product_id:
            return cart_line
    print(f"No cart line with id {product_id}")
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
    product = read_product(storage, product_id)
    if not product:
        return None
    if product[QUANTITY_INDEX] < quantity:
        print(f"Not enough stock for product {product_id}: {product[QUANTITY_INDEX]} available, {quantity} requested.")
        return None
    dif = product[QUANTITY_INDEX] - quantity
    for index_product, cell in enumerate(storage):
        if cell[PRODUCT_ID_INDEX] == product[PRODUCT_ID_INDEX]:
            refresh_product = [0, 0, 0, 0]
            refresh_product[PRODUCT_ID_INDEX] = cell[PRODUCT_ID_INDEX]
            refresh_product[NAME_INDEX] = cell[NAME_INDEX]
            refresh_product[PRICE_INDEX] = cell[PRICE_INDEX]
            refresh_product[QUANTITY_INDEX] = dif
            refresh_product = tuple(refresh_product)
            storage[index_product] = refresh_product
            for index_line, purchase in enumerate(cart):
                if purchase[LINE_PRODUCT_ID_INDEX] == product_id:
                    refresh_line = [0, 0]
                    refresh_line[LINE_PRODUCT_ID_INDEX] = purchase[LINE_PRODUCT_ID_INDEX]
                    refresh_line[LINE_QUANTITY_INDEX] = purchase[LINE_QUANTITY_INDEX] + quantity
                    purchase = tuple(refresh_line)
                    cart[index_line] = purchase
                    return purchase
            new_line = [0, 0]
            new_line[LINE_PRODUCT_ID_INDEX] = product_id
            new_line[LINE_QUANTITY_INDEX] = quantity
            new_line = tuple(new_line)
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
    our_line = find_cart_line(cart, product_id)
    if not our_line:
        return None
    if our_line[LINE_QUANTITY_INDEX] < quantity:
        print(f"Cart holds only {our_line[LINE_QUANTITY_INDEX]} unit(s) of product {product_id}, can't remove {quantity}")
        return None
    product = read_product(storage, product_id)
    if not product:
        return None
    for index_cart_line, cart_line in enumerate(cart):
        if our_line[LINE_PRODUCT_ID_INDEX] == cart_line[LINE_PRODUCT_ID_INDEX]:
            updation_line = [0, 0]
            updation_line[LINE_PRODUCT_ID_INDEX] = our_line[LINE_PRODUCT_ID_INDEX]
            updation_line[LINE_QUANTITY_INDEX] = our_line[LINE_QUANTITY_INDEX] - quantity
            updation_line = tuple(updation_line)
            for index_product, stored_product in enumerate(storage):
                if stored_product[PRODUCT_ID_INDEX] == product[PRODUCT_ID_INDEX]:
                    refresh_product = [0, 0, 0, 0]
                    refresh_product[PRODUCT_ID_INDEX] = stored_product[PRODUCT_ID_INDEX]
                    refresh_product[NAME_INDEX] = stored_product[NAME_INDEX]
                    refresh_product[PRICE_INDEX] = stored_product[PRICE_INDEX]
                    refresh_product[QUANTITY_INDEX] = stored_product[QUANTITY_INDEX] + quantity
                    refresh_product = tuple(refresh_product)
                    storage[index_product] = refresh_product
            if updation_line[LINE_QUANTITY_INDEX] == 0:
                del cart[index_cart_line]
            else:
                cart[index_cart_line] = updation_line
            return updation_line
    
