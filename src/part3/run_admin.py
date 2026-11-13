from decimal import Decimal
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
    if result:
        print(result)


def run_command(storage: list[Product], line: str) -> bool:
    words = line.split()
    match words:
        case ["help"]:
            show_help()
            return True
        case ["exit"]:
            return False
        case ["show"]:
            get_storage_str_representation(storage)
            return True
        case [
            "create",
            *_,
            price,
            quantity,
        ]:
            name = " ".join(words[1:-2])
            pocket_create = create_product(
                storage, (name, Decimal(price), int(quantity))
            )
            if pocket_create:
                print(pocket_create)
            return True
        case ["read", id_num]:
            output = read_product(storage, int(id_num))
            if output:
                print(output)
            return True
        case [
            "update",
            id_num,
            *_,
            price,
            quantity,
        ]:
            name = " ".join(words[2:-2])
            pocket_update = update_product(
                storage, int(id_num), (name, Decimal(price), int(quantity))
            )
            if pocket_update:
                print(pocket_update)
            return True
        case ["delete", id_num]:
            pocket_delete = delete_product(storage, int(id_num))
            if pocket_delete:
                print(pocket_delete)
            return True
        case _:
            sentance = " ".join(words)
            print(f"'{sentance}' is not a command")
            return True


def main() -> None:

    storage: list[Product] = []
    running = True

    while running:
        line = input(PROMPT).strip()

        try:
            running = run_command(storage, line)

        except ValueError:
            print(f"{line!r} names a command but its arguments are invalid")


if __name__ == "__main__":
    main()
