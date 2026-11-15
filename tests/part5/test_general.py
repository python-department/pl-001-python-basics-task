from decimal import Decimal, InvalidOperation

import pytest

from src.part5.decorators import collect_stats
from src.part5.utils import get_stats_str_representation


def test_collect_stats():
    registry = {}

    @collect_stats("divide", registry)
    def divide(a, b):
        if b == 0:
            print("division by zero")
            return None
        return a / b

    print(registry)          # {'divide': {'success': 0, 'fails': 0}}

    print(divide(10, 4))     # 2.5
    print(divide(0, 5))      # 0.0 (ложный результат, но не None: считается успехом)
    print(divide(1, 0))      # division by zero (печатает сама divide)
                            # None

    print(registry)          # {'divide': {'success': 2, 'fails': 1}}

def test_get_stats_str_representation():
    print()
    print(get_stats_str_representation({"create": {"success": 2, "fails": 1}, "read": {"success": 0, "fails": 0}, "delete": {"success": 5, "fails": 0}}))