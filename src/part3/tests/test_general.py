from decimal import Decimal, InvalidOperation

import pytest

from ..crud import create_product, update_product
from ..run_admin import HELP_TEXT, PROMPT, main, print_result, run_command, show_help
from ..storage import Product
from ..utils import (
    TABLE_HEADERS,
    get_storage_str_representation,
    normalize_product_name,
)


def test_normalize_product_name() -> None:
    assert normalize_product_name("  Cordless Drill  ") == "cordless drill"
    assert normalize_product_name("abc    def\tghi\tjkl") == "abc def ghi jkl"
    assert normalize_product_name(" \t\n ") == ""
    assert normalize_product_name("claw hammer") == "claw hammer"
    assert normalize_product_name("") == ""
    assert normalize_product_name("Cordless\tDrill\n  ") == "cordless drill"


def test_constants() -> None:
    assert PROMPT == "admin> "
    assert TABLE_HEADERS == ("ID", "name", "price", "quantity")


def test_get_storage_str_representation() -> None:
    # пустое хранилище: только заголовки и разделитель
    assert (
        get_storage_str_representation([])
        == """| ID | name | price | quantity |
|----|------|-------|----------|"""
    )

    test1_str = """| ID | name | price | quantity |
|----|------|-------|----------|
| 1  | saw  | 9.90  | 5        |
| 2  | axe  | 12.00 | 8        |"""
    assert (
        get_storage_str_representation(
            [(1, "saw", Decimal("9.90"), 5), (2, "axe", Decimal("12.00"), 8)]
        )
        == test1_str
    )

    test2_str = """| ID | name       | price   | quantity |
|----|------------|---------|----------|
| 10 | compressor | 1299.99 | 3        |
| 2  | nail       | 2.50    | 500      |"""
    assert (
        get_storage_str_representation(
            [
                (10, "compressor", Decimal("1299.99"), 3),
                (2, "nail", Decimal("2.50"), 500),
            ]
        )
        == test2_str
    )

    # инварианты: все строки одной длины, | на краях каждой строки
    lines = test2_str.split("\n")
    assert len({len(line) for line in lines}) == 1
    assert all(line.startswith("|") and line.endswith("|") for line in lines)


def test_create_product(capsys: pytest.CaptureFixture[str]) -> None:
    taken: list[Product] = [
        (1, "saw", Decimal("9.90"), 5),
        (2, "axe", Decimal("12.00"), 8),
    ]

    # пустое имя: пустая строка или только пробельные символы
    for name in ("", "   ", " \n \t "):
        assert create_product(taken, (name, Decimal("1.00"), 1)) is None
        assert capsys.readouterr().out == "product name must not be blank\n"

    # имя занято, сравнение идёт по нормализованной форме
    assert create_product(taken, ("saw", Decimal("1.00"), 1)) is None
    assert capsys.readouterr().out == "product name 'saw' is already taken\n"
    assert create_product(taken, (" SAw   ", Decimal("1.00"), 1)) is None
    assert capsys.readouterr().out == "product name 'saw' is already taken\n"
    assert taken == [
        (1, "saw", Decimal("9.90"), 5),
        (2, "axe", Decimal("12.00"), 8),
    ]

    # успех: имя и цена нормализуются, id на один больше наибольшего
    assert create_product(taken, ("sword", Decimal("1.00"), 1)) == 3
    assert taken == [
        (1, "saw", Decimal("9.90"), 5),
        (2, "axe", Decimal("12.00"), 8),
        (3, "sword", Decimal("1.00"), 1),
    ]

    # id считается как max + 1, а не len + 1
    gappy: list[Product] = [
        (1, "saw", Decimal("9.90"), 5),
        (3, "axe", Decimal("12.00"), 8),
    ]
    assert create_product(gappy, ("sword", Decimal("1.00"), 1)) == 4

    # примеры из TASK.md
    storage1: list[Product] = []
    first_id = create_product(storage1, ("  Cordless   Drill ", Decimal("89.999"), 12))
    second_id = create_product(storage1, ("Claw Hammer", Decimal("9.9"), 40))
    assert first_id == 1
    assert second_id == 2
    assert storage1 == [
        (1, "cordless drill", Decimal("90.00"), 12),
        (2, "claw hammer", Decimal("9.90"), 40),
    ]

    storage2: list[Product] = []
    assert create_product(storage2, ("cordless drill", Decimal(50), 3)) == 1
    result = create_product(storage2, ("  CORDLESS   DRILL  ", Decimal(75), 1))
    assert result is None
    assert capsys.readouterr().out == "product name 'cordless drill' is already taken\n"
    assert storage2 == [(1, "cordless drill", Decimal("50.00"), 3)]

    storage3: list[Product] = []
    result = create_product(storage3, ("     ", Decimal(10), 5))
    assert result is None
    assert capsys.readouterr().out == "product name must not be blank\n"
    assert storage3 == []


def test_update_product(capsys: pytest.CaptureFixture[str]) -> None:
    storage1: list[Product] = [
        (1, "cordless drill", Decimal("90.00"), 12),
        (2, "claw hammer", Decimal("9.90"), 40),
    ]

    # успех: имя и цена нормализуются, идентификатор сохраняется
    result = update_product(storage1, 2, ("  Rubber   Mallet ", Decimal("7.505"), 25))
    assert result == (2, "rubber mallet", Decimal("7.51"), 25)
    assert storage1 == [
        (1, "cordless drill", Decimal("90.00"), 12),
        (2, "rubber mallet", Decimal("7.51"), 25),
    ]

    storage2: list[Product] = [
        (1, "cordless drill", Decimal("90.00"), 12),
        (2, "claw hammer", Decimal("9.90"), 40),
    ]

    # обновление под собственным именем (в другом написании) — не конфликт
    result = update_product(storage2, 1, ("CORDLESS  Drill", Decimal(85), 10))
    assert result == (1, "cordless drill", Decimal("85.00"), 10)

    storage3: list[Product] = [
        (1, "cordless drill", Decimal("90.00"), 12),
        (2, "claw hammer", Decimal("9.90"), 40),
    ]

    # имя занято другим товаром
    result = update_product(storage3, 1, (" Claw Hammer ", Decimal(85), 10))
    assert result is None
    assert capsys.readouterr().out == "product name 'claw hammer' is already taken\n"
    assert storage3 == [
        (1, "cordless drill", Decimal("90.00"), 12),
        (2, "claw hammer", Decimal("9.90"), 40),
    ]

    storage4: list[Product] = [
        (1, "cordless drill", Decimal("90.00"), 12),
        (2, "claw hammer", Decimal("9.90"), 40),
    ]

    # товара с таким id нет
    result = update_product(storage4, 99, ("saw", Decimal(20), 5))
    assert result is None
    assert capsys.readouterr().out == "no product with id 99\n"

    # пустое имя отвергается до поиска по идентификатору
    result = update_product(storage4, 99, ("     ", Decimal(20), 5))
    assert result is None
    assert capsys.readouterr().out == "product name must not be blank\n"
    assert storage4 == [
        (1, "cordless drill", Decimal("90.00"), 12),
        (2, "claw hammer", Decimal("9.90"), 40),
    ]


def test_show_help(capsys: pytest.CaptureFixture[str]) -> None:
    show_help()
    assert capsys.readouterr().out == HELP_TEXT + "\n"


def test_print_result(capsys: pytest.CaptureFixture[str]) -> None:
    print_result(None)
    assert capsys.readouterr().out == ""

    print_result(42)
    assert capsys.readouterr().out == "42\n"

    product: Product = (1, "saw", Decimal("9.90"), 5)
    print_result(product)
    assert capsys.readouterr().out == "(1, 'saw', Decimal('9.90'), 5)\n"


def sample_storage() -> list[Product]:
    """A fresh store with two products, for the run_command tests."""
    return [
        (1, "cordless drill", Decimal("89.99"), 12),
        (2, "claw hammer", Decimal("9.90"), 40),
    ]


def test_run_command_help_exit(capsys: pytest.CaptureFixture[str]) -> None:
    storage: list[Product] = []

    assert run_command(storage, "help") is True
    assert capsys.readouterr().out == HELP_TEXT + "\n"

    assert run_command(storage, "exit") is False
    assert capsys.readouterr().out == ""
    assert storage == []


def test_run_command_create(capsys: pytest.CaptureFixture[str]) -> None:
    storage: list[Product] = []

    # имя нормализуется, цена округляется, печатается новый id
    assert run_command(storage, "create Cordless Drill 89.99 12") is True
    assert capsys.readouterr().out == "1\n"

    assert run_command(storage, "create  claw   hammer 9.9 40") is True
    assert capsys.readouterr().out == "2\n"
    assert storage == [
        (1, "cordless drill", Decimal("89.99"), 12),
        (2, "claw hammer", Decimal("9.90"), 40),
    ]


def test_run_command_show(capsys: pytest.CaptureFixture[str]) -> None:
    storage: list[Product] = []

    assert run_command(storage, "show") is True
    assert capsys.readouterr().out == (
        "| ID | name | price | quantity |\n|----|------|-------|----------|\n"
    )

    run_command(storage, "create Cordless Drill 89.99 12")
    run_command(storage, "create  claw   hammer 9.9 40")
    capsys.readouterr()

    assert run_command(storage, "show") is True
    assert capsys.readouterr().out == (
        "| ID | name           | price | quantity |\n"
        "|----|----------------|-------|----------|\n"
        "| 1  | cordless drill | 89.99 | 12       |\n"
        "| 2  | claw hammer    | 9.90  | 40       |\n"
    )


def test_run_command_read(capsys: pytest.CaptureFixture[str]) -> None:
    storage = sample_storage()

    assert run_command(storage, "read 1") is True
    assert capsys.readouterr().out == "(1, 'cordless drill', Decimal('89.99'), 12)\n"

    assert run_command(storage, "read 5") is True
    assert capsys.readouterr().out == "no product with id 5\n"
    assert storage == [
        (1, "cordless drill", Decimal("89.99"), 12),
        (2, "claw hammer", Decimal("9.90"), 40),
    ]


def test_run_command_update(capsys: pytest.CaptureFixture[str]) -> None:
    storage = sample_storage()

    assert run_command(storage, "update 2 mallet 7.50 30") is True
    assert capsys.readouterr().out == "(2, 'mallet', Decimal('7.50'), 30)\n"
    assert storage == [
        (1, "cordless drill", Decimal("89.99"), 12),
        (2, "mallet", Decimal("7.50"), 30),
    ]


def test_run_command_delete(capsys: pytest.CaptureFixture[str]) -> None:
    storage = sample_storage()

    assert run_command(storage, "delete 2") is True
    assert capsys.readouterr().out == "2\n"

    assert run_command(storage, "delete 2") is True
    assert capsys.readouterr().out == "no product with id 2\n"
    assert storage == [(1, "cordless drill", Decimal("89.99"), 12)]


def test_run_command_not_a_command(capsys: pytest.CaptureFixture[str]) -> None:
    storage = sample_storage()

    # неизвестная команда, неверное число аргументов и create/update без
    # слов имени: одно и то же сообщение, хранилище не меняется
    for line in (
        "frobnicate 1 2",
        "read 1 2 3",
        "read",
        "delete",
        "help me",
        "exit now",
        "show extra",
        "create 89.90 12",
        "update 1 89.90 12",
    ):
        assert run_command(storage, line) is True
        assert capsys.readouterr().out == f"'{line}' is not a command\n"
    assert storage == [
        (1, "cordless drill", Decimal("89.99"), 12),
        (2, "claw hammer", Decimal("9.90"), 40),
    ]


# помогла написать нейронка
def test_run_command_invalid_arguments(capsys: pytest.CaptureFixture[str]) -> None:
    storage = sample_storage()

    # id/цена/количество не разбираются: исключение (ловится в main),
    # хранилище и stdout не меняются
    for line, exc_type in (
        ("read abc", ValueError),
        ("delete abc", ValueError),
        ("update abc claw hammer 1.00 1", ValueError),
        ("create foo 1.00 abc", ValueError),
        ("create foo abc 5", InvalidOperation),
        ("update 1 foo abc 2", InvalidOperation),
    ):
        with pytest.raises(exc_type):
            run_command(storage, line)
        assert capsys.readouterr().out == ""
    assert storage == [
        (1, "cordless drill", Decimal("89.99"), 12),
        (2, "claw hammer", Decimal("9.90"), 40),
    ]


# помогла написать нейронка
def test_main_session(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    lines = iter(
        [
            "create Cordless Drill 89.99 12",
            "create  claw   hammer 9.9 40",
            "show",
            "read 5",
            "exit",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda prompt="": next(lines))
    main()
    assert capsys.readouterr().out == (
        "1\n"
        "2\n"
        "| ID | name           | price | quantity |\n"
        "|----|----------------|-------|----------|\n"
        "| 1  | cordless drill | 89.99 | 12       |\n"
        "| 2  | claw hammer    | 9.90  | 40       |\n"
        "no product with id 5\n"
    )


# помогла написать нейронка
def test_main_catches_invalid_arguments(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    lines = iter(["create foo abc 5", "read x", "exit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(lines))
    main()
    assert capsys.readouterr().out == (
        "'create foo abc 5' names a command but its arguments are invalid\n"
        "'read x' names a command but its arguments are invalid\n"
    )
