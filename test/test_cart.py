from decimal import Decimal

from src.part2.cart import add_to_cart, remove_from_cart
from src.part2.crud import create_product, read_product


def test_add_remove_returns_to_initial_state() -> None:
    storage: list = []
    cart: list = []
    pid = create_product(storage, ("a", Decimal("10"), 10))

    add_to_cart(storage, cart, pid, 3)
    assert read_product(storage, pid)[3] == 7
    assert cart == [(pid, 3)]

    remove_from_cart(storage, cart, pid, 3)
    assert read_product(storage, pid)[3] == 10
    assert cart == []


def test_stock_conservation() -> None:
    storage: list = []
    cart: list = []
    pid = create_product(storage, ("a", Decimal("10"), 5))
    add_to_cart(storage, cart, pid, 2)
    on_stock = read_product(storage, pid)[3]
    in_cart = cart[0][1]
    assert on_stock + in_cart == 5


def test_add_beyond_stock_fails_cleanly() -> None:
    storage: list = []
    cart: list = []
    pid = create_product(storage, ("a", Decimal("10"), 3))
    assert add_to_cart(storage, cart, pid, 5) is None
    assert cart == []
    assert read_product(storage, pid)[3] == 3
