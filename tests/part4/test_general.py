from decimal import Decimal, InvalidOperation

import pytest
import uuid

from src.part4.cart import add_to_cart, remove_from_cart
from src.part4.crud import (
    create_product,
    delete_product,
    generate_product_id,
    read_product,
    update_product,
)
from src.part4.run_admin import (
    HELP_TEXT,
    PROMPT,
    main,
    print_result,
    run_command,
    show_help,
)
from src.part4.storage import PRICE_KEY, QUANTITY_KEY, NAME_KEY, Product
from src.part4.utils import (
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
        get_storage_str_representation(dict())
        == """| ID | name | price | quantity |
|----|------|-------|----------|"""
    )

    test1_str = """| ID | name | price | quantity |
|----|------|-------|----------|
| 1  | saw  | 9.90  | 5        |
| 2  | axe  | 12.00 | 8        |"""
    assert (
        get_storage_str_representation(
            {
                "1": {"name": "saw", "price": Decimal("9.90"), "quantity": 5},
                "2": {"name": "axe", "price": Decimal("12.00"), "quantity": 8},
            }
        )
        == test1_str
    )

    test2_str = """| ID | name       | price   | quantity |
|----|------------|---------|----------|
| 10 | compressor | 1299.99 | 3        |
| 2  | nail       | 2.50    | 500      |"""
    assert (
        get_storage_str_representation(
            {
                "10": {"name": "compressor", "price": Decimal("1299.99"), "quantity": 3},
                "2": {"name": "nail", "price": Decimal("2.50"), "quantity": 500},
            }
        )
        == test2_str
    )

    # инварианты: все строки одной длины, | на краях каждой строки
    lines = test2_str.split("\n")
    assert len({len(line) for line in lines}) == 1
    assert all(line.startswith("|") and line.endswith("|") for line in lines)


def test_generate_product_id():
    test_id_1 = generate_product_id()
    test_id_2 = generate_product_id()

    assert str(type(test_id_1)) == "<class 'str'>"
    assert len(test_id_1) == 36
    assert uuid.UUID(test_id_1).version == 4
    assert test_id_1 != test_id_2


def test_create_product(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[str, Product] = {}
    product_names: set[str] = set()

    product_id = create_product(
        storage,
        product_names,
        {
            NAME_KEY: "  Cordless   Drill ",
            PRICE_KEY: Decimal("89.999"),
            QUANTITY_KEY: 12,
        },
    )

    assert storage == {
        list(storage.keys())[0]: {
            "name": "cordless drill",
            "price": Decimal("90.00"),
            "quantity": 12,
        }
    }
    assert product_names == {"cordless drill"}

    storage: dict[str, Product] = {}
    product_names: set[str] = set()

    create_product(
        storage,
        product_names,
        {NAME_KEY: "cordless drill", PRICE_KEY: Decimal("50"), QUANTITY_KEY: 3},
    )
    result = create_product(
        storage,
        product_names,
        {
            NAME_KEY: "  CORDLESS   DRILL  ",
            PRICE_KEY: Decimal("75"),
            QUANTITY_KEY: 1,
        },
    )
    assert capsys.readouterr().out == "product name 'cordless drill' is already taken\n"

    assert result is None
    assert len(storage) == 1
    assert product_names == {"cordless drill"}

    # пустое имя: пустая строка или только пробельные символы
    storage: dict[str, Product] = {}
    product_names: set[str] = set()

    for name in ("", "   ", " \n \t "):
        result = create_product(
            storage,
            product_names,
            {NAME_KEY: name, PRICE_KEY: Decimal("1.00"), QUANTITY_KEY: 1},
        )
        assert result is None
        assert capsys.readouterr().out == "product name must not be blank\n"
        assert len(storage) == 0
        assert product_names == set()


def test_read_product(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[str, Product] = {}
    product_names: set[str] = set()

    product_id = create_product(
        storage,
        product_names,
        {NAME_KEY: "saw", PRICE_KEY: Decimal("9.90"), QUANTITY_KEY: 5},
    )

    # успешное чтение
    result = read_product(storage, product_id)
    assert result == {"name": "saw", "price": Decimal("9.90"), "quantity": 5}

    # товара с таким id нет
    result = read_product(storage, "nonexistent-id")
    assert result is None
    assert capsys.readouterr().out == "no product with id nonexistent-id\n"


def test_update_product(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[str, Product] = {}
    product_names: set[str] = set()

    product_id = create_product(
        storage,
        product_names,
        {
            NAME_KEY: "Cordless Drill",
            PRICE_KEY: Decimal("89.99"),
            QUANTITY_KEY: 12,
        },
    )

    # Частичное обновление: меняется только количество, индекс имён остаётся прежним
    assert update_product(storage, product_names, product_id, {QUANTITY_KEY: 7}) == {
        "name": "cordless drill",
        "price": Decimal("89.99"),
        "quantity": 7,
    }
    assert product_names == {"cordless drill"}

    # Переименование: имя и цена нормализуются, в индексе старое имя заменяется новым
    assert update_product(
        storage,
        product_names,
        product_id,
        {NAME_KEY: "  Hammer   Drill ", PRICE_KEY: Decimal("109.999")},
    ) == {
        "name": "hammer drill",
        "price": Decimal("110.00"),
        "quantity": 7,
    }
    assert product_names == {"hammer drill"}

    # обновление под собственным именем (в другом написании) — не конфликт
    storage: dict[str, Product] = {}
    product_names: set[str] = set()

    product_id = create_product(
        storage,
        product_names,
        {NAME_KEY: "cordless drill", PRICE_KEY: Decimal("90.00"), QUANTITY_KEY: 12},
    )

    result = update_product(
        storage,
        product_names,
        product_id,
        {NAME_KEY: "CORDLESS  Drill", PRICE_KEY: Decimal(85), QUANTITY_KEY: 10},
    )
    assert result == {
        "name": "cordless drill",
        "price": Decimal("85.00"),
        "quantity": 10,
    }

    # имя занято другим товаром
    storage: dict[str, Product] = {}
    product_names: set[str] = set()

    id1 = create_product(
        storage,
        product_names,
        {NAME_KEY: "cordless drill", PRICE_KEY: Decimal("90.00"), QUANTITY_KEY: 12},
    )
    id2 = create_product(
        storage,
        product_names,
        {NAME_KEY: "claw hammer", PRICE_KEY: Decimal("9.90"), QUANTITY_KEY: 40},
    )

    result = update_product(
        storage,
        product_names,
        id1,
        {NAME_KEY: " Claw Hammer ", PRICE_KEY: Decimal(85), QUANTITY_KEY: 10},
    )
    assert result is None
    assert capsys.readouterr().out == "product name 'claw hammer' is already taken\n"

    # товара с таким id нет
    result = update_product(storage, product_names, "nonexistent-id", {NAME_KEY: "saw"})
    assert result is None
    assert capsys.readouterr().out == "no product with id nonexistent-id\n"

    # пустое имя отвергается
    result = update_product(storage, product_names, id1, {NAME_KEY: "     "})
    assert result is None
    assert capsys.readouterr().out == "product name must not be blank\n"


def test_delete_product(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[str, Product] = {}
    product_names: set[str] = set()

    product_id = create_product(
        storage,
        product_names,
        {NAME_KEY: "saw", PRICE_KEY: Decimal("9.90"), QUANTITY_KEY: 5},
    )

    # успешное удаление
    result = delete_product(storage, product_names, product_id)
    assert result == product_id
    assert len(storage) == 0
    assert product_names == set()

    # товара с таким id нет
    result = delete_product(storage, product_names, "nonexistent-id")
    assert result is None
    assert capsys.readouterr().out == "no product with id nonexistent-id\n"


def test_add_to_cart(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[str, Product] = {}
    product_names: set[str] = set()
    cart: dict[str, int] = {}

    product_id = create_product(
        storage,
        product_names,
        {NAME_KEY: "saw", PRICE_KEY: Decimal("9.90"), QUANTITY_KEY: 5},
    )

    # успешное добавление в корзину
    result = add_to_cart(storage, product_names, cart, product_id, 3)
    assert result == 3
    assert cart == {product_id: 3}
    assert storage[product_id][QUANTITY_KEY] == 2

    # добавление еще товара
    result = add_to_cart(storage, product_names, cart, product_id, 2)
    assert result == 5
    assert cart == {product_id: 5}
    assert storage[product_id][QUANTITY_KEY] == 0

    # товара недостаточно на складе
    result = add_to_cart(storage, product_names, cart, product_id, 1)
    assert result is None
    assert capsys.readouterr().out == (
        f"not enough stock for product {product_id}: 0 available, 1 requested\n"
    )

    # товара нет в хранилище
    result = add_to_cart(storage, product_names, cart, "nonexistent-id", 1)
    assert result is None
    assert capsys.readouterr().out == "no product with id nonexistent-id\n"


def test_remove_from_cart(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[str, Product] = {}
    product_names: set[str] = set()
    cart: dict[str, int] = {}

    product_id = create_product(
        storage,
        product_names,
        {NAME_KEY: "saw", PRICE_KEY: Decimal("9.90"), QUANTITY_KEY: 5},
    )

    # добавляем в корзину
    add_to_cart(storage, product_names, cart, product_id, 3)

    # успешное удаление из корзины
    result = remove_from_cart(storage, product_names, cart, product_id, 2)
    assert result == 1
    assert cart == {product_id: 1}
    assert storage[product_id][QUANTITY_KEY] == 4

    # удаление оставшегося товара
    result = remove_from_cart(storage, product_names, cart, product_id, 1)
    assert result == 0
    assert product_id not in cart
    assert storage[product_id][QUANTITY_KEY] == 5

    # товара нет в корзине
    result = remove_from_cart(storage, product_names, cart, product_id, 1)
    assert result is None
    assert capsys.readouterr().out == f"product {product_id} is not in the cart\n"

    # в корзине недостаточно товара
    add_to_cart(storage, product_names, cart, product_id, 2)
    result = remove_from_cart(storage, product_names, cart, product_id, 5)
    assert result is None
    assert capsys.readouterr().out == (
        f"cart holds only 2 unit(s) of product {product_id}, cannot remove 5\n"
    )


def test_show_help(capsys: pytest.CaptureFixture[str]) -> None:
    show_help()
    assert capsys.readouterr().out == HELP_TEXT + "\n"


def test_print_result(capsys: pytest.CaptureFixture[str]) -> None:
    print_result(None)
    assert capsys.readouterr().out == ""

    print_result(42)
    assert capsys.readouterr().out == "42\n"

    product: Product = {"name": "saw", "price": Decimal("9.90"), "quantity": 5}
    print_result(product)
    # Проверяем что результат содержит ключевые части словаря
    output = capsys.readouterr().out
    assert "saw" in output
    assert "9.90" in output
    assert "5" in output


def test_run_command_help_exit(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[str, Product] = {}
    product_names: set[str] = set()

    assert run_command(storage, product_names, "help") is True
    assert capsys.readouterr().out == HELP_TEXT + "\n"

    assert run_command(storage, product_names, "exit") is False
    assert capsys.readouterr().out == ""
    assert storage == {}


def test_run_command_create(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[str, Product] = {}
    product_names: set[str] = set()

    # имя нормализуется, цена округляется, печатается новый id
    assert run_command(storage, product_names, "create Cordless Drill 89.99 12") is True
    out = capsys.readouterr().out
    product_id_1 = out.strip()
    assert len(storage) == 1

    assert run_command(storage, product_names, "create  claw   hammer 9.9 40") is True
    out = capsys.readouterr().out
    product_id_2 = out.strip()
    assert len(storage) == 2


def test_run_command_show(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[str, Product] = {}
    product_names: set[str] = set()

    assert run_command(storage, product_names, "show") is True
    assert capsys.readouterr().out == (
        "| ID | name | price | quantity |\n|----|------|-------|----------|\n"
    )

    run_command(storage, product_names, "create Cordless Drill 89.99 12")
    run_command(storage, product_names, "create  claw   hammer 9.9 40")
    capsys.readouterr()

    assert run_command(storage, product_names, "show") is True
    output = capsys.readouterr().out
    assert "cordless drill" in output
    assert "claw hammer" in output
    assert "89.99" in output
    assert "9.90" in output


def test_run_command_read(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[str, Product] = {}
    product_names: set[str] = set()

    product_id = create_product(
        storage,
        product_names,
        {NAME_KEY: "cordless drill", PRICE_KEY: Decimal("89.99"), QUANTITY_KEY: 12},
    )

    assert run_command(storage, product_names, f"read {product_id}") is True
    output = capsys.readouterr().out
    assert "cordless drill" in output
    assert "89.99" in output

    assert run_command(storage, product_names, "read nonexistent-id") is True
    assert capsys.readouterr().out == "no product with id nonexistent-id\n"


def test_run_command_update(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[str, Product] = {}
    product_names: set[str] = set()

    product_id = create_product(
        storage,
        product_names,
        {NAME_KEY: "claw hammer", PRICE_KEY: Decimal("9.90"), QUANTITY_KEY: 40},
    )
    capsys.readouterr()

    assert run_command(storage, product_names, f"update {product_id} mallet 7.50 30") is True
    output = capsys.readouterr().out
    assert "mallet" in output
    assert "7.50" in output
    assert "30" in output


def test_run_command_delete(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[str, Product] = {}
    product_names: set[str] = set()

    product_id = create_product(
        storage,
        product_names,
        {NAME_KEY: "claw hammer", PRICE_KEY: Decimal("9.90"), QUANTITY_KEY: 40},
    )
    capsys.readouterr()

    assert run_command(storage, product_names, f"delete {product_id}") is True
    assert capsys.readouterr().out == f"{product_id}\n"

    assert run_command(storage, product_names, f"delete {product_id}") is True
    assert capsys.readouterr().out == f"no product with id {product_id}\n"


def test_run_command_not_a_command(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[str, Product] = {}
    product_names: set[str] = set()

    # неизвестная команда, неверное число аргументов: одно и то же сообщение
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
        assert run_command(storage, product_names, line) is True
        assert capsys.readouterr().out == f"'{line}' is not a command\n"
    assert storage == {}


def test_run_command_invalid_arguments(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[str, Product] = {}
    product_names: set[str] = set()

    # цена/количество не разбираются: исключение (ловится в main)
    # Note: для части 4 id передается строкой, поэтому ValueError не возникает
    for line, exc_type in (
        ("create foo 1.00 abc", ValueError),
        ("create foo abc 5", InvalidOperation),
        ("update id-1 foo abc 2", InvalidOperation),
    ):
        with pytest.raises(exc_type):
            run_command(storage, product_names, line)
        assert capsys.readouterr().out == ""
    assert storage == {}


def test_main_session(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    lines = iter(
        [
            "create Cordless Drill 89.99 12",
            "create  claw   hammer 9.9 40",
            "show",
            "read nonexistent-id",
            "exit",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda prompt="": next(lines))
    main()
    output = capsys.readouterr().out
    assert "cordless drill" in output
    assert "claw hammer" in output
    assert "no product with id nonexistent-id" in output


def test_main_catches_invalid_arguments(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    lines = iter(["create foo abc 5", "read x", "exit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(lines))
    main()
    output = capsys.readouterr().out
    assert "names a command but its arguments are invalid" in output
