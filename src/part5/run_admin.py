from decimal import Decimal, InvalidOperation
from typing import Any, Final

from .crud import (
    STATS_REGISTRY,
    create_product,
    delete_product,
    generate_snowflake_id,
    read_product,
    update_product,
)
from .storage import NAME_KEY, PRICE_KEY, QUANTITY_KEY, Product
from .utils import get_stats_str_representation, get_storage_str_representation

PROMPT: Final = "> "

HELP_TEXT: Final = """Available commands:
  help                                       show this message
  exit                                       leave the console
  show                                       print the whole store as a table
  create <name...> <price> <quantity>        add a product, print its new id
  read <id>                                  print the product with that id
  update <id> <name...> <price> <quantity>   overwrite that product's fields
  delete <id>                                remove the product with that id
  stats                                      print call statistics of the CRUD commands

For create and update the price and quantity are the last two words of the
line; everything before them is the product name, so it may contain spaces
(for example "Gibson SG Junior") and needs no quoting."""


def show_help() -> None:
    print(HELP_TEXT)


def print_result(result: Any) -> None:
    if result is not None:
        print(result)


def _parse_price(raw_price: str) -> Decimal:
    price = Decimal(raw_price)
    if not price.is_finite():
        raise InvalidOperation
    return price


def run_command(
    storage: dict[int, Product],
    product_names: set[str],
    line: str,
) -> bool:
    stripped = line.strip()
    if not stripped:
        return True

    if stripped == "help":
        show_help()
        return True
    if stripped == "exit":
        return False
    if stripped == "show":
        print(get_storage_str_representation(storage))
        return True
    if stripped == "stats":
        print(get_stats_str_representation(STATS_REGISTRY))
        return True

    tokens = stripped.split()
    command = tokens[0]

    if command == "create":
        if len(tokens) < 4:
            print(f"'{stripped}' names a command but its arguments are invalid")
            return True
        try:
            price = _parse_price(tokens[-2])
            quantity = int(tokens[-1])
        except (ValueError, InvalidOperation):
            print(f"'{stripped}' names a command but its arguments are invalid")
            return True

        name = " ".join(tokens[1:-2])
        fields: dict[str, Any] = {
            NAME_KEY: name,
            PRICE_KEY: price,
            QUANTITY_KEY: quantity,
        }
        print_result(
            create_product(storage, product_names, fields, generate_snowflake_id)
        )
        return True

    if command == "read":
        if len(tokens) != 2:
            print(f"'{stripped}' names a command but its arguments are invalid")
            return True
        try:
            product_id = int(tokens[1])
        except ValueError:
            print(f"'{stripped}' names a command but its arguments are invalid")
            return True

        print_result(read_product(storage, product_id))
        return True

    if command == "update":
        if len(tokens) < 5:
            print(f"'{stripped}' names a command but its arguments are invalid")
            return True
        try:
            product_id = int(tokens[1])
            price = _parse_price(tokens[-2])
            quantity = int(tokens[-1])
        except (ValueError, InvalidOperation):
            print(f"'{stripped}' names a command but its arguments are invalid")
            return True

        name = " ".join(tokens[2:-2])
        fields = {
            NAME_KEY: name,
            PRICE_KEY: price,
            QUANTITY_KEY: quantity,
        }
        print_result(update_product(storage, product_names, product_id, fields))
        return True

    if command == "delete":
        if len(tokens) != 2:
            print(f"'{stripped}' names a command but its arguments are invalid")
            return True
        try:
            product_id = int(tokens[1])
        except ValueError:
            print(f"'{stripped}' names a command but its arguments are invalid")
            return True

        print_result(delete_product(storage, product_names, product_id))
        return True

    print(f"'{stripped}' is not a command")
    return True


def main() -> None:
    storage: dict[int, Product] = {}
    product_names: set[str] = set()

    while True:
        try:
            line = input(PROMPT)
        except EOFError:
            break

        if not run_command(storage, product_names, line):
            break


if __name__ == "__main__":
    main()