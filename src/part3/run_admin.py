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


PROMPT: Final[str] = "admin>"
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
(for example "Gibson SG Junior") and needs no quoting.
"""


def show_help() -> None:
    print(HELP_TEXT)


def print_result(result: object) -> None:
    if result is not None:
        print(result)
        return
    return


def run_command(storage: list[Product], line: str) -> bool:
    input_line = line.strip()
    match input_line.split():
        case ["help"]:
            show_help()
            return True

        case ["exit"]:
            return False

        case ["show"]:
            print_result(get_storage_str_representation(storage))
            return True

        case ["create", first_name_part, *rest_name, price, quantity]:
            name = [first_name_part] + rest_name
            fields = (" ".join(name), Decimal(price), int(quantity))
            print_result(create_product(storage, fields))
            return True

        case ["read", product_id]:
            print_result(read_product(storage, int(product_id)))
            return True

        case ["update", product_id, first_name_part, *rest_name, price, quantity]:
            name = [first_name_part] + rest_name
            fields = (" ".join(name), Decimal(price), int(quantity))
            print_result(update_product(storage, int(product_id), fields))
            return True

        case ["delete", product_id]:
            print_result(delete_product(storage, int(product_id)))
            return True

        case _:
            print(f"'{input_line}' is not a command")
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
