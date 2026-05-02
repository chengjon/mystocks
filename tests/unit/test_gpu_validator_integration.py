import numpy as np
import pandas as pd

from src.governance.engine.gpu_validator import GPUValidator


def test_validate_adds_quality_summary_without_breaking_rule_outputs():
    data = pd.DataFrame(
        {
            "open": [10.0, 10.0, 10.0],
            "high": [11.0, 9.0, 10.0],
            "low": [9.0, 9.0, 10.0],
            "close": [10.5, 10.5, 10.0],
            "volume": [100, 100, 0],
        }
    )

    validator = GPUValidator()
    validator.use_gpu = False

    results = validator.validate(data, rules=["ohlc", "missing", "suspension"])

    assert len(results["ohlc"]) == 1
    assert results["missing"].empty
    assert len(results["suspension"]) == 1

    quality_summary = results["quality_summary"]
    assert quality_summary["passed"] is False
    assert quality_summary["total_checks"] == 3
    assert quality_summary["passed_checks"] >= 1
    assert quality_summary["failed_checks"] >= 1
    assert quality_summary["quality_score"] < 100.0
    assert isinstance(quality_summary["results"], list)
    assert any(item["check_type"] == "logic_check" for item in quality_summary["results"])


def test_validate_large_dataset_preserves_quality_summary_contract():
    rng = np.random.default_rng(42)
    close = rng.uniform(10.0, 20.0, 100000)
    data = pd.DataFrame(
        {
            "open": close - 0.05,
            "high": close + 0.20,
            "low": close - 0.20,
            "close": close,
            "volume": rng.integers(1000, 10000, 100000),
        }
    )

    validator = GPUValidator()
    validator.use_gpu = False

    results = validator.validate(data, rules=["ohlc", "missing", "suspension"])

    assert results["ohlc"].empty
    assert results["missing"].empty
    assert results["suspension"].empty

    quality_summary = results["quality_summary"]
    assert quality_summary["passed"] is True
    assert quality_summary["total_checks"] == 3
    assert quality_summary["passed_checks"] == 3
    assert quality_summary["failed_checks"] == 0
    assert quality_summary["quality_score"] == 100.0
    assert len(quality_summary["results"]) == 3
