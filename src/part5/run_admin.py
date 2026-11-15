from decimal import Decimal
from typing import Final

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


COMMANDS_EXECUTED: int = 0


def run_command(
    storage: dict[int, Product], product_names: set[str], line: str
) -> bool:
    global COMMANDS_EXECUTED
    parts = line.split()
    if not parts:
        print(f"{line!r} is not a command")
        return True

    COMMANDS_EXECUTED += 1
    command = parts[0]
    result: object

    if command == "help" and len(parts) == 1:
        show_help()
        return True

    if command == "exit" and len(parts) == 1:
        return False

    if command == "stats" and len(parts) == 1:
        print(get_stats_str_representation(STATS_REGISTRY))
        return True

    if command == "show" and len(parts) == 1:
        print(get_storage_str_representation(storage))
        return True

    if command == "create" and len(parts) >= 4:
        name = " ".join(parts[1:-2])
        price = Decimal(parts[-2])
        quantity = int(parts[-1])
        result = create_product(
            storage,
            product_names,
            {
                NAME_KEY: name,
                PRICE_KEY: price,
                QUANTITY_KEY: quantity,
            },
            generate_snowflake_id,
        )
        print_result(result)
        return True

    if command == "read" and len(parts) == 2:
        product_id = int(parts[1])
        result = read_product(storage, product_id)
        print_result(result)
        return True

    if command == "update" and len(parts) >= 5:
        product_id = int(parts[1])
        name = " ".join(parts[2:-2])
        price = Decimal(parts[-2])
        quantity = int(parts[-1])
        result = update_product(
            storage,
            product_names,
            product_id,
            {NAME_KEY: name, PRICE_KEY: price, QUANTITY_KEY: quantity},
        )
        print_result(result)
        return True

    if command == "delete" and len(parts) == 2:
        product_id = int(parts[1])
        result = delete_product(storage, product_names, product_id)
        print_result(result)
        return True

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

        except Exception:  # noqa: BLE001
            print(f"{line!r} names a command but its arguments are invalid")


if __name__ == "__main__":
    main()
