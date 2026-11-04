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

TABUL: Final[int] = 45
INDENT: Final[str] = "  "

HELP_TEXT: Final[str] = (
    "Available commands:\n"
    + (INDENT + "help").ljust(TABUL)
    + "show this message\n"
    + (INDENT + "exit").ljust(TABUL)
    + "leave the console\n"
    + (INDENT + "show").ljust(TABUL)
    + "print the whole store as a table\n"
    + (INDENT + "create <name...> <price> <quantity>").ljust(TABUL)
    + "add a product, print its new id\n"
    + (INDENT + "read <id>").ljust(TABUL)
    + "print the product with that id\n"
    + (INDENT + "update <id> <name...> <price> <quantity>").ljust(TABUL)
    + "overwrite that product's fields\n"
    + (INDENT + "delete <id>").ljust(TABUL)
    + "remove the product with that id\n"
    + "\n"
    + "For create and update the price and quantity are the last two words of the\n"
    + "line; everything before them is the product name, so it may contain spaces\n"
    + '(for example "Gibson SG Junior") and needs no quoting.'
)


def show_help() -> None:
    print(HELP_TEXT)


def print_result(result: object) -> None:
    if result is not None:
        print(result)


def run_command(
    storage: dict[str, Product], product_names: set[str], line: str
) -> bool:
    line_array = line.split()
    match line_array:
        case ["exit"]:
            return False
        case ["help"]:
            show_help()
            return True
        case ["show"]:
            print(get_storage_str_representation(storage))
            return True
        case ["create", *name, price_str, quantity_str] if name:
            name_ = " ".join(name)
            price = Decimal(price_str)
            quantity = int(quantity_str)

            fields = {NAME_KEY: name_, PRICE_KEY: price, QUANTITY_KEY: quantity}

            print_result(create_product(storage, product_names, fields))
            return True

        case ["read", product_id]:
            print_result(read_product(storage, product_id))
            return True

        case ["update", product_id, *name, price_str, quantity_str] if name:
            name_ = " ".join(name)

            price = Decimal(price_str)
            quantity = int(quantity_str)

            fields = {NAME_KEY: name_, PRICE_KEY: price, QUANTITY_KEY: quantity}
            print_result(update_product(storage, product_names, product_id, fields))
            return True

        case ["delete", product_id]:
            print_result(delete_product(storage, product_names, product_id))
            return True

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
