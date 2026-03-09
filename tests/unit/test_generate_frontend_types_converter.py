import importlib
from pathlib import Path

from scripts.generate_frontend_types import TypeConverter


def _line_count(path: str) -> int:
    return sum(1 for _ in Path(path).read_text(encoding="utf-8").splitlines())


def test_convert_union_tuple_style_list_annotations() -> None:
    result = TypeConverter.convert_type("Union[(List[float], List[List[float]])]")
    assert result == "number[] | number[][]"


def test_convert_optional_dict_tuple_style_annotations() -> None:
    result = TypeConverter.convert_type("Optional[Dict[(str, List[Any])]]")
    assert result == "Record<string, unknown[]> | null"


def test_convert_nested_list_preserves_dimension() -> None:
    result = TypeConverter.convert_type("List[List[float]]")
    assert result == "number[][]"


def test_generate_frontend_types_module_stays_below_800_lines() -> None:
    assert _line_count("scripts/generate_frontend_types.py") < 800


def test_generate_frontend_types_cli_helper_remains_importable() -> None:
    helper = importlib.import_module("scripts._generate_frontend_types_cli")
    module = importlib.import_module("scripts.generate_frontend_types")

    assert callable(helper.build_argument_parser)
    assert callable(helper.run_generation)
    assert callable(module.main)
