from collections.abc import Callable
from typing import Final


SUCCESS_KEY: Final[str] = "success"
FAILS_KEY: Final[str] = "fails"


type Stats = dict[str, int]
type Registry = dict[str, Stats]


def collect_stats[**P, R](
    key: str, registry: Registry
) -> Callable[[Callable[P, R | None]], Callable[P, R | None]]:

    def decorator(func: Callable[P, R | None]) -> Callable[P, R | None]:
        if key in registry:
            print(f"stats key {key!r} is already registered")
            return func

        registry[key] = {SUCCESS_KEY: 0, FAILS_KEY: 0}

        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
            result = func(*args, **kwargs)
            if result is None:
                registry[key][FAILS_KEY] += 1
            else:
                registry[key][SUCCESS_KEY] += 1
            return result

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator
