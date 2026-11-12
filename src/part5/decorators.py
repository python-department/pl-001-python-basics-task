"""Decorators that add bookkeeping around the part5 CRUD operations.

The module provides :func:`collect_stats`, a parametric decorator that counts
how often a function succeeds and how often it fails. The counters are kept in
a *registry* shared with the caller -- a plain dictionary mapping a string key
to a :data:`Stats` record -- so that other code (for example the ``stats``
command of :mod:`src.part5.run_admin`) can read them without knowing
anything about the decorated functions.

A call counts as a failure when the decorated function returns ``None`` -- the
convention every operation in :mod:`src.part5.crud` uses to report that it
printed an explanation and changed nothing. Any other return value, including
a falsy one such as ``0``, counts as a success.
"""

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

    def decorator(func: Callable[P, R | None]) -> Callable[P, R | None]:
        if key in registry:
            print(f"stats key {key}!r is already registered")
            return func

        registry[key] = {SUCCESS_KEY: 0, FAILS_KEY: 0}

        @wraps(func)
        def do_check(*args: P.args, **kwargs: P.kwargs) -> R | None:
            result = func(*args, **kwargs)
            if result is None:
                registry[key][FAILS_KEY] += 1
            else:
                registry[key][SUCCESS_KEY] += 1
            return result

        return do_check

    return decorator
