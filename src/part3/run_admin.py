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


# TODO: задайте приглашение и текст справки
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
    if result != None:
        print(result)
        return
    else:
        return


def run_command(storage: list[Product], line: str) -> bool:
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
            try:
                price = Decimal(price_str)
                quantity = int(quantity_str)
            except (InvalidOperation, ValueError):
                print(f"{line} is not a command")
                return True
            print_result(
                create_product(storage, (str(name_), Decimal(price), int(quantity)))
            )
            return True

        case ["read", product_id_str]:
            try:
                product_id = int(product_id_str)
            except ValueError:
                print(f"{line} is not a command")
                return True
            print_result(read_product(storage, product_id))
            return True

        case ["update", product_id_str, *name, price_str, quantity_str] if name:
            name_ = " ".join(name)
            try:
                product_id = int(product_id_str)
                price = Decimal(price_str)
                quantity = int(quantity_str)
            except (InvalidOperation, ValueError):
                print(f"{line} is not a command")
                return True
            print_result(update_product(storage, product_id, (name_, price, quantity)))
            return True

        case ["delete", product_id_str]:
            try:
                product_id = int(product_id_str)
            except ValueError:
                print(f"{line} is not a command")
                return True
            print_result(delete_product(storage, product_id))
            return True

        case _:
            print(f"{line} is not a command")
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
