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


def add_to_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    """Move ``quantity`` units of ``product_id`` from the store into ``cart``."""
    # 1. Ищем товар. read_product сам напечатает сообщение, если не нашёл.
    product = read_product(storage, product_id)
    if product is None:
        return None

    product_name = product[NAME_INDEX]
    product_price = product[PRICE_INDEX]
    product_quantity = product[QUANTITY_INDEX]

    # 2. Проверяем остаток
    if product_quantity < quantity:
        print(
            f"not enough stock for product {product_id}: "
            f"{product_quantity} available, {quantity} requested"
        )
        return None

    # 3. Списываем со склада
    update_product(
        storage,
        product_id,
        (product_name, product_price, product_quantity - quantity),
    )

    # 4. Обновляем строку корзины или создаём новую
    for i, line in enumerate(cart):
        if line[LINE_PRODUCT_ID_INDEX] == product_id:
            new_line = (product_id, line[LINE_QUANTITY_INDEX] + quantity)
            cart[i] = new_line
            return new_line

    new_line = (product_id, quantity)
    cart.append(new_line)
    return new_line


def remove_from_cart(
    storage: list[Product],
    cart: list[CartLine],
    product_id: int,
    quantity: int,
) -> CartLine | None:
    """Move ``quantity`` units of ``product_id`` from ``cart`` back to the store."""
    # 1. Ищем строку корзины
    line_index = None
    for i, line in enumerate(cart):
        if line[LINE_PRODUCT_ID_INDEX] == product_id:
            line_index = i
            break

    if line_index is None:
        print(f"product {product_id} is not in the cart")
        return None

    # 2. Проверяем, хватает ли единиц в строке
    line_quantity = cart[line_index][LINE_QUANTITY_INDEX]
    if line_quantity < quantity:
        print(
            f"not enough units of product {product_id} in cart: "
            f"{line_quantity} available, {quantity} requested"
        )
        return None

    # 3. Находим товар на складе, чтобы вернуть ему единицы
    product = read_product(storage, product_id)
    if product is None:
        print(f"product {product_id} is missing from the store")
        return None

    product_name = product[NAME_INDEX]
    product_price = product[PRICE_INDEX]
    product_quantity = product[QUANTITY_INDEX]

    # 4. Возвращаем единицы на склад
    update_product(
        storage,
        product_id,
        (product_name, product_price, product_quantity + quantity),
    )

    # 5. Уменьшаем строку; если стало 0 — удаляем
    remaining = line_quantity - quantity
    if remaining == 0:
        del cart[line_index]
        return (product_id, 0)

    new_line = (product_id, remaining)
    cart[line_index] = new_line
    return new_line
