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
  help                                      show this message
  exit                                      leave the console
  show                                      print the whole store as a table
  create <name...> <price> <quantity>       add a product, print its new id
  read <id>                                 print the product with that id
  update <id> <name...> <price> <quantity>  overwrite that product's fields
  delete <id>                               remove the product with that id

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

    match parts:
        case ["help"]:
            show_help()

        case ["exit"]:
            return False

        case ["show"]:
            print(get_storage_str_representation(storage))

        case ["create", *args] if len(args) >= 3:
            name = " ".join(args[:-2])
            price = Decimal(args[-2])
            quantity = int(args[-1])
            print_result(create_product(storage, (name, price, quantity)))

        case ["read", product_id]:
            print_result(read_product(storage, int(product_id)))

        case ["update", product_id, *args] if len(args) >= 3:
            name = " ".join(args[:-2])
            price = Decimal(args[-2])
            quantity = int(args[-1])
            result = update_product(
                storage,
                int(product_id),
                (name, price, quantity),
            )
            print_result(result)

        case ["delete", product_id]:
            print_result(delete_product(storage, int(product_id)))

        case _:
            print(f"'{line}' is not a command")

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
