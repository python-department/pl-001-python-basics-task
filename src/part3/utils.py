from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .storage import NAME_INDEX, PRICE_INDEX, PRODUCT_ID_INDEX, QUANTITY_INDEX, Product


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)

TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    normalized_name = " ".join(name.split()).lower()
    return normalized_name


def get_storage_str_representation(storage: list[Product]) -> str:
    lens = [[len(h)] for h in TABLE_HEADERS]

    for product in storage:
        for elem, pointer in zip(
            product, [PRODUCT_ID_INDEX, NAME_INDEX, PRICE_INDEX, QUANTITY_INDEX]
        ):
            lens[pointer].append(len(str(elem)))

    maxlens = list(map(max, lens))

    header_str = "|"
    separating_str = "|"
    for header, length in zip(TABLE_HEADERS, maxlens):
        header_str += f" {header.ljust(length)} |"
        separating_str += "-" + "-" * length + "-|"

    table = header_str + "\n" + separating_str

    for product in storage:
        table += "\n|"
        for elem, length in zip(product, maxlens):
            table += f" {str(elem).ljust(length)} |"

    return table
