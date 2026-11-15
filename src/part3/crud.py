from decimal import Decimal

from .storage import (
    NAME_INDEX,
    PRODUCT_ID_INDEX,
    PRODUCT_ID_MIN,
    Product,
)
from .utils import normalize_price, normalize_product_name


def generate_product_id(storage: list[Product]) -> int:
    if not storage:
        return PRODUCT_ID_MIN
    return max(product[PRODUCT_ID_INDEX] for product in storage) + 1


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    normalized_name = normalize_product_name(fields[0])

    if not normalized_name:
        print("product name must not be blank")
        return None
    elif normalized_name in (product[NAME_INDEX] for product in storage):
        print(f"product name '{normalized_name}' is already taken")
        return None

    product_id = generate_product_id(storage)
    storage.append((product_id, normalized_name, normalize_price(fields[1]), fields[2]))
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
    normalized_name = normalize_product_name(fields[0])

    if not normalized_name:
        print("product name must not be blank")
        return None

    id_existance = False
    name_already_taken = False

    for product in storage:
        if product[PRODUCT_ID_INDEX] == product_id:
            id_existance = True
        if (
            product[NAME_INDEX] == normalized_name
            and product[PRODUCT_ID_INDEX] != product_id
        ):
            name_already_taken = True

    if not id_existance:
        print(f"no product with id {product_id}")
        return None

    if name_already_taken:
        print(f"product name '{normalized_name}' is already taken")
        return None

    for old_product in storage:
        if product_id == old_product[PRODUCT_ID_INDEX]:
            new_product = (
                product_id,
                normalized_name,
                normalize_price(fields[1]),
                fields[2],
            )
            storage.append(new_product)
            storage.remove(old_product)
            break
    return new_product


def delete_product(storage: list[Product], product_id: int) -> int | None:
    for product in storage:
        if product[PRODUCT_ID_INDEX] == product_id:
            storage.remove(product)
            return product[PRODUCT_ID_INDEX]

    print(f"no product with id {product_id}")
    return None
