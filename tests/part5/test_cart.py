from decimal import Decimal

import pytest
from src.part5.cart import add_to_cart, remove_from_cart
from src.part5.storage import NAME_KEY, PRICE_KEY, QUANTITY_KEY, Product


PRODUCT_ID = 1288834974657000001


def make_store(quantity: int = 10) -> tuple[dict[int, Product], set[str]]:
    storage: dict[int, Product] = {
        PRODUCT_ID: {
            NAME_KEY: "saw",
            PRICE_KEY: Decimal("1.00"),
            QUANTITY_KEY: quantity,
        }
    }
    return storage, {"saw"}


def test_add_to_cart_new_product() -> None:
    storage, names = make_store()
    cart: dict[int, int] = {}

    assert add_to_cart(storage, names, cart, PRODUCT_ID, 3) == 3

    assert cart == {PRODUCT_ID: 3}
    assert storage[PRODUCT_ID][QUANTITY_KEY] == 7


def test_add_to_cart_existing_product_accumulates() -> None:
    storage, names = make_store()
    cart: dict[int, int] = {}

    add_to_cart(storage, names, cart, PRODUCT_ID, 3)

    assert add_to_cart(storage, names, cart, PRODUCT_ID, 2) == 5
    assert cart == {PRODUCT_ID: 5}
    assert storage[PRODUCT_ID][QUANTITY_KEY] == 5


def test_add_to_cart_whole_stock() -> None:
    storage, names = make_store()
    cart: dict[int, int] = {}

    assert add_to_cart(storage, names, cart, PRODUCT_ID, 10) == 10
    assert storage[PRODUCT_ID][QUANTITY_KEY] == 0


def test_add_to_cart_unknown_product(capsys: pytest.CaptureFixture[str]) -> None:
    storage, names = make_store()
    cart: dict[int, int] = {}

    assert add_to_cart(storage, names, cart, 5, 1) is None

    assert capsys.readouterr().out == "no product with id 5\n"
    assert cart == {}
    assert storage[PRODUCT_ID][QUANTITY_KEY] == 10


def test_add_to_cart_not_enough_stock(capsys: pytest.CaptureFixture[str]) -> None:
    storage, names = make_store()
    cart: dict[int, int] = {}

    assert add_to_cart(storage, names, cart, PRODUCT_ID, 11) is None

    assert capsys.readouterr().out == (
        f"not enough stock for product {PRODUCT_ID}: 10 available, 11 requested\n"
    )
    assert cart == {}
    assert storage[PRODUCT_ID][QUANTITY_KEY] == 10


def test_remove_from_cart_partial() -> None:
    storage, names = make_store(quantity=7)
    cart = {PRODUCT_ID: 3}

    assert remove_from_cart(storage, names, cart, PRODUCT_ID, 1) == 2

    assert cart == {PRODUCT_ID: 2}
    assert storage[PRODUCT_ID][QUANTITY_KEY] == 8


def test_remove_from_cart_all_drops_product() -> None:
    storage, names = make_store(quantity=7)
    cart = {PRODUCT_ID: 3}

    assert remove_from_cart(storage, names, cart, PRODUCT_ID, 3) == 0

    assert cart == {}
    assert storage[PRODUCT_ID][QUANTITY_KEY] == 10


def test_remove_from_cart_product_not_in_cart(
    capsys: pytest.CaptureFixture[str],
) -> None:
    storage, names = make_store()
    cart: dict[int, int] = {}

    assert remove_from_cart(storage, names, cart, PRODUCT_ID, 1) is None

    assert capsys.readouterr().out == f"product {PRODUCT_ID} is not in the cart\n"
    assert storage[PRODUCT_ID][QUANTITY_KEY] == 10


def test_remove_from_cart_too_many(capsys: pytest.CaptureFixture[str]) -> None:
    storage, names = make_store(quantity=7)
    cart = {PRODUCT_ID: 3}

    assert remove_from_cart(storage, names, cart, PRODUCT_ID, 4) is None

    assert capsys.readouterr().out == (
        f"cart holds only 3 unit(s) of product {PRODUCT_ID}, cannot remove 4\n"
    )
    assert cart == {PRODUCT_ID: 3}
    assert storage[PRODUCT_ID][QUANTITY_KEY] == 7


def test_remove_from_cart_product_deleted_from_storage(
    capsys: pytest.CaptureFixture[str],
) -> None:
    cart = {PRODUCT_ID: 3}

    assert remove_from_cart({}, set(), cart, PRODUCT_ID, 1) is None

    assert capsys.readouterr().out == f"no product with id {PRODUCT_ID}\n"
    assert cart == {PRODUCT_ID: 3}


def test_total_is_preserved() -> None:
    storage, names = make_store()
    cart: dict[int, int] = {}

    for action, amount in (
        (add_to_cart, 4),
        (add_to_cart, 2),
        (remove_from_cart, 5),
        (add_to_cart, 1),
        (remove_from_cart, 2),
    ):
        action(storage, names, cart, PRODUCT_ID, amount)
        assert storage[PRODUCT_ID][QUANTITY_KEY] + cart.get(PRODUCT_ID, 0) == 10
