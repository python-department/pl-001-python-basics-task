"""Interactive admin console for the part3 in-memory product store.

Running this module starts a read-eval-print loop over a single product
store that lives in memory for the lifetime of the process. Every line
typed at the prompt is stripped of surrounding whitespace and matched
against the set of known commands:

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

The four CRUD commands forward to :mod:`src.part3.crud`; whatever
that call returns is printed unless it is ``None``. A line whose first
word is not a known verb, or that carries the wrong number of arguments
for its verb, prints an "is not a command" notice. A line that names a
command correctly but whose id, price or quantity argument will not
parse prints a distinct "arguments are invalid" notice. Either way the
store is left untouched and the loop keeps running; only ``exit`` stops
it.
"""

from collections.abc import Callable
from decimal import Decimal, InvalidOperation
from typing import Final

from .crud import (
    create_product,
    delete_product,
    read_product,
    update_product,
)
from .storage import Product
from .utils import get_storage_str_representation


PROMPT: Final[str] = "admin> "
HELP_TEXT: Final[str] = """Available commands:
  help                                       show this message
  exit                                       leave the console
  show                                       print the whole store as a table
  create <name...> <price> <quantity>        add a product, print its new id
  read <id>                                  print the product with that id
  update <id> <name...> <price> <quantity>   overwrite that product's fields
  delete <id>                                remove the product with that id

For create and update the price and quantity are the last two words of the
line; everything before them is the product name, so it may contain spaces
(for example "Gibson SG Junior") and needs no quoting."""

_NAME_AND_TWO_NUMBERS: Final = 3
_ID_AND_NAME_AND_TWO_NUMBERS: Final = 4
_VARIADIC: Final = frozenset({"create", "update"})


def show_help() -> None:
    print(HELP_TEXT)


def print_result(result: object) -> None:
    if result is not None:
        print(result)


def _parse_fields(args: list[str]) -> tuple[str, Decimal, int]:
    name = " ".join(args[:-2])
    price = Decimal(args[-2])
    quantity = int(args[-1])
    return name, price, quantity


def _run_read(storage: list[Product], args: list[str]) -> None:
    print_result(read_product(storage, int(args[0])))


def _run_delete(storage: list[Product], args: list[str]) -> None:
    print_result(delete_product(storage, int(args[0])))


def _run_create(storage: list[Product], args: list[str]) -> None:
    print_result(create_product(storage, _parse_fields(args)))


def _run_update(storage: list[Product], args: list[str]) -> None:
    product_id = int(args[0])
    fields = _parse_fields(args[1:])
    print_result(update_product(storage, product_id, fields))


def _run_show(storage: list[Product], args: list[str]) -> None:
    print(get_storage_str_representation(storage))


def _run_help(storage: list[Product], args: list[str]) -> None:
    show_help()


def _run_exit(storage: list[Product], args: list[str]) -> bool | None:
    return False


type _Handler = Callable[[list[Product], list[str]], bool | None]


_COMMANDS: Final[dict[str, tuple[_Handler, int | None]]] = {
    "help": (_run_help, 0),
    "exit": (_run_exit, 0),
    "show": (_run_show, 0),
    "read": (_run_read, 1),
    "delete": (_run_delete, 1),
    "create": (_run_create, _NAME_AND_TWO_NUMBERS),
    "update": (_run_update, _ID_AND_NAME_AND_TWO_NUMBERS),
}


def _accepts(verb: str, args: list[str]) -> bool:
    _, arity = _COMMANDS[verb]
    if arity is None:
        return True
    if verb in _VARIADIC:
        return len(args) >= arity
    return len(args) == arity


def run_command(storage: list[Product], line: str) -> bool:
    words = line.split()
    verb = words[0] if words else ""

    if verb not in _COMMANDS or not _accepts(verb, words[1:]):
        print(f"'{line}' is not a command")
        return True

    handler, _ = _COMMANDS[verb]
    return handler(storage, words[1:]) is not False


def main() -> None:
    """Run the admin console until the ``exit`` command is entered.

    A single product store is created empty and kept in memory for the
    whole session. Each iteration reads one line from stdin, strips its
    surrounding whitespace and hands it to :func:`run_command`. A line
    that names a command but whose id, price or quantity argument does
    not parse is caught here and reported without stopping the loop; only
    ``exit`` ends it.
    """
    storage: list[Product] = []
    running = True

    while running:
        line = input(PROMPT).strip()

        try:
            running = run_command(storage, line)

        except (ValueError, InvalidOperation):
            print(f"{line!r} names a command but its arguments are invalid")


if __name__ == "__main__":
    main()
