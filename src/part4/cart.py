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
    product = read_product(storage, product_id)
    if product is None:
        return None

    current_stock = product[QUANTITY_KEY]
    if current_stock < quantity:
        print(
            f"not enough stock for product {product_id}: "
            f"{current_stock} available, {quantity} requested"
        )
        return None

    update_product(
        storage,
        product_names,
        product_id,
        {QUANTITY_KEY: current_stock - quantity},
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
    if product_id not in cart:
        print(f"product {product_id} is not in the cart")
        return None

    if cart[product_id] < quantity:
        print(
            f"cart holds only {cart[product_id]} unit(s) of product "
            f"{product_id}, cannot remove {quantity}"
        )
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
    cart[product_id] -= quantity
    if cart[product_id] == 0:
        del cart[product_id]
        return 0
    return cart[product_id]
