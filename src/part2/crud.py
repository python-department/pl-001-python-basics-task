from decimal import Decimal
from utils import normalize_price
from storage import (
    Product,
    PRODUCT_ID_MIN, 
    PRODUCT_ID_INDEX,
    NAME_INDEX,
    PRICE_INDEX,
    QUANTITY_INDEX,
)
def generate_product_id(storage: list[Product]) -> int:
    if not storage:
        return PRODUCT_ID_MIN
    return max(i[PRODUCT_ID_INDEX] for i in storage) + 1
def create_product(storage: list[Product], fields: tuple[str, Decimal, int]) -> int | None:
    name, price, qty = fields
    for i in storage:
        if i[NAME_INDEX] == name:
            print(f"product name '<{name}>' is already taken")
            return 0
    new_id = generate_product_id(storage)
    norm_price = normalize_price(price)
    storage.append((new_id, name, norm_price, qty))
    return new_id
def read_product(storage: list[Product], product_id: int) -> Product | None:
    for i in storage:
        if i[PRODUCT_ID_INDEX] == product_id:
            return i
    print(f"no product with id <{product_id}>")
    return None
def update_product(storage: list[Product], product_id: int, fields: tuple[str, Decimal, int]) -> Product | None:
    name, price, qty = fields
    for i, p in enumerate(storage):
        if p[PRODUCT_ID_INDEX] == product_id:
            norm_price = normalize_price(price)
            updated_product = (product_id, name, norm_price, qty)
            storage[i] = update_product
            return update_product
        print(f"no product with id <{product_id}>")
        return None
    def delete_product(storage: list[Product], product_id: int) -> int | None:
        for i, p in enumerate(storage):
            if p[PRODUCT_ID_INDEX] == product_id:
                storage.pop(i)
                return product_id
    print(f"no product with id <{product_id}>")
    return None