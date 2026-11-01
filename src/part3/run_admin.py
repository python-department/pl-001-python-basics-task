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
HELP_TEXT: Final[str] = """
    Available commands:
  help                                       show this message
  exit                                       leave the console
  show                                       print the whole store as a table
  create <name...> <price> <quantity>        add a product, print its new id
  read <id>                                  print the product with that id
  update <id> <name...> <price> <quantity>   overwrite that product's fields
  delete <id>                                remove the product with that id

For create and update the price and quantity are the last two words of the line;
everything before them is the product name, so it may contain spaces
(for example "Gibson SG Junior") and needs no quoting."""


def show_help() -> None:
    print(HELP_TEXT)


def print_result(result: object) -> None:
    if result:
        print(result)


def run_command(storage: list[Product], line: str) -> bool:
    command = line.split()
    match command:
        case ["help"]:
            show_help()
            return True
        case ["exit"]:
            return False
        case ["show"]:
            print(get_storage_str_representation(storage))
            return True
        case ["create", name, s_price, s_quantity]:
            price = Decimal(s_price)
            quantity = int(s_quantity)
            fields = (name, price, quantity)
            res = create_product(storage, fields)
            if res:
                print(res)
            return True
        case ["read", s_product_id]:
            product_id = int(s_product_id)
            res_r = read_product(storage, product_id)
            if res_r:
                print(res_r)
            return True
        case ["update", s_product_id, name, s_price, s_quantity]:
            product_id = int(s_product_id)
            price = Decimal(s_price)
            quantity = int(s_quantity)
            fields = (name, price, quantity)
            res_u = update_product(storage, product_id, fields)
            if res_u:
                print(res_u)
            return True
        case ["delete", s_product_id]:
            product_id = int(s_product_id)
            res_d = delete_product(storage, product_id)
            if res_d:
                print(res_d)
                return True
        case [_]:
            print(f"{line} is not a command")
            return True
    return False


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
