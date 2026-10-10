from decimal import Decimal, InvalidOperation  # noqa: F401
from typing import Final

from .crud import (  # noqa: F401
    create_product,
    delete_product,
    read_product,
    update_product,
)
from .storage import Product
from .utils import get_storage_str_representation  # noqa: F401


# TODO: задайте приглашение и текст справки
PROMPT: Final[str] = "admin> "
HELP_TEXT: Final[str] =  '''
  Available commands:
    help                                       show this message
    exit                                       leave the console
    show                                       print the whole store as a table
    create <name...> <price> <quantity>        add a product, print its new id
    read <id>                                  print the product with that id
    update <id> <name...> <price> <quantity>   overwrite that product's fields
    delete <id>                                remove the product with that id

  For create and update the price and quantity are the last two words of the
  line; everything before them is the product name, so it may contain spaces
  (for example "Gibson SG Junior") and needs no quoting.
  '''


def show_help() -> None:
    print(HELP_TEXT)


def print_result(result: object) -> None:
    if result:
        print(result)


def run_command(storage: list[Product], line: str) -> bool:
    match line.split():
        case ["help"]:
            show_help()
        case ["exit"]:
            return False
        case ["show"]:
            print(get_storage_str_representation(storage))
        case ["create", *name, price, quantity]:
            fields = (' '.join(name), Decimal(price), int(quantity))
            print_result(create_product(storage, fields))
        case ["read", product_id]:
            print_result(read_product(storage, int(product_id)))
        case ["update", product_id, *name, price, quantity]:
            fields = (' '.join(name), Decimal(price), int(quantity))
            print_result(update_product(storage, int(product_id), fields))
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
