"""Standalone helpers shared by the part3 storage and CRUD modules.

Normalisation:

* :func:`normalize_price` rounds a raw :class:`~decimal.Decimal` amount to
  the fixed number of fractional digits (:data:`PRICE_PRECISION`) that
  every stored price uses, keeping currency values free of binary
  floating-point error.
* :func:`normalize_product_name` strips surrounding whitespace from a
  product name, collapses every internal run of whitespace to a single
  space and lower-cases it, giving every stored name a single canonical
  form.

Presentation:

* :func:`get_storage_str_representation` renders the whole store as a
  text table meant to be printed to a terminal; each column is sized to
  the longest value it holds in that particular call.
"""

from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .storage import NAME_INDEX, PRICE_INDEX, PRODUCT_ID_INDEX, QUANTITY_INDEX, Product


# Number of fractional digits every stored price is rounded to.
# Quantisation step derived from PRICE_PRECISION, e.g. Decimal("0.01").
# TODO: задайте число знаков после запятой и шаг квантования (используйте своё
# решение части 2)
PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)

# Column headers of the table produced by get_storage_str_representation,
# left to right. The width of each column is not fixed here -- it is
# measured per call from the data (see the function).
# TODO: задайте заголовки столбцов таблицы
TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    """Round a price to the precision every stored record uses.

    Args:
        price: The raw price amount.

    Returns:
        ``price`` quantised to :data:`PRICE_PRECISION` fractional digits,
        with halves rounded up.
    """
    ratio = price / PRICE_STEP
    steps = ratio.quantize(Decimal("1."), rounding=ROUND_HALF_UP)
    real_price = steps * PRICE_STEP
    return real_price


def normalize_product_name(name: str) -> str:
    """Reduce a product name to the canonical form the store keeps.

    Args:
        name: The raw product name.

    Returns:
        ``name`` with every leading and trailing whitespace character
        removed, every internal run of whitespace (spaces, tabs and the
        like) collapsed to a single space, and the rest lower-cased. For
        example ``"abc    def\tghi\tjkl"`` becomes ``"abc def ghi jkl"``.
        The result is an empty string when ``name`` holds nothing but
        whitespace.
    """
    pars_name = name.split()
    norm_list = [norm_word.lower() for word in pars_name if (norm_word := word.strip())]
    norm_name = " ".join(norm_list)
    return norm_name


def from_product_to_list(product: Product) -> list[str]:
    return [
        str(product[PRODUCT_ID_INDEX]),
        str(product[NAME_INDEX]),
        str(product[PRICE_INDEX]),
        str(product[QUANTITY_INDEX]),
    ]


def calculate_of_wight(new_storage: list[list[str]]) -> list[int]:
    wights = [len(words) for words in TABLE_HEADERS]

    for products in new_storage:
        for i, word in enumerate(products):
            wights[i] = max(wights[i], len(word))
    return wights


def render_row(new_products: list[str], widths: list[int]) -> str:
    parts = ["|"]

    for i in range(len(new_products)):
        element = new_products[i].ljust(widths[i])
        parts.append(" " + element + " ")
        parts.append("|")

    return "".join(parts)


def render_sep(widhts: list[int]) -> str:
    parts = ["|"]

    for wight in widhts:
        parts.append("-" * (wight + 2))
        parts.append("|")

    return "".join(parts)


def get_storage_str_representation(storage: list[Product]) -> str:
    """Render the product store as a text table with data-sized columns.

    The table has the columns named by :data:`TABLE_HEADERS` -- id, name,
    price and quantity. Each column is made exactly as wide as the longest
    value it carries in this call (its header counted), so the columns
    line up when the string is printed to a terminal and no value is ever
    truncated.

    Args:
        storage: The product store to render.

    Returns:
        A multi-line string: a header row, a dashed separator row, then
        one row per product in ``storage`` in list order. When ``storage``
        is empty only the header and separator rows are returned, sized to
        the header labels.
    """
    new_storage = []
    for product in storage:
        new_storage.append(from_product_to_list(product))

    wights = calculate_of_wight(new_storage)

    lines = []

    lines.append(render_row(list(TABLE_HEADERS), wights))
    lines.append(render_sep(wights))

    for elements in new_storage:
        lines.append(render_row(elements, wights))

    return "\n".join(lines)
