from crud import id_check
from storage import QUANTITY_KEY, Product


def add_to_cart(
    storage: dict[str, Product],
    product_names: set[str],  # ?
    cart: dict[str, int],
    product_id: str,
    quantity: int,
) -> int | None:

    if not id_check(product_id, storage):
        return None
    if storage[product_id][QUANTITY_KEY] < quantity:
        print(
            f"not enough stock for product {product_id}: {storage[product_id][QUANTITY_KEY]} available, {quantity} requested"
        )
        return None

    if product_id in cart:
        cart[product_id][QUANTITY_KEY] += quantity
    else:
        cart[product_id] = storage[product_id]
        cart[product_id][QUANTITY_KEY] = quantity
    storage[product_id][QUANTITY_KEY] -= quantity

    return cart[product_id][QUANTITY_KEY]


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
    if cart[product_id][QUANTITY_KEY] < quantity:
        print(
            f"cart holds only {cart[product_id][QUANTITY_KEY]} unit(s) of product {product_id}, cannot remove {quantity}"
        )
        return None
    if not id_check(product_id, storage):
        return None

    storage[product_id][QUANTITY_KEY] += quantity
    cart[product_id][QUANTITY_KEY] -= quantity
    if cart[product_id][QUANTITY_KEY] == 0:
        del cart[product_id]
        return 0
    return cart[product_id][QUANTITY_KEY]
