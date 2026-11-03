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
from typing import Final

from .crud import (
    create_product,
    delete_product,
    read_product,
    update_product,
)
from .storage import NAME_KEY, PRICE_KEY, QUANTITY_KEY, Product
from .utils import get_storage_str_representation


PROMPT: Final[str] = "> "
HELP_TEXT: Final[str] = (
    "Commands:\n"
    "  help                                              -- show this help\n"
    "  exit                                              -- quit\n"
    "  show                                              -- show the store\n"
    "  create <name...> <price> <quantity>              -- add a product\n"
    "  read <id>                                         -- show a product\n"
    "  update <id> <name...> <price> <quantity>          -- update a product\n"
    "  delete <id>                                       -- remove a product\n"
    "Multi-word names need no quoting: the price and quantity are the last two words."
)


def show_help() -> None:
    print(HELP_TEXT)


def print_result(result: object) -> None:
    if result is not None:
        print(result)


def run_command(
    storage: dict[str, Product], product_names: set[str], line: str
) -> bool:
    parts = line.split()
    if not parts:
        print(f"{line!r} is not a command")
        return True

    command = parts[0]

    match command:
        case "help" if len(parts) == 1:
            show_help()
        case "exit" if len(parts) == 1:
            return False
        case "show" if len(parts) == 1:
            print(get_storage_str_representation(storage))
        case "create" if len(parts) >= 4:
            *name_parts, price_str, quantity_str = parts[1:]
            fields = {
                NAME_KEY: " ".join(name_parts),
                PRICE_KEY: Decimal(price_str),
                QUANTITY_KEY: int(quantity_str),
            }
            print_result(create_product(storage, product_names, fields))
        case "read" if len(parts) == 2:
            print_result(read_product(storage, parts[1]))
        case "update" if len(parts) >= 5:
            product_id = parts[1]
            *name_parts, price_str, quantity_str = parts[2:]
            fields = {
                NAME_KEY: " ".join(name_parts),
                PRICE_KEY: Decimal(price_str),
                QUANTITY_KEY: int(quantity_str),
            }
            print_result(update_product(storage, product_names, product_id, fields))
        case "delete" if len(parts) == 2:
            print_result(delete_product(storage, product_names, parts[1]))
        case _:
            if command in ("help", "exit", "show", "create", "read", "update", "delete"):
                print(f"{line!r} names a command but its arguments are invalid")
            else:
                print(f"{line!r} is not a command")
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
