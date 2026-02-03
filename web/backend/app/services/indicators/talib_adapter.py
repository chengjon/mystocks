"""
TA-Lib Indicator Adapter
========================

Generic adapter for TA-Lib indicators to work with the V2 Indicator System.
This allows quickly migrating 90% of standard indicators to the new architecture.

Version: 1.0.0
Author: MyStocks Project
"""

import logging
from typing import Any, Dict

import numpy as np
import talib

from .indicator_interface import (
    IndicatorInterface,
    IndicatorPluginFactory,
    IndicatorResult,
    OHLCVData,
)
from .indicator_registry import get_indicator_registry

logger = logging.getLogger(__name__)


class TalibGenericIndicator(IndicatorInterface):
    """
    通用TA-Lib指标适配器

    根据Registry中的元数据，动态适配TA-Lib函数调用。
    """

    def __init__(self, abbreviation: str):
        super().__init__()
        self.ABBREVIATION = abbreviation
        self._registry = get_indicator_registry()
        self._meta = self._registry.get(abbreviation)

        if not self._meta:
            raise ValueError(f"Indicator {abbreviation} not found in registry")

        # 使用Pydantic模型属性访问
        self.FULL_NAME = self._meta.full_name
        self.CHINESE_NAME = self._meta.chinese_name

    def calculate(self, data: OHLCVData, parameters: Dict[str, Any]) -> IndicatorResult:
        """
        计算指标

        Args:
            data: OHLCV数据
            parameters: 参数字典

        Returns:
            IndicatorResult: 计算结果
        """
        # 1. 验证参数
        try:
            # self._meta.parameters 是 List[IndicatorParameter]
            # validate_parameters 期望 Dict[str, Any] 但通常只是检查 keys
            # 为了兼容性，我们需要构造符合 validate_parameters 预期的字典
            # IndicatorInterface.validate_parameters 期望 valid_params 包含 param definitions
            # 实际上 IndicatorInterface.validate_parameters 的实现期望 valid_params 是 Dict[str, Dict]
            # 这里我们需要适配一下

            valid_params_dict = {}
            for p in self._meta.parameters:
                # 转换为字典格式以匹配基类验证逻辑
                p_dict = p.dict()
                # 确保 constraints 存在
                if not p_dict.get("constraints"):
                    p_dict["constraints"] = {}
                # 确保 type 是字符串
                if hasattr(p.type, "value"):
                    p_dict["type"] = p.type.value

                valid_params_dict[p.name] = p_dict

            self.validate_parameters(parameters, valid_params_dict)
        except Exception as e:
            return self._create_error_result(parameters, str(e))

        # 2. 验证数据点数量
        min_points = self._registry.get_min_data_points(self.ABBREVIATION, parameters)
        try:
            self.validate_data(data, min_points)
        except Exception as e:
            # 返回INSUFFICIENT_DATA状态
            return self._create_insufficient_data_result(parameters, min_points, data.length)

        # 3. 调用TA-Lib函数
        try:
            values = self._call_talib(data, parameters)
            return self._create_success_result(parameters, values)
        except Exception as e:
            logger.error("Calculation failed for {self.ABBREVIATION}: %(e)s")
            return self._create_error_result(parameters, f"TA-Lib calculation failed: {str(e)}")

    def _call_talib(self, data: OHLCVData, parameters: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """调用底层的TA-Lib函数 (逻辑复用自V1 Calculator)"""

        # 准备数据
        # 注意: TA-Lib需要double类型
        close = data.close.astype(np.double)
        high = data.high.astype(np.double)
        low = data.low.astype(np.double)
        open_price = data.open.astype(np.double)
        volume = data.volume.astype(np.double)

        abbr = self.ABBREVIATION

        # --- 趋势指标 ---
        if abbr == "SMA":
            return {"sma": talib.SMA(close, timeperiod=parameters.get("timeperiod", 20))}

        elif abbr == "EMA":
            return {"ema": talib.EMA(close, timeperiod=parameters.get("timeperiod", 20))}

        elif abbr == "WMA":
            return {"wma": talib.WMA(close, timeperiod=parameters.get("timeperiod", 20))}

        elif abbr == "MACD":
            macd, signal, hist = talib.MACD(
                close,
                fastperiod=parameters.get("fastperiod", 12),
                slowperiod=parameters.get("slowperiod", 26),
                signalperiod=parameters.get("signalperiod", 9),
            )
            return {"macd": macd, "signal": signal, "hist": hist}

        elif abbr == "BBANDS":
            upper, middle, lower = talib.BBANDS(
                close,
                timeperiod=parameters.get("timeperiod", 20),
                nbdevup=parameters.get("nbdevup", 2.0),
                nbdevdn=parameters.get("nbdevdn", 2.0),
            )
            return {"upperband": upper, "middleband": middle, "lowerband": lower}

        elif abbr == "SAR":
            return {
                "sar": talib.SAR(
                    high, low, acceleration=parameters.get("acceleration", 0.02), maximum=parameters.get("maximum", 0.2)
                )
            }

        elif abbr == "ADX":
            return {"adx": talib.ADX(high, low, close, timeperiod=parameters.get("timeperiod", 14))}

        # --- 动量指标 ---
        elif abbr == "RSI":
            return {"rsi": talib.RSI(close, timeperiod=parameters.get("timeperiod", 14))}

        elif abbr == "STOCH":
            slowk, slowd = talib.STOCH(
                high,
                low,
                close,
                fastk_period=parameters.get("fastk_period", 9),
                slowk_period=parameters.get("slowk_period", 3),
                slowd_period=parameters.get("slowd_period", 3),
            )
            return {"slowk": slowk, "slowd": slowd}

        elif abbr == "CCI":
            return {"cci": talib.CCI(high, low, close, timeperiod=parameters.get("timeperiod", 14))}

        elif abbr == "MFI":
            return {"mfi": talib.MFI(high, low, close, volume, timeperiod=parameters.get("timeperiod", 14))}

        elif abbr == "WILLR":
            return {"willr": talib.WILLR(high, low, close, timeperiod=parameters.get("timeperiod", 14))}

        elif abbr == "ROC":
            return {"roc": talib.ROC(close, timeperiod=parameters.get("timeperiod", 10))}

        elif abbr == "MOM":
            return {"mom": talib.MOM(close, timeperiod=parameters.get("timeperiod", 10))}

        # --- 波动率指标 ---
        elif abbr == "ATR":
            return {"atr": talib.ATR(high, low, close, timeperiod=parameters.get("timeperiod", 14))}

        elif abbr == "NATR":
            return {"natr": talib.NATR(high, low, close, timeperiod=parameters.get("timeperiod", 14))}

        elif abbr == "TRANGE":
            return {"trange": talib.TRANGE(high, low, close)}

        # --- 成交量指标 ---
        elif abbr == "OBV":
            return {"obv": talib.OBV(close, volume)}

        elif abbr == "AD":
            return {"ad": talib.AD(high, low, close, volume)}

        elif abbr == "ADOSC":
            return {
                "adosc": talib.ADOSC(
                    high,
                    low,
                    close,
                    volume,
                    fastperiod=parameters.get("fastperiod", 3),
                    slowperiod=parameters.get("slowperiod", 10),
                )
            }

        # --- K线形态 ---
        elif abbr == "CDLDOJI":
            return {"pattern": talib.CDLDOJI(open_price, high, low, close)}

        elif abbr == "CDLHAMMER":
            return {"pattern": talib.CDLHAMMER(open_price, high, low, close)}

        elif abbr == "CDLENGULFING":
            return {"pattern": talib.CDLENGULFING(open_price, high, low, close)}

        else:
            raise NotImplementedError(f"Logic for {abbr} not implemented in adapter")

    def get_parameter_defaults(self) -> Dict[str, Any]:
        """获取参数默认值"""
        defaults = {}
        for param in self._meta.parameters:
            defaults[param.name] = param.default
        return defaults


def register_all_talib_indicators():
    """
    注册所有支持的TA-Lib指标到Factory
    """
    registry = get_indicator_registry()
    supported_indicators = [
        "SMA",
        "EMA",
        "WMA",
        "MACD",
        "BBANDS",
        "SAR",
        "ADX",  # Trend
        "RSI",
        "STOCH",
        "CCI",
        "MFI",
        "WILLR",
        "ROC",
        "MOM",  # Momentum
        "ATR",
        "NATR",
        "TRANGE",  # Volatility
        "OBV",
        "AD",
        "ADOSC",  # Volume
        "CDLDOJI",
        "CDLHAMMER",
        "CDLENGULFING",  # Pattern
    ]

    count = 0
    for abbr in supported_indicators:
        indicator_class_name = f"TalibIndicator_{abbr}"

        # 定义动态类
        DynamicClass = type(
            indicator_class_name,
            (TalibGenericIndicator,),
            {"__init__": lambda self, a=abbr: TalibGenericIndicator.__init__(self, a), "ABBREVIATION": abbr},
        )

        IndicatorPluginFactory.register(abbr, DynamicClass)
        count += 1

    logger.info("Registered %(count)s TA-Lib indicators via Generic Adapter")
