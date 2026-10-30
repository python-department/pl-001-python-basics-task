# Shopping-cart operations layered on top of the product store.

import sys
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
    cart: list[CartLine], product_id: int
) -> tuple[int, CartLine] | None:
    # Вспомогательная функция для поиска строки в корзине и её индекса.
    for i, line in enumerate(cart):
        if line[LINE_PRODUCT_ID_INDEX] == product_id:
            return i, line
    return None


def add_to_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    # Move ``quantity`` units of ``product_id`` from the store into ``cart``.
    # 1. Поиск товара на складе
    product = read_product(storage, product_id)
    if product is None:
        return None
    # 2. Проверка доступного количества
    available = product[QUANTITY_INDEX]
    if available < quantity:
        print(
            f"not enough stock for product {product_id}: "
            f"{available} available, {quantity} requested",
            file=sys.stdout,
        )
        return None
    # 3. Обновление склада
    new_fields = (product[NAME_INDEX], product[PRICE_INDEX], available - quantity)
    update_product(storage, product_id, new_fields)
    # 4. Обновление корзины
    cart_search = find_cart_line(cart, product_id)
    if cart_search:
        idx, old_line = cart_search
        new_line: CartLine = (product_id, old_line[LINE_QUANTITY_INDEX] + quantity)
        cart[idx] = new_line
    else:
        new_line = (product_id, quantity)
        cart.append(new_line)
    return new_line


def remove_from_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    # Move ``quantity`` units of ``product_id`` from ``cart`` back to the store.
    # 1. Поиск строки в корзине
    cart_search = find_cart_line(cart, product_id)
    if not cart_search:
        print(f"product {product_id} is not in the cart", file=sys.stdout)
        return None

    idx, line = cart_search
    in_cart = line[LINE_QUANTITY_INDEX]
    # 2. Проверка количества в корзине
    if in_cart < quantity:
        print(
            f"cart holds only {in_cart} unit(s) of product {product_id}, "
            f"cannot remove {quantity}",
            file=sys.stdout,
        )
        return None
    # 3. Проверка существования товара на складе
    product = read_product(storage, product_id)
    if product is None:
        return None
    # 4. Обновление склада и корзины
    available = product[QUANTITY_INDEX]
    new_fields = (product[NAME_INDEX], product[PRICE_INDEX], available + quantity)
    update_product(storage, product_id, new_fields)
    remaining_quantity = in_cart - quantity
    if remaining_quantity == 0:
        cart.pop(idx)
        return (product_id, 0)
    else:
        new_line: CartLine = (product_id, remaining_quantity)
        cart[idx] = new_line
        return new_line
