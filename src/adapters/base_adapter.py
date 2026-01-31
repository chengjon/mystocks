"""
数据源适配器基类
提供通用的适配器功能和数据质量检查集成
"""

import logging
from abc import ABC
from typing import Any, Dict, List, Optional

import pandas as pd

from src.core.data_quality_validator import DataQualityValidator

logger = logging.getLogger(__name__)


class BaseDataSourceAdapter(ABC):
    """
    数据源适配器基类

    提供通用功能：
    1. 数据质量检查集成
    2. 通用日志记录
    3. 错误处理辅助方法
    4. 性能监控
    """

    def __init__(self, source_name: str):
        """
        初始化适配器基类

        Args:
            source_name: 数据源名称
        """
        self.source_name = source_name
        self.quality_validator = DataQualityValidator(source_name)
        self.logger = logging.getLogger(f"{__name__}.{source_name}")

        self.logger.info("✅ %s 适配器基类初始化完成", source_name)

    def _apply_quality_check(self, df: pd.DataFrame, symbol: str, data_type: str = "daily") -> pd.DataFrame:
        """
        应用数据质量检查

        Args:
            df: 待检查的数据
            symbol: 股票代码
            data_type: 数据类型

        Returns:
            原始DataFrame（质量检查失败不影响数据返回）
        """
        if df.empty:
            self.logger.warning("数据为空，跳过质量检查: %s %s", symbol, data_type)
            return df

        try:
            quality_result = self.quality_validator.validate_stock_data(df, symbol, data_type)

            if quality_result["quality_score"] < 80:
                self.logger.warning(
                    "数据质量检查失败: %s %s - "
                    f"得分: {quality_result['quality_score']:.1f}, "
                    f"问题数: {len(quality_result['issues'])}"
                )

                # 记录严重问题
                critical_issues = [issue for issue in quality_result["issues"] if issue.get("severity") == "critical"]
                if critical_issues:
                    for issue in critical_issues:
                        self.logger.error("  - %s: %s", issue["type"], issue["message"])
                else:
                    # 只记录警告级别的问题
                    warning_issues = [issue for issue in quality_result["issues"] if issue.get("severity") == "warning"]
                    for issue in warning_issues:
                        self.logger.warning("  - %s: %s", issue["type"], issue["message"])
            else:
                self.logger.info(
                    "数据质量检查通过: %s %s - 得分: %.1f", symbol, data_type, quality_result["quality_score"]
                )

        except Exception as e:
            self.logger.error("数据质量检查异常: %s %s - %s", symbol, data_type, e)
            # 质量检查失败不应影响数据返回

        return df

    def _apply_quality_check_realtime(self, data: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """
        应用实时数据质量检查

        Args:
            data: 实时数据字典
            symbol: 股票代码

        Returns:
            原始数据字典（质量检查失败不影响数据返回）
        """
        if not data:
            self.logger.warning("实时数据为空，跳过质量检查: %s", symbol)
            return data

        try:
            # 转换为DataFrame进行质量检查
            df = pd.DataFrame([data])

            # 确保有必需的时间戳
            if "timestamp" not in data:
                from datetime import datetime

                df["timestamp"] = datetime.now().isoformat()

            quality_result = self.quality_validator.validate_stock_data(df, symbol, "realtime")

            if quality_result["quality_score"] < 80:
                self.logger.warning("实时数据质量检查失败: %s - 得分: %.1f", symbol, quality_result["quality_score"])

                # 记录严重问题
                critical_issues = [issue for issue in quality_result["issues"] if issue.get("severity") == "critical"]
                if critical_issues:
                    for issue in critical_issues:
                        self.logger.error("  - %s: %s", issue["type"], issue["message"])
            else:
                self.logger.debug("实时数据质量检查通过: %s", symbol)

        except Exception as e:
            self.logger.error("实时数据质量检查异常: %s - %s", symbol, e)

        return data

    def _log_data_fetch(
        self,
        symbol: str,
        data_type: str,
        record_count: int,
        columns: Optional[List[str]] = None,
    ):
        """
        记录数据获取日志

        Args:
            symbol: 股票代码
            data_type: 数据类型
            record_count: 记录数量
            columns: 列名列表
        """
        self.logger.info("获取%s数据: %s - 记录数: %s", data_type, symbol, record_count)

        if columns:
            self.logger.debug("数据列: %s", columns)

    def _handle_empty_data(self, symbol: str, data_type: str, fallback_data: Any = None):
        """
        处理空数据情况

        Args:
            symbol: 股票代码
            data_type: 数据类型
            fallback_data: 备用数据

        Returns:
            空DataFrame或fallback_data
        """
        self.logger.info("获取到空数据: %s %s", symbol, data_type)

        if fallback_data is not None:
            self.logger.info("使用备用数据: %s", type(fallback_data))
            return fallback_data

        return pd.DataFrame()

    def _validate_symbol(self, symbol: str) -> str:
        """
        验证股票代码格式

        Args:
            symbol: 原始股票代码

        Returns:
            验证后的股票代码
        """
        if not symbol or not isinstance(symbol, str):
            raise ValueError(f"无效的股票代码: {symbol}")

        # 基本格式检查
        symbol = symbol.strip().upper()

        if len(symbol) < 4:
            raise ValueError(f"股票代码长度不足: {symbol}")

        return symbol

    def _validate_date_range(self, start_date: str, end_date: str) -> tuple:
        """
        验证日期范围

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            验证后的日期元组
        """
        from datetime import datetime

        try:
            start_dt = datetime.strptime(start_date.replace("-", ""), "%Y%m%d")
            end_dt = datetime.strptime(end_date.replace("-", ""), "%Y%m%d")

            if start_dt > end_dt:
                raise ValueError(f"开始日期不能大于结束日期: {start_date} > {end_date}")

            return start_date, end_date

        except ValueError as e:
            raise ValueError(f"无效的日期格式: {e}")

    def get_quality_statistics(self) -> Dict[str, Any]:
        """
        获取质量统计信息

        Returns:
            质量统计字典
        """
        try:
            # 这里可以从质量验证器获取统计信息
            return {
                "source_name": self.source_name,
                "validator_initialized": True,
                "quality_thresholds": self.quality_validator.thresholds,
            }
        except Exception as e:
            self.logger.error("获取质量统计失败: %s", e)
            return {"source_name": self.source_name, "error": str(e)}

    def set_quality_thresholds(self, **kwargs):
        """
        设置质量检查阈值

        Args:
            **kwargs: 阈值参数
        """
        self.quality_validator.set_thresholds(**kwargs)
        self.logger.info("质量阈值已更新: %s", kwargs)


class QualityMixin:
    """
    质量检查混入类

    为现有适配器提供质量检查功能，无需继承BaseDataSourceAdapter
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, "source_name"):
            self.quality_validator = DataQualityValidator(self.source_name)

    def apply_quality_check(self, df: pd.DataFrame, symbol: str, data_type: str = "daily") -> pd.DataFrame:
        """应用数据质量检查的便捷方法"""
        if hasattr(self, "_apply_quality_check"):
            return self._apply_quality_check(df, symbol, data_type)
        else:
            return df

    def apply_quality_check_realtime(self, data: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """应用实时数据质量检查的便捷方法"""
        if hasattr(self, "_apply_quality_check_realtime"):
            return self._apply_quality_check_realtime(data, symbol)
        else:
            return data
