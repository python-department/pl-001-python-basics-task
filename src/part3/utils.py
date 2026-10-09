"""Standalone helpers shared by the part3 storage and CRUD modules."""

from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .storage import Product

# Округление цен
PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal("0.01")

# Заголовки столбцов таблицы
TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    """Round a price to the precision every stored record uses."""
    return price.quantize(PRICE_STEP, rounding=ROUND_HALF_UP)


def normalize_product_name(name: str) -> str:
    """Reduce a product name to the canonical form the store keeps."""
    words = name.split()
    if not words:
        return ""
    return " ".join(words).lower()


def get_storage_str_representation(storage: list[Product]) -> str:
    """Render the product store as a text table with data-sized columns."""
    # Собираем все строки таблицы (сначала заголовки)
    rows_data = [TABLE_HEADERS]
    for p in storage:
        rows_data.append((str(p[0]), p[1], str(p[2]), str(p[3])))

    # Вычисляем максимальную ширину для каждого столбца
    col_widths = []
    for col_idx in range(len(TABLE_HEADERS)):
        max_w = max(len(row[col_idx]) for row in rows_data)
        col_widths.append(max_w)

    # Строим строку заголовков
    header_parts = [f" {TABLE_HEADERS[i].ljust(col_widths[i])} " for i in range(len(TABLE_HEADERS))]
    header_row = f"|{'|'.join(header_parts)}|"

    # Строим разделительную строку
    sep_parts = ["-" * (w + 2) for w in col_widths]
    sep_row = f"|{'|'.join(sep_parts)}|"

    result_lines = [header_row, sep_row]

    # Строим строки с данными товаров
    for row in rows_data[1:]:
        row_parts = [f" {row[i].ljust(col_widths[i])} " for i in range(len(TABLE_HEADERS))]
        result_lines.append(f"|{'|'.join(row_parts)}|")

    return "\n".join(result_lines)
