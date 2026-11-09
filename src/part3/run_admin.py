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


def show_help() -> None:
    print(HELP_TEXT)


def print_result(result: object) -> None:
    if result is not None:
        print(result)


def run_command(storage: list[Product], line: str) -> bool:
    parts = line.split()
    if not parts:
        print(f"'{line}' is not a command")
        return True
    cmd = parts[0]

    if cmd == "help" and len(parts) == 1:
        show_help()
        return True
    elif cmd == "exit" and len(parts) == 1:
        return False
    elif cmd == "show" and len(parts) == 1:
        print(get_storage_str_representation(storage))
        return True
    elif cmd == "read" and len(parts) == 2:
        pid = int(parts[1])
        res = read_product(storage, pid)
        print_result(res)
        return True
    elif cmd == "delete" and len(parts) == 2:
        pid = int(parts[1])
        res1 = delete_product(storage, pid)
        print_result(res1)
        return True
    elif cmd == "create" and len(parts) >= 4:
        qty = int(parts[-1])
        price = Decimal(parts[-2])
        name = " ".join(parts[1:-2])
        res2 = create_product(storage, (name, price, qty))
        print_result(res2)
        return True
    elif cmd == "update" and len(parts) >= 5:
        pid = int(parts[1])
        qty = int(parts[-1])
        price = Decimal(parts[-2])
        name = " ".join(parts[2:-2])
        res3 = update_product(storage, pid, (name, price, qty))
        print_result(res3)
        return True
    print(f"'{line}' is not a command")
    return True


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
