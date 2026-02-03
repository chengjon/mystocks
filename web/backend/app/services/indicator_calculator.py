"""
Indicator Calculator Service
基于TA-Lib的技术指标计算服务
"""

import logging
from typing import Any, Dict, List, Optional

import numpy as np
import talib

from .indicator_registry import get_indicator_registry

logger = logging.getLogger(__name__)


class InsufficientDataError(Exception):
    """数据点不足错误"""


class IndicatorCalculationError(Exception):
    """指标计算错误"""


class IndicatorCalculator:
    """
    技术指标计算器

    封装TA-Lib函数,提供统一的指标计算接口
    支持批量计算和错误处理
    """

    def __init__(self):
        """初始化计算器"""
        self.registry = get_indicator_registry()

    def calculate_indicator(
        self,
        abbreviation: str,
        ohlcv_data: Dict[str, np.ndarray],
        parameters: Dict[str, Any],
    ) -> Dict[str, np.ndarray]:
        """
        计算单个指标

        Args:
            abbreviation: 指标缩写 (如 "SMA", "RSI")
            ohlcv_data: OHLCV数据字典
                {
                    "open": np.array([...]),
                    "high": np.array([...]),
                    "low": np.array([...]),
                    "close": np.array([...]),
                    "volume": np.array([...])
                }
            parameters: 指标参数字典

        Returns:
            指标计算结果字典 {"output_name": np.array([...])}

        Raises:
            InsufficientDataError: 数据点不足
            IndicatorCalculationError: 计算失败
        """
        # 获取指标元数据
        indicator_meta = self.registry.get_indicator(abbreviation)
        if not indicator_meta:
            raise ValueError(f"未知指标: {abbreviation}")

        # 验证参数
        is_valid, error_msg = self.registry.validate_indicator(abbreviation, parameters)
        if not is_valid:
            raise ValueError(f"参数验证失败: {error_msg}")

        # 检查数据点数量
        min_points = self.registry.get_min_data_points(abbreviation, parameters)
        data_length = len(ohlcv_data["close"])
        if data_length < min_points:
            raise InsufficientDataError(
                f"指标 {abbreviation} 需要至少 {min_points} 个数据点, "
                f"但只有 {data_length} 个数据点。"
                f"建议: 请将日期范围扩大至至少 {min_points} 个交易日"
            )

        try:
            # 根据指标类型调用对应的TA-Lib函数
            result = self._call_talib_function(abbreviation, ohlcv_data, parameters, indicator_meta)
            return result

        except Exception as e:
            logger.error("计算指标 %(abbreviation)s 时出错: %(e)s")
            raise IndicatorCalculationError(f"计算指标 {abbreviation} 失败: {str(e)}")

    def _call_talib_function(
        self,
        abbreviation: str,
        ohlcv_data: Dict[str, np.ndarray],
        parameters: Dict[str, Any],
        indicator_meta: Dict[str, Any],
    ) -> Dict[str, np.ndarray]:
        """
        调用TA-Lib函数计算指标

        Returns:
            {output_name: result_array}
        """
        close = ohlcv_data["close"]
        high = ohlcv_data["high"]
        low = ohlcv_data["low"]
        open_price = ohlcv_data["open"]
        volume = ohlcv_data["volume"]

        # 趋势指标
        if abbreviation == "SMA":
            result = talib.SMA(close, timeperiod=parameters.get("timeperiod", 20))
            return {"sma": result}

        elif abbreviation == "EMA":
            result = talib.EMA(close, timeperiod=parameters.get("timeperiod", 20))
            return {"ema": result}

        elif abbreviation == "WMA":
            result = talib.WMA(close, timeperiod=parameters.get("timeperiod", 20))
            return {"wma": result}

        elif abbreviation == "MACD":
            macd, signal, hist = talib.MACD(
                close,
                fastperiod=parameters.get("fastperiod", 12),
                slowperiod=parameters.get("slowperiod", 26),
                signalperiod=parameters.get("signalperiod", 9),
            )
            return {"macd": macd, "signal": signal, "hist": hist}

        elif abbreviation == "BBANDS":
            upper, middle, lower = talib.BBANDS(
                close,
                timeperiod=parameters.get("timeperiod", 20),
                nbdevup=parameters.get("nbdevup", 2.0),
                nbdevdn=parameters.get("nbdevdn", 2.0),
            )
            return {"upperband": upper, "middleband": middle, "lowerband": lower}

        elif abbreviation == "SAR":
            result = talib.SAR(
                high,
                low,
                acceleration=parameters.get("acceleration", 0.02),
                maximum=parameters.get("maximum", 0.2),
            )
            return {"sar": result}

        elif abbreviation == "ADX":
            result = talib.ADX(high, low, close, timeperiod=parameters.get("timeperiod", 14))
            return {"adx": result}

        # 动量指标
        elif abbreviation == "RSI":
            result = talib.RSI(close, timeperiod=parameters.get("timeperiod", 14))
            return {"rsi": result}

        elif abbreviation == "STOCH":
            slowk, slowd = talib.STOCH(
                high,
                low,
                close,
                fastk_period=parameters.get("fastk_period", 9),
                slowk_period=parameters.get("slowk_period", 3),
                slowd_period=parameters.get("slowd_period", 3),
            )
            return {"slowk": slowk, "slowd": slowd}

        elif abbreviation == "CCI":
            result = talib.CCI(high, low, close, timeperiod=parameters.get("timeperiod", 14))
            return {"cci": result}

        elif abbreviation == "MFI":
            result = talib.MFI(high, low, close, volume, timeperiod=parameters.get("timeperiod", 14))
            return {"mfi": result}

        elif abbreviation == "WILLR":
            result = talib.WILLR(high, low, close, timeperiod=parameters.get("timeperiod", 14))
            return {"willr": result}

        elif abbreviation == "ROC":
            result = talib.ROC(close, timeperiod=parameters.get("timeperiod", 10))
            return {"roc": result}

        elif abbreviation == "MOM":
            result = talib.MOM(close, timeperiod=parameters.get("timeperiod", 10))
            return {"mom": result}

        # 波动率指标
        elif abbreviation == "ATR":
            result = talib.ATR(high, low, close, timeperiod=parameters.get("timeperiod", 14))
            return {"atr": result}

        elif abbreviation == "NATR":
            result = talib.NATR(high, low, close, timeperiod=parameters.get("timeperiod", 14))
            return {"natr": result}

        elif abbreviation == "TRANGE":
            result = talib.TRANGE(high, low, close)
            return {"trange": result}

        # 成交量指标
        elif abbreviation == "OBV":
            result = talib.OBV(close, volume)
            return {"obv": result}

        elif abbreviation == "AD":
            result = talib.AD(high, low, close, volume)
            return {"ad": result}

        elif abbreviation == "ADOSC":
            result = talib.ADOSC(
                high,
                low,
                close,
                volume,
                fastperiod=parameters.get("fastperiod", 3),
                slowperiod=parameters.get("slowperiod", 10),
            )
            return {"adosc": result}

        # K线形态识别
        elif abbreviation == "CDLDOJI":
            result = talib.CDLDOJI(open_price, high, low, close)
            return {"pattern": result}

        elif abbreviation == "CDLHAMMER":
            result = talib.CDLHAMMER(open_price, high, low, close)
            return {"pattern": result}

        elif abbreviation == "CDLENGULFING":
            result = talib.CDLENGULFING(open_price, high, low, close)
            return {"pattern": result}

        else:
            raise NotImplementedError(f"指标 {abbreviation} 的计算尚未实现")

    def calculate_multiple_indicators(
        self, indicators: List[Dict[str, Any]], ohlcv_data: Dict[str, np.ndarray]
    ) -> Dict[str, Dict[str, Any]]:
        """
        批量计算多个指标

        Args:
            indicators: 指标列表
                [
                    {"abbreviation": "SMA", "parameters": {"timeperiod": 20}},
                    {"abbreviation": "RSI", "parameters": {"timeperiod": 14}}
                ]
            ohlcv_data: OHLCV数据字典

        Returns:
            {
                "SMA": {
                    "values": {"sma": np.array([...])},
                    "parameters": {"timeperiod": 20},
                    "panel_type": "overlay",
                    "reference_lines": None
                },
                "RSI": {
                    "values": {"rsi": np.array([...])},
                    "parameters": {"timeperiod": 14},
                    "panel_type": "oscillator",
                    "reference_lines": [30, 70]
                }
            }
        """
        results = {}

        for idx, indicator_spec in enumerate(indicators):
            abbreviation = indicator_spec["abbreviation"]
            parameters = indicator_spec.get("parameters", {})

            try:
                # 计算指标
                values = self.calculate_indicator(abbreviation, ohlcv_data, parameters)

                # 获取元数据
                indicator_meta = self.registry.get_indicator(abbreviation)

                # 创建唯一key: 如果同一指标有多个配置,添加索引
                # 例如: SMA_0, SMA_1, SMA_2 或者 RSI_0
                result_key = f"{abbreviation}_{idx}"

                # 组装结果
                results[result_key] = {
                    "values": values,
                    "parameters": parameters,
                    "panel_type": indicator_meta["panel_type"].value,
                    "reference_lines": indicator_meta.get("reference_lines"),
                    "abbreviation": abbreviation,  # 保留原始缩写
                }

            except (InsufficientDataError, IndicatorCalculationError) as e:
                logger.warning("跳过指标 %(abbreviation)s: %(e)s")
                # 可以选择跳过失败的指标,或者抛出异常
                # 这里选择记录警告并继续
                result_key = f"{abbreviation}_{idx}"
                results[result_key] = {
                    "error": str(e),
                    "parameters": parameters,
                    "abbreviation": abbreviation,
                }

        return results

    def validate_data_quality(self, ohlcv_data: Dict[str, np.ndarray]) -> tuple[bool, Optional[str]]:
        """
        验证OHLCV数据质量

        Args:
            ohlcv_data: OHLCV数据字典

        Returns:
            (是否有效, 错误消息)
        """
        # 检查必需字段
        required_fields = ["open", "high", "low", "close", "volume"]
        for field in required_fields:
            if field not in ohlcv_data:
                return False, f"缺少必需字段: {field}"

        # 检查数据长度一致性
        lengths = [len(ohlcv_data[field]) for field in required_fields]
        if len(set(lengths)) > 1:
            return False, f"数据长度不一致: {dict(zip(required_fields, lengths))}"

        # 检查OHLC关系
        open_price = ohlcv_data["open"]
        high = ohlcv_data["high"]
        low = ohlcv_data["low"]
        close = ohlcv_data["close"]

        # high应该是最高价
        if not np.all(high >= open_price) or not np.all(high >= close):
            return False, "数据异常: high应大于等于open和close"

        # low应该是最低价
        if not np.all(low <= open_price) or not np.all(low <= close):
            return False, "数据异常: low应小于等于open和close"

        # volume应该非负
        if not np.all(ohlcv_data["volume"] >= 0):
            return False, "数据异常: volume不能为负数"

        return True, None


# 全局单例
_indicator_calculator = None


def get_indicator_calculator() -> IndicatorCalculator:
    """获取指标计算器单例"""
    global _indicator_calculator
    if _indicator_calculator is None:
        _indicator_calculator = IndicatorCalculator()
    return _indicator_calculator
