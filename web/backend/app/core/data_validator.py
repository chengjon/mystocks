"""
数据验证和质量检查模块
支持API响应数据完整性验证、数据一致性检查和异常值检测
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Tuple

import pandas as pd
import structlog

logger = structlog.get_logger()


@dataclass
class ValidationResult:
    """数据验证结果"""

    is_valid: bool
    errors: List[str]
    warnings: List[str]
    data_quality_score: float
    record_count: int


class StockDataValidator:
    """股票数据验证器"""

    # 股票基本信息的必需字段
    STOCKS_BASIC_REQUIRED_FIELDS = {"symbol", "name", "industry", "market"}

    # K线数据的必需字段
    KLINE_REQUIRED_FIELDS = {"date", "open", "high", "low", "close", "volume"}

    # 数值字段范围验证
    PRICE_RANGE = (0.01, 100000)  # 股票价格合理范围
    VOLUME_RANGE = (0, 10**12)  # 交易量合理范围

    @classmethod
    def validate_stocks_basic(cls, df: pd.DataFrame) -> ValidationResult:
        """验证股票基本信息数据"""
        errors = []
        warnings = []
        record_count = len(df)

        if df.empty:
            return ValidationResult(
                is_valid=False, errors=["数据为空"], warnings=[], data_quality_score=0.0, record_count=0
            )

        # 检查必需字段
        missing_fields = cls.STOCKS_BASIC_REQUIRED_FIELDS - set(df.columns)
        if missing_fields:
            errors.append(f"缺少必需字段: {missing_fields}")

        # 检查重复的symbol
        duplicate_symbols = df[df.duplicated(subset=["symbol"], keep=False)]
        if not duplicate_symbols.empty:
            errors.append(f"发现 {len(duplicate_symbols)} 条重复的股票代码")

        # 检查空值
        null_counts = df.isnull().sum()
        for col, count in null_counts.items():
            if count > 0:
                null_ratio = count / len(df)
                if col in cls.STOCKS_BASIC_REQUIRED_FIELDS and null_ratio > 0.1:
                    errors.append(f"字段 {col} 有 {null_ratio:.1%} 的空值")
                elif null_ratio > 0.3:
                    warnings.append(f"字段 {col} 有 {null_ratio:.1%} 的空值")

        # 验证symbol格式（应该包含市场标识）
        if "symbol" in df.columns:
            invalid_symbols = df[~df["symbol"].str.match(r"^[0-9]{6}\.[SH|SZ]$", na=False)]
            if not invalid_symbols.empty:
                warnings.append(f"发现 {len(invalid_symbols)} 条格式不标准的股票代码")

        # 计算数据质量评分
        quality_score = cls._calculate_quality_score(len(errors), len(warnings), null_counts.sum())

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            data_quality_score=quality_score,
            record_count=record_count,
        )

    @classmethod
    def validate_kline_data(cls, df: pd.DataFrame) -> ValidationResult:
        """验证K线数据"""
        errors = []
        warnings = []
        record_count = len(df)

        if df.empty:
            return ValidationResult(
                is_valid=False, errors=["K线数据为空"], warnings=[], data_quality_score=0.0, record_count=0
            )

        # 检查必需字段
        missing_fields = cls.KLINE_REQUIRED_FIELDS - set(df.columns)
        if missing_fields:
            errors.append(f"缺少必需字段: {missing_fields}")

        # 检查日期连续性
        if "date" in df.columns:
            try:
                dates = pd.to_datetime(df["date"]).sort_values()
                date_diff = dates.diff()
                # 检查是否有很大的日期间隔（>5个工作日）
                large_gaps = date_diff[date_diff > pd.Timedelta(days=5)]
                if not large_gaps.empty:
                    warnings.append(f"发现 {len(large_gaps)} 个日期断裂（大于5个工作日）")
            except Exception as e:
                errors.append(f"日期格式错误: {str(e)}")

        # 检查OHLC关系
        if all(col in df.columns for col in ["open", "high", "low", "close"]):
            invalid_ohlc = df[
                (df["high"] < df["low"])
                | (df["open"] > df["high"])
                | (df["open"] < df["low"])
                | (df["close"] > df["high"])
                | (df["close"] < df["low"])
            ]
            if not invalid_ohlc.empty:
                errors.append(f"发现 {len(invalid_ohlc)} 条OHLC关系不合理的数据")

        # 检查价格范围
        for price_col in ["open", "high", "low", "close"]:
            if price_col in df.columns:
                out_of_range = df[(df[price_col] < cls.PRICE_RANGE[0]) | (df[price_col] > cls.PRICE_RANGE[1])]
                if not out_of_range.empty:
                    warnings.append(f"字段 {price_col} 有 {len(out_of_range)} 条超出合理范围的值")

        # 检查成交量范围
        if "volume" in df.columns:
            out_of_range = df[(df["volume"] < cls.VOLUME_RANGE[0]) | (df["volume"] > cls.VOLUME_RANGE[1])]
            if not out_of_range.empty:
                warnings.append(f"成交量有 {len(out_of_range)} 条超出合理范围的值")

        # 检查空值
        null_counts = df.isnull().sum()
        for col in cls.KLINE_REQUIRED_FIELDS:
            if col in df.columns:
                count = null_counts.get(col, 0)
                if count > 0:
                    errors.append(f"字段 {col} 有 {count} 个空值")

        # 计算数据质量评分
        quality_score = cls._calculate_quality_score(len(errors), len(warnings), null_counts.sum())

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            data_quality_score=quality_score,
            record_count=record_count,
        )

    @classmethod
    def validate_api_response(
        cls, response: Dict[str, Any], expected_fields: List[str] = None
    ) -> Tuple[bool, List[str]]:
        """验证API响应格式"""
        errors = []

        # 检查基本响应结构
        if not isinstance(response, dict):
            errors.append("响应不是有效的JSON对象")
            return False, errors

        if "success" not in response:
            errors.append("缺少 success 字段")

        if "timestamp" not in response:
            errors.append("缺少 timestamp 字段")

        # 如果指定了期望字段，检查是否存在
        if expected_fields:
            missing = set(expected_fields) - set(response.keys())
            if missing:
                errors.append(f"缺少字段: {missing}")

        return len(errors) == 0, errors

    @staticmethod
    def _calculate_quality_score(error_count: int, warning_count: int, null_count: int) -> float:
        """计算数据质量评分 (0-100)"""
        # 基础分100分，每个错误减20分，每个警告减5分，每个空值减0.1分
        score = 100.0
        score -= error_count * 20
        score -= warning_count * 5
        score -= min(null_count * 0.1, 30)  # 空值最多减30分
        return max(0, min(score, 100))


class DataConsistencyValidator:
    """数据一致性验证器 - 用于端到端验证"""

    @staticmethod
    def validate_stocks_search_consistency(
        basic_stocks: pd.DataFrame, search_results: pd.DataFrame
    ) -> ValidationResult:
        """验证搜索结果与基本数据的一致性"""
        errors = []
        warnings = []

        if basic_stocks.empty and search_results.empty:
            return ValidationResult(is_valid=True, errors=[], warnings=[], data_quality_score=100.0, record_count=0)

        if search_results.empty:
            warnings.append("搜索结果为空")
            return ValidationResult(
                is_valid=True, errors=[], warnings=warnings, data_quality_score=80.0, record_count=0
            )

        # 检查搜索结果中的所有stock是否都在基本数据中
        search_symbols = set(search_results["symbol"].unique())
        basic_symbols = set(basic_stocks["symbol"].unique())

        unknown_symbols = search_symbols - basic_symbols
        if unknown_symbols:
            warnings.append(f"搜索结果中有 {len(unknown_symbols)} 个未知的股票代码")

        # 检查字段一致性
        for symbol in search_symbols & basic_symbols:
            search_row = search_results[search_results["symbol"] == symbol].iloc[0]
            basic_row = basic_stocks[basic_stocks["symbol"] == symbol].iloc[0]

            # 检查关键字段是否一致
            for field in ["name", "industry", "market"]:
                if field in search_row.index and field in basic_row.index:
                    if str(search_row[field]) != str(basic_row[field]):
                        errors.append(
                            f"股票 {symbol} 的 {field} 不一致: " f"搜索={search_row[field]}, 基本={basic_row[field]}"
                        )

        is_valid = len(errors) == 0
        score = StockDataValidator._calculate_quality_score(len(errors), len(warnings), 0)

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            data_quality_score=score,
            record_count=len(search_results),
        )

    @staticmethod
    def validate_kline_consistency(
        stock_symbol: str, kline_data: pd.DataFrame, expected_columns: List[str] = None
    ) -> ValidationResult:
        """验证K线数据的一致性和完整性"""
        errors = []
        warnings = []

        if kline_data.empty:
            return ValidationResult(
                is_valid=False, errors=["K线数据为空"], warnings=[], data_quality_score=0.0, record_count=0
            )

        # 使用StockDataValidator进行基本验证
        validator = StockDataValidator.validate_kline_data(kline_data)
        errors.extend(validator.errors)
        warnings.extend(validator.warnings)

        # 检查数据点数量
        if len(kline_data) < 10:
            warnings.append(f"K线数据点太少: {len(kline_data)} < 10")

        # 检查收益率异常值（>10%的单日涨跌）
        if "close" in kline_data.columns and len(kline_data) > 1:
            returns = kline_data["close"].pct_change() * 100
            extreme_returns = returns[abs(returns) > 10]
            if not extreme_returns.empty:
                warnings.append(f"发现 {len(extreme_returns)} 个极端收益率（>10%）")

        is_valid = len(errors) == 0
        score = StockDataValidator._calculate_quality_score(len(errors), len(warnings), 0)

        return ValidationResult(
            is_valid=is_valid, errors=errors, warnings=warnings, data_quality_score=score, record_count=len(kline_data)
        )
