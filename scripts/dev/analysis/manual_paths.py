from __future__ import annotations

from pathlib import Path


MANUAL_ROOT_RELATIVE = Path("docs/references/function-classification-manual")
MANUAL_METADATA_DIRNAME = "metadata"


def get_manual_root(project_root: Path) -> Path:
    return project_root / MANUAL_ROOT_RELATIVE


def get_manual_metadata_dir(project_root: Path) -> Path:
    return get_manual_root(project_root) / MANUAL_METADATA_DIRNAME
