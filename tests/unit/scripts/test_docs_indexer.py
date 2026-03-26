from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_docs_indexer_category_indices_stay_under_requested_path(tmp_path: Path) -> None:
    docs_root = tmp_path / "docs"
    guides_root = docs_root / "guides"
    topic_dir = guides_root / "topic"
    topic_dir.mkdir(parents=True)
    (topic_dir / "example.md").write_text("# Example\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "dev" / "tools" / "docs_indexer.py"),
            "--path",
            str(guides_root),
            "--output",
            str(guides_root / "INDEX.md"),
            "--categories",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (guides_root / "topic" / "INDEX.md").is_file()
    assert not (docs_root / "topic" / "INDEX.md").exists()

    category_index = (guides_root / "topic" / "INDEX.md").read_text(encoding="utf-8")

    assert "[example](example.md)" in category_index
    assert "(topic/example.md)" not in category_index
