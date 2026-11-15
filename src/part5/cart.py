from .storage import QUANTITY_KEY, Product


def add_to_cart(
    storage: dict[int, Product],
    product_names: set[str],
    cart: dict[int, int],
    product_id: int,
    quantity: int,
) -> int | None:
    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None

    stock: int = storage[product_id][QUANTITY_KEY]
    if stock < quantity:
        print(
            f"not enough stock for product {product_id}: {stock} available, {quantity} requested"
        )
        return None

    storage[product_id][QUANTITY_KEY] -= quantity
    cart[product_id] = cart.get(product_id, 0) + quantity

    return cart[product_id]


def remove_from_cart(
    storage: dict[int, Product],
    product_names: set[str],
    cart: dict[int, int],
    product_id: int,
    quantity: int,
) -> int | None:
    if product_id not in cart:
        print(f"product {product_id} is not in the cart")
        return None

    cart_quantity: int = cart[product_id]
    if cart_quantity < quantity:
        print(
            f"cart holds only {cart_quantity} unit(s) of product {product_id}, cannot remove {quantity}"
        )
        return None

    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None

    storage[product_id][QUANTITY_KEY] += quantity
    cart[product_id] -= quantity

    if cart[product_id] == 0:
        del cart[product_id]

    return cart.get(product_id, 0)
