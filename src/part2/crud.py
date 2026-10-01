from decimal import Decimal

from .storage import ( 
    NAME_INDEX, 
    PRODUCT_ID_INDEX,
    PRODUCT_ID_MIN,
    Product,
)
from .utils import normalize_price


def generate_product_id(storage: list[Product]) -> int:
    if not storage:
        return PRODUCT_ID_MIN
    return max([product[PRODUCT_ID_INDEX] for product in storage]) + 1


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    product_name = fields[0]
    storage_product_names = [product[NAME_INDEX] for product in storage]
    if product_name in storage_product_names:
        print(f"product name '{product_name}' is already taken")
        return None
        
    product_id = generate_product_id(storage)
    product_price = normalize_price(fields[1])
    product_quantity = fields[2]
    storage.append((
        product_id,
        product_name,
        product_price,
        product_quantity
    ))
    return product_id


def read_product(storage: list[Product], product_id: int) -> Product | None:
    for product in storage:
        if product[PRODUCT_ID_INDEX] == product_id:
            return product
    print(f"no product with id {product_id}")
    return None


def update_product(
    storage: list[Product],
    product_id: int,
    fields: tuple[str, Decimal, int],
) -> Product | None:
    for i, product in enumerate(storage):
        if product[PRODUCT_ID_INDEX] == product_id:
            updated_product = (
                product_id,
                fields[0],
                normalize_price(fields[1]),
                fields[2]
            )
            storage[i] = updated_product
            return updated_product
    print(f"no product with id {product_id}")
    return None


def delete_product(storage: list[Product], product_id: int) -> int | None:
    for product in storage:
        if product[PRODUCT_ID_INDEX] == product_id:
            storage.remove(product)
            return product_id
    print(f"no product with id {product_id}")
    return None