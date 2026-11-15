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
HELP_TEXT: Final[str] = (
    "Available commands:\n"
    "  help                                       show this message\n"
    "  exit                                       leave the console\n"
    "  show                                       print the whole store as a table\n"
    "  create <name...> <price> <quantity>        add a product, print its new id\n"
    "  read <id>                                  print the product with that id\n"
    "  update <id> <name...> <price> <quantity>   overwrite that product's fields\n"
    "  delete <id>                                remove the product with that id\n"
    "\n"
    "For create and update the price and quantity are the last two words of the\n"
    "line; everything before them is the product name, so it may contain spaces\n"
    '(for example "Gibson SG Junior") and needs no quoting.'
)


def show_help() -> None:
    print(HELP_TEXT)


def print_result(result: object) -> None:
    if result is not None:
        print(result)


def run_command(
    storage: dict[str, Product],
    product_names: set[str],
    line: str,
) -> bool:
    commands = line.split()

    match commands:
        case ["help"]:
            show_help()
            return True
        case ["exit"]:
            return False
        case ["show"]:
            print_result(get_storage_str_representation(storage))
            return True
        case ["read", product_id]:
            print_result(read_product(storage, product_id))
            return True
        case ["delete", product_id]:
            print_result(delete_product(storage, product_names, product_id))
            return True
        case ["update", product_id, *args] if len(args) >= 3:
            name = " ".join(args[:-2])
            price = Decimal(args[-2])
            quantity = int(args[-1])
            print_result(
                update_product(
                    storage,
                    product_names,
                    product_id,
                    {NAME_KEY: name, PRICE_KEY: price, QUANTITY_KEY: quantity},
                )
            )
            return True
        case ["create", *args] if len(args) >= 3:
            name = " ".join(args[:-2])
            price = Decimal(args[-2])
            quantity = int(args[-1])
            print_result(
                create_product(
                    storage,
                    product_names,
                    {NAME_KEY: name, PRICE_KEY: price, QUANTITY_KEY: quantity},
                )
            )
            return True
        case _:
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
