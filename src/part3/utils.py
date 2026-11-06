from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .storage import Product


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)

TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    return Decimal(price).quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    rename = (" ".join(name.split())).lower()
    return rename


def get_storage_str_representation(storage: list[Product]) -> str:
    storage_str = []
    for item in storage:
        ids, name, price, quantity = item
        item_str = [str(ids), name, str(price), str(quantity)]
        storage_str.append(item_str)

    namemaxlen = max(
        [len(item_str[1]) for item_str in storage_str] + [len(TABLE_HEADERS[1])]
    )
    idsmaxlen = max(
        [len(item_str[0]) for item_str in storage_str] + [len(TABLE_HEADERS[0])]
    )
    pricemaxlen = max(
        [len(item_str[2]) for item_str in storage_str] + [len(TABLE_HEADERS[2])]
    )
    quantitymaxlen = max(
        [len(item_str[3]) for item_str in storage_str] + [len(TABLE_HEADERS[3])]
    )

    s = (
        "|"
        + " "
        + "ID"
        + (" " * (idsmaxlen - len("ID") + 1))
        + "|"
        + " "
        + "name"
        + (" " * (namemaxlen - len("name") + 1))
        + "|"
        + " "
        + "price"
        + (" " * (pricemaxlen - len("price") + 1))
        + "|"
        + " "
        + "quantity"
        + (" " * (quantitymaxlen - len("quantity") + 1))
        + "|"
    )

    s_ = (
        "|"
        + ("-" * (idsmaxlen + 2))
        + "|"
        + ("-" * (namemaxlen + 2))
        + "|"
        + ("-" * (pricemaxlen + 2))
        + "|"
        + ("-" * (quantitymaxlen + 2))
        + "|"
    )
    storage_ans = []
    for item_str in storage_str:
        item_ans = (
            "|"
            + " "
            + item_str[0]
            + (" " * (idsmaxlen - len(item_str[0]) + 1))
            + "|"
            + " "
            + item_str[1]
            + (" " * (namemaxlen - len(item_str[1]) + 1))
            + "|"
            + " "
            + item_str[2]
            + (" " * (pricemaxlen - len(item_str[2]) + 1))
            + "|"
            + " "
            + item_str[3]
            + (" " * (quantitymaxlen - len(item_str[3]) + 1))
            + "|"
        )
        storage_ans.append(item_ans)
    result = "\n".join([s, s_] + storage_ans)
    return result
