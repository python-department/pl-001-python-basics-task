from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .storage import NAME_INDEX, PRICE_INDEX, PRODUCT_ID_INDEX, QUANTITY_INDEX, Product


PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)

TABLE_HEADERS: Final = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    return " ".join(name.split()).lower()


def get_storage_str_representation(storage: list[Product]) -> str:
    w_id = len(TABLE_HEADERS[0])
    w_name = len(TABLE_HEADERS[1])
    w_price = len(TABLE_HEADERS[2])
    w_qty = len(TABLE_HEADERS[3])
    rows: list[tuple[str, str, str, str]] = []
    for p in storage:
        pid_str = str(p[PRODUCT_ID_INDEX])
        name_str = str(p[NAME_INDEX])
        price_str = str(p[PRICE_INDEX])
        qty_str = str(p[QUANTITY_INDEX])
        rows.append((pid_str, name_str, price_str, qty_str))
        w_id = max(w_id, len(pid_str))
        w_name = max(w_name, len(name_str))
        w_price = max(w_price, len(price_str))
        w_qty = max(w_qty, len(qty_str))

    def format_row(c1: str, c2: str, c3: str, c4: str) -> str:
        return f"| {c1:<{w_id}} | {c2:<{w_name}} | {c3:<{w_price}} | {c4:<{w_qty}} |"

    lines = []
    lines.append(format_row(*TABLE_HEADERS))
    sep = f"|-{'-' * w_id}-|-{'-' * w_name}-|-{'-' * w_price}-|-{'-' * w_qty}-|"
    lines.append(sep)

    for row in rows:
        lines.append(format_row(*row))

    return "\n".join(lines)
