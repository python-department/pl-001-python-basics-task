"""Create/read/update/delete operations over the in-memory product store."""

from decimal import Decimal

from .storage import (
    NAME_INDEX,
    PRODUCT_ID_INDEX,
    PRODUCT_ID_MIN,
    Product,
)
from .utils import normalize_price, normalize_product_name


def generate_product_id(storage: list[Product]) -> int:
    """Choose the identifier for the next product added to ``storage``."""
    if not storage:
        return PRODUCT_ID_MIN
    return max(p[PRODUCT_ID_INDEX] for p in storage) + 1


def create_product(
    storage: list[Product], fields: tuple[str, Decimal, int]
) -> int | None:
    """Append a new product to ``storage`` and return its new identifier."""
    name, price, quantity = fields
    norm_name = normalize_product_name(name)

    if not norm_name:
        print("product name must not be blank")
        return None

    for p in storage:
        if p[NAME_INDEX] == norm_name:
            print(f"product name '{norm_name}' is already taken")
            return None

    product_id = generate_product_id(storage)
    norm_price = normalize_price(price)
    
    storage.append((product_id, norm_name, norm_price, quantity))
    return product_id


def read_product(storage: list[Product], product_id: int) -> Product | None:
    """Return the product stored under ``product_id``."""
    for p in storage:
        if p[PRODUCT_ID_INDEX] == product_id:
            return p
    print(f"no product with id {product_id}")
    return None


def update_product(
    storage: list[Product],
    product_id: int,
    fields: tuple[str, Decimal, int],
) -> Product | None:
    """Overwrite the fields of the product stored under ``product_id``."""
    name, price, quantity = fields
    norm_name = normalize_product_name(name)

    if not norm_name:
        print("product name must not be blank")
        return None

    target_idx = -1
    for i, p in enumerate(storage):
        if p[PRODUCT_ID_INDEX] == product_id:
            target_idx = i
            break

    if target_idx == -1:
        print(f"no product with id {product_id}")
        return None

    for i, p in enumerate(storage):
        if i != target_idx and p[NAME_INDEX] == norm_name:
            print(f"product name '{norm_name}' is already taken")
            return None

    norm_price = normalize_price(price)
    updated_product = (product_id, norm_name, norm_price, quantity)
    storage[target_idx] = updated_product
    return updated_product


def delete_product(storage: list[Product], product_id: int) -> int | None:
    """Remove the product stored under ``product_id`` from ``storage``."""
    for i, p in enumerate(storage):
        if p[PRODUCT_ID_INDEX] == product_id:
            storage.pop(i)
            return product_id
    print(f"no product with id {product_id}")
    return None
