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
    quantity_in_shop = product[QUANTITY_KEY]

    if quantity > quantity_in_shop:
        print(
            f"not enough stock for product {product_id}: {quantity_in_shop} available, {quantity} requested"
        )
        return None

    product[QUANTITY_KEY] = quantity_in_shop - quantity

    product_in_cart = cart.get(product_id, 0)
    cart[product_id] = product_in_cart + quantity
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
            f"cart holds only {cart[product_id]} unit(s) of product {product_id}, cannot remove {quantity}"
        )
        return None

    if product_id not in storage:
        print(f"no product with id {product_id}")
        return None

    product = storage[product_id]
    product_in_shop = product[QUANTITY_KEY]
    product[QUANTITY_KEY] = product_in_shop + quantity

    if cart[product_id] == quantity:
        del cart[product_id]
        return 0

    cart[product_id] -= quantity
    return cart[product_id] - quantity
