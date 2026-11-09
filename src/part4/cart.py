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
    if storage[product_id][QUANTITY_KEY] < quantity:
        print(
            f"not enough stock for product {product_id}: "
            f"{storage[product_id][QUANTITY_KEY]} available, "
            f"{quantity} requested"
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
    if cart[product_id] < quantity:
        print(
            f"cart holds only {cart[product_id]} unit(s) "
            f"of product {product_id}, cannot remove {quantity}"
        )
        return None
    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None
    storage[product_id][QUANTITY_KEY] += quantity
    cart[product_id] -= quantity
    if not cart[product_id]:
        del cart[product_id]
        return 0
    return cart[product_id]
