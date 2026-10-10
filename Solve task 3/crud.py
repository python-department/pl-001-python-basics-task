from decimal import Decimal

from storage import ( 
    NAME_INDEX,
    PRODUCT_ID_INDEX,
    PRODUCT_ID_MIN,
    Product,
)
from utils import normalize_price, normalize_product_name


def generate_product_id(storage: list[Product]) -> int:
    if not storage:
        return PRODUCT_ID_MIN
    return max(storage)[PRODUCT_ID_INDEX] + 1


def create_product(storage: list[Product], fields: tuple[str, Decimal, int]) -> int | None:
    fields = (normalize_product_name(fields[0]), fields[1], fields[2])
    if fields[0] == "":
        print ("product name must not be blank")
        return None
    for prod in storage:
        if fields[0] == prod[NAME_INDEX]:
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
    norm_name = normalize_product_name(fields[0])
    if norm_name == "":
            print ("product name must not be blank")
            return None
    prod = 0
    for i in range(len(storage)):
        if storage[i][NAME_INDEX] == norm_name and storage[i][PRODUCT_ID_INDEX] != product_id:
            print (f"product name '{norm_name}' is already taken")
            return None
        elif storage[i][PRODUCT_ID_INDEX] == product_id:
            prod = (product_id, norm_name, normalize_price(fields[1]), fields[2])
            prod_num = i
    if prod != 0:
        storage[prod_num] = prod
        return prod 
    print (f"no product with id {product_id}")
    return None


def delete_product(storage: list[Product], product_id: int) -> int | None:
    for i in range(len(storage)):
        if storage[i][PRODUCT_ID_INDEX] is product_id:
            del storage[i]
            return product_id
    print (f"no product with id {product_id}")
    return None