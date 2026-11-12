from decimal import Decimal, InvalidOperation
from typing import Final

from .crud import create_product, delete_product, read_product, update_product
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
    parts = line.split()
    cmd = parts[0] if parts else ""

    if cmd == "help" and len(parts) == 1:
        show_help()
    elif cmd == "exit" and len(parts) == 1:
        return False
    elif cmd == "show" and len(parts) == 1:
        print(get_storage_str_representation(storage))
    elif cmd == "create" and len(parts) >= 4:
        result = create_product(
            storage,
            (" ".join(parts[1:-2]), Decimal(parts[-2]), int(parts[-1])),
        )
        print_result(result)
    elif cmd == "read" and len(parts) == 2:
        print_result(read_product(storage, int(parts[1])))
    elif cmd == "update" and len(parts) >= 5:
        result = update_product(
            storage,
            int(parts[1]),
            (" ".join(parts[2:-2]), Decimal(parts[-2]), int(parts[-1])),
        )
        print_result(result)
    elif cmd == "delete" and len(parts) == 2:
        print_result(delete_product(storage, int(parts[1])))
    else:
        print(f"'{line}' is not a command")

    return True


def main() -> None:
    storage: list[Product] = []
    while True:
        line = input(PROMPT).strip()
        try:
            if not run_command(storage, line):
                break
        except (ValueError, InvalidOperation):
            print(f"'{line}' names a command but its arguments are invalid")


if __name__ == "__main__":
    main()