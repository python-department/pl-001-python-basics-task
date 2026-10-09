"""Interactive admin console for the part3 in-memory product store."""

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
HELP_TEXT: Final[str] = (
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
    "(for example \"Gibson SG Junior\") and needs no quoting."
)


def show_help() -> None:
    """Print the command reference to stdout."""
    print(HELP_TEXT)


def print_result(result: object) -> None:
    """Print a CRUD result to stdout unless it is ``None``."""
    if result is not None:
        print(result)


def run_command(storage: list[Product], line: str) -> bool:
    """Parse one console line and carry out the command it names."""
    words = line.split()
    if not words:
        print(f"'{line}' is not a command")
        return True

    command = words[0]

    if command == "exit":
        if len(words) != 1:
            print(f"'{line}' is not a command")
            return True
        return False

    elif command == "help":
        if len(words) != 1:
            print(f"'{line}' is not a command")
            return True
        show_help()
        return True

    elif command == "show":
        if len(words) != 1:
            print(f"'{line}' is not a command")
            return True
        print(get_storage_str_representation(storage))
        return True

    elif command == "read":
        if len(words) != 2:
            print(f"'{line}' is not a command")
            return True
        product_id = int(words[1])
        res = read_product(storage, product_id)
        print_result(res)
        return True

    elif command == "delete":
        if len(words) != 2:
            print(f"'{line}' is not a command")
            return True
        product_id = int(words[1])
        res = delete_product(storage, product_id)
        print_result(res)
        return True

    elif command == "create":
        # Минимум: 'create', одно слово имени, цена, количество (итого 4 слова)
        if len(words) < 4:
            print(f"'{line}' is not a command")
            return True
        quantity = int(words[-1])
        price = Decimal(words[-2])
        name = " ".join(words[1:-2])
        res = create_product(storage, (name, price, quantity))
        print_result(res)
        return True

    elif command == "update":
        # Минимум: 'update', id, одно слово имени, цена, количество (итого 5 слов)
        if len(words) < 5:
            print(f"'{line}' is not a command")
            return True
        product_id = int(words[1])
        quantity = int(words[-1])
        price = Decimal(words[-2])
        name = " ".join(words[2:-2])
        res = update_product(storage, product_id, (name, price, quantity))
        print_result(res)
        return True

    else:
        print(f"'{line}' is not a command")
        return True


def main() -> None:
    """Run the admin console until the ``exit`` command is entered."""
    storage: list[Product] = []
    running = True

    while running:
        try:
            line = input(PROMPT).strip()
        except EOFError:
            break

        try:
            running = run_command(storage, line)
        except (ValueError, InvalidOperation):
            print(f"{line!r} names a command but its arguments are invalid")


if __name__ == "__main__":
    main()
