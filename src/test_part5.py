from decimal import Decimal

import pytest

# ---------- импорты тестируемого кода ----------
import part5.crud as crud
import part5.run_admin as run_admin
from part5.cart import add_to_cart, remove_from_cart
from part5.constants import (
    NODE_ID_MAX,
    SEQUENCE_ID_MAX,
    TIMESTAMP_MS_MAX,
)
from part5.crud import (
    CREATE_KEY,
    DELETE_KEY,
    READ_KEY,
    STATS_REGISTRY,
    UPDATE_KEY,
    create_product,
    delete_product,
    generate_snowflake_id,
    read_product,
    update_product,
)
from part5.decorators import FAILS_KEY, SUCCESS_KEY, collect_stats
from part5.snowflake import (
    decode_node_id,
    decode_sequence_id,
    decode_timestamp_ms,
    get_snowflake_id_generator,
)
from part5.storage import NAME_KEY, PRICE_KEY, QUANTITY_KEY
from part5.utils import (
    get_stats_str_representation,
    get_storage_str_representation,
    normalize_price,
    normalize_product_name,
)


# ============================================================
# Общие фикстуры и хелперы
# ============================================================

@pytest.fixture(autouse=True)
def reset_stats():
    """Сбрасывает глобальный реестр перед каждым тестом."""
    for key in (CREATE_KEY, READ_KEY, UPDATE_KEY, DELETE_KEY):
        STATS_REGISTRY[key][SUCCESS_KEY] = 0
        STATS_REGISTRY[key][FAILS_KEY] = 0
    yield


def make_fields(name="apple", price=Decimal("1.00"), quantity=5):
    return {NAME_KEY: name, PRICE_KEY: price, QUANTITY_KEY: quantity}


def fixed_id_gen(value):
    def gen():
        return value
    return gen


def make_storage(quantity=10, pid=1):
    storage, names = {}, set()
    create_product(
        storage, names,
        {NAME_KEY: "apple", PRICE_KEY: Decimal("1.00"), QUANTITY_KEY: quantity},
        lambda: pid,
    )
    return storage, names, pid


# ============================================================
# SNOWFLAKE
# ============================================================

def test_snowflake_roundtrip_decode():
    gen = get_snowflake_id_generator(node_id=5)
    sid = gen()
    assert decode_node_id(sid) == 5
    assert 0 <= decode_sequence_id(sid) <= SEQUENCE_ID_MAX


def test_snowflake_id_range():
    sid = get_snowflake_id_generator()()
    assert 0 < sid < 2**63


def test_snowflake_ids_increase():
    gen = get_snowflake_id_generator()
    ids = [gen() for _ in range(100)]
    assert ids == sorted(ids)
    assert len(set(ids)) == 100


def test_snowflake_node_id_negative(capsys):
    assert get_snowflake_id_generator(node_id=-1) is None
    assert f"node_id must be in [0, {NODE_ID_MAX}], got -1" in capsys.readouterr().out


def test_snowflake_node_id_too_big(capsys):
    assert get_snowflake_id_generator(node_id=NODE_ID_MAX + 1) is None
    assert f"got {NODE_ID_MAX + 1}" in capsys.readouterr().out


def test_snowflake_node_id_max_ok():
    assert get_snowflake_id_generator(node_id=NODE_ID_MAX) is not None


def test_snowflake_epoch_future_rejected(capsys):
    import time
    future = int(time.time() * 1000) + 10_000
    assert get_snowflake_id_generator(epoch_ms=future) is None
    assert "epoch_ms must not be in the future" in capsys.readouterr().out


def test_snowflake_epoch_now_ok():
    import time
    assert get_snowflake_id_generator(epoch_ms=int(time.time() * 1000)) is not None


def test_snowflake_valid_creation_silent(capsys):
    get_snowflake_id_generator()
    assert capsys.readouterr().out == ""


def test_snowflake_sequence_starts_zero(monkeypatch):
    monkeypatch.setattr("part5.snowflake.read_current_millis", lambda epoch: 1000)
    gen = get_snowflake_id_generator(node_id=3)
    ids = [gen() for _ in range(5)]
    assert [decode_sequence_id(i) for i in ids] == [0, 1, 2, 3, 4]
    assert all(decode_node_id(i) == 3 for i in ids)


def test_snowflake_sequence_resets_new_ms(monkeypatch):
    times = iter([1000, 1000, 1001, 1001])
    monkeypatch.setattr(
        "part5.snowflake.read_current_millis", lambda epoch: next(times)
    )
    gen = get_snowflake_id_generator()
    assert [decode_sequence_id(gen()) for _ in range(4)] == [0, 1, 0, 1]


def test_snowflake_sequence_overflow(monkeypatch, capsys):
    monkeypatch.setattr("part5.snowflake.read_current_millis", lambda epoch: 1000)
    gen = get_snowflake_id_generator()
    for _ in range(SEQUENCE_ID_MAX + 1):
        assert gen() is not None
    assert gen() is None
    assert (
        f"sequence_id must be in [0, {SEQUENCE_ID_MAX}], got {SEQUENCE_ID_MAX + 1}"
        in capsys.readouterr().out
    )


def test_snowflake_recovers_next_ms(monkeypatch):
    times = [1000] * (SEQUENCE_ID_MAX + 2) + [1001]
    it = iter(times)
    monkeypatch.setattr(
        "part5.snowflake.read_current_millis", lambda epoch: next(it)
    )
    gen = get_snowflake_id_generator()
    for _ in range(SEQUENCE_ID_MAX + 1):
        gen()
    assert gen() is None
    sid = gen()
    assert sid is not None
    assert decode_sequence_id(sid) == 0


def test_snowflake_timestamp_overflow(monkeypatch, capsys):
    monkeypatch.setattr(
        "part5.snowflake.read_current_millis", lambda epoch: TIMESTAMP_MS_MAX + 1
    )
    gen = get_snowflake_id_generator()
    assert gen() is None
    assert (
        f"timestamp {TIMESTAMP_MS_MAX + 1} ms overflows {TIMESTAMP_MS_MAX} ms"
        in capsys.readouterr().out
    )


def test_snowflake_timestamp_exactly_max(monkeypatch):
    monkeypatch.setattr(
        "part5.snowflake.read_current_millis", lambda epoch: TIMESTAMP_MS_MAX
    )
    assert get_snowflake_id_generator()() is not None


def test_snowflake_generators_independent(monkeypatch):
    monkeypatch.setattr("part5.snowflake.read_current_millis", lambda epoch: 1000)
    a = get_snowflake_id_generator(node_id=1)
    b = get_snowflake_id_generator(node_id=2)
    a(); a(); a()
    sid = b()
    assert decode_node_id(sid) == 2
    assert decode_sequence_id(sid) == 0


def test_snowflake_timestamp_matches_now():
    import time
    before = int(time.time() * 1000)
    gen = get_snowflake_id_generator()
    sid = gen()
    after = int(time.time() * 1000)
    from part5.constants import EPOCH_MS_DEFAULT
    ts = decode_timestamp_ms(sid, EPOCH_MS_DEFAULT)
    assert before <= ts <= after


# ============================================================
# DECORATORS
# ============================================================

def test_stats_registers_zero_counters():
    registry = {}

    @collect_stats("f", registry)
    def f():
        return 1

    assert registry == {"f": {SUCCESS_KEY: 0, FAILS_KEY: 0}}


def test_stats_counts_success_and_fails():
    registry = {}

    @collect_stats("divide", registry)
    def divide(a, b):
        if b == 0:
            return None
        return a / b

    assert divide(10, 4) == 2.5
    assert divide(0, 5) == 0.0
    assert divide(1, 0) is None
    assert registry["divide"] == {SUCCESS_KEY: 2, FAILS_KEY: 1}


def test_stats_falsey_non_none_is_success():
    registry = {}

    @collect_stats("f", registry)
    def f(x):
        return x

    for v in [0, 0.0, "", [], False]:
        f(v)
    assert registry["f"] == {SUCCESS_KEY: 5, FAILS_KEY: 0}


def test_stats_wraps_metadata():
    registry = {}

    @collect_stats("f", registry)
    def original(x):
        """doc"""
        return x

    assert original.__name__ == "original"
    assert original.__doc__ == "doc"


def test_stats_forwards_args():
    registry = {}

    @collect_stats("f", registry)
    def f(a, b=10, *, c=20):
        return a + b + c

    assert f(1, b=2, c=3) == 6
    assert f(1) == 31


def test_stats_busy_key(capsys):
    registry = {"k": {SUCCESS_KEY: 5, FAILS_KEY: 2}}

    @collect_stats("k", registry)
    def f():
        return 1

    assert "stats key 'k' is already registered" in capsys.readouterr().out
    f(); f(); f()
    assert registry["k"] == {SUCCESS_KEY: 5, FAILS_KEY: 2}


def test_stats_busy_key_returns_original():
    registry = {"k": {SUCCESS_KEY: 0, FAILS_KEY: 0}}

    def f():
        return 1

    assert collect_stats("k", registry)(f) is f


def test_stats_exception_not_counted():
    registry = {}

    @collect_stats("f", registry)
    def f():
        raise ValueError("boom")

    with pytest.raises(ValueError):
        f()
    assert registry["f"] == {SUCCESS_KEY: 0, FAILS_KEY: 0}


def test_stats_independent_keys():
    registry = {}

    @collect_stats("a", registry)
    def a():
        return 1

    @collect_stats("b", registry)
    def b():
        return None

    a(); a(); b()
    assert registry["a"] == {SUCCESS_KEY: 2, FAILS_KEY: 0}
    assert registry["b"] == {SUCCESS_KEY: 0, FAILS_KEY: 1}


# ============================================================
# CRUD
# ============================================================

def test_crud_registry_has_four_entries():
    assert set(STATS_REGISTRY) == {CREATE_KEY, READ_KEY, UPDATE_KEY, DELETE_KEY}
    for stats in STATS_REGISTRY.values():
        assert stats == {SUCCESS_KEY: 0, FAILS_KEY: 0}


def test_crud_generate_snowflake_id_ints():
    a = generate_snowflake_id()
    b = generate_snowflake_id()
    assert isinstance(a, int) and isinstance(b, int)
    assert a != b


def test_crud_generate_snowflake_does_not_touch_stats():
    before = {k: dict(v) for k, v in STATS_REGISTRY.items()}
    generate_snowflake_id()
    generate_snowflake_id()
    assert STATS_REGISTRY == before


def test_crud_generate_snowflake_none_when_generator_none(monkeypatch):
    monkeypatch.setattr(crud, "_GENERATOR", None)
    assert generate_snowflake_id() is None


def test_crud_create_success():
    storage, names = {}, set()
    pid = create_product(storage, names, make_fields(), generate_snowflake_id)
    assert pid in storage
    assert storage[pid][NAME_KEY] == "apple"
    assert names == {"apple"}
    assert STATS_REGISTRY[CREATE_KEY][SUCCESS_KEY] == 1


def test_crud_create_blank_name():
    storage, names = {}, set()
    called = []
    pid = create_product(
        storage, names, make_fields(name="   "),
        lambda: called.append(1) or 1,
    )
    assert pid is None
    assert called == []
    assert storage == {} and names == set()
    assert STATS_REGISTRY[CREATE_KEY][FAILS_KEY] == 1


def test_crud_create_duplicate_name():
    storage, names = {}, set()
    create_product(storage, names, make_fields(name="Apple"), generate_snowflake_id)
    called = []
    pid = create_product(
        storage, names, make_fields(name="apple"),
        lambda: called.append(1) or 2,
    )
    assert pid is None
    assert called == []
    assert len(storage) == 1


def test_crud_create_generate_none_is_silent(capsys):
    storage, names = {}, set()
    pid = create_product(storage, names, make_fields(), lambda: None)
    assert pid is None
    assert capsys.readouterr().out == ""
    assert storage == {} and names == set()
    assert STATS_REGISTRY[CREATE_KEY][FAILS_KEY] == 1


def test_crud_create_normalizes_price():
    storage, names = {}, set()
    pid = create_product(
        storage, names, make_fields(price=Decimal("1.005")), fixed_id_gen(42)
    )
    assert storage[pid][PRICE_KEY] == Decimal("1.01")


def test_crud_read_existing():
    storage, names = {}, set()
    pid = create_product(storage, names, make_fields(), fixed_id_gen(1))
    assert read_product(storage, pid) == storage[pid]
    assert STATS_REGISTRY[READ_KEY][SUCCESS_KEY] == 1


def test_crud_read_missing(capsys):
    assert read_product({}, 999) is None
    assert "no product with id 999" in capsys.readouterr().out
    assert STATS_REGISTRY[READ_KEY][FAILS_KEY] == 1


def test_crud_update_success():
    storage, names = {}, set()
    pid = create_product(storage, names, make_fields(), fixed_id_gen(1))
    result = update_product(
        storage, names, pid,
        {NAME_KEY: "Pear", PRICE_KEY: Decimal("2.5"), QUANTITY_KEY: 7},
    )
    assert result == storage[pid]
    assert storage[pid][NAME_KEY] == "pear"
    assert storage[pid][PRICE_KEY] == Decimal("2.50")
    assert storage[pid][QUANTITY_KEY] == 7
    assert names == {"pear"}
    assert STATS_REGISTRY[UPDATE_KEY][SUCCESS_KEY] == 1


def test_crud_update_missing():
    assert update_product({}, set(), 1, {NAME_KEY: "x"}) is None
    assert STATS_REGISTRY[UPDATE_KEY][FAILS_KEY] == 1


def test_crud_update_blank_name():
    storage, names = {}, set()
    pid = create_product(storage, names, make_fields(), fixed_id_gen(1))
    assert update_product(storage, names, pid, {NAME_KEY: "   "}) is None
    assert storage[pid][NAME_KEY] == "apple"


def test_crud_update_duplicate_name():
    storage, names = {}, set()
    create_product(storage, names, make_fields(name="apple"), fixed_id_gen(1))
    pid2 = create_product(storage, names, make_fields(name="pear"), fixed_id_gen(2))
    assert update_product(storage, names, pid2, {NAME_KEY: "apple"}) is None
    assert storage[pid2][NAME_KEY] == "pear"
    assert names == {"apple", "pear"}


def test_crud_update_same_name_allowed():
    storage, names = {}, set()
    pid = create_product(storage, names, make_fields(name="apple"), fixed_id_gen(1))
    assert update_product(storage, names, pid, {NAME_KEY: "apple"}) is not None


def test_crud_delete_success():
    storage, names = {}, set()
    pid = create_product(storage, names, make_fields(), fixed_id_gen(1))
    assert delete_product(storage, names, pid) == pid
    assert storage == {} and names == set()
    assert STATS_REGISTRY[DELETE_KEY][SUCCESS_KEY] == 1


def test_crud_delete_missing(capsys):
    assert delete_product({}, set(), 5) is None
    assert "no product with id 5" in capsys.readouterr().out
    assert STATS_REGISTRY[DELETE_KEY][FAILS_KEY] == 1


def test_crud_names_index_invariant():
    storage, names = {}, set()
    create_product(storage, names, make_fields(name="A"), fixed_id_gen(1))
    create_product(storage, names, make_fields(name="B"), fixed_id_gen(2))
    update_product(storage, names, 1, {NAME_KEY: "C"})
    delete_product(storage, names, 2)
    assert names == {p[NAME_KEY] for p in storage.values()}


def test_crud_each_call_increments_exactly_one_counter():
    storage, names = {}, set()
    create_product(storage, names, make_fields(), fixed_id_gen(1))
    total_before = sum(
        s[SUCCESS_KEY] + s[FAILS_KEY] for s in STATS_REGISTRY.values()
    )
    read_product(storage, 1)
    total_after = sum(
        s[SUCCESS_KEY] + s[FAILS_KEY] for s in STATS_REGISTRY.values()
    )
    assert total_after - total_before == 1


# ============================================================
# CART
# ============================================================

def test_cart_add_success():
    storage, names, pid = make_storage(quantity=10)
    cart = {}
    assert add_to_cart(storage, names, cart, pid, 3) == 3
    assert storage[pid][QUANTITY_KEY] == 7
    assert cart[pid] == 3


def test_cart_add_not_enough(capsys):
    storage, names, pid = make_storage(quantity=2)
    assert add_to_cart(storage, names, {}, pid, 5) is None
    assert "not enough stock" in capsys.readouterr().out


def test_cart_add_missing(capsys):
    storage, names, _ = make_storage()
    assert add_to_cart(storage, names, {}, 999, 1) is None
    assert "no product with id 999" in capsys.readouterr().out


def test_cart_add_accumulates():
    storage, names, pid = make_storage(quantity=10)
    cart = {}
    add_to_cart(storage, names, cart, pid, 2)
    add_to_cart(storage, names, cart, pid, 3)
    assert cart[pid] == 5
    assert storage[pid][QUANTITY_KEY] == 5


def test_cart_remove_success():
    storage, names, pid = make_storage(quantity=10)
    cart = {}
    add_to_cart(storage, names, cart, pid, 5)
    assert remove_from_cart(storage, names, cart, pid, 3) == 2
    assert storage[pid][QUANTITY_KEY] == 8
    assert cart[pid] == 2


def test_cart_remove_empties():
    storage, names, pid = make_storage(quantity=10)
    cart = {}
    add_to_cart(storage, names, cart, pid, 2)
    assert remove_from_cart(storage, names, cart, pid, 2) == 0
    assert pid not in cart
    assert storage[pid][QUANTITY_KEY] == 10


def test_cart_remove_not_in_cart(capsys):
    storage, names, pid = make_storage()
    assert remove_from_cart(storage, names, {}, pid, 1) is None
    assert f"product {pid} is not in the cart" in capsys.readouterr().out


def test_cart_remove_too_many(capsys):
    storage, names, pid = make_storage(quantity=10)
    cart = {}
    add_to_cart(storage, names, cart, pid, 2)
    assert remove_from_cart(storage, names, cart, pid, 5) is None
    assert "cannot remove" in capsys.readouterr().out


def test_cart_sum_invariant():
    storage, names, pid = make_storage(quantity=10)
    cart = {}
    add_to_cart(storage, names, cart, pid, 4)
    add_to_cart(storage, names, cart, pid, 3)
    remove_from_cart(storage, names, cart, pid, 2)
    assert storage[pid][QUANTITY_KEY] + cart.get(pid, 0) == 10


# ============================================================
# UTILS
# ============================================================

def test_utils_normalize_price():
    assert normalize_price(Decimal("1.005")) == Decimal("1.01")
    assert normalize_price(Decimal("1.004")) == Decimal("1.00")


def test_utils_normalize_name():
    assert normalize_product_name("  Gibson   SG  ") == "gibson sg"


def test_utils_empty_storage_table():
    assert get_storage_str_representation({}) == (
        "| ID | name | price | quantity |\n"
        "|----|------|-------|----------|"
    )


def test_utils_storage_table_19_digit_id():
    storage = {
        1288834974657000001: {
            "name": "x", "price": Decimal("1.00"), "quantity": 2,
        }
    }
    lines = get_storage_str_representation(storage).splitlines()
    assert len(lines[0]) == len(lines[1]) == len(lines[2])
    assert "1288834974657000001" in lines[2]


def test_utils_empty_stats_table():
    lines = get_stats_str_representation({}).splitlines()
    assert len(lines) == 2
    assert "command name" in lines[0]
    assert "success rate" in lines[0]


def test_utils_stats_values():
    registry = {
        "create": {SUCCESS_KEY: 2, FAILS_KEY: 1},
        "read":   {SUCCESS_KEY: 0, FAILS_KEY: 0},
        "delete": {SUCCESS_KEY: 5, FAILS_KEY: 0},
    }
    out = get_stats_str_representation(registry)
    assert "| create       | 2       | 1     | 66.67%       |" in out
    assert "| read         | 0       | 0     | 0.00%        |" in out
    assert "| delete       | 5       | 0     | 100.00%      |" in out


def test_utils_stats_insertion_order():
    registry = {
        "z": {SUCCESS_KEY: 1, FAILS_KEY: 0},
        "a": {SUCCESS_KEY: 1, FAILS_KEY: 0},
    }
    out = get_stats_str_representation(registry)
    assert out.index("| z") < out.index("| a")


def test_utils_stats_long_name():
    registry = {"update-everything-twice": {SUCCESS_KEY: 1, FAILS_KEY: 30}}
    out = get_stats_str_representation(registry)
    assert "| update-everything-twice | 1       | 30    | 3.23%        |" in out


def test_utils_stats_rounding():
    registry = {"x": {SUCCESS_KEY: 1, FAILS_KEY: 2}}
    assert "33.33%" in get_stats_str_representation(registry)


# ============================================================
# RUN_ADMIN
# ============================================================

def test_admin_help(capsys):
    run_admin.run_command({}, set(), "help")
    out = capsys.readouterr().out
    assert "Available commands:" in out
    assert "stats" in out


def test_admin_create_prints_int_id(capsys):
    storage, names = {}, set()
    run_admin.run_command(storage, names, "create Apple 1.00 5")
    pid = int(capsys.readouterr().out.strip())
    assert pid in storage
    assert names == {"apple"}


def test_admin_create_invalid_args_not_in_stats(capsys):
    run_admin.run_command({}, set(), "create Apple not-a-price 5")
    assert STATS_REGISTRY[CREATE_KEY] == {SUCCESS_KEY: 0, FAILS_KEY: 0}


def test_admin_read(capsys):
    storage, names = {}, set()
    run_admin.run_command(storage, names, "create Apple 1.00 5")
    pid = int(capsys.readouterr().out.strip())
    run_admin.run_command(storage, names, f"read {pid}")
    assert "apple" in capsys.readouterr().out


def test_admin_read_invalid_id_not_in_stats(capsys):
    run_admin.run_command({}, set(), "read abc")
    assert STATS_REGISTRY[READ_KEY] == {SUCCESS_KEY: 0, FAILS_KEY: 0}


def test_admin_delete(capsys):
    storage, names = {}, set()
    run_admin.run_command(storage, names, "create Apple 1.00 5")
    pid = int(capsys.readouterr().out.strip())
    run_admin.run_command(storage, names, f"delete {pid}")
    assert storage == {}
    assert STATS_REGISTRY[DELETE_KEY][SUCCESS_KEY] == 1


def test_admin_update(capsys):
    storage, names = {}, set()
    run_admin.run_command(storage, names, "create Apple 1.00 5")
    pid = int(capsys.readouterr().out.strip())
    run_admin.run_command(storage, names, f"update {pid} Pear 2.50 3")
    assert storage[pid][NAME_KEY] == "pear"
    assert storage[pid][PRICE_KEY] == Decimal("2.50")


def test_admin_stats_command(capsys):
    storage, names = {}, set()
    run_admin.run_command(storage, names, "create Apple 1.00 5")
    capsys.readouterr()
    run_admin.run_command(storage, names, "stats")
    out = capsys.readouterr().out
    assert "command name" in out
    assert "create" in out


def test_admin_stats_with_extra_words(capsys):
    run_admin.run_command({}, set(), "stats create")
    assert "'stats create' is not a command" in capsys.readouterr().out


def test_admin_unknown_command(capsys):
    run_admin.run_command({}, set(), "nonsense")
    assert "'nonsense' is not a command" in capsys.readouterr().out


def test_admin_show_empty(capsys):
    run_admin.run_command({}, set(), "show")
    out = capsys.readouterr().out
    assert "ID" in out and "name" in out


def test_admin_main_exits():
    from unittest.mock import patch
    with patch("builtins.input", side_effect=["exit"]):
        run_admin.main()


def test_admin_main_invalid_args_message(capsys):
    from unittest.mock import patch
    with patch("builtins.input", side_effect=["create Apple x 1", "exit"]):
        run_admin.main()
    assert "names a command but its arguments are invalid" in capsys.readouterr().out