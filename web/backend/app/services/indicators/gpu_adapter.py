"""
GPU Indicator Adapter - GPU指标适配器

利用NVIDIA RAPIDS (cuDF/cuPy) 提供高性能技术指标计算：
- 向量化的GPU计算
- 自动CPU回退
- 批量处理优化
- 内存效率优化

作者: Claude Code (Sisyphus)
日期: 2026-01-14
"""

import logging
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod
import time
import numpy as np

from typing import Dict, Any, Optional, List
import dataclasses


# Simple indicator configuration
@dataclasses.dataclass
class IndicatorConfig:
    name: str
    type: str
    parameters: Dict[str, Any] = dataclasses.field(default_factory=dict)


# Simple indicator result
@dataclasses.dataclass
class IndicatorResult:
    indicator_name: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = dataclasses.field(default_factory=dict)


# Base indicator interface
class IndicatorInterface(ABC):
    @abstractmethod
    def calculate(
        self, data: Dict[str, Any], parameters: Optional[Dict[str, Any]] = None
    ) -> IndicatorResult:
        pass


logger = logging.getLogger(__name__)

try:
    import cudf
    import cupy as cp

    GPU_AVAILABLE = True
    logger.info("✅ GPU libraries available (cuDF, cuPy)")
except ImportError:
    GPU_AVAILABLE = False
    logger.warning("⚠️ GPU libraries not available, falling back to CPU")

try:
    from numba import jit, cuda

    NUMBA_CUDA_AVAILABLE = True
    logger.info("✅ Numba CUDA acceleration available")
except ImportError:
    NUMBA_CUDA_AVAILABLE = False
    logger.info("ℹ️ Numba CUDA not available, using standard GPU acceleration")


class GPUResourceManager:
    """
    GPU资源管理器

    管理GPU内存和计算资源：
    - GPU内存监控
    - 自动CPU回退
    - 资源清理
    - 性能监控
    """

    def __init__(self):
        self.gpu_memory_limit = 0.8  # 使用80%的GPU内存
        self.cpu_fallback_threshold = 0.9  # GPU内存使用超过90%时回退到CPU

        if GPU_AVAILABLE:
            try:
                # 检查GPU内存
                gpu_memory = cp.cuda.runtime.memGetInfo()
                total_memory = gpu_memory[1]
                free_memory = gpu_memory[0]
                self.available_memory = free_memory * self.gpu_memory_limit

                logger.info(".1f.1f.1f")
            except Exception as e:
                logger.warning(f"Failed to get GPU memory info: {e}")
                self.available_memory = 1024 * 1024 * 1024  # 1GB 默认
        else:
            self.available_memory = 0

    def should_use_gpu(self, estimated_memory: int) -> bool:
        """
        判断是否应该使用GPU

        Args:
            estimated_memory: 预估需要的内存（字节）

        Returns:
            是否使用GPU
        """
        if not GPU_AVAILABLE:
            return False

        if estimated_memory > self.available_memory:
            logger.warning(".1f.1f")
            return False

        return True

    def get_optimal_batch_size(self, data_size: int, indicator_type: str) -> int:
        """
        获取最优批量大小

        Args:
            data_size: 数据大小
            indicator_type: 指标类型

        Returns:
            批量大小
        """
        # 基于指标类型和数据大小计算最优批量
        base_batch_size = 10000

        if indicator_type in ["macd", "rsi", "bbands"]:
            batch_size = min(data_size, base_batch_size * 2)
        elif indicator_type in ["stoch", "williams", "cci"]:
            batch_size = min(data_size, base_batch_size)
        else:
            batch_size = min(data_size, base_batch_size // 2)

        return max(100, batch_size)  # 最小批量100


class GPUIndicatorAdapter(IndicatorInterface):
    """
    GPU指标适配器

    提供GPU加速的技术指标计算：
    - 自动GPU/CPU选择
    - 批量处理优化
    - 内存效率优化
    - 回退机制
    """

    def __init__(self, config: IndicatorConfig):
        """
        初始化GPU指标适配器

        Args:
            config: 指标配置
        """
        super().__init__(config)
        self.resource_manager = GPUResourceManager()
        self.use_gpu = self._should_use_gpu()

        # 性能统计
        self.calculation_times = []
        self.memory_usage = []
        self.batch_sizes = []

        logger.info(f"✅ GPU Indicator Adapter initialized (GPU: {self.use_gpu})")

    def _should_use_gpu(self) -> bool:
        """判断是否应该使用GPU"""
        # 估算内存使用量
        estimated_memory = self._estimate_memory_usage()

        return self.resource_manager.should_use_gpu(estimated_memory)

    def _estimate_memory_usage(self) -> int:
        """估算内存使用量"""
        # 基于配置估算内存使用
        # 这里简化计算，实际应该基于具体指标和数据量
        base_memory = 1024 * 1024  # 1MB基础内存

        # 根据数据量调整
        if hasattr(self.config.parameters, "period"):
            period = self.config.parameters["period"]
            base_memory *= max(1, period // 10)

        return base_memory

    def calculate(
        self, data: Dict[str, Any], parameters: Optional[Dict[str, Any]] = None
    ) -> IndicatorResult:
        """
        计算技术指标

        Args:
            data: 市场数据
            parameters: 计算参数

        Returns:
            指标结果
        """
        start_time = time.time()

        try:
            # 合并参数
            params = {**self.config.parameters}
            if parameters:
                params.update(parameters)

            # 选择计算方法
            if self.use_gpu:
                result = self._calculate_gpu(data, params)
            else:
                result = self._calculate_cpu(data, params)

            # 记录性能统计
            calculation_time = time.time() - start_time
            self.calculation_times.append(calculation_time)

            return IndicatorResult(
                indicator_name=self.config.name,
                data=result,
                metadata={
                    "calculation_time": calculation_time,
                    "used_gpu": self.use_gpu,
                    "batch_size": len(data.get("close", [])),
                    "parameters": params,
                },
            )

        except Exception as e:
            logger.error(f"Error calculating {self.config.name}: {e}")
            # 回退到CPU计算
            if self.use_gpu:
                logger.info(f"Falling back to CPU calculation for {self.config.name}")
                self.use_gpu = False
                return self.calculate(data, parameters)

            raise

    @abstractmethod
    def _calculate_gpu(
        self, data: Dict[str, Any], parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        GPU计算实现

        Args:
            data: 市场数据
            parameters: 计算参数

        Returns:
            计算结果
        """
        pass

    @abstractmethod
    def _calculate_cpu(
        self, data: Dict[str, Any], parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        CPU计算实现（回退用）

        Args:
            data: 市场数据
            parameters: 计算参数

        Returns:
            计算结果
        """
        pass

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        if not self.calculation_times:
            return {}

        return {
            "average_calculation_time": np.mean(self.calculation_times),
            "max_calculation_time": np.max(self.calculation_times),
            "min_calculation_time": np.min(self.calculation_times),
            "total_calculations": len(self.calculation_times),
            "gpu_enabled": self.use_gpu,
            "gpu_available": GPU_AVAILABLE,
        }


class GPUMACDIndicator(GPUIndicatorAdapter):
    """GPU加速MACD指标"""

    def __init__(self, config: IndicatorConfig):
        super().__init__(config)

    def _calculate_gpu(
        self, data: Dict[str, Any], parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """GPU计算MACD"""
        if not GPU_AVAILABLE:
            raise RuntimeError("GPU not available")

        try:
            # 获取参数
            fast_period = parameters.get("fast_period", 12)
            slow_period = parameters.get("slow_period", 26)
            signal_period = parameters.get("signal_period", 9)

            # 转换为cuDF
            close_prices = cudf.Series(data["close"])

            # 计算EMA
            fast_ema = self._gpu_ema(close_prices, fast_period)
            slow_ema = self._gpu_ema(close_prices, slow_period)

            # 计算MACD线
            macd_line = fast_ema - slow_ema

            # 计算信号线
            signal_line = self._gpu_ema(macd_line, signal_period)

            # 计算直方图
            histogram = macd_line - signal_line

            return {
                "macd": macd_line.to_pandas().fillna(0).values,
                "signal": signal_line.to_pandas().fillna(0).values,
                "histogram": histogram.to_pandas().fillna(0).values,
            }

        except Exception as e:
            logger.error(f"GPU MACD calculation failed: {e}")
            raise

    def _calculate_cpu(
        self, data: Dict[str, Any], parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """CPU计算MACD"""
        close_prices = np.array(data["close"])

        fast_period = parameters.get("fast_period", 12)
        slow_period = parameters.get("slow_period", 26)
        signal_period = parameters.get("signal_period", 9)

        # 计算EMA
        fast_ema = self._cpu_ema(close_prices, fast_period)
        slow_ema = self._cpu_ema(close_prices, slow_period)

        # 计算MACD
        macd_line = fast_ema - slow_ema
        signal_line = self._cpu_ema(macd_line, signal_period)
        histogram = macd_line - signal_line

        return {"macd": macd_line, "signal": signal_line, "histogram": histogram}

    def _gpu_ema(self, series: cudf.Series, period: int) -> cudf.Series:
        """GPU计算EMA"""
        return series.ewm(span=period, adjust=False).mean()

    def _cpu_ema(self, data: np.ndarray, period: int) -> np.ndarray:
        """CPU计算EMA"""
        alpha = 2 / (period + 1)
        ema = np.zeros_like(data, dtype=float)

        # 第一个值
        ema[period - 1] = np.mean(data[:period])

        # 计算EMA
        for i in range(period, len(data)):
            ema[i] = alpha * data[i] + (1 - alpha) * ema[i - 1]

        return ema


class GPURSIIndicator(GPUIndicatorAdapter):
    """GPU加速RSI指标"""

    def __init__(self, config: IndicatorConfig):
        super().__init__(config)

    def _calculate_gpu(
        self, data: Dict[str, Any], parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """GPU计算RSI"""
        if not GPU_AVAILABLE:
            raise RuntimeError("GPU not available")

        try:
            period = parameters.get("period", 14)

            # 转换为cuDF
            close_prices = cudf.Series(data["close"])

            # 计算价格变化
            price_changes = close_prices.diff()

            # 分离上涨和下跌
            gains = price_changes.where(price_changes > 0, 0)
            losses = -price_changes.where(price_changes < 0, 0)

            # 计算平均涨幅和跌幅
            avg_gain = gains.rolling(window=period).mean()
            avg_loss = losses.rolling(window=period).mean()

            # 计算RS和RSI
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

            return {
                "rsi": rsi.to_pandas().fillna(50).values  # RSI默认50
            }

        except Exception as e:
            logger.error(f"GPU RSI calculation failed: {e}")
            raise

    def _calculate_cpu(
        self, data: Dict[str, Any], parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """CPU计算RSI"""
        close_prices = np.array(data["close"])
        period = parameters.get("period", 14)

        price_changes = np.diff(close_prices)
        gains = np.where(price_changes > 0, price_changes, 0)
        losses = np.where(price_changes < 0, -price_changes, 0)

        # 计算初始平均值
        avg_gain = np.convolve(gains, np.ones(period) / period, mode="valid")
        avg_loss = np.convolve(losses, np.ones(period) / period, mode="valid")

        # 计算RS和RSI
        rs = avg_gain / (avg_loss + 1e-10)  # 避免除零
        rsi = 100 - (100 / (1 + rs))

        # 填充前面NaN值
        rsi_full = np.full(len(close_prices), 50.0)
        rsi_full[period:] = rsi

        return {"rsi": rsi_full}


class GPUBollingerBandsIndicator(GPUIndicatorAdapter):
    """GPU加速布林带指标"""

    def __init__(self, config: IndicatorConfig):
        super().__init__(config)

    def _calculate_gpu(
        self, data: Dict[str, Any], parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """GPU计算布林带"""
        if not GPU_AVAILABLE:
            raise RuntimeError("GPU not available")

        try:
            period = parameters.get("period", 20)
            std_dev = parameters.get("std_dev", 2.0)

            # 转换为cuDF
            close_prices = cudf.Series(data["close"])

            # 计算移动平均
            sma = close_prices.rolling(window=period).mean()

            # 计算标准差
            std = close_prices.rolling(window=period).std()

            # 计算上下轨
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)

            return {
                "upper": upper_band.to_pandas().fillna(method="bfill").values,
                "middle": sma.to_pandas().fillna(method="bfill").values,
                "lower": lower_band.to_pandas().fillna(method="bfill").values,
            }

        except Exception as e:
            logger.error(f"GPU Bollinger Bands calculation failed: {e}")
            raise

    def _calculate_cpu(
        self, data: Dict[str, Any], parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """CPU计算布林带"""
        close_prices = np.array(data["close"])
        period = parameters.get("period", 20)
        std_dev = parameters.get("std_dev", 2.0)

        # 计算移动平均
        sma = np.convolve(close_prices, np.ones(period) / period, mode="valid")

        # 计算标准差
        std = []
        for i in range(period - 1, len(close_prices)):
            window = close_prices[i - period + 1 : i + 1]
            std.append(np.std(window))

        std = np.array(std)

        # 计算上下轨
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)

        # 填充前面NaN值
        upper_full = np.full(len(close_prices), close_prices[0])
        middle_full = np.full(len(close_prices), close_prices[0])
        lower_full = np.full(len(close_prices), close_prices[0])

        upper_full[period - 1 :] = upper_band
        middle_full[period - 1 :] = sma
        lower_full[period - 1 :] = lower_band

        return {"upper": upper_full, "middle": middle_full, "lower": lower_full}


# GPU指标工厂
class GPUIndicatorFactory:
    """GPU指标工厂"""

    INDICATOR_MAP = {
        "macd": GPUMACDIndicator,
        "rsi": GPURSIIndicator,
        "bbands": GPUBollingerBandsIndicator,
        # 可以继续添加更多GPU指标
    }

    @classmethod
    def create_indicator(
        cls, indicator_type: str, config: IndicatorConfig
    ) -> GPUIndicatorAdapter:
        """
        创建GPU指标实例

        Args:
            indicator_type: 指标类型
            config: 指标配置

        Returns:
            GPU指标实例
        """
        if indicator_type not in cls.INDICATOR_MAP:
            raise ValueError(f"Unsupported GPU indicator: {indicator_type}")

        indicator_class = cls.INDICATOR_MAP[indicator_type]
        return indicator_class(config)

    @classmethod
    def get_supported_indicators(cls) -> List[str]:
        """获取支持的GPU指标列表"""
        return list(cls.INDICATOR_MAP.keys())

    @classmethod
    def is_gpu_accelerated(cls, indicator_type: str) -> bool:
        """检查指标是否支持GPU加速"""
        return indicator_type in cls.INDICATOR_MAP
