import numpy as np
import pandas as pd
import pytest

try:
    import cudf
except ImportError:
    cudf = None
from src.governance.engine.gpu_validator import GPUValidator


@pytest.mark.skipif(cudf is None, reason="cudf not installed")
class TestGPUValidator:

    def test_ohlc_validation(self):
        # 构造数据：
        # Row 0: Normal
        # Row 1: High < Open (异常)
        # Row 2: Low > Close (异常)
        data = pd.DataFrame(
            {
                "open": [10.0, 10.0, 10.0],
                "close": [11.0, 11.0, 11.0],
                "high": [12.0, 9.0, 12.0],  # 9.0 < 10.0 (Open) -> Error
                "low": [9.0, 9.0, 12.0],  # 12.0 > 11.0 (Close) -> Error
                "volume": [100, 100, 100],
            }
        )

        validator = GPUValidator()
        results = validator.validate(data, rules=["ohlc"])

        invalid_rows = results["ohlc"]
        # 转换回 pandas 以便断言，或者直接用 cuDF API
        if hasattr(invalid_rows, "to_pandas"):
            df_invalid = invalid_rows.to_pandas()
        else:
            df_invalid = invalid_rows

        # 应该有 2 行异常
        assert len(df_invalid) == 2
        assert 1 in df_invalid.index
        assert 2 in df_invalid.index

    def test_missing_validation(self):
        data = pd.DataFrame(
            {
                "open": [10.0, np.nan],
                "close": [11.0, 11.0],
                "high": [12.0, 12.0],
                "low": [9.0, 9.0],
                "volume": [100, 100],
            }
        )

        validator = GPUValidator()
        results = validator.validate(data, rules=["missing"])

        invalid_rows = results["missing"]
        assert len(invalid_rows) == 1

        if hasattr(invalid_rows, "to_pandas"):
            df_invalid = invalid_rows.to_pandas()
        else:
            df_invalid = invalid_rows

        assert 1 in df_invalid.index
