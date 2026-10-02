from crud import read_product, update_product
from storage import NAME_INDEX, PRICE_INDEX, QUANTITY_INDEX, Final, Product


CartLine = tuple[int, int]
LINE_PRODUCT_ID_INDEX: Final[int] = 0
LINE_QUANTITY_INDEX: Final[int] = 1


def find_cart_line(cart: list[CartLine], product_id: int) -> int | None:
    for i, line in enumerate(cart):
        if line[LINE_PRODUCT_ID_INDEX] == product_id:
            return i
    return None


def add_to_cart(
    storage: list[Product], cart: list[CartLine], product_id: int, quantity: int
) -> CartLine | None:
    product = read_product(storage, product_id)
    if product is None:
        return None
    stock = product[QUANTITY_INDEX]
    if stock < quantity:
        print(
            f"not enough stock for product <{product_id}>: <{stock}> available, <{quantity}> requested"
        )
        return None
    new_stock = stock - quantity
    update_product(
        storage, product_id, (product[NAME_INDEX], product[PRICE_INDEX], new_stock)
    )


def remove_from_cart(
    storage: list[Product], cart: list[CartLine], product_id: int, quantity: int
) -> CartLine | None:
    idx = find_cart_line(cart, product_id)
    if idx is None:
        print(f"product <{product_id}> is not in the cart")
        return None
    cart_qty = cart[idx][LINE_QUANTITY_INDEX]
    if cart_qty < quantity:
        print(
            f"cart holds only <{cart_qty}> unit(s) of product <{product_id}>, cannot remove <quantity>"
        )
        return None
    product = read_product(storage, product_id)
    if product is None:
        return None
    new_stock = product[QUANTITY_INDEX] + quantity
    update_product(
        storage, product_id, (product[NAME_INDEX], product[PRICE_INDEX], new_stock)
    )
    new_cart_qty = cart_qty - quantity
    new_line = (product_id, new_cart_qty)
    if new_cart_qty == 0:
        cart.pop(idx)
    else:
        cart[idx] = new_line
