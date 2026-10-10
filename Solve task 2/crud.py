from decimal import Decimal

from storage import ( 
    NAME_INDEX,
    PRODUCT_ID_INDEX,
    PRODUCT_ID_MIN,
    Product,
)
from utils import normalize_price


def generate_product_id(storage: list[Product]) -> int:
    if not storage:
        return 0
    return max(storage)[PRODUCT_ID_INDEX] + 1


def create_product(storage: list[Product], fields: tuple[str, Decimal, int]) -> int | None:
    for prod in storage:
        if fields [0] is prod[NAME_INDEX]:
            print (f"product name '{fields [0]}' is already taken")
            return None
    new_product = (generate_product_id(storage), fields[0], normalize_price(fields[1]), fields[2])
    storage.append(new_product)
    return new_product[0]


def read_product(storage: list[Product], product_id: int) -> Product | None:
    for prod in storage:
        if prod[0] is product_id:
            return prod
    print (f"no product with id {product_id}")
    return None


def update_product(
    storage: list[Product],
    product_id: int,
    fields: tuple[str, Decimal, int],
) -> Product | None:
    for i in range(len(storage)):
        if storage[i][PRODUCT_ID_INDEX] is product_id:
            storage[i] = (product_id, fields[0], normalize_price(fields[1]), fields[2])
            return storage[i]
    print (f"no product with id {product_id}")
    return None


def delete_product(storage: list[Product], product_id: int) -> int | None:
    for i in range(len(storage)):
        if storage[i][PRODUCT_ID_INDEX] is product_id:
            del storage[i]
            return product_id
    print (f"no product with id {product_id}")
    return None
