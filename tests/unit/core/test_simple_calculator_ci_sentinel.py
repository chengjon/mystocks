from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import types

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = PROJECT_ROOT / "src"
CORE_ROOT = SRC_ROOT / "core"
MODULE_NAME = "src.core.simple_calculator"
MODULE_PATH = CORE_ROOT / "simple_calculator.py"

src_package = sys.modules.setdefault("src", types.ModuleType("src"))
src_package.__path__ = [str(SRC_ROOT)]

core_package = sys.modules.setdefault("src.core", types.ModuleType("src.core"))
core_package.__path__ = [str(CORE_ROOT)]
setattr(src_package, "core", core_package)

MODULE_SPEC = importlib.util.spec_from_file_location(MODULE_NAME, MODULE_PATH)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None

simple_calculator = importlib.util.module_from_spec(MODULE_SPEC)
sys.modules[MODULE_NAME] = simple_calculator
MODULE_SPEC.loader.exec_module(simple_calculator)
setattr(core_package, "simple_calculator", simple_calculator)

SimpleCalculator = simple_calculator.SimpleCalculator
create_calculator = simple_calculator.create_calculator
perform_calculation_sequence = simple_calculator.perform_calculation_sequence


def test_basic_operations_and_statistics_cover_core_behaviors() -> None:
    calculator = SimpleCalculator()

    assert calculator.get_last_result() is None
    assert calculator.get_operation_count() == 0
    assert calculator.get_statistics() == {
        "last_result": None,
        "operation_count": 0,
        "is_first_operation": True,
    }

    assert calculator.add(2, 3) == 5
    assert calculator.subtract(10, 4) == 6
    assert calculator.multiply(3, 4) == 12
    assert calculator.divide(12, 3) == 4.0
    assert calculator.power(2, 5) == 32

    assert calculator.get_last_result() == 32
    assert calculator.get_operation_count() == 5
    assert calculator.get_statistics() == {
        "last_result": 32,
        "operation_count": 5,
        "is_first_operation": False,
    }

    calculator.reset()
    assert calculator.get_last_result() is None
    assert calculator.get_operation_count() == 0


def test_list_helpers_validation_and_safe_divide_cover_error_branches() -> None:
    calculator = SimpleCalculator()

    assert calculator.calculate_average([1, 2, 3, 4]) == 2.5
    assert calculator.find_max([1, 9, 3]) == 9
    assert calculator.find_min([7, 2, 5]) == 2
    assert calculator.sum_list([1, 2, 3, 4]) == 10
    assert calculator.validate_input(3.14) is True
    assert calculator.safe_divide(9, 3) == 3.0
    assert calculator.safe_divide(9, 0) == 0

    with pytest.raises(ValueError, match="除数不能为零"):
        calculator.divide(1, 0)

    with pytest.raises(ValueError, match="数字列表不能为空"):
        calculator.calculate_average([])

    with pytest.raises(ValueError, match="数字列表不能为空"):
        calculator.find_max([])

    with pytest.raises(ValueError, match="数字列表不能为空"):
        calculator.find_min([])

    with pytest.raises(TypeError, match="输入必须是数字"):
        calculator.validate_input("invalid")


def test_factory_and_sequence_helpers_cover_remaining_paths() -> None:
    calculator = create_calculator()

    assert isinstance(calculator, SimpleCalculator)
    assert perform_calculation_sequence(
        calculator,
        [
            {"type": "add", "a": 2, "b": 3},
            {"type": "subtract", "a": 9, "b": 4},
            {"type": "multiply", "a": 2, "b": 5},
            {"type": "divide", "a": 12, "b": 4},
        ],
    ) == [5, 5, 10, 3.0]

    with pytest.raises(ValueError, match="不支持的操作类型: noop"):
        perform_calculation_sequence(calculator, [{"type": "noop", "a": 1, "b": 1}])
