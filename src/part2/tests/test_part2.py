from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Any, cast

import pytest

from part2.cart import (
    LINE_PRODUCT_ID_INDEX,
    LINE_QUANTITY_INDEX,
    CartLine,
    add_to_cart,
    remove_from_cart,
)
from part2.crud import (
    create_product,
    delete_product,
    generate_product_id,
    read_product,
    update_product,
)
from part2.storage import (
    NAME_INDEX,
    PRICE_INDEX,
    PRODUCT_ID_INDEX,
    PRODUCT_ID_MIN,
    QUANTITY_INDEX,
    Product,
)
from part2.utils import PRICE_PRECISION, PRICE_STEP, normalize_price


# ============================================================
# Helpers
# ============================================================


def product(
    product_id: int,
    name: str,
    price: str = "10.00",
    quantity: int = 10,
) -> Product:
    """
    Build a Product through the public index constants.

    The tests deliberately do not assume that product fields live at
    positions 0, 1, 2, 3. If the tuple layout is reordered together with
    the *_INDEX constants, the tests continue to work.
    """
    fields: list[Any] = [None] * 4
    fields[PRODUCT_ID_INDEX] = product_id
    fields[NAME_INDEX] = name
    fields[PRICE_INDEX] = normalize_price(Decimal(price))
    fields[QUANTITY_INDEX] = quantity
    return cast(Product, tuple(fields))


def cart_line(product_id: int, quantity: int) -> CartLine:
    """
    Build a CartLine through the public index constants instead of hardcoding
    its tuple order.
    """
    fields: list[Any] = [None] * 2
    fields[LINE_PRODUCT_ID_INDEX] = product_id
    fields[LINE_QUANTITY_INDEX] = quantity
    return cast(CartLine, tuple(fields))


def product_id(record: Product) -> int:
    return record[PRODUCT_ID_INDEX]


def product_name(record: Product) -> str:
    return record[NAME_INDEX]


def product_price(record: Product) -> Decimal:
    return record[PRICE_INDEX]


def product_quantity(record: Product) -> int:
    return record[QUANTITY_INDEX]


def line_product_id(line: CartLine) -> int:
    return line[LINE_PRODUCT_ID_INDEX]


def line_quantity(line: CartLine) -> int:
    return line[LINE_QUANTITY_INDEX]


# ============================================================
# storage — константы
# ============================================================


class TestStorageConstants:
    def test_first_product_id_is_defined_by_constant(self) -> None:
        storage: list[Product] = []

        product_id_created = create_product(
            storage,
            ("apple", Decimal(10), 1),
        )

        assert product_id_created == PRODUCT_ID_MIN

    def test_product_helper_respects_index_constants(self) -> None:
        record = product(7, "apple", "12.34", 5)

        assert product_id(record) == 7
        assert product_name(record) == "apple"
        assert product_price(record) == Decimal("12.34")
        assert product_quantity(record) == 5


# ============================================================
# utils — PRICE_STEP / PRICE_PRECISION
# ============================================================


class TestPriceConstants:
    def test_step_is_derived_from_precision(self) -> None:
        assert PRICE_STEP == Decimal(1).scaleb(-PRICE_PRECISION)


class TestNormalizePrice:
    def test_rounds_above_half_up(self) -> None:
        raw = Decimal(10) + PRICE_STEP * Decimal("1.5")
        expected = Decimal(10) + PRICE_STEP * Decimal(2)

        result = normalize_price(raw)

        assert result == expected
        assert result.as_tuple().exponent == -PRICE_PRECISION

    def test_rounds_below_half_down(self) -> None:
        raw = Decimal(10) + PRICE_STEP * Decimal("1.4")
        expected = Decimal(10) + PRICE_STEP

        result = normalize_price(raw)

        assert result == expected
        assert result.as_tuple().exponent == -PRICE_PRECISION

    def test_exact_half_uses_round_half_up(self) -> None:
        raw = Decimal(10) + PRICE_STEP / Decimal(2)
        expected = Decimal(10) + PRICE_STEP

        result = normalize_price(raw)

        assert result == expected

    def test_negative_exact_half_rounds_away_from_zero(self) -> None:
        raw = Decimal(-10) - PRICE_STEP / Decimal(2)
        expected = Decimal(-10) - PRICE_STEP

        assert normalize_price(raw) == expected

    def test_integer_gets_fixed_precision(self) -> None:
        result = normalize_price(Decimal(5))

        assert result == Decimal(5).quantize(
            PRICE_STEP,
            rounding=ROUND_HALF_UP,
        )
        assert result.as_tuple().exponent == -PRICE_PRECISION

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("12.999", "13.00"),
            ("2.3451", "2.35"),
            ("2.3449", "2.34"),
            ("0.005", "0.01"),
            ("-2.345", "-2.35"),
        ],
    )
    def test_examples_from_task(self, raw: str, expected: str) -> None:
        result = normalize_price(Decimal(raw))

        assert result == Decimal(expected)
        assert result.as_tuple().exponent == -PRICE_PRECISION


# ============================================================
# crud — generate_product_id
# ============================================================


class TestGenerateProductId:
    def test_empty_storage_returns_minimum(self) -> None:
        assert generate_product_id([]) == PRODUCT_ID_MIN

    def test_returns_maximum_id_plus_one(self) -> None:
        storage = [
            product(1, "a", quantity=1),
            product(5, "b", quantity=1),
            product(3, "c", quantity=1),
        ]

        assert generate_product_id(storage) == 6

    def test_does_not_reuse_gap_after_delete(self) -> None:
        storage = [
            product(1, "a"),
            product(2, "b"),
            product(3, "c"),
        ]

        assert delete_product(storage, 2) == 2
        assert generate_product_id(storage) == 4


# ============================================================
# crud — create_product
# ============================================================


class TestCreateProduct:
    def test_success_adds_normalized_product(self) -> None:
        storage: list[Product] = []

        created_id = create_product(
            storage,
            ("apple", Decimal("10.999"), 7),
        )

        assert created_id == PRODUCT_ID_MIN
        assert len(storage) == 1

        saved = storage[0]
        assert product_id(saved) == created_id
        assert product_name(saved) == "apple"
        assert product_price(saved) == normalize_price(Decimal("10.999"))
        assert product_quantity(saved) == 7

    def test_successful_create_is_readable(self) -> None:
        storage: list[Product] = []
        created_id = create_product(storage, ("apple", Decimal(10), 4))

        assert created_id is not None
        assert read_product(storage, created_id) == storage[0]

    def test_duplicate_name_does_not_change_storage(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        storage = [product(1, "apple", quantity=1)]
        before = list(storage)

        result = create_product(
            storage,
            ("apple", Decimal(5), 10),
        )

        assert result is None
        assert storage == before

        out = capsys.readouterr().out
        assert "apple" in out
        assert "already taken" in out


# ============================================================
# crud — read_product
# ============================================================


class TestReadProduct:
    def test_existing_product_is_returned(self) -> None:
        record = product(1, "apple", quantity=3)
        storage = [record]

        assert read_product(storage, 1) == record

    def test_missing_product_returns_none_without_mutation(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        storage = [product(1, "apple", quantity=3)]
        before = list(storage)

        assert read_product(storage, 42) is None
        assert storage == before

        out = capsys.readouterr().out
        assert "42" in out
        assert "no product" in out


# ============================================================
# crud — update_product
# ============================================================


class TestUpdateProduct:
    def test_success_changes_name_price_and_quantity_but_keeps_id(self) -> None:
        storage = [product(7, "apple", "10", 5)]

        updated = update_product(
            storage,
            7,
            ("pear", Decimal("12.345"), 9),
        )

        assert updated is not None
        assert product_id(updated) == 7
        assert product_name(updated) == "pear"
        assert product_price(updated) == normalize_price(Decimal("12.345"))
        assert product_quantity(updated) == 9
        assert storage == [updated]

    def test_update_does_not_require_unique_name(self) -> None:
        storage = [
            product(1, "apple", quantity=5),
            product(2, "pear", quantity=6),
        ]

        updated = update_product(
            storage,
            1,
            ("pear", Decimal("7.777"), 8),
        )

        assert updated is not None
        assert product_name(updated) == "pear"
        assert product_quantity(updated) == 8
        assert product_price(updated) == normalize_price(Decimal("7.777"))
        assert len(storage) == 2

    def test_missing_product_does_not_change_storage(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        storage = [product(1, "apple", "10", 5)]
        before = list(storage)

        result = update_product(
            storage,
            99,
            ("pear", Decimal(1), 2),
        )

        assert result is None
        assert storage == before

        out = capsys.readouterr().out
        assert "99" in out
        assert "no product" in out


# ============================================================
# crud — delete_product
# ============================================================


class TestDeleteProduct:
    def test_existing_product_is_removed_and_id_returned(self) -> None:
        first = product(1, "apple", quantity=5)
        second = product(2, "pear", quantity=6)
        storage = [first, second]

        assert delete_product(storage, 1) == 1
        assert storage == [second]

    def test_deleted_product_is_no_longer_readable(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        storage = [product(1, "apple", quantity=5)]

        assert delete_product(storage, 1) == 1
        capsys.readouterr()

        assert read_product(storage, 1) is None
        assert "no product" in capsys.readouterr().out

    def test_missing_product_does_not_change_storage(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        storage = [product(1, "apple", quantity=5)]
        before = list(storage)

        assert delete_product(storage, 42) is None
        assert storage == before

        out = capsys.readouterr().out
        assert "42" in out
        assert "no product" in out


# ============================================================
# cart — add_to_cart
# ============================================================


class TestAddToCart:
    def test_new_line_is_created_and_stock_decreases(self) -> None:
        storage = [product(1, "apple", "10", 5)]
        cart: list[CartLine] = []

        line = add_to_cart(storage, cart, 1, 3)

        assert line is not None
        assert line_product_id(line) == 1
        assert line_quantity(line) == 3
        assert cart == [line]
        assert product_quantity(storage[0]) == 2
        assert product_name(storage[0]) == "apple"
        assert product_price(storage[0]) == Decimal("10.00")

    def test_existing_line_is_incremented(self) -> None:
        storage = [product(1, "apple", quantity=5)]
        cart = [cart_line(1, 1)]

        line = add_to_cart(storage, cart, 1, 2)

        assert line is not None
        assert line_product_id(line) == 1
        assert line_quantity(line) == 3
        assert cart == [line]
        assert product_quantity(storage[0]) == 3

    def test_add_updates_only_matching_cart_line(self) -> None:
        storage = [
            product(1, "apple", quantity=5),
            product(2, "pear", quantity=7),
        ]
        cart = [cart_line(2, 4), cart_line(1, 1)]

        line = add_to_cart(storage, cart, 1, 2)

        assert line is not None
        assert line_product_id(line) == 1
        assert line_quantity(line) == 3
        assert cart == [cart_line(2, 4), cart_line(1, 3)]
        assert product_quantity(storage[0]) == 3
        assert product_quantity(storage[1]) == 7

    def test_all_stock_is_allowed(self) -> None:
        storage = [product(1, "apple", quantity=3)]
        cart: list[CartLine] = []

        line = add_to_cart(storage, cart, 1, 3)

        assert line is not None
        assert line_quantity(line) == 3
        assert product_quantity(storage[0]) == 0

    def test_missing_product_returns_none_without_changes(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        storage: list[Product] = []
        cart: list[CartLine] = []

        assert add_to_cart(storage, cart, 42, 1) is None
        assert storage == []
        assert cart == []

        out = capsys.readouterr().out
        assert "42" in out
        assert "no product" in out

    def test_not_enough_stock_returns_none_without_changes(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        storage = [product(1, "apple", quantity=2)]
        cart: list[CartLine] = []
        before = list(storage)

        assert add_to_cart(storage, cart, 1, 3) is None
        assert storage == before
        assert cart == []

        out = capsys.readouterr().out
        assert "not enough stock" in out
        assert "2 available" in out
        assert "3 requested" in out


# ============================================================
# cart — remove_from_cart
# ============================================================


class TestRemoveFromCart:
    def test_partial_remove_moves_quantity_back_to_stock(self) -> None:
        storage = [product(1, "apple", "10", 2)]
        cart = [cart_line(1, 5)]

        line = remove_from_cart(storage, cart, 1, 3)

        assert line is not None
        assert line_product_id(line) == 1
        assert line_quantity(line) == 2
        assert cart == [line]
        assert product_quantity(storage[0]) == 5
        assert product_name(storage[0]) == "apple"
        assert product_price(storage[0]) == Decimal("10.00")

    def test_full_remove_returns_zero_and_deletes_line(self) -> None:
        storage = [product(1, "apple", "10", 2)]
        cart = [cart_line(1, 4)]

        line = remove_from_cart(storage, cart, 1, 4)

        assert line is not None
        assert line_product_id(line) == 1
        assert line_quantity(line) == 0
        assert cart == []
        assert product_quantity(storage[0]) == 6

    def test_removes_matching_line_even_when_it_is_not_first(self) -> None:
        storage = [
            product(1, "apple", quantity=2),
            product(2, "pear", quantity=4),
        ]
        cart = [cart_line(2, 1), cart_line(1, 5)]

        line = remove_from_cart(storage, cart, 1, 2)

        assert line is not None
        assert line == cart_line(1, 3)
        assert cart == [cart_line(2, 1), cart_line(1, 3)]
        assert product_quantity(storage[0]) == 4
        assert product_quantity(storage[1]) == 4

    def test_not_in_cart_returns_none_without_changes(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        storage = [product(1, "apple", quantity=2)]
        cart: list[CartLine] = []
        before_storage = list(storage)
        before_cart = list(cart)

        assert remove_from_cart(storage, cart, 1, 1) is None
        assert storage == before_storage
        assert cart == before_cart

        out = capsys.readouterr().out
        assert "1" in out
        assert "not in the cart" in out

    def test_not_enough_in_cart_returns_none_without_changes(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        storage = [product(1, "apple", quantity=2)]
        cart = [cart_line(1, 1)]
        before_storage = list(storage)
        before_cart = list(cart)

        assert remove_from_cart(storage, cart, 1, 2) is None
        assert storage == before_storage
        assert cart == before_cart

        out = capsys.readouterr().out
        assert "cart holds only 1" in out
        assert "cannot remove 2" in out

    def test_product_missing_in_storage_returns_none_without_changes(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        storage: list[Product] = []
        cart = [cart_line(42, 3)]
        before_cart = list(cart)

        assert remove_from_cart(storage, cart, 42, 1) is None
        assert storage == []
        assert cart == before_cart

        out = capsys.readouterr().out
        assert "42" in out
        assert "no product" in out


# ============================================================
# Invariants
# ============================================================


class TestInvariants:
    def test_create_then_read(self) -> None:
        storage: list[Product] = []

        created_id = create_product(
            storage,
            ("apple", Decimal("10.999"), 5),
        )

        assert created_id is not None
        record = read_product(storage, created_id)
        assert record is not None
        assert product_id(record) == created_id
        assert product_name(record) == "apple"
        assert product_price(record) == normalize_price(Decimal("10.999"))
        assert product_quantity(record) == 5

    def test_delete_then_read_is_none(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        storage = [product(1, "apple", quantity=5)]

        assert delete_product(storage, 1) == 1
        capsys.readouterr()
        assert read_product(storage, 1) is None
        assert "no product" in capsys.readouterr().out

    def test_add_then_remove_restores_exact_state(self) -> None:
        storage = [product(1, "apple", "10", 5)]
        cart: list[CartLine] = []
        initial_storage = list(storage)
        initial_cart = list(cart)

        added = add_to_cart(storage, cart, 1, 3)
        removed = remove_from_cart(storage, cart, 1, 3)

        assert added is not None
        assert removed is not None
        assert line_quantity(added) == 3
        assert line_quantity(removed) == 0
        assert storage == initial_storage
        assert cart == initial_cart

    def test_quantity_is_conserved_on_add(self) -> None:
        storage = [product(1, "apple", quantity=5)]
        cart: list[CartLine] = []
        total_before = product_quantity(storage[0])

        line = add_to_cart(storage, cart, 1, 3)

        assert line is not None
        total_after = product_quantity(storage[0]) + line_quantity(line)
        assert total_after == total_before

    def test_quantity_is_conserved_on_remove(self) -> None:
        storage = [product(1, "apple", quantity=2)]
        cart = [cart_line(1, 5)]
        total_before = product_quantity(storage[0]) + line_quantity(cart[0])

        line = remove_from_cart(storage, cart, 1, 3)

        assert line is not None
        total_after = product_quantity(storage[0]) + line_quantity(line)
        assert total_after == total_before

    def test_normalized_price_is_preserved_through_create_and_update(self) -> None:
        storage: list[Product] = []
        created_id = create_product(
            storage,
            ("apple", Decimal("2.3451"), 5),
        )

        assert created_id is not None
        created = read_product(storage, created_id)
        assert created is not None
        assert product_price(created) == normalize_price(Decimal("2.3451"))

        updated = update_product(
            storage,
            created_id,
            ("apple", Decimal("7.7777"), 8),
        )

        assert updated is not None
        assert product_price(updated) == normalize_price(Decimal("7.7777"))
