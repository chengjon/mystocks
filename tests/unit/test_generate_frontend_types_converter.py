import importlib
from pathlib import Path

from scripts.generate_frontend_types import PydanticModelExtractor, TypeGenerationConfig
from scripts._generate_frontend_types_cli import generate_index_file as cli_generate_index_file
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


def test_generate_frontend_types_cli_accepts_openapi_spec_argument() -> None:
    helper = importlib.import_module("scripts._generate_frontend_types_cli")
    parser = helper.build_argument_parser()

    args = parser.parse_args(["--openapi-spec", "generated_openapi.json"])

    assert args.openapi_spec == "generated_openapi.json"


def test_generated_types_output_is_deterministic(tmp_path: Path) -> None:
    generator = TypeScriptGenerator()
    models = {
        "AuditLogResponse": {
            "type": "interface",
            "fields": {
                "log_id": {"type": "str"},
            },
        }
    }

    domain_output = generator.generate_domain("admin", models)
    assert "Generated at:" not in domain_output

    generator.write_common_split_files(models, tmp_path)
    assert "Generated at:" not in (tmp_path / "common.ts").read_text(encoding="utf-8")
    assert "Generated at:" not in (tmp_path / "common" / "all.ts").read_text(encoding="utf-8")

    generator.write_generated_types_compat_barrel(tmp_path)
    assert "Generated at:" not in (tmp_path / "generated-types.ts").read_text(encoding="utf-8")

    index_output = cli_generate_index_file(["admin"], tmp_path)
    assert "Generated at:" not in index_output


def test_extractor_recognizes_models_inheriting_from_local_pydantic_base(tmp_path: Path) -> None:
    source_file = tmp_path / "analysis_models.py"
    source_file.write_text(
        """
from pydantic import BaseModel


class ParentRequest(BaseModel):
    request_id: str


class ChildRequest(ParentRequest):
    pred_len: int
""",
        encoding="utf-8",
    )

    extractor = PydanticModelExtractor(TypeGenerationConfig())
    extractor.extract_from_file(source_file)

    assert "ParentRequest" in extractor.models
    assert "ChildRequest" in extractor.models
    assert extractor.models["ChildRequest"]["fields"]["pred_len"]["type"] == "int"
    assert extractor.models["ChildRequest"]["extends"] == ["ParentRequest"]


def test_generator_emits_interface_extends_clause_for_inherited_models() -> None:
    generator = TypeScriptGenerator()
    models = {
        "ParentRequest": {
            "type": "interface",
            "fields": {
                "request_id": {"type": "str"},
            },
            "extends": [],
        },
        "ChildRequest": {
            "type": "interface",
            "fields": {
                "pred_len": {"type": "int"},
            },
            "extends": ["ParentRequest"],
        },
    }

    output = generator.generate_domain("analysis", models)

    assert "export interface ChildRequest extends ParentRequest {" in output
