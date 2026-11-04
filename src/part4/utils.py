from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .storage import (
    NAME_KEY,
    PRICE_KEY,
    QUANTITY_KEY,
    Product,
)


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final[Decimal] = Decimal(1).scaleb(-PRICE_PRECISION)

TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return " ".join(name.lower().split())


def heider_one_write(width: int) -> str:
    return "|" + "-" * (width + 2)


def post_heider_write(w1: int, w2: int, w3: int, w4: int) -> str:
    return (
        heider_one_write(w1)
        + heider_one_write(w2)
        + heider_one_write(w3)
        + heider_one_write(w4)
        + "|"
    )


def max_storege_len(storage: dict[str, Product], id: int) -> int:
    widths = [len(TABLE_HEADERS[id])]
    for uuid, product in storage.items():
        if id == 0:
            widths.append(len(str(uuid)))
        elif id == 1:
            widths.append(len(str(product[NAME_KEY])))
        elif id == 2:
            widths.append(len(str(product[PRICE_KEY])))
        elif id == 3:
            widths.append(len(str(product[QUANTITY_KEY])))
    return max(widths)


def get_storage_str_representation(storage: dict[str, Product]) -> str:

    widths_colomn = [max_storege_len(storage, i) for i in range(len(TABLE_HEADERS))]

    header = (
        "|"
        + "|".join(
            f" {TABLE_HEADERS[i].ljust(widths_colomn[i])} "
            for i in range(len(TABLE_HEADERS))
        )
        + "|"
    )

    razdel = post_heider_write(*widths_colomn)

    lines = [header, razdel]
    for uuid, product in storage.items():
        one_product = [
            str(uuid),
            str(product[NAME_KEY]),
            str(product[PRICE_KEY]),
            str(product[QUANTITY_KEY]),
        ]
        output_product_one = (
            "|"
            + "|".join(
                f" {one_product[i].ljust(widths_colomn[i])} "
                for i in range(len(TABLE_HEADERS))
            )
            + "|"
        )
        lines.append(output_product_one)

    return "\n".join(lines)
