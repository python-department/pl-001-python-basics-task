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
    words = line.split()
    if not words:
        return True

    command = words[0]

    if command == "help" and len(words) == 1:
        show_help()
        return True

    if command == "exit" and len(words) == 1:
        return False

    if command == "show" and len(words) == 1:
        print_result(get_storage_str_representation(storage))
        return True

    if command == "create":
        if len(words) < 4:
            print(f"{line!r} is not a command")
            return True
        name = " ".join(words[1:-2])
        price = Decimal(words[-2])
        quantity = int(words[-1])
        print_result(create_product(storage, (name, price, quantity)))
        return True

    if command == "read":
        if len(words) != 2:
            print(f"{line!r} is not a command")
            return True
        product_id = int(words[1])
        print_result(read_product(storage, product_id))
        return True

    if command == "update":
        if len(words) < 5:
            print(f"{line!r} is not a command")
            return True
        product_id = int(words[1])
        name = " ".join(words[2:-2])
        price = Decimal(words[-2])
        quantity = int(words[-1])
        print_result(update_product(storage, product_id, (name, price, quantity)))
        return True

    if command == "delete":
        if len(words) != 2:
            print(f"{line!r} is not a command")
            return True
        product_id = int(words[1])
        print_result(delete_product(storage, product_id))
        return True

    print(f"{line!r} is not a command")
    return True


def main() -> None:
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
