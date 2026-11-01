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
    elif (storage_quantity := storage[product_id][QUANTITY_KEY]) < quantity:
        print(
            f"not enough stock for product {product_id}:"
            f" {storage_quantity} available,"
            f" {quantity} requested"
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
    if product_id not in cart:
        print(f"product {product_id} is not in the cart")
        return None
    elif (cart_quantity := cart[product_id]) < quantity:
        print(
            f"cart holds only {cart_quantity}"
            f" unit(s) of product {product_id},"
            f" cannot remove {quantity}"
        )
        return None
    elif product_id not in storage:
        print(f"no product with id {product_id}")
        return None

    storage[product_id][QUANTITY_KEY] += quantity
    cart[product_id] -= quantity

    if cart[product_id] == 0:
        del cart[product_id]
        return 0
    else:
        return cart[product_id]
