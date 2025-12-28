"""
数据质量验证器
为数据源适配器提供实时数据质量检查功能
"""

import pandas as pd
from typing import Dict, Any, List, Optional
import logging

from src.monitoring.data_quality_monitor import DataQualityMonitor, get_quality_monitor

logger = logging.getLogger(__name__)


class DataQualityValidator:
    """
    数据质量验证器

    为数据源适配器提供实时的数据质量检查功能，
    包括完整性、准确性和一致性验证。
    """

    def __init__(self, source_name: str, quality_monitor: Optional[DataQualityMonitor] = None):
        """
        初始化数据质量验证器

        Args:
            source_name: 数据源名称
            quality_monitor: 数据质量监控器实例
        """
        self.source_name = source_name
        self.quality_monitor = quality_monitor or get_quality_monitor()

        # 数据质量阈值配置
        self.thresholds = {
            "missing_rate_threshold": 5.0,  # 缺失率阈值 5%
            "invalid_rate_threshold": 1.0,  # 无效率阈值 1%
            "duplicate_rate_threshold": 0.5,  # 重复率阈值 0.5%
            "outlier_rate_threshold": 2.0,  # 异常值率阈值 2%
            "freshness_threshold_seconds": 300,  # 新鲜度阈值 5分钟
        }

        logger.info("✅ DataQualityValidator initialized for %s", source_name)

    def validate_stock_data(self, df: pd.DataFrame, symbol: str, data_type: str = "daily") -> Dict[str, Any]:
        """
        验证股票数据质量

        Args:
            df: 股票数据DataFrame
            symbol: 股票代码
            data_type: 数据类型 (daily, realtime, etc.)

        Returns:
            Dict: 验证结果 {
                'is_valid': bool,
                'quality_score': float,
                'issues': List[Dict],
                'statistics': Dict
            }
        """
        if df.empty:
            return {
                "is_valid": False,
                "quality_score": 0.0,
                "issues": [{"type": "empty_data", "message": "数据为空"}],
                "statistics": {},
            }

        issues = []
        quality_score = 100.0

        # 1. 检查必需列
        required_columns = self._get_required_columns(data_type)
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            issues.append(
                {
                    "type": "missing_columns",
                    "message": f"缺少必需列: {missing_columns}",
                    "severity": "critical",
                }
            )
            quality_score -= 30 * len(missing_columns)

        # 2. 检查数据完整性
        completeness_issues = self._check_completeness(df, required_columns)
        issues.extend(completeness_issues)
        quality_score -= sum(issue.get("score_penalty", 0) for issue in completeness_issues)

        # 3. 检查数据准确性
        accuracy_issues = self._check_accuracy(df, symbol)
        issues.extend(accuracy_issues)
        quality_score -= sum(issue.get("score_penalty", 0) for issue in accuracy_issues)

        # 4. 检查数据一致性
        consistency_issues = self._check_consistency(df, data_type)
        issues.extend(consistency_issues)
        quality_score -= sum(issue.get("score_penalty", 0) for issue in consistency_issues)

        # 5. 检查重复数据
        duplicate_issues = self._check_duplicates(df)
        issues.extend(duplicate_issues)
        quality_score -= sum(issue.get("score_penalty", 0) for issue in duplicate_issues)

        # 6. 检查异常值
        outlier_issues = self._check_outliers(df)
        issues.extend(outlier_issues)
        quality_score -= sum(issue.get("score_penalty", 0) for issue in outlier_issues)

        # 计算统计信息
        statistics = self._calculate_statistics(df)

        # 确定最终有效性
        is_valid = quality_score >= 70.0 and not any(issue.get("severity") == "critical" for issue in issues)

        # 记录质量检查结果
        self._log_quality_check(symbol, data_type, is_valid, quality_score, issues, statistics)

        return {
            "is_valid": is_valid,
            "quality_score": max(0.0, quality_score),
            "issues": issues,
            "statistics": statistics,
        }

    def _get_required_columns(self, data_type: str) -> List[str]:
        """获取必需列"""
        if data_type == "realtime":
            return ["code", "name", "price", "volume", "timestamp"]
        elif data_type in ["daily", "index_daily"]:
            return ["date", "open", "high", "low", "close", "volume"]
        else:
            return ["date", "close"]

    def _check_completeness(self, df: pd.DataFrame, required_columns: List[str]) -> List[Dict]:
        """检查数据完整性"""
        issues = []

        for col in required_columns:
            if col not in df.columns:
                continue

            missing_count = df[col].isnull().sum()
            missing_rate = (missing_count / len(df)) * 100

            if missing_rate > self.thresholds["missing_rate_threshold"]:
                severity = "critical" if missing_rate > 20 else "warning"
                penalty = min(20, missing_rate)

                issues.append(
                    {
                        "type": "missing_data",
                        "column": col,
                        "missing_rate": missing_rate,
                        "message": f"列 {col} 缺失率 {missing_rate:.2f}%",
                        "severity": severity,
                        "score_penalty": penalty,
                    }
                )

        return issues

    def _check_accuracy(self, df: pd.DataFrame, symbol: str) -> List[Dict]:
        """检查数据准确性"""
        issues = []

        # 检查价格数据的合理性
        price_columns = ["open", "high", "low", "close"]
        available_price_cols = [col for col in price_columns if col in df.columns]

        if available_price_cols:
            # 检查负价格
            for col in available_price_cols:
                negative_count = (df[col] < 0).sum()
                if negative_count > 0:
                    issues.append(
                        {
                            "type": "invalid_price",
                            "column": col,
                            "invalid_count": negative_count,
                            "message": f"列 {col} 存在 {negative_count} 个负价格",
                            "severity": "critical",
                            "score_penalty": 15,
                        }
                    )

            # 检查价格逻辑（high >= low, high/open/close等）
            if all(col in df.columns for col in ["high", "low"]):
                invalid_high_low = (df["high"] < df["low"]).sum()
                if invalid_high_low > 0:
                    issues.append(
                        {
                            "type": "price_logic_error",
                            "message": f"存在 {invalid_high_low} 条记录的最高价低于最低价",
                            "severity": "critical",
                            "score_penalty": 20,
                        }
                    )

        # 检查成交量
        if "volume" in df.columns:
            negative_volume = (df["volume"] < 0).sum()
            if negative_volume > 0:
                issues.append(
                    {
                        "type": "invalid_volume",
                        "invalid_count": negative_volume,
                        "message": f"存在 {negative_volume} 条负成交量记录",
                        "severity": "critical",
                        "score_penalty": 10,
                    }
                )

        return issues

    def _check_consistency(self, df: pd.DataFrame, data_type: str) -> List[Dict]:
        """检查数据一致性"""
        issues = []

        # 检查日期格式一致性
        if "date" in df.columns:
            try:
                # 尝试转换为日期格式
                pd.to_datetime(df["date"])
            except Exception as e:
                issues.append(
                    {
                        "type": "date_format_inconsistent",
                        "message": f"日期格式不一致: {str(e)}",
                        "severity": "warning",
                        "score_penalty": 5,
                    }
                )

        # 检查时间戳格式（实时数据）
        if "timestamp" in df.columns:
            try:
                pd.to_datetime(df["timestamp"])
            except Exception as e:
                issues.append(
                    {
                        "type": "timestamp_format_inconsistent",
                        "message": f"时间戳格式不一致: {str(e)}",
                        "severity": "warning",
                        "score_penalty": 5,
                    }
                )

        return issues

    def _check_duplicates(self, df: pd.DataFrame) -> List[Dict]:
        """检查重复数据"""
        issues = []

        # 检查完全重复的行
        duplicate_rows = df.duplicated().sum()
        if duplicate_rows > 0:
            duplicate_rate = (duplicate_rows / len(df)) * 100

            if duplicate_rate > self.thresholds["duplicate_rate_threshold"]:
                issues.append(
                    {
                        "type": "duplicate_rows",
                        "duplicate_count": duplicate_rows,
                        "duplicate_rate": duplicate_rate,
                        "message": f"存在 {duplicate_rows} 条重复记录 ({duplicate_rate:.2f}%)",
                        "severity": "warning",
                        "score_penalty": min(10, duplicate_rate * 2),
                    }
                )

        return issues

    def _check_outliers(self, df: pd.DataFrame) -> List[Dict]:
        """检查异常值"""
        issues = []

        # 检查价格异常值（使用IQR方法）
        price_columns = ["open", "high", "low", "close"]
        available_price_cols = [col for col in price_columns if col in df.columns]

        for col in available_price_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
            if outliers > 0:
                outlier_rate = (outliers / len(df)) * 100

                if outlier_rate > self.thresholds["outlier_rate_threshold"]:
                    issues.append(
                        {
                            "type": "price_outliers",
                            "column": col,
                            "outlier_count": outliers,
                            "outlier_rate": outlier_rate,
                            "message": f"列 {col} 存在 {outliers} 个异常值 ({outlier_rate:.2f}%)",
                            "severity": "warning",
                            "score_penalty": min(8, outlier_rate),
                        }
                    )

        return issues

    def _calculate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算数据统计信息"""
        stats = {
            "total_records": len(df),
            "columns": list(df.columns),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
        }

        # 日期范围
        if "date" in df.columns:
            try:
                dates = pd.to_datetime(df["date"])
                # 过滤掉无效日期
                valid_dates = dates.dropna()
                if len(valid_dates) > 0:
                    date_diff = valid_dates.max() - valid_dates.min()
                    stats["date_range"] = {
                        "start": valid_dates.min().strftime("%Y-%m-%d"),
                        "end": valid_dates.max().strftime("%Y-%m-%d"),
                        "days": int(date_diff.days) if hasattr(date_diff, "days") else 0,
                    }
            except Exception:
                pass

        # 价格统计
        price_columns = ["open", "high", "low", "close"]
        available_price_cols = [col for col in price_columns if col in df.columns]

        if available_price_cols:
            stats["price_summary"] = {}
            for col in available_price_cols:
                # 过滤掉NA值进行统计计算
                valid_values = df[col].dropna()
                if len(valid_values) > 0:
                    stats["price_summary"][col] = {
                        "min": float(valid_values.min()),
                        "max": float(valid_values.max()),
                        "mean": float(valid_values.mean()),
                        "std": float(valid_values.std()) if len(valid_values) > 1 else 0.0,
                    }
                else:
                    stats["price_summary"][col] = {
                        "min": 0.0,
                        "max": 0.0,
                        "mean": 0.0,
                        "std": 0.0,
                    }

        return stats

    def _log_quality_check(
        self,
        symbol: str,
        data_type: str,
        is_valid: bool,
        quality_score: float,
        issues: List[Dict],
        statistics: Dict,
    ):
        """记录质量检查结果"""
        try:
            # 使用数据质量监控器记录结果
            table_name = f"{self.source_name}_{data_type}"

            # 计算问题统计
            critical_issues = len([i for i in issues if i.get("severity") == "critical"])
            warning_issues = len([i for i in issues if i.get("severity") == "warning"])

            # 记录到监控数据库
            if self.quality_monitor:
                if critical_issues > 0:
                    self.quality_monitor.check_accuracy(
                        classification="MARKET_DATA",
                        database_type=self.source_name.upper(),
                        table_name=table_name,
                        total_records=statistics.get("total_records", 0),
                        invalid_records=critical_issues + warning_issues,
                        validation_rules=f"DataQualityValidator-{data_type}",
                        threshold=self.thresholds["invalid_rate_threshold"],
                    )

                self.quality_monitor.check_completeness(
                    classification="MARKET_DATA",
                    database_type=self.source_name.upper(),
                    table_name=table_name,
                    total_records=statistics.get("total_records", 0),
                    null_records=0,  # 已经在_check_completeness中处理
                    required_columns=self._get_required_columns(data_type),
                    threshold=self.thresholds["missing_rate_threshold"],
                )
self.logger.info("数据质量验证完成")
            logger.info("质量检查完成: {symbol} {data_type} - "
                f"得分: {quality_score:.1f}, 有效: {is_valid}, "
                f"问题: {len(issues)} (严重: {critical_issues}, 警告: {warning_issues})"
            )

        except Exception as e:
            logger.error("记录质量检查结果失败: %s", e)

    def set_thresholds(self, **kwargs):
        """自定义阈值配置"""
        self.thresholds.update(kwargs)
        logger.info("质量阈值已更新: %s", kwargs)


# 便捷函数
def create_validator(source_name: str) -> DataQualityValidator:
    """创建数据质量验证器"""
    return DataQualityValidator(source_name)


def validate_dataframe(df: pd.DataFrame, source_name: str, symbol: str, data_type: str = "daily") -> Dict[str, Any]:
    """便捷的数据验证函数"""
    validator = create_validator(source_name)
    return validator.validate_stock_data(df, symbol, data_type)
