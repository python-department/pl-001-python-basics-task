from .storage import QUANTITY_KEY, Product


def add_to_cart(
    storage: dict[str, Product],
    product_names: set[str],
    cart: dict[str, int],
    product_id: str,
    quantity: int,
) -> int | None:

    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None

    product = storage[product_id]
    available = product[QUANTITY_KEY]

    if available < quantity:
        print(
            f"not enough stock for product {product_id}: "
            f"{available} available, {quantity} requested"
        )
        return None

    product[QUANTITY_KEY] -= quantity

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

    cart_quantity = cart[product_id]

    if cart_quantity < quantity:
        print(
            f"cart holds only {cart_quantity} unit(s) of product "
            f"{product_id}, cannot remove {quantity}"
        )
        return None

    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None

    storage[product_id][QUANTITY_KEY] += quantity

    remaining = cart_quantity - quantity

    if remaining == 0:
        del cart[product_id]
    else:
        cart[product_id] = remaining

    return remaining
