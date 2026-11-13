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


PROMPT: Final[str] = "admin> "
HELP_TEXT: Final[str] = """Available commands:
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


def print_result(result: object) -> None:
    if result is not None:
        print(result)


def _parse_product_fields(words: list[str]) -> dict[str, Any]:
    return {
        NAME_KEY: " ".join(words[:-2]),
        PRICE_KEY: Decimal(words[-2]),
        QUANTITY_KEY: int(words[-1]),
    }


def run_command(
    storage: dict[int, Product], product_names: set[str], line: str
) -> bool:
    words = line.split()
    if not words:
        return True

    match words:
        case ["help"]:
            show_help()
            return True

        case ["exit"]:
            return False

        case ["show"]:
            print_result(get_storage_str_representation(storage))
            return True

        case ["create", *rest] if len(rest) >= 3:
            fields = _parse_product_fields(rest)
            print_result(
                create_product(storage, product_names, fields, generate_snowflake_id)
            )
            return True

        case ["read", product_id_word]:
            print_result(read_product(storage, int(product_id_word)))
            return True

        case ["update", product_id_word, *rest] if len(rest) >= 3:
            fields = _parse_product_fields(rest)
            print_result(
                update_product(storage, product_names, int(product_id_word), fields)
            )
            return True

        case ["delete", product_id_word]:
            print_result(delete_product(storage, product_names, int(product_id_word)))
            return True

        case ["stats"]:
            print_result(get_stats_str_representation(STATS_REGISTRY))
            return True

        case _:
            print(f"{line!r} is not a command")
            return True


def main() -> None:
    storage: dict[int, Product] = {}
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
