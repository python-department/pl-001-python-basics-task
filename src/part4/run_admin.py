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


# TODO: задайте приглашение и текст справки (используйте своё решение части 3)
PROMPT: Final[str] = "admin> "
HELP_TEXT: Final[str] = """
  Available commands:
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
    """Print the command reference to stdout.

    The text is the module-level :data:`HELP_TEXT` constant, printed as
    is: a heading, one line per command with a short description, and a
    note on how multi-word names are parsed.
    """
    print(HELP_TEXT)


def print_result(result: object) -> None:
    """Print a CRUD result to stdout unless it is ``None``.

    Args:
        result: The value returned by a CRUD operation. ``None`` means the
            operation already reported its own failure, so nothing is
            printed in that case.
    """
    if result:
        print(result)


def get_fields(name: list[str], price: str, quantity: str) -> Product:
    return {
        NAME_KEY: " ".join(name),
        PRICE_KEY: Decimal(price),
        QUANTITY_KEY: int(quantity),
    }


def run_command(
    storage: dict[str, Product], product_names: set[str], line: str
) -> bool:
    """Parse one console line and carry out the command it names.

    Args:
        storage: The product store shared across the session; mutated in
            place by the ``create``, ``update`` and ``delete`` commands.
        product_names: The normalised names already in ``storage``; kept
            in sync by the ``create``, ``update`` and ``delete`` commands.
        line: One line of console input, already stripped of surrounding
            whitespace.

    Returns:
        ``True`` to keep the read-eval-print loop running, or ``False``
        once the ``exit`` command has been seen. A line that is not a
        known command prints a notice and still returns ``True``.

    Raises:
        ValueError: If the quantity argument of a CRUD command does not
            parse as a base-10 integer.
        decimal.InvalidOperation: If the price argument of ``create`` or
            ``update`` does not parse as a decimal number.
    """
    match line.split():
        case ["help"]:
            show_help()
        case ["exit"]:
            return False
        case ["show"]:
            print(get_storage_str_representation(storage))
        case ["create", *name, price, quantity]:
            fields = get_fields(name, price, quantity)
            print_result(create_product(storage, product_names, fields))
        case ["read", product_id]:
            print_result(read_product(storage, product_id))
        case ["update", product_id, *name, price, quantity]:
            fields = get_fields(name, price, quantity)
            print_result(update_product(storage, product_names, product_id, fields))
        case ["delete", product_id]:
            print_result(delete_product(storage, product_names, product_id))
        case _:
            print(f"'{line}' is not a command")
    return True


def main() -> None:
    """Run the admin console until the ``exit`` command is entered.

    A single product store, and the set of normalised names it holds, are
    created empty and kept in memory for the whole session. Each iteration
    reads one line from stdin, strips its surrounding whitespace and hands
    it to :func:`run_command`. A line that names a command but whose price
    or quantity argument does not parse is caught here and reported
    without stopping the loop; only ``exit`` ends it.
    """
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
