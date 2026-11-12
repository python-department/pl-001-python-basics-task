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
from typing import Any, Final


SUCCESS_KEY: Final[str] = "success"
FAILS_KEY: Final[str] = "fails"


type Stats = dict[str, int]
type Registry = dict[str, Stats]


def collect_stats[**P, R](
    key: str, registry: Registry
) -> Callable[[Callable[P, R | None]], Callable[P, R | None]]:
    """Build a decorator that counts successful and failed calls of a function.

    Decorating registers a fresh record ``{"success": 0, "fails": 0}`` in
    ``registry`` under ``key``. Every call of the decorated function then
    updates that record in place: a call that returns ``None`` adds one to the
    failure counter, any other result adds one to the success counter. The
    result is passed through unchanged, and a call that raises an exception
    is not counted at all.

    If ``key`` is already in ``registry``, a message is printed, the existing
    record is left untouched and the function is returned undecorated, so its
    calls never mix into the counters of whoever registered the key first.

    Args:
        key: The registry key to keep this function's counters under, for
            example the name of the console command it implements.
        registry: The dictionary that receives the counters; modified in
            place when the function is decorated and on every later call.

    Returns:
        A decorator for a function whose result is either some value or
        ``None``. The decorated function has the same signature, name and
        docstring as the original (see :func:`functools.wraps`).
    """
    def decorator(function: Callable[..., Any]) -> Callable[..., Any]:
        if key in registry:
            print(f"stats key {repr(key)} is already registered")
            return function

        registry[key] = {SUCCESS_KEY: 0, FAILS_KEY: 0}

        @wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            res = function(*args, **kwargs)
            if res is None:
                registry[key][FAILS_KEY] += 1
            else:
                registry[key][SUCCESS_KEY] += 1

            return res

        return wrapper
        
    return decorator
