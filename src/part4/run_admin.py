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


def run_command(
    storage: dict[str, Product], product_names: set[str], line: str
) -> bool:
    parts = line.split()
    if not parts:
        print(f"'{line}' is not a command")
        return True

    cmd = parts[0]
    n = len(parts)

    if cmd == "help" and n == 1:
        show_help()
        return True

    if cmd == "exit" and n == 1:
        return False

    if cmd == "show" and n == 1:
        print(get_storage_str_representation(storage))
        return True

    if cmd == "read" and n == 2:
        print_result(read_product(storage, parts[1]))
        return True

    if cmd == "delete" and n == 2:
        print_result(delete_product(storage, product_names, parts[1]))
        return True

    if cmd == "create" and n >= 4:
        fields = {
            NAME_KEY: " ".join(parts[1:-2]),
            PRICE_KEY: Decimal(parts[-2]),
            QUANTITY_KEY: int(parts[-1]),
        }
        print_result(create_product(storage, product_names, fields))
        return True

    if cmd == "update" and n >= 5:
        fields = {
            NAME_KEY: " ".join(parts[2:-2]),
            PRICE_KEY: Decimal(parts[-2]),
            QUANTITY_KEY: int(parts[-1]),
        }

        print_result(update_product(storage, product_names, parts[1], fields))

        return True
    print(f"'{line}' is not a command")
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
