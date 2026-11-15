import time
from decimal import Decimal

import pytest
from src.part5 import run_admin
from src.part5.constants import EPOCH_MS_DEFAULT
from src.part5.crud import STATS_REGISTRY
from src.part5.run_admin import (
    HELP_TEXT,
    PROMPT,
    build_fields,
    main,
    print_result,
    run_command,
    show_help,
)
from src.part5.snowflake import decode_timestamp_ms, read_current_millis
from src.part5.storage import NAME_KEY, PRICE_KEY, QUANTITY_KEY, Product
from src.part5.utils import get_stats_str_representation


def run(
    storage: dict[int, Product],
    names: set[str],
    line: str,
    capsys: pytest.CaptureFixture[str],
) -> tuple[bool, str]:
    keep_running = run_command(storage, names, line)
    return keep_running, capsys.readouterr().out


def create(
    storage: dict[int, Product],
    names: set[str],
    line: str,
    capsys: pytest.CaptureFixture[str],
) -> int:
    _, out = run(storage, names, line, capsys)
    return int(out.strip())


def test_constants() -> None:
    assert PROMPT == "admin> "
    assert HELP_TEXT.splitlines()[-5].startswith("  stats ")
    assert HELP_TEXT.splitlines()[-6].startswith("  delete <id>")
    assert HELP_TEXT.startswith("Available commands:\n  help ")
    assert HELP_TEXT.endswith("needs no quoting.")


def test_show_help(capsys: pytest.CaptureFixture[str]) -> None:
    show_help()

    assert capsys.readouterr().out == HELP_TEXT + "\n"


def test_print_result(capsys: pytest.CaptureFixture[str]) -> None:
    print_result(None)
    assert capsys.readouterr().out == ""

    print_result(0)
    print_result("text")
    assert capsys.readouterr().out == "0\ntext\n"


def test_build_fields() -> None:
    assert build_fields(["Gibson", "SG"], "9.99", "3") == {
        NAME_KEY: "Gibson SG",
        PRICE_KEY: Decimal("9.99"),
        QUANTITY_KEY: 3,
    }


def test_help_and_exit(capsys: pytest.CaptureFixture[str]) -> None:
    assert run({}, set(), "help", capsys) == (True, HELP_TEXT + "\n")
    assert run({}, set(), "exit", capsys) == (False, "")


def test_create_prints_snowflake_id(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[int, Product] = {}
    names: set[str] = set()

    product_id = create(storage, names, "create Gibson SG Junior 999.99 3", capsys)

    assert storage == {
        product_id: {
            NAME_KEY: "gibson sg junior",
            PRICE_KEY: Decimal("999.99"),
            QUANTITY_KEY: 3,
        }
    }
    assert names == {"gibson sg junior"}
    created_at = decode_timestamp_ms(product_id, EPOCH_MS_DEFAULT)
    assert abs(created_at - time.time() * 1000) < 5000
    assert read_current_millis(EPOCH_MS_DEFAULT) > 0


def test_create_duplicate_name(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[int, Product] = {}
    names: set[str] = set()
    create(storage, names, "create saw 1 1", capsys)

    assert run(storage, names, "create SAW 2 2", capsys) == (
        True,
        "product name 'saw' is already taken\n",
    )
    assert len(storage) == 1


@pytest.mark.parametrize("line", ["create", "create 1 2", "create saw", "create saw 1"])
def test_create_wrong_arguments(line: str, capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[int, Product] = {}

    assert run(storage, set(), line, capsys) == (
        True,
        f"'{line}' is not a command\n",
    )
    assert storage == {}


def test_read(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[int, Product] = {}
    names: set[str] = set()
    product_id = create(storage, names, "create saw 9.9 5", capsys)

    keep, out = run(storage, names, f"read {product_id}", capsys)

    assert keep is True
    assert out == f"{storage[product_id]}\n"
    assert run(storage, names, "read 12345", capsys) == (
        True,
        "no product with id 12345\n",
    )


def test_update(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[int, Product] = {}
    names: set[str] = set()
    product_id = create(storage, names, "create saw 9.9 5", capsys)

    keep, out = run(storage, names, f"update {product_id} Big Saw 1.5 2", capsys)

    assert keep is True
    assert storage[product_id] == {
        NAME_KEY: "big saw",
        PRICE_KEY: Decimal("1.50"),
        QUANTITY_KEY: 2,
    }
    assert out == f"{storage[product_id]}\n"
    assert names == {"big saw"}


def test_update_missing_and_wrong_arguments(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert run({}, set(), "update 5 saw 1 1", capsys) == (
        True,
        "no product with id 5\n",
    )
    for line in ("update", "update 5", "update 5 1 1", "update 5 saw"):
        assert run({}, set(), line, capsys) == (True, f"'{line}' is not a command\n")


def test_delete(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[int, Product] = {}
    names: set[str] = set()
    product_id = create(storage, names, "create saw 9.9 5", capsys)

    assert run(storage, names, f"delete {product_id}", capsys) == (
        True,
        f"{product_id}\n",
    )
    assert storage == {} and names == set()
    assert run(storage, names, f"delete {product_id}", capsys) == (
        True,
        f"no product with id {product_id}\n",
    )


def test_show(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[int, Product] = {}
    names: set[str] = set()

    assert run(storage, names, "show", capsys) == (
        True,
        "| ID | name | price | quantity |\n|----|------|-------|----------|\n",
    )
    product_id = create(storage, names, "create saw 9.9 5", capsys)

    out = run(storage, names, "show", capsys)[1]

    assert f"| {product_id} | saw  | 9.90  | 5        |" in out


def test_stats_prints_registry_table(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[int, Product] = {}

    keep, out = run(storage, set(), "stats", capsys)

    assert keep is True
    assert out == get_stats_str_representation(STATS_REGISTRY) + "\n"
    assert out.splitlines()[0].startswith("| command name ")
    assert [line.split("|")[1].strip() for line in out.splitlines()[2:]] == [
        "create",
        "read",
        "update",
        "delete",
    ]
    assert storage == {}


def test_stats_with_extra_words_is_not_a_command(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert run({}, set(), "stats create", capsys) == (
        True,
        "'stats create' is not a command\n",
    )


def test_commands_update_statistics(capsys: pytest.CaptureFixture[str]) -> None:
    storage: dict[int, Product] = {}
    names: set[str] = set()
    before = {key: dict(value) for key, value in STATS_REGISTRY.items()}

    product_id = create(storage, names, "create saw 9.9 5", capsys)
    run(storage, names, "create saw 9.9 5", capsys)
    run(storage, names, f"read {product_id}", capsys)
    run(storage, names, "read 1", capsys)
    run(storage, names, f"update {product_id} axe 1 1", capsys)
    run(storage, names, "update 1 axe 1 1", capsys)
    run(storage, names, f"delete {product_id}", capsys)
    run(storage, names, f"delete {product_id}", capsys)

    for key in ("create", "read", "update", "delete"):
        assert STATS_REGISTRY[key]["success"] == before[key]["success"] + 1
        assert STATS_REGISTRY[key]["fails"] == before[key]["fails"] + 1


def test_unparsable_arguments_are_not_counted() -> None:
    before = {key: dict(value) for key, value in STATS_REGISTRY.items()}

    with pytest.raises(ValueError):
        run_command({}, set(), "read abc")
    with pytest.raises(ValueError):
        run_command({}, set(), "delete 1.5")
    with pytest.raises(ValueError):
        run_command({}, set(), "create saw 1 x")
    with pytest.raises(ArithmeticError):
        run_command({}, set(), "create saw x 1")
    with pytest.raises(ValueError):
        run_command({}, set(), "update abc saw 1 1")

    assert STATS_REGISTRY == before


@pytest.mark.parametrize("line", ["", "unknown", "help me", "exit now", "show all"])
def test_unknown_commands(line: str, capsys: pytest.CaptureFixture[str]) -> None:
    assert run({}, set(), line, capsys) == (True, f"'{line}' is not a command\n")


def test_main_loop(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    lines = iter(
        [
            "  create saw 9.9 5  ",
            "read abc",
            "create saw x 1",
            "bogus",
            "show",
            "exit",
            "show",
        ]
    )
    prompts: list[str] = []

    def fake_input(prompt: str) -> str:
        prompts.append(prompt)
        return next(lines)

    monkeypatch.setattr("builtins.input", fake_input)

    main()

    out = capsys.readouterr().out
    assert prompts == [PROMPT] * 6
    assert "'read abc' names a command but its arguments are invalid\n" in out
    assert "'create saw x 1' names a command but its arguments are invalid\n" in out
    assert "'bogus' is not a command\n" in out
    assert "| saw  | 9.90  | 5        |" in out
    assert run_admin.__name__ == "src.part5.run_admin"
