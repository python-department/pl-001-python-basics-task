import functools
from collections.abc import Callable
from typing import Any, Final


SUCCESS_KEY: Final[str] = "success"
FAILS_KEY: Final[str] = "fails"


type Stats = dict[str, int]
type Registry = dict[str, Stats]


def collect_stats[**P, R](
    key: str, registry: Registry
) -> Callable[[Callable[P, R | None]], Callable[P, R | None]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if key in registry:
            print(f"stats key {key!r} is already registered")
            return func
        registry[key] = {SUCCESS_KEY: 0, FAILS_KEY: 0}

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            if result is None:
                registry[key][FAILS_KEY] += 1
            else:
                registry[key][SUCCESS_KEY] += 1

            return result

        return wrapper

    return decorator
