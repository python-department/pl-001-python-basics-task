from collections.abc import Callable
from functools import wraps
from typing import Final, ParamSpec, TypeVar


SUCCESS_KEY: Final = "success"
FAILS_KEY: Final = "fails"

type Stats = dict[str, int]
type Registry = dict[str, Stats]

P = ParamSpec("P")
T = TypeVar("T")


def collect_stats(
    key: str,
    registry: Registry,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        if key in registry:
            print(f"stats key {key!r} is already registered")
            return func

        registry[key] = {SUCCESS_KEY: 0, FAILS_KEY: 0}

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            result = func(*args, **kwargs)
            if result is None:
                registry[key][FAILS_KEY] += 1
            else:
                registry[key][SUCCESS_KEY] += 1
            return result

        return wrapper

    return decorator
