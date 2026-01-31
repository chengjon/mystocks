#!/usr/bin/env python3
"""
健康度计算引擎工厂
智能选择CPU或GPU计算引擎

功能：
- 根据数据规模选择引擎
- 根据GPU健康状态选择引擎
- 自动降级处理
- 切换决策日志

配置阈值：
- >3000行用GPU
- 显存>4GB用GPU

作者: Claude Code
创建日期: 2026-01-07
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar, Union

import pandas as pd

from .calculator_cpu import CalculatorConfig, HealthScoreInput, VectorizedHealthCalculator
from .calculator_gpu import GPUCalculatorConfig, GPUHealthCalculator
from .market_regime import MarketRegimeConfig, MarketRegimeIdentifier, MarketRegimeResult
from .risk_metrics import AdvancedRiskCalculator, RiskMetricsConfig, RiskMetricsInput

logger = logging.getLogger(__name__)


class EngineType(Enum):
    """引擎类型"""

    CPU = "cpu"
    GPU = "gpu"
    AUTO = "auto"


@dataclass
class FactoryConfig:
    """工厂配置"""

    cpu_gpu_threshold: int = 3000
    gpu_memory_threshold_gb: float = 4.0
    prefer_gpu_threshold: int = 500
    enable_auto_switch: bool = True
    log_switch_decisions: bool = True

    cpu_config: Optional[CalculatorConfig] = None
    gpu_config: Optional[GPUCalculatorConfig] = None
    risk_config: Optional[RiskMetricsConfig] = None
    market_regime_config: Optional[MarketRegimeConfig] = None


T = TypeVar("T")


class HealthCalculatorFactory:
    """
    健康度计算引擎工厂

    智能选择计算引擎：
    1. 数据规模 > CPU/GPU阈值 → GPU
    2. 数据规模 ≤ CPU/GPU阈值 → CPU
    3. GPU不可用 → CPU
    4. 显存不足 → CPU
    """

    _instance = None
    _initialized = False

    def __new__(cls, config: Optional[FactoryConfig] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config: Optional[FactoryConfig] = None):
        if HealthCalculatorFactory._initialized:
            return

        self.config = config or FactoryConfig()
        self._cpu_calculator: Optional[VectorizedHealthCalculator] = None
        self._gpu_calculator: Optional[GPUHealthCalculator] = None
        self._risk_calculator: Optional[AdvancedRiskCalculator] = None
        self._market_regime_identifier: Optional[MarketRegimeIdentifier] = None
        self._switch_history: List[Dict[str, Any]] = []

        HealthCalculatorFactory._initialized = True
        logger.info("HealthCalculatorFactory 初始化完成")

    def get_calculator(
        self,
        engine_type: EngineType = EngineType.AUTO,
        data_size: int = 0,
    ) -> Union[VectorizedHealthCalculator, GPUHealthCalculator]:
        """
        获取计算引擎

        Args:
            engine_type: 引擎类型（auto/cpu/gpu）
            data_size: 数据规模（行数）

        Returns:
            计算引擎实例
        """
        actual_engine = self._select_engine(engine_type, data_size)

        if actual_engine == EngineType.GPU:
            return self._get_gpu_calculator()
        else:
            return self._get_cpu_calculator()

    def _select_engine(
        self,
        requested: EngineType,
        data_size: int,
    ) -> EngineType:
        """
        选择计算引擎

        Args:
            requested: 请求的引擎类型
            data_size: 数据规模

        Returns:
            实际使用的引擎类型
        """
        if requested == EngineType.CPU:
            return EngineType.CPU

        if requested == EngineType.GPU:
            if self._is_gpu_available():
                return EngineType.GPU
            else:
                self._log_switch_decision(
                    requested=EngineType.GPU,
                    actual=EngineType.CPU,
                    reason="GPU不可用",
                )
                return EngineType.CPU

        if requested == EngineType.AUTO:
            if data_size > self.config.cpu_gpu_threshold:
                if self._is_gpu_available() and self._has_enough_memory():
                    result = EngineType.GPU
                    reason = f"大规模数据 ({data_size} > {self.config.cpu_gpu_threshold})"
                else:
                    result = EngineType.CPU
                    reason = "GPU不可用或显存不足"
            else:
                result = EngineType.CPU
                reason = f"小规模数据 ({data_size} <= {self.config.cpu_gpu_threshold})"

            if data_size > 0:
                self._log_switch_decision(
                    requested=EngineType.AUTO,
                    actual=result,
                    reason=reason,
                    data_size=data_size,
                )

            return result

    def _is_gpu_available(self) -> bool:
        """检查GPU是否可用"""
        if self._gpu_calculator is None:
            self._gpu_calculator = self._create_gpu_calculator()

        return self._gpu_calculator.is_available()

    def _has_enough_memory(self) -> bool:
        """检查是否有足够显存"""
        if self._gpu_calculator is None:
            self._gpu_calculator = self._create_gpu_calculator()

        health_status = self._gpu_calculator.get_health_status()
        free_memory = float(health_status.get("free_memory_gb", 0))

        return free_memory >= self.config.gpu_memory_threshold_gb

    def _get_cpu_calculator(self) -> VectorizedHealthCalculator:
        """获取CPU计算引擎"""
        if self._cpu_calculator is None:
            self._cpu_calculator = self._create_cpu_calculator()
        return self._cpu_calculator

    def _get_gpu_calculator(self) -> GPUHealthCalculator:
        """获取GPU计算引擎"""
        if self._gpu_calculator is None:
            self._gpu_calculator = self._create_gpu_calculator()
        return self._gpu_calculator

    def _create_cpu_calculator(self) -> VectorizedHealthCalculator:
        """创建CPU计算引擎"""
        config = self.config.cpu_config or CalculatorConfig()
        return VectorizedHealthCalculator(config)

    def _create_gpu_calculator(self) -> GPUHealthCalculator:
        """创建GPU计算引擎"""
        config = self.config.gpu_config or GPUCalculatorConfig()
        return GPUHealthCalculator(config)

    def calculate_health_scores(
        self,
        inputs: List[Dict[str, Any]],
        engine_type: EngineType = EngineType.AUTO,
        include_risk_metrics: bool = False,
    ) -> Dict[str, Any]:
        """
        计算健康度评分

        Args:
            inputs: 输入数据列表
            engine_type: 引擎类型
            include_risk_metrics: 是否包含高级风险指标

        Returns:
            计算结果
        """
        start_time = time.time()
        data_size = len(inputs)

        actual_engine = self._select_engine(engine_type, data_size)
        engine_used: str = "CPU"
        results: List[Dict[str, Any]]

        if actual_engine == EngineType.GPU:
            calculator = self._get_gpu_calculator()
            results = calculator.calculate(inputs, fallback=False)
            engine_used = "GPU"
        else:
            cpu_calc = self._get_cpu_calculator()
            score_inputs = [
                HealthScoreInput(
                    stock_code=inp.get("stock_code", f"UNKNOWN_{i}"),
                    close=inp.get("close", 100),
                    high=inp.get("high"),
                    low=inp.get("low"),
                    volume=inp.get("volume"),
                    market_regime=inp.get("market_regime", "choppy"),
                )
                for i, inp in enumerate(inputs)
            ]
            cpu_results = cpu_calc.calculate(score_inputs)
            results = [r.to_dict() for r in cpu_results]
            engine_used = "CPU"

        elapsed_ms = (time.time() - start_time) * 1000

        if include_risk_metrics:
            risk_calculator = self._get_risk_calculator()
            risk_inputs = [
                RiskMetricsInput(
                    stock_code=inp.get("stock_code", f"UNKNOWN_{i}"),
                    close_prices=[inp.get("close", 100)] * 60,
                )
                for i, inp in enumerate(inputs)
            ]
            risk_results = risk_calculator.calculate(risk_inputs)
            for i, result in enumerate(results):
                if i < len(risk_results):
                    result["risk_metrics"] = risk_results[i].to_dict()

        return {
            "results": results,
            "engine_used": engine_used,
            "data_size": data_size,
            "calculation_time_ms": round(elapsed_ms, 2),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def identify_market_regime(
        self,
        index_data: pd.DataFrame,
        market_breadth_data: Optional[pd.DataFrame] = None,
    ) -> MarketRegimeResult:
        """识别市场体制"""
        if self._market_regime_identifier is None:
            config = self.config.market_regime_config or MarketRegimeConfig()
            self._market_regime_identifier = MarketRegimeIdentifier(config)

        return self._market_regime_identifier.identify(index_data, market_breadth_data)

    def _get_risk_calculator(self) -> AdvancedRiskCalculator:
        """获取风险指标计算器"""
        if self._risk_calculator is None:
            config = self.config.risk_config or RiskMetricsConfig()
            self._risk_calculator = AdvancedRiskCalculator(config)
        return self._risk_calculator

    def _log_switch_decision(
        self,
        requested: EngineType,
        actual: EngineType,
        reason: str,
        data_size: int = 0,
    ):
        """记录引擎切换决策"""
        decision = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "requested": requested.value,
            "actual": actual.value,
            "reason": reason,
            "data_size": data_size,
        }
        self._switch_history.append(decision)

        if self.config.log_switch_decisions:
            logger.info("引擎切换决策: {requested.value} → {actual.value} (%(reason)s)")

    def get_switch_history(self) -> List[Dict[str, Any]]:
        """获取切换历史"""
        return self._switch_history

    def get_engine_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        gpu_status = {"available": False}
        if self._is_gpu_available():
            gpu_status = self._get_gpu_calculator().get_health_status()

        return {
            "cpu_available": True,
            "gpu_available": self._is_gpu_available(),
            "gpu_status": gpu_status,
            "switch_history_count": len(self._switch_history),
            "config": {
                "cpu_gpu_threshold": self.config.cpu_gpu_threshold,
                "gpu_memory_threshold_gb": self.config.gpu_memory_threshold_gb,
                "enable_auto_switch": self.config.enable_auto_switch,
            },
        }


def get_calculator_factory(
    config: Optional[FactoryConfig] = None,
) -> HealthCalculatorFactory:
    """获取计算引擎工厂实例"""
    return HealthCalculatorFactory(config)


def calculate_health_score(
    stock_code: str,
    close: float,
    market_regime: str = "choppy",
    engine_type: EngineType = EngineType.AUTO,
) -> Optional[Dict[str, Any]]:
    """
    便捷函数：计算单只股票健康度评分

    Args:
        stock_code: 股票代码
        close: 收盘价
        market_regime: 市场体制
        engine_type: 引擎类型

    Returns:
        健康度评分结果
    """
    factory = get_calculator_factory()
    results = factory.calculate_health_scores(
        [{"stock_code": stock_code, "close": close, "market_regime": market_regime}],
        engine_type=engine_type,
    )
    return results["results"][0] if results["results"] else None
