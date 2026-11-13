from collections.abc import Callable
from functools import wraps
from typing import Final


SUCCESS_KEY: Final[str] = "success"
FAILS_KEY: Final[str] = "fails"


type Stats = dict[str, int]
type Registry = dict[str, Stats]


def collect_stats[**P, R](
    key: str, registry: Registry
) -> Callable[[Callable[P, R | None]], Callable[P, R | None]]:

    def decorator(
        function: Callable[P, R | None],
    ) -> Callable[P, R | None]:
        if key in registry:
            print(f"stats key {key!r} is already registered")
            return function

        registry[key] = {SUCCESS_KEY: 0, FAILS_KEY: 0}

        @wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
            result = function(*args, **kwargs)
            if result is None:
                registry[key][FAILS_KEY] += 1
            else:
                registry[key][SUCCESS_KEY] += 1
            return result

        return wrapper

    return decorator
