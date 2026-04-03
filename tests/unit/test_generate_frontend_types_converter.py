import importlib
from pathlib import Path

from scripts._generate_frontend_types_cli import generate_index_file as generate_types_index_file
from scripts.generate_frontend_types import TypeConverter, TypeScriptGenerator


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


def test_single_file_generation_is_deterministic() -> None:
    generator = TypeScriptGenerator()
    models = {
        "AuditLogResponse": {
            "type": "interface",
            "fields": {
                "log_id": {"type": "str"},
            },
        }
    }

    first = generator.generate(models)
    second = generator.generate(models)

    assert "Generated at:" not in first
    assert first == second


def test_domain_generation_is_deterministic() -> None:
    generator = TypeScriptGenerator()
    models = {
        "AuditLogResponse": {
            "type": "interface",
            "fields": {
                "log_id": {"type": "str"},
            },
        }
    }

    first = generator.generate_domain("admin", models)
    second = generator.generate_domain("admin", models)

    assert "Generated at:" not in first
    assert first == second


def test_helper_files_generation_is_deterministic(tmp_path: Path) -> None:
    generator = TypeScriptGenerator()
    models = {
        "UnifiedAuditLog": {
            "type": "interface",
            "fields": {
                "log_id": {"type": "str"},
            },
        }
    }

    generator.write_common_split_files(models, tmp_path)
    generator.write_generated_types_compat_barrel(tmp_path)
    first_common_entry = (tmp_path / "common.ts").read_text(encoding="utf-8")
    first_common_all = (tmp_path / "common" / "all.ts").read_text(encoding="utf-8")
    first_generated_types = (tmp_path / "generated-types.ts").read_text(encoding="utf-8")
    first_index = generate_types_index_file(["common"], tmp_path)

    generator.write_common_split_files(models, tmp_path)
    generator.write_generated_types_compat_barrel(tmp_path)
    second_common_entry = (tmp_path / "common.ts").read_text(encoding="utf-8")
    second_common_all = (tmp_path / "common" / "all.ts").read_text(encoding="utf-8")
    second_generated_types = (tmp_path / "generated-types.ts").read_text(encoding="utf-8")
    second_index = generate_types_index_file(["common"], tmp_path)

    assert "Generated at:" not in first_common_entry
    assert "Generated at:" not in first_common_all
    assert "Generated at:" not in first_generated_types
    assert "Generated at:" not in first_index
    assert first_common_entry == second_common_entry
    assert first_common_all == second_common_all
    assert first_generated_types == second_generated_types
    assert first_index == second_index
