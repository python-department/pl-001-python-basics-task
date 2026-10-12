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
    parts = line.split()

    if parts == ["exit"]:
        return False

    if parts == ["help"]:
        show_help()
        return True

    if parts == ["show"]:
        print(get_storage_str_representation(storage))
        return True

    if len(parts) == 1 and parts[0] in {"create", "read", "update", "delete"}:
        print(f"{line!r} is not a command")
        return True

    command = parts[0] if parts else ""

    if command == "create" and len(parts) >= 4:
        name = " ".join(parts[1:-2])
        price = Decimal(parts[-2])
        quantity = int(parts[-1])

        created_id = create_product(storage, (name, price, quantity))
        print_result(created_id)

    elif command == "read" and len(parts) == 2:
        product_id = int(parts[1])
        product = read_product(storage, product_id)
        print_result(product)

    elif command == "update" and len(parts) >= 5:
        product_id = int(parts[1])
        name = " ".join(parts[2:-2])
        price = Decimal(parts[-2])
        quantity = int(parts[-1])

        updated_product = update_product(
            storage,
            product_id,
            (name, price, quantity),
        )
        print_result(updated_product)

    elif command == "delete" and len(parts) == 2:
        product_id = int(parts[1])
        deleted_id = delete_product(storage, product_id)
        print_result(deleted_id)

    else:
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
