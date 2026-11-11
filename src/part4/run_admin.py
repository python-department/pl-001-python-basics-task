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
(for example "Gibson SG Junior") and needs no quoting.
"""


def show_help() -> None:
    print(HELP_TEXT)


def print_result(result: object) -> None:
    if result is not None:
        print(result)


def run_command(
    storage: dict[str, Product], product_names: set[str], line: str
) -> bool:
    splitted_line = line.split()

    if not splitted_line:
        print(f"'{line}' is not a command")
        return True

    match splitted_line.pop(0):
        case "help" if not splitted_line:
            show_help()
            return True
        case "exit" if not splitted_line:
            return False
        case "show" if not splitted_line:
            print(get_storage_str_representation(storage))
            return True
        case "create" if len(splitted_line) >= 3:
            print_result(
                create_product(
                    storage,
                    product_names,
                    {
                        NAME_KEY: " ".join(splitted_line[:-2]),
                        PRICE_KEY: Decimal(splitted_line[-2]),
                        QUANTITY_KEY: int(splitted_line[-1]),
                    },
                )
            )
            return True
        case "update" if len(splitted_line) >= 4:
            print_result(
                update_product(
                    storage,
                    product_names,
                    splitted_line[0],
                    {
                        NAME_KEY: " ".join(splitted_line[1:-2]),
                        PRICE_KEY: Decimal(splitted_line[-2]),
                        QUANTITY_KEY: int(splitted_line[-1]),
                    },
                )
            )
            return True
        case "read" if len(splitted_line) == 1:
            print_result(read_product(storage, splitted_line[0]))
            return True
        case "delete" if len(splitted_line) == 1:
            print_result(delete_product(storage, product_names, splitted_line[0]))
            return True
        case _:
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
