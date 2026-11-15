from decimal import Decimal

from src.part2.crud import create_product, delete_product, read_product, update_product


def test_create_read_roundtrip() -> None:
    storage: list = []
    pid = create_product(storage, ("яблоко", Decimal("10.005"), 5))
    assert pid == 1
    assert read_product(storage, pid) == (1, "яблоко", Decimal("10.01"), 5)


def test_delete_then_read_none() -> None:
    storage: list = []
    pid = create_product(storage, ("груша", Decimal("20"), 3))
    assert delete_product(storage, pid) == pid
    assert read_product(storage, pid) is None


def test_unique_name_rejected() -> None:
    storage: list = []
    create_product(storage, ("a", Decimal("1"), 1))
    assert create_product(storage, ("a", Decimal("2"), 2)) is None
    assert len(storage) == 1


def test_update_keeps_id_and_normalizes() -> None:
    storage: list = []
    pid = create_product(storage, ("a", Decimal("1"), 1))
    updated = update_product(storage, pid, ("b", Decimal("2.999"), 7))
    assert updated == (pid, "b", Decimal("3.00"), 7)
