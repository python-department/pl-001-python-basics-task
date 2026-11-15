from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .decorators import FAILS_KEY, SUCCESS_KEY, Registry
from .storage import Product


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)


TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")
STATS_TABLE_HEADERS: Final[tuple[str, ...]] = (
    "command name",
    "success",
    "fails",
    "success rate",
)


def normalize_price(price: Decimal) -> Decimal:
    return Decimal(price).quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    rename = (" ".join(name.split())).lower()
    return rename


def get_storage_str_representation(storage: dict[int, Product]) -> str:
    storage_str = []

    idsmaxlen = len(TABLE_HEADERS[0])
    namemaxlen = len(TABLE_HEADERS[1])
    pricemaxlen = len(TABLE_HEADERS[2])
    quantitymaxlen = len(TABLE_HEADERS[3])

    for product_id, product in storage.items():
        p_id = str(product_id)
        p_name = str(product["name"])
        p_price = str(product["price"])
        p_qty = str(product["quantity"])

        storage_str.append([p_id, p_name, p_price, p_qty])

        idsmaxlen = max(idsmaxlen, len(p_id))
        namemaxlen = max(namemaxlen, len(p_name))
        pricemaxlen = max(pricemaxlen, len(p_price))
        quantitymaxlen = max(quantitymaxlen, len(p_qty))

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


def get_stats_str_representation(registry: Registry) -> str:
    command_str = []

    command_max_len = len(STATS_TABLE_HEADERS[0])
    success_max_len = len(STATS_TABLE_HEADERS[1])
    fails_max_len = len(STATS_TABLE_HEADERS[2])
    rate_max_len = len(STATS_TABLE_HEADERS[3])

    for command_name, stats in registry.items():
        command = str(command_name)
        success = str(stats[SUCCESS_KEY])
        fails = str(stats[FAILS_KEY])

        command_str.append([command, success, fails])

        command_max_len = max(command_max_len, len(command))
        success_max_len = max(success_max_len, len(success))
        fails_max_len = max(fails_max_len, len(fails))

    first_str = (
        "|"
        + " "
        + "command name"
        + (" " * (command_max_len - len(STATS_TABLE_HEADERS[0]) + 1))
        + "|"
        + " "
        + "success"
        + (" " * (success_max_len - len(STATS_TABLE_HEADERS[1]) + 1))
        + "|"
        + " "
        + "fails"
        + (" " * (fails_max_len - len(STATS_TABLE_HEADERS[2]) + 1))
        + "|"
        + " "
        + "success rate"
        + (" " * (rate_max_len - len(STATS_TABLE_HEADERS[3]) + 1))
        + "|"
    )
    second_str = (
        "|"
        + ("-" * (command_max_len + 2))
        + "|"
        + ("-" * (success_max_len + 2))
        + "|"
        + ("-" * (fails_max_len + 2))
        + "|"
        + ("-" * (rate_max_len + 2))
        + "|"
    )
    command_ans = []
    for item_str in command_str:
        if int(item_str[1]) + int(item_str[2]) == 0:
            rate_str = "0.00%"
        else:
            rate_str = (
                str(
                    normalize_price(
                        (int(item_str[1]) / (int(item_str[1]) + int(item_str[2]))) * 100
                    )
                )
                + "%"
            )
        item_ans = (
            "|"
            + " "
            + item_str[0]
            + (" " * (command_max_len - len(item_str[0]) + 1))
            + "|"
            + " "
            + item_str[1]
            + (" " * (success_max_len - len(item_str[1]) + 1))
            + "|"
            + " "
            + item_str[2]
            + (" " * (fails_max_len - len(item_str[2]) + 1))
            + "|"
            + " "
            + rate_str
            + (" " * (rate_max_len - len(rate_str) + 1))
            + "|"
        )
        command_ans.append(item_ans)

    result = "\n".join([first_str, second_str] + command_ans)
    return result
