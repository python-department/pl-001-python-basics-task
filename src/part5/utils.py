from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .decorators import FAILS_KEY, SUCCESS_KEY, Registry
from .storage import (
    NAME_KEY,
    PRICE_KEY,
    QUANTITY_KEY,
    Product,
)


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)


TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")
ID_KEY: Final[str] = TABLE_HEADERS[0]

STATS_TABLE_HEADERS: Final[tuple[str, ...]] = (
    "command name",
    "success",
    "fails",
    "success rate",
)
COMMAND_NAME_KEY: Final[str] = STATS_TABLE_HEADERS[0]
SUCCESS_RATE_KEY: Final[str] = STATS_TABLE_HEADERS[3]


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    normalized_name = " ".join(name.split()).lower()
    return normalized_name


def get_success_rate(success: int, fails: int) -> str:
    calls_quantity = success + fails
    if calls_quantity == 0:
        return "0.00%"

    return f"{success / calls_quantity:.2%}"


def get_storage_str_representation(storage: dict[int, Product]) -> str:
    lens = {
        key: [len(h)]
        for key, h in zip((ID_KEY, NAME_KEY, PRICE_KEY, QUANTITY_KEY), TABLE_HEADERS)
    }

    for product_id, product in storage.items():
        lens[ID_KEY].append(len(str(product_id)))
        for key in (NAME_KEY, PRICE_KEY, QUANTITY_KEY):
            lens[key].append(len(str(product[key])))

    maxlens = list(map(max, lens.values()))

    header_str = "|"
    separating_str = "|"
    for header, length in zip(TABLE_HEADERS, maxlens):
        header_str += f" {header.ljust(length)} |"
        separating_str += "-" + "-" * length + "-|"

    table = header_str + "\n" + separating_str

    for product_id, product in storage.items():
        table += "\n|"
        elems = (
            product_id,
            product[NAME_KEY],
            product[PRICE_KEY],
            product[QUANTITY_KEY],
        )
        for elem, length in zip(elems, maxlens):
            table += f" {str(elem).ljust(length)} |"

    return table


def get_stats_str_representation(registry: Registry) -> str:
    lens = {
        key: [len(h)]
        for key, h in zip(
            (COMMAND_NAME_KEY, SUCCESS_KEY, FAILS_KEY, SUCCESS_RATE_KEY),
            STATS_TABLE_HEADERS,
        )
    }

    for command_name, statistics in registry.items():
        lens[COMMAND_NAME_KEY].append(len(command_name))
        for key in (SUCCESS_KEY, FAILS_KEY):
            lens[key].append(len(str(statistics[key])))

    maxlens = list(map(max, lens.values()))

    header_str = "|"
    separating_str = "|"
    for header, length in zip(STATS_TABLE_HEADERS, maxlens):
        header_str += f" {header.ljust(length)} |"
        separating_str += "-" + "-" * length + "-|"

    table = header_str + "\n" + separating_str

    for command_name, statistics in registry.items():
        table += "\n|"

        successes = statistics[SUCCESS_KEY]
        fails = statistics[FAILS_KEY]
        elems = (
            command_name,
            successes,
            fails,
            get_success_rate(successes, fails),
        )
        for elem, length in zip(elems, maxlens):
            table += f" {str(elem).ljust(length)} |"

    return table
