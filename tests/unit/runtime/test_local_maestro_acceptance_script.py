from __future__ import annotations

import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_local_maestro_acceptance_script_exists_and_references_validated_commands() -> None:
    script_path = PROJECT_ROOT / "scripts" / "runtime" / "run_local_maestro_acceptance.sh"

    assert script_path.is_file()

    content = script_path.read_text(encoding="utf-8")
    assert "python scripts/runtime/coordctl.py work list --output json" in content
    assert "python scripts/runtime/smoke_mongo_multicli.py" in content
    assert "python scripts/runtime/smoke_graphiti_preflight.py --actor-cli cli-preflight" in content
    assert "python scripts/runtime/export_collab_snapshots.py --output-dir /tmp/mongo-collab-snapshots-codex" in content


def test_local_maestro_acceptance_script_has_valid_bash_syntax() -> None:
    script_path = PROJECT_ROOT / "scripts" / "runtime" / "run_local_maestro_acceptance.sh"

    subprocess.run(["bash", "-n", str(script_path)], check=True)
