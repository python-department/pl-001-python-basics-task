from decimal import Decimal, InvalidOperation
from typing import Any, Final

from .crud import create_product, delete_product, read_product, update_product
from .storage import NAME_KEY, PRICE_KEY, QUANTITY_KEY, Product
from .utils import get_storage_str_representation

PROMPT: Final = "admin> "
HELP_TEXT: Final = (
    "Available commands:\n"
    "  help                                       show this message\n"
    "  exit                                       leave the console\n"
    "  show                                       print the whole store as a table\n"
    "  create <name...> <price> <quantity>        add a product, print its new id\n"
    "  read <id>                                  print the product with that id\n"
    "  update <id> <name...> <price> <quantity>   overwrite that product's fields\n"
    "  delete <id>                                remove the product with that id\n\n"
    "For create and update the price and quantity are the last two words of the\n"
    "line; everything before them is the product name, so it may contain spaces\n"
    '(for example "Gibson SG Junior") and needs no quoting.'
)


def show_help() -> None:
    print(HELP_TEXT)


def print_result(result: Any) -> None:
    if result is not None:
        print(result)


def run_command(
    storage: dict[str, Product], product_names: set[str], line: str
) -> bool:
    words = line.split()
    if not words:
        print(f"{line!r} is not a command")
        return True

    cmd = words[0]

    if cmd == "help" and len(words) == 1:
        show_help()
        return True

    if cmd == "exit" and len(words) == 1:
        return False

    if (cmd == "show" or cmd == "list") and len(words) == 1:
        print_result(get_storage_str_representation(storage))
        return True

    if cmd == "read" and len(words) == 2:
        product_id = words[1]
        print_result(read_product(storage, product_id))
        return True

    if cmd == "delete" and len(words) == 2:
        product_id = words[1]
        print_result(delete_product(storage, product_names, product_id))
        return True

    if cmd == "create" and len(words) >= 4:
        name = " ".join(words[1:-2])
        price = Decimal(words[-2])
        qty = int(words[-1])
        fields = {
            NAME_KEY: name,
            PRICE_KEY: price,
            QUANTITY_KEY: qty,
        }
        print_result(create_product(storage, product_names, fields))
        return True

    if cmd == "update" and len(words) >= 5:
        product_id = words[1]
        name = " ".join(words[2:-2])
        price = Decimal(words[-2])
        qty = int(words[-1])
        fields = {
            NAME_KEY: name,
            PRICE_KEY: price,
            QUANTITY_KEY: qty,
        }
        print_result(update_product(storage, product_names, product_id, fields))
        return True

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