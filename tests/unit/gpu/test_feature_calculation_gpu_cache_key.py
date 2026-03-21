import importlib.util
from pathlib import Path
from unittest.mock import patch

import pandas as pd


def _load_part2_mixin():
    module_path = (
        Path(__file__).resolve().parents[3]
        / "src/gpu/acceleration/feature_calculation_gpu/feature_calculation_gpu_methods/part2.py"
    )
    spec = importlib.util.spec_from_file_location("feature_calculation_gpu_part2", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module.FeatureCalculationGPUCalculatePriceVolumeMixin


def test_generate_cache_key_marks_md5_as_non_security_use() -> None:
    engine = _load_part2_mixin()()
    data = pd.DataFrame({"close": [1.0, 2.0, 3.0, 4.0, 5.0]})
    feature_types = ["technical"]

    with patch("hashlib.md5") as mock_md5:
        mock_md5.return_value.hexdigest.return_value = "cache-key"

        cache_key = engine._generate_cache_key(data, feature_types)

    assert cache_key == "cache-key"
    mock_md5.assert_called_once()
    _, kwargs = mock_md5.call_args
    assert kwargs["usedforsecurity"] is False
