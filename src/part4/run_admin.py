"""Interactive admin console for the part4 in-memory product store.

Running this module starts a read-eval-print loop over a single product
store that lives in memory for the lifetime of the process. Every line
typed at the prompt is stripped of surrounding whitespace and matched,
with a ``match`` statement, against the set of known commands:

* ``help`` -- print the list of commands and what each one does;
* ``exit`` -- leave the loop and end the program;
* ``show`` -- print the whole store as a text table;
* ``create <name...> <price> <quantity>`` -- add a product;
* ``read <id>`` -- print one product;
* ``update <id> <name...> <price> <quantity>`` -- overwrite a product;
* ``delete <id>`` -- remove a product.

For ``create`` and ``update`` the price and quantity are always the last
two words of the line; everything between the verb (and, for ``update``,
the id) and those two words is joined with single spaces into the
product name, so a multi-word name such as ``Gibson SG Junior`` needs no
quoting.

The four CRUD commands forward to :mod:`src.part4.crud`; whatever
that call returns is printed unless it is ``None``. A line whose first
word is not a known verb, or that carries the wrong number of arguments
for its verb, prints an "is not a command" notice. A line that names a
command correctly but whose price or quantity argument will not parse
prints a distinct "arguments are invalid" notice. Either way the store
is left untouched and the loop keeps running; only ``exit`` stops it.
"""

from decimal import Decimal, InvalidOperation
from typing import Any, Final

from .crud import (
    create_product,
    delete_product,
    read_product,
    update_product,
)
from .storage import NAME_KEY, PRICE_KEY, QUANTITY_KEY, Product
from .utils import get_storage_str_representation


PROMPT: Final[str] = "admin>"
HELP_TEXT: Final[str] = """
    Available commands:
  help                                       show this message
  exit                                       leave the console
  show                                       print the whole store as a table
  create <name...> <price> <quantity>        add a product, print its new id
  read <id>                                  print the product with that id
  update <id> <name...> <price> <quantity>   overwrite that product's fields
  delete <id>                                remove the product with that id

For create and update the price and quantity are the last two words of the line;
everything before them is the product name, so it may contain spaces
(for example "Gibson SG Junior") and needs no quoting."""


def show_help() -> None:
    print(HELP_TEXT)


def print_result(result: object) -> None:
    if result is not None:
        print(result)


def create_fields(name: list[str], s_price: str, s_quantity: str) -> dict[str, Any]:
    return {
        NAME_KEY: " ".join(name),
        PRICE_KEY: Decimal(s_price),
        QUANTITY_KEY: int(s_quantity),
    }


def run_command(
    storage: dict[str, Product], product_names: set[str], line: str
) -> bool:
    command = line.split()
    match command:
        case ["help"]:
            show_help()

        case ["exit"]:
            return False
        case ["show"]:
            print(get_storage_str_representation(storage))

        case ["create", *name, s_price, s_quantity]:
            fields = create_fields(name, s_price, s_quantity)
            print_result(create_product(storage, product_names, fields))

        case ["read", s_product_id]:
            print_result(read_product(storage, s_product_id))

        case ["update", s_product_id, *name, s_price, s_quantity]:
            fields = create_fields(name, s_price, s_quantity)
            print_result(update_product(storage, product_names, s_product_id, fields))

        case ["delete", s_product_id]:
            print_result(delete_product(storage, product_names, s_product_id))

        case _:
            print(f"{line} is not a command")
    return True


def main() -> None:

    storage: dict[str, Product] = {}
    product_names: set[str] = set()
    running = True

    while running:
        line = input(PROMPT).strip()

        try:
            running = run_command(storage, product_names, line)

        except (ValueError, InvalidOperation):
            print(f"{line!r} names a command but its arguments are invalid")


if __name__ == "__main__":
    main()
