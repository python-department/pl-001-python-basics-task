"""Standalone helpers shared by the part4 storage and CRUD modules.

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

from decimal import ROUND_HALF_UP, Decimal  # noqa: F401
from typing import Final

from .storage import (  # noqa: F401
    NAME_KEY,
    PRICE_KEY,
    QUANTITY_KEY,
    ID_KEY,
    Product,
)


# Number of fractional digits every stored price is rounded to.
# Quantisation step derived from PRICE_PRECISION, e.g. Decimal("0.01").
PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)

# Column headers of the table produced by get_storage_str_representation,
# left to right. The width of each column is not fixed here -- it is
# measured per call from the data (see the function).
TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")


def normalize_price(price: Decimal) -> Decimal:
    """Round a price to the precision every stored record uses.

    Args:
        price: The raw price amount.

    Returns:
        ``price`` quantised to :data:`PRICE_PRECISION` fractional digits,
        with halves rounded up.
    """
    return price.quantize(PRICE_STEP, ROUND_HALF_UP)


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
    name_words = name.split()
    normalized_name = " ".join(name_words).lower()

    return normalized_name


def get_line_separator(storage_column_lengths: dict) -> str:
    """Принимает словарь с названиями столбцов и их длинами и возвращает строку-разделитель
    вида |------|------|-----|-----|
    """
    dashes = [ f"{'-'*(length + 2)}" for length in storage_column_lengths.values() ] # +2 чтобы учесть пробелы: | ID | name |...
    separator = f"|{"|".join(dashes)}|"
    return separator


def get_max_column_lenght(storage: dict[str, Product], KEY: str) -> int:
    """Принимает storage и возвращает длину максимального элемента из всех Product
    """
    values = [len(KEY)]
    for product_dict in storage.values(): #product_dict: dict[str, Any]
        values.append(len(str(product_dict[KEY])))

    return max(values)


def get_storage_str_representation(storage: dict[str, Product]) -> str:
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
        one row per product in ``storage``, in insertion order. When
        ``storage`` is empty only the header and separator rows are
        returned, sized to the header labels.
    """
    storage_column_lengths = {} #dict с длинами для каждого столбца
    for key in TABLE_HEADERS:
        match key:
            case _header if _header == ID_KEY:
                storage_column_lengths[ID_KEY] = max([len(ID_KEY)] + [len(storage_key) for storage_key in storage.keys()])

            case _header if _header == NAME_KEY:
                storage_column_lengths[NAME_KEY] = get_max_column_lenght(storage, NAME_KEY)

            case _header if _header == PRICE_KEY:
                storage_column_lengths[PRICE_KEY] = get_max_column_lenght(storage, PRICE_KEY)

            case _header if _header == QUANTITY_KEY:
                storage_column_lengths[QUANTITY_KEY] = get_max_column_lenght(storage, QUANTITY_KEY)

    # блок формирует первую и вторую строки таблицы
    headers = list()
    for key, value in storage_column_lengths.items():
        headers.append(f" {key:<{value}} ")
    table = f'|{"|".join(headers)}|\n{get_line_separator(storage_column_lengths)}'

    for _id, product_dict in storage.items():
        row = [f" {_id:<{storage_column_lengths[ID_KEY]}} "]
        for key in product_dict.keys():
            match key:
                case _header if _header == NAME_KEY:
                    row.append(f" {str(product_dict[NAME_KEY]):<{storage_column_lengths[NAME_KEY]}} ")
    
                case _header if _header == PRICE_KEY:
                    row.append(f" {str(product_dict[PRICE_KEY]):<{storage_column_lengths[PRICE_KEY]}} ")
    
                case _header if _header == QUANTITY_KEY:
                    row.append(f" {str(product_dict[QUANTITY_KEY]):<{storage_column_lengths[QUANTITY_KEY]}} ")

        table += f"\n|{'|'.join(row)}|"

    return table
