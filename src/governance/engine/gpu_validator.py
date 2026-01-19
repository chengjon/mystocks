import logging
import numpy as np
from typing import Any, Dict, List, Optional
from .base import BaseValidator

logger = logging.getLogger(__name__)

# 尝试导入 cudf
try:
    import cudf
    import cupy

    # 简单的 check，不一定代表运行时真的有 GPU
    _CUDF_IMPORTED = True
except ImportError:
    _CUDF_IMPORTED = False
    cudf = None


class GPUValidator(BaseValidator):
    """
    基于 cuDF 的 GPU 验证器 (带 CPU Fallback)

    设计理念：
    优先使用 GPU 加速，如果环境不支持 GPU（如 CI/CD 环境），则自动降级到 Pandas 实现。
    """

    def __init__(self):
        self.use_gpu = _CUDF_IMPORTED
        if self.use_gpu:
            try:
                # 尝试初始化一个小对象来验证 GPU 是否真正可用
                cudf.Series([1])
            except Exception as e:
                logger.warning(f"检测到 cudf 但无法连接 GPU: {e}。自动降级到 CPU 模式。")
                self.use_gpu = False

    def validate(self, data: Any, rules: List[str] = None) -> Dict[str, Any]:
        """
        执行验证

        Args:
            data: pandas.DataFrame 或 cudf.DataFrame
            rules: 规则列表，如 ['ohlc', 'missing', 'limit_move']

        Returns:
            Dict: { 'rule_name': invalid_rows_dataframe }
        """
        if self.use_gpu:
            return self._validate_gpu(data, rules)
        else:
            return self._validate_cpu(data, rules)

    def _validate_gpu(self, data: Any, rules: List[str] = None) -> Dict[str, Any]:
        # 自动转换 pandas 到 cudf
        if hasattr(data, "to_pandas"):  # 已经是 cudf (duck typing)
            gdf = data
        else:
            try:
                gdf = cudf.DataFrame.from_pandas(data)
            except Exception as e:
                logger.error(f"数据传输到 GPU 失败: {e}。尝试降级到 CPU。")
                self.use_gpu = False
                return self._validate_cpu(data, rules)

        results = {}
        rules = rules or ["ohlc", "missing"]

        for rule in rules:
            try:
                if rule == "ohlc":
                    results["ohlc"] = self._validate_ohlc_gpu(gdf)
                elif rule == "missing":
                    results["missing"] = self._validate_missing_gpu(gdf)
                elif rule == "suspension":
                    results["suspension"] = self._validate_suspension_gpu(gdf)
                else:
                    logger.warning(f"未知规则: {rule}")
            except Exception as e:
                logger.error(f"GPU规则 {rule} 执行失败: {e}")

        return results

    def _validate_cpu(self, data: Any, rules: List[str] = None) -> Dict[str, Any]:
        """CPU 模式实现 (Pandas)"""
        import pandas as pd

        if hasattr(data, "to_pandas"):
            df = data.to_pandas()
        else:
            df = data

        results = {}
        rules = rules or ["ohlc", "missing"]

        for rule in rules:
            try:
                if rule == "ohlc":
                    results["ohlc"] = self._validate_ohlc_cpu(df)
                elif rule == "missing":
                    results["missing"] = self._validate_missing_cpu(df)
                elif rule == "suspension":
                    results["suspension"] = self._validate_suspension_cpu(df)
                else:
                    logger.warning(f"未知规则: {rule}")
            except Exception as e:
                logger.error(f"CPU规则 {rule} 执行失败: {e}")
        return results

    # ---------------- GPU Implementations ----------------

    def _validate_ohlc_gpu(self, gdf: Any) -> Any:
        max_oc = gdf["open"].where(gdf["open"] > gdf["close"], gdf["close"])
        min_oc = gdf["open"].where(gdf["open"] < gdf["close"], gdf["close"])

        invalid_high = gdf["high"] < max_oc
        invalid_low = gdf["low"] > min_oc

        return gdf[invalid_high | invalid_low]

    def _validate_missing_gpu(self, gdf: Any) -> Any:
        critical_cols = [c for c in ["open", "high", "low", "close", "volume"] if c in gdf.columns]
        if not critical_cols:
            # 返回空 DataFrame
            return gdf.iloc[:0]
        mask = gdf[critical_cols].isnull().any(axis=1)
        return gdf[mask]

    def _validate_suspension_gpu(self, gdf: Any) -> Any:
        if "volume" not in gdf.columns:
            return gdf.iloc[:0]
        return gdf[gdf["volume"] == 0]

    # ---------------- CPU Implementations ----------------

    def _validate_ohlc_cpu(self, df: Any) -> Any:
        # Pandas 向量化实现
        max_oc = df[["open", "close"]].max(axis=1)
        min_oc = df[["open", "close"]].min(axis=1)

        invalid_high = df["high"] < max_oc
        invalid_low = df["low"] > min_oc

        return df[invalid_high | invalid_low]

    def _validate_missing_cpu(self, df: Any) -> Any:
        critical_cols = [c for c in ["open", "high", "low", "close", "volume"] if c in df.columns]
        if not critical_cols:
            return df.iloc[:0]
        mask = df[critical_cols].isnull().any(axis=1)
        return df[mask]

    def _validate_suspension_cpu(self, df: Any) -> Any:
        if "volume" not in df.columns:
            return df.iloc[:0]
        return df[df["volume"] == 0]
