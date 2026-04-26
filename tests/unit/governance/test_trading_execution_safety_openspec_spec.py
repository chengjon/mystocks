from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRADING_EXECUTION_SAFETY_SPEC_PATH = PROJECT_ROOT / "openspec" / "specs" / "trading-execution-safety" / "spec.md"


def test_trading_execution_safety_spec_mentions_phase_d_requirements() -> None:
    spec_text = TRADING_EXECUTION_SAFETY_SPEC_PATH.read_text(encoding="utf-8")

    assert "Trading Domain Safety Contract" in spec_text
    assert "Trading Pre-Execution Risk Gate" in spec_text
    assert "Idempotent Trading Submission" in spec_text
    assert "Trading Confirmation Policy" in spec_text
    assert "Trading Audit Minimum Fields" in spec_text
    assert "simulated, experimental, or production-eligible" in spec_text
    assert "configured capital, concentration, or exposure threshold" in spec_text
    assert "explicit confirmation step or approved equivalent safeguard" in spec_text
    assert "request identity, actor identity, execution path, decision outcome, and timestamp" in spec_text
    assert "persisted to durable storage" in spec_text
