import pytest
from src.part5.decorators import (
    FAILS_KEY,
    SUCCESS_KEY,
    Registry,
    collect_stats,
)


def test_keys() -> None:
    assert SUCCESS_KEY == "success"
    assert FAILS_KEY == "fails"


def test_registers_zero_record_on_decoration() -> None:
    registry: Registry = {}

    @collect_stats("divide", registry)
    def divide(a: float, b: float) -> float | None:
        return a / b if b else None

    assert registry == {"divide": {"success": 0, "fails": 0}}


def test_counts_success_and_fails(capsys: pytest.CaptureFixture[str]) -> None:
    registry: Registry = {}

    @collect_stats("divide", registry)
    def divide(a: float, b: float) -> float | None:
        if b == 0:
            print("division by zero")
            return None
        return a / b

    assert divide(10, 4) == 2.5
    assert divide(0, 5) == 0.0
    assert divide(1, 0) is None

    assert registry == {"divide": {"success": 2, "fails": 1}}
    assert capsys.readouterr().out == "division by zero\n"


def test_falsy_results_count_as_success() -> None:
    registry: Registry = {}

    @collect_stats("falsy", registry)
    def falsy(value: object) -> object:
        return value

    for value in (0, "", [], False, 0.0):
        falsy(value)

    assert registry["falsy"] == {"success": 5, "fails": 0}


def test_passes_positional_and_keyword_arguments() -> None:
    registry: Registry = {}

    @collect_stats("join", registry)
    def join(first: str, second: str, *, sep: str = "-") -> str:
        return f"{first}{sep}{second}"

    assert join("a", "b") == "a-b"
    assert join("a", second="b", sep="+") == "a+b"
    assert registry["join"][SUCCESS_KEY] == 2


def test_preserves_metadata() -> None:
    registry: Registry = {}

    @collect_stats("documented", registry)
    def documented() -> int:
        """Return one."""
        return 1

    assert documented.__name__ == "documented"
    assert documented.__doc__ == "Return one."


def test_exception_is_not_counted() -> None:
    registry: Registry = {}

    @collect_stats("boom", registry)
    def boom() -> int:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        boom()

    assert registry["boom"] == {"success": 0, "fails": 0}


def test_keys_are_independent() -> None:
    registry: Registry = {}

    @collect_stats("one", registry)
    def one() -> int:
        return 1

    @collect_stats("none", registry)
    def none() -> None:
        return None

    one()
    one()
    none()

    assert registry == {
        "one": {"success": 2, "fails": 0},
        "none": {"success": 0, "fails": 1},
    }


def test_duplicate_key_returns_original_function(
    capsys: pytest.CaptureFixture[str],
) -> None:
    registry: Registry = {}

    @collect_stats("create", registry)
    def first() -> int:
        return 1

    first()
    assert capsys.readouterr().out == ""

    def second() -> int | None:
        return None

    decorated = collect_stats("create", registry)(second)

    assert capsys.readouterr().out == "stats key 'create' is already registered\n"
    assert decorated is second
    assert decorated() is None
    assert registry == {"create": {"success": 1, "fails": 0}}


def test_separate_registries_do_not_interfere() -> None:
    registry_a: Registry = {}
    registry_b: Registry = {}

    @collect_stats("f", registry_a)
    def func_a() -> int:
        return 1

    @collect_stats("f", registry_b)
    def func_b() -> None:
        return None

    func_a()
    func_b()

    assert registry_a == {"f": {"success": 1, "fails": 0}}
    assert registry_b == {"f": {"success": 0, "fails": 1}}
