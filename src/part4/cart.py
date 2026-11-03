from .crud import (
    read_product,
    update_product,
)
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
    # 1. Ищем товар. read_product сам напечатает сообщение, если не нашёл
    product = read_product(storage, product_id)
    if product is None:
        return None

    product_quantity = product[QUANTITY_KEY]

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
        product_names,
        product_id,
        {QUANTITY_KEY: product_quantity - quantity},
    )

    # 4. Добавляем quantity единиц в корзину
    remaining = cart.get(product_id, 0) + quantity
    cart[product_id] = remaining
    return remaining


def remove_from_cart(
    storage: dict[str, Product],
    product_names: set[str],
    cart: dict[str, int],
    product_id: str,
    quantity: int,
) -> int | None:
    # 1. Есть ли товар в корзине
    if product_id not in cart:
        print(f"product {product_id} is not in the cart")
        return None

    cart_quantity_now = cart[product_id]

    # 2. Достаточно ли quantity в корзине
    if cart_quantity_now < quantity:
        print(
            f"cart holds only {cart_quantity_now} unit(s) of product "
            f"{product_id}, cannot remove {quantity}"
        )
        return None

    # 3. Есть ли товар в хранилище
    product = read_product(storage, product_id)
    if product is None:
        return None

    product_quantity = product[QUANTITY_KEY]

    # Возвращаем на склад
    update_product(
        storage,
        product_names,
        product_id,
        {QUANTITY_KEY: product_quantity + quantity},
    )

    remaining = cart_quantity_now - quantity
    if remaining == 0:
        del cart[product_id]
        return 0

    cart[product_id] = remaining
    return remaining
