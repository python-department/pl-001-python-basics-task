from .crud import read_product
from .storage import QUANTITY_KEY, Product


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

    available = product[QUANTITY_KEY]
    if available < quantity:
        print(
            f"not enough stock for product {product_id}: "
            f"{available} available, {quantity} requested"
        )
        return None

    product[QUANTITY_KEY] = available - quantity
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

    in_cart = cart[product_id]
    if in_cart < quantity:
        print(
            f"cart holds only {in_cart} unit(s) of product "
            f"{product_id}, cannot remove {quantity}"
        )
        return None

    product = read_product(storage, product_id)
    if product is None:
        return None

    product[QUANTITY_KEY] += quantity
    cart[product_id] = in_cart - quantity
    if cart[product_id] == 0:
        del cart[product_id]
        return 0
    return cart[product_id]