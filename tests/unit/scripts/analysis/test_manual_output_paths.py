from __future__ import annotations

import importlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
EXPECTED_MANUAL_ROOT = PROJECT_ROOT / "docs" / "references" / "function-classification-manual"
EXPECTED_METADATA_DIR = EXPECTED_MANUAL_ROOT / "metadata"


def test_manual_paths_helpers_resolve_references_location() -> None:
    manual_paths = importlib.import_module("scripts.dev.analysis.manual_paths")

    assert manual_paths.get_manual_root(PROJECT_ROOT) == EXPECTED_MANUAL_ROOT
    assert manual_paths.get_manual_metadata_dir(PROJECT_ROOT) == EXPECTED_METADATA_DIR


def test_analysis_scripts_import_and_expose_new_manual_paths() -> None:
    module_names = [
        "scripts.dev.analysis.scan_codebase",
        "scripts.dev.analysis.generate_docs",
        "scripts.dev.analysis.generate_optimization_roadmap",
        "scripts.dev.analysis.generate_consolidation_guide",
        "scripts.dev.analysis.detect_duplicates",
    ]

    for module_name in module_names:
        module = importlib.import_module(module_name)
        assert module.MANUAL_ROOT == EXPECTED_MANUAL_ROOT
        assert module.MANUAL_METADATA_DIR == EXPECTED_METADATA_DIR


def test_markdown_writer_module_uses_new_manual_root_constant() -> None:
    markdown_writer = importlib.import_module("scripts.dev.analysis.utils.markdown_writer")

    assert Path(markdown_writer.DEFAULT_OUTPUT_DIR) == EXPECTED_MANUAL_ROOT
