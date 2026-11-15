"""Interactive admin console for the part5 in-memory product store.

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
* ``delete <id>`` -- remove a product;
* ``stats`` -- print how many times each CRUD command succeeded and failed,
  with its success rate, as a text table.

For ``create`` and ``update`` the price and quantity are always the last
two words of the line; everything between the verb (and, for ``update``,
the id) and those two words is joined with single spaces into the
product name, so a multi-word name such as ``Gibson SG Junior`` needs no
quoting.

The four CRUD commands forward to :mod:`src.part5.crud`; whatever
that call returns is printed unless it is ``None``. ``create`` hands
:func:`~src.part5.crud.generate_snowflake_id` to the CRUD layer as the
source of the new product's identifier; the ``<id>`` typed for ``read``,
``update`` and ``delete`` is converted to an integer before it is looked
up. The counters behind ``stats`` are collected by the CRUD layer itself
(:data:`~src.part5.crud.STATS_REGISTRY`); a command whose arguments do
not parse never reaches it and is not counted. A line whose first
word is not a known verb, or that carries the wrong number of arguments
for its verb, prints an "is not a command" notice. A line that names a
command correctly but whose id, price or quantity argument will not parse
prints a distinct "arguments are invalid" notice. Either way the store
is left untouched and the loop keeps running; only ``exit`` stops it.
"""

from decimal import Decimal, InvalidOperation
from typing import Final

from .storage import NAME_KEY, PRICE_KEY, QUANTITY_KEY, Product
from .crud import (
    STATS_REGISTRY,
    create_product,
    delete_product,
    generate_snowflake_id,
    read_product,
    update_product,
)
from .utils import (
    get_stats_str_representation,
    get_storage_str_representation,
)



PROMPT: Final[str] = "> "
HELP_TEXT: Final[str] = (
    "Available commands:\n"
    "  help                                       show this message\n"
    "  exit                                       leave the console\n"
    "  show                                       print the whole store as a table\n"
    "  create <name...> <price> <quantity>        add a product, print its new id\n"
    "  read <id>                                  print the product with that id\n"
    "  update <id> <name...> <price> <quantity>   overwrite that product's fields\n"
    "  delete <id>                                remove the product with that id\n"
    "  stats                                      print call statistics of the CRUD commands\n"
    "\n"
    "For create and update the price and quantity are the last two words of the\n"
    "line; everything before them is the product name, so it may contain spaces\n"
    "(for example \"Gibson SG Junior\") and needs no quoting."
)


def show_help() -> None:
    print(HELP_TEXT)


def print_result(result: object) -> None:
   if result is not None:
       print(result)


def run_command(
    storage: dict[int, Product], product_names: set[str], line: str
) -> bool:
    match line.split():
        case ["help"]:
            show_help()
        case ["exit"]:
            return False
        case ["show"]:
            print(get_storage_str_representation(storage))
        case ["stats"]:
            print(get_stats_str_representation(STATS_REGISTRY))
        case ["create", *args] if len(args) >= 3:
            fields = {
                NAME_KEY: " ".join(args[:-2]),
                PRICE_KEY: Decimal(args[-2]),
                QUANTITY_KEY: int(args[-1]),
            }
            print_result(
                create_product(
                    storage, product_names, fields, generate_snowflake_id
                )
            )
        case ["read", id_str]:
            print_result(read_product(storage, int(id_str)))
        case ["update", id_str, *args] if len(args) >= 3:
            fields = {
                NAME_KEY: " ".join(args[:-2]),
                PRICE_KEY: Decimal(args[-2]),
                QUANTITY_KEY: int(args[-1]),
            }
            print_result(
                update_product(storage, product_names, int(id_str), fields)
            )
        case ["delete", id_str]:
            print_result(delete_product(storage, product_names, int(id_str)))
        case _:
            print(f"{line!r} is not a command")
    return True


def main() -> None:
    storage: dict[int, Product] = {}
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
