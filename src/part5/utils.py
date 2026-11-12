"""Standalone helpers shared by the part5 storage and CRUD modules.

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
* :func:`get_stats_str_representation` renders the call statistics gathered
  by :func:`~src.part5.decorators.collect_stats` as a table of the same
  look, with the success rate of every command as a percentage.
"""

from decimal import ROUND_HALF_UP, Decimal
import re
from typing import Any, Final

from .decorators import Registry, SUCCESS_KEY, FAILS_KEY
from .storage import Product


# Number of fractional digits every stored price is rounded to.
# Quantisation step derived from PRICE_PRECISION, e.g. Decimal("0.01").
PRICE_PRECISION: Final[int] = 2
PRICE_STEP: Final = Decimal(1).scaleb(-PRICE_PRECISION)

# Column headers of the table produced by get_storage_str_representation,
# left to right. The width of each column is not fixed here -- it is
# measured per call from the data (see the function).
TABLE_HEADERS: Final[tuple[str, ...]] = ("ID", "name", "price", "quantity")
STATS_TABLE_HEADERS: Final[tuple[str, ...]] = ("command name", "success", "fails", "success rate")

SUCCESS_RATE = "success rate"

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
    return re.sub(r"\s+", " ", name.strip().lower())


def get_columns_values(headers: tuple[str, ...]) -> list[list[str]]:
    """Getter for list of starting values of columns_values

    Args:
        headers (tuple[str, ...]): first row

    Returns:
        list[list[str]]: list of starting values of columns_values
    """
    return [[column_header] for column_header in headers]

def fill_columns_values(storage: dict[int, Product], columns_values: list[list[str]]) -> None:
    """Fill columns_values by values in storage

    Args:
        storage (dict[int, Product]): from what columns_values will be filled
        columns_values (list[list[str]]): what we fill
    """
    for product_id, product in storage.items():
        column_fields = (product_id, *product.values())
        for col_ind in range(len(column_fields)):
            columns_values[col_ind].append(str(column_fields[col_ind]))

def get_width_columns(columns_values: list[list[str]]) -> list[int]:
    """Getter for width of columns of str representation

    Args:
        columns_values (list[list[str]]): values of columns

    Returns:
        list[int]: list of widths of columns
    """
    return [len(max(column_values, key=len)) for column_values in columns_values]

def get_row_str_representation(first_row : int, last_row: int, columns_values: list[list[str]], width_columns: list[int]) -> str:
    """Get row representation by str

    Args:
        first_row (int): first row of representation
        last_row (int): last row of representation
        columns_values (list[list[str]]): values of columns
        width_columns (list[int]): list of widths of columns

    Returns:
        str: row representation
    """
    output_str: str = ""
    for row_ind in range(first_row, last_row + 1):
        output_str += "|"
        for col_ind in range(len(columns_values)):
            output_str += (
                f" {f'{columns_values[col_ind][row_ind]}':<{width_columns[col_ind]}} |"
            )
        output_str += "\n"
    return output_str

def get_dashe_separator_row(columns_values: list[list[str]], width_columns: list[int]) -> str:
    """_summary_

    Args:
        columns_values (list[list[str]]): values of columns
        width_columns (list[int]): list of widths of columns

    Returns:
        str: dashe separator row
    """
    output_str: str = "|"
    for col_ind in range(len(columns_values)):
        output_str += f"{'-' * (width_columns[col_ind] + 2)}|"
    output_str += "\n"
    return output_str

def get_str_representation(data: dict[Any, Any], headers: tuple[str, ...]) -> str:
    """Render the call statistics as a text table with data-sized columns.

    Args:
        data (dict[Any, Any]): text of table
        headers (tuple[str, ...]): first row

    Returns:
        str: 
            A multi-line string: a header row, a dashed separator row, then one
            row per registry entry in insertion order. When ``registry`` is
            empty only the header and separator rows are returned, sized to the
            header labels.
    """
    columns_values: list[list[str]] = get_columns_values(headers)
    fill_columns_values(data, columns_values)
    width_columns = get_width_columns(columns_values)
    output_str: str = ""
    output_str += get_row_str_representation(0, 0, columns_values, width_columns)
    output_str += get_dashe_separator_row(columns_values, width_columns)
    output_str += get_row_str_representation(1, len(data), columns_values, width_columns)
    return output_str.removesuffix("\n")


def get_storage_str_representation(storage: dict[int, Product]) -> str:
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
    return get_str_representation(storage, TABLE_HEADERS)

def get_success_rate(success_calls: int, fail_calls: int) -> int:
    """Getter for success rate

    Args:
        success_calls (int): quantity of success_calls
        fail_calls (int): quantity of fail_calls

    Returns:
        int: success rate
    """
    if not success_calls and not fail_calls:
        return f"{0:.2f}"
    return f"{success_calls / (success_calls + fail_calls) * 100:.2f}%"

def get_stats_str_representation(registry: Registry) -> str:
    """Render the call statistics as a text table with data-sized columns.

    The table has the columns named by :data:`STATS_TABLE_HEADERS` -- command
    name, number of successful calls, number of failed calls and success
    rate. It is laid out like the one from
    :func:`get_storage_str_representation`: every column is as wide as the
    longest value it carries, its header counted.

    Args:
        registry: The statistics to render, a mapping of command name to the
            counters kept by :func:`~src.part5.decorators.collect_stats`.

    Returns:
        A multi-line string: a header row, a dashed separator row, then one
        row per registry entry in insertion order. When ``registry`` is
        empty only the header and separator rows are returned, sized to the
        header labels.
    """
    update_registery = {
        crud_op : 
        stats | {SUCCESS_RATE : get_success_rate(stats[SUCCESS_KEY], stats[FAILS_KEY])} for crud_op, stats in registry.items()
    }
    
    return get_str_representation(update_registery, STATS_TABLE_HEADERS)
