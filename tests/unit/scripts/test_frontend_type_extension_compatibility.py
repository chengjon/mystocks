from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_type_extension_compatibility_smoke_fixture_exists() -> None:
    fixture = PROJECT_ROOT / "web/frontend/src/api/types/compatibility-smoke.ts"

    assert fixture.is_file()

    source = fixture.read_text(encoding="utf-8")

    assert 'from "@/api/types"' in source
    assert 'from "@/api/types/extensions"' in source
    assert "TypeExtensionCompatibilitySmoke" in source
