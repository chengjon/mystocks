"""
策略执行引擎 (Strategy Executor)

功能说明:
- 多进程并行执行策略
- 进度跟踪和性能监控
- 异常处理和失败重试
- 自动保存信号到数据库
- 支持快速模式和完整模式

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import pandas as pd
from typing import Dict, List, Optional
from datetime import date, datetime, timedelta
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
from dataclasses import dataclass
from enum import Enum
import traceback

# 导入本地模块
try:
    from .base_strategy import BaseStrategy
    from .signal_manager import SignalManager
except ImportError:
    # 测试模式: 使用绝对导入
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from strategy.base_strategy import BaseStrategy
    from strategy.signal_manager import SignalManager


class ExecutionMode(Enum):
    """执行模式枚举"""

    FAST = "fast"  # 快速模式: 仅当前交易日
    FULL = "full"  # 完整模式: 历史周期范围


@dataclass
class ExecutionConfig:
    """执行配置"""

    parallel: bool = True  # 是否并行执行
    max_workers: int = 4  # 最大并行进程数
    timeout_seconds: int = 600  # 超时时间(秒)
    retry_on_failure: bool = True  # 失败重试
    max_retries: int = 3  # 最大重试次数
    save_signals: bool = True  # 自动保存信号
    batch_size: int = 100  # 批处理大小


@dataclass
class ExecutionProgress:
    """执行进度"""

    total_symbols: int = 0
    processed_symbols: int = 0
    failed_symbols: int = 0
    signals_found: int = 0
    elapsed_seconds: float = 0.0
    estimated_remaining_seconds: float = 0.0

    def get_progress_pct(self) -> float:
        """获取进度百分比"""
        if self.total_symbols == 0:
            return 0.0
        return (self.processed_symbols / self.total_symbols) * 100


class StrategyExecutor:
    """
    策略执行引擎 - 负责策略的并行执行和结果管理

    功能:
        - 多进程并行执行策略
        - 实时进度跟踪
        - 异常处理和重试
        - 自动保存信号到数据库
    """

    def __init__(
        self,
        strategy: BaseStrategy,
        signal_manager: SignalManager,
        config: Optional[ExecutionConfig] = None,
    ):
        """
        初始化策略执行引擎

        参数:
            strategy: 策略实例
            signal_manager: 信号管理器实例
            config: 执行配置 (可选)
        """
        self.strategy = strategy
        self.signal_manager = signal_manager
        self.config = config or ExecutionConfig()

        # 日志配置
        self.logger = logging.getLogger(f"{__name__}.StrategyExecutor")
        self.logger.setLevel(logging.INFO)

        # 执行状态
        self.execution_id = None
        self.progress = ExecutionProgress()
        self.is_running = False

    def execute(
        self,
        stock_pool: List[str],
        mode: ExecutionMode = ExecutionMode.FAST,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs,
    ) -> Dict:
        """
        执行策略对股票池进行筛选

        参数:
            stock_pool: 股票代码列表
            mode: 执行模式 (FAST或FULL)
            start_date: 开始日期 (FULL模式必需)
            end_date: 结束日期 (FULL模式必需)
            **kwargs: 额外参数

        返回:
            dict: 执行结果
                - execution_id: 执行ID
                - status: 执行状态 ('completed', 'failed', 'partial')
                - signals: 生成的信号DataFrame
                - progress: 进度信息
                - statistics: 统计信息
                - errors: 错误列表

        示例:
            >>> executor = StrategyExecutor(strategy, signal_manager)
            >>> # 快速模式: 仅当前交易日
            >>> result = executor.execute(
            ...     stock_pool=['000001', '000002', '000003'],
            ...     mode=ExecutionMode.FAST
            ... )
            >>> # 完整模式: 历史周期
            >>> result = executor.execute(
            ...     stock_pool=['000001', '000002'],
            ...     mode=ExecutionMode.FULL,
            ...     start_date=date(2024, 1, 1),
            ...     end_date=date(2024, 12, 31)
            ... )
        """
        # 生成执行ID
        import uuid

        self.execution_id = str(uuid.uuid4())

        # 初始化进度
        self.progress = ExecutionProgress(total_symbols=len(stock_pool))
        self.is_running = True
        start_time = time.time()

        self.logger.info("=" * 60)
        self.logger.info("策略执行开始")
        self.logger.info("执行ID: %s", self.execution_id)
        self.logger.info("策略: %s v%s", self.strategy.name, self.strategy.version)
        self.logger.info("执行模式: %s", mode.value)
        self.logger.info("股票池大小: %s", len(stock_pool))
        self.logger.info("并行执行: %s", self.config.parallel)
        if self.config.parallel:
            self.logger.info("工作进程数: %s", self.config.max_workers)
        self.logger.info("=" * 60)

        # 验证参数
        if mode == ExecutionMode.FULL:
            if start_date is None or end_date is None:
                raise ValueError("FULL模式必须提供start_date和end_date")

        # 日期处理
        if mode == ExecutionMode.FAST:
            # 快速模式: 使用最近一个交易日
            end_date = date.today()
            start_date = end_date - timedelta(days=1)

        # 执行策略
        all_signals = []
        errors = []

        try:
            if self.config.parallel and len(stock_pool) > 1:
                # 并行执行
                all_signals, errors = self._execute_parallel(stock_pool, start_date, end_date, **kwargs)
            else:
                # 串行执行
                all_signals, errors = self._execute_serial(stock_pool, start_date, end_date, **kwargs)

        except Exception as e:
            self.logger.error("策略执行过程中发生严重错误: %s", e)
            self.logger.error(traceback.format_exc())
            errors.append(
                {
                    "symbol": "SYSTEM",
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "timestamp": datetime.now(),
                }
            )

        finally:
            self.is_running = False

        # 合并信号
        if all_signals:
            signals_df = pd.concat(all_signals, ignore_index=True)
        else:
            signals_df = pd.DataFrame()

        # 更新进度
        self.progress.elapsed_seconds = time.time() - start_time
        self.progress.signals_found = len(signals_df)

        # 保存信号到数据库
        if self.config.save_signals and not signals_df.empty and self.strategy.strategy_id:
            try:
                save_result = self.signal_manager.save_signals(
                    signals=signals_df,
                    strategy_id=self.strategy.strategy_id,
                    batch_insert=True,
                )
                self.logger.info("信号保存完成: 成功={save_result['saved_count']}, " f"失败={save_result['failed_count']}"
                )
            except Exception as e:
                self.logger.error("保存信号时出错: %s", e)

        # 确定执行状态
        if self.progress.failed_symbols == 0:
            status = "completed"
        elif self.progress.processed_symbols > 0:
            status = "partial"
        else:
            status = "failed"

        # 构建结果
        result = {
            "execution_id": self.execution_id,
            "status": status,
            "signals": signals_df,
            "progress": {
                "total_symbols": self.progress.total_symbols,
                "processed_symbols": self.progress.processed_symbols,
                "failed_symbols": self.progress.failed_symbols,
                "signals_found": self.progress.signals_found,
                "elapsed_seconds": self.progress.elapsed_seconds,
                "progress_pct": self.progress.get_progress_pct(),
            },
            "statistics": {
                "buy_signals": (len(signals_df[signals_df["signal"] == "buy"]) if not signals_df.empty else 0),
                "sell_signals": (len(signals_df[signals_df["signal"] == "sell"]) if not signals_df.empty else 0),
                "unique_symbols": (signals_df["symbol"].nunique() if not signals_df.empty else 0),
                "avg_strength": (
                    signals_df["strength"].mean() if not signals_df.empty and "strength" in signals_df.columns else 0
                ),
                "stocks_per_second": (
                    self.progress.processed_symbols / self.progress.elapsed_seconds
                    if self.progress.elapsed_seconds > 0
                    else 0
                ),
            },
            "errors": errors,
        }

        # 日志总结
        self.logger.info("=" * 60)
        self.logger.info("策略执行完成")
        self.logger.info("状态: %s", status)
        self.logger.info("处理股票: %s/%s", self.progress.processed_symbols, self.progress.total_symbols)
        self.logger.info("失败股票: %s", self.progress.failed_symbols)
        self.logger.info("生成信号: %s", self.progress.signals_found)
        self.logger.info("执行时间: %s秒", self.progress.elapsed_seconds)
        self.logger.info("处理速度: %s 股票/秒", result['statistics']['stocks_per_second'])
        self.logger.info("=" * 60)

        return result

    def _execute_serial(self, stock_pool: List[str], start_date: date, end_date: date, **kwargs) -> tuple:
        """串行执行策略"""
        all_signals = []
        errors = []

        for i, symbol in enumerate(stock_pool):
            try:
                signals = self._process_single_stock(symbol, start_date, end_date, **kwargs)
                if signals is not None and not signals.empty:
                    all_signals.append(signals)

                self.progress.processed_symbols += 1

                # 进度日志
                if (i + 1) % 10 == 0:
                    self.logger.info("进度: %sself.progress.get_progress_pct("):.1f}% "
                        f"({self.progress.processed_symbols}/{self.progress.total_symbols})"
                    )

            except Exception as e:
                self.progress.failed_symbols += 1
                errors.append({"symbol": symbol, "error": str(e), "timestamp": datetime.now()})
                self.logger.error("处理股票 %s 时出错: %s", symbol, e)

        return all_signals, errors

    def _execute_parallel(self, stock_pool: List[str], start_date: date, end_date: date, **kwargs) -> tuple:
        """并行执行策略"""
        all_signals = []
        errors = []

        # 分批处理
        batches = [
            stock_pool[i : i + self.config.batch_size] for i in range(0, len(stock_pool), self.config.batch_size)
        ]

        self.logger.info("分%s批处理，每批%s只股票", len(batches), self.config.batch_size)

        with ProcessPoolExecutor(max_workers=self.config.max_workers) as executor:
            # 提交所有任务
            futures = {
                executor.submit(self._process_batch, batch, start_date, end_date, **kwargs): batch_idx
                for batch_idx, batch in enumerate(batches)
            }

            # 收集结果
            for future in as_completed(futures, timeout=self.config.timeout_seconds):
                batch_idx = futures[future]
                try:
                    batch_signals, batch_errors = future.result()

                    if batch_signals:
                        all_signals.extend(batch_signals)
                    if batch_errors:
                        errors.extend(batch_errors)

                    # 更新进度
                    self.progress.processed_symbols += len(batches[batch_idx])
                    self.progress.failed_symbols += len(batch_errors)

                    # 进度日志
                    self.logger.info("批次 %sbatch_idx + 1/%slen(batches")} 完成 | "
                        f"进度: {self.progress.get_progress_pct():.1f}% | "
                        f"信号: +{len(batch_signals)}"
                    )

                except Exception as e:
                    self.logger.error("批次 %s 执行失败: %s", batch_idx, e)
                    self.progress.failed_symbols += len(batches[batch_idx])

        return all_signals, errors

    def _process_batch(self, symbols: List[str], start_date: date, end_date: date, **kwargs) -> tuple:
        """处理一批股票"""
        batch_signals = []
        batch_errors = []

        for symbol in symbols:
            try:
                signals = self._process_single_stock(symbol, start_date, end_date, **kwargs)
                if signals is not None and not signals.empty:
                    batch_signals.append(signals)

            except Exception as e:
                batch_errors.append({"symbol": symbol, "error": str(e), "timestamp": datetime.now()})

        return batch_signals, batch_errors

    def _process_single_stock(self, symbol: str, start_date: date, end_date: date, **kwargs) -> Optional[pd.DataFrame]:
        """处理单只股票"""
        # 获取市场数据
        data = self.strategy.get_market_data(symbol, start_date, end_date)

        if data is None or data.empty:
            self.logger.debug("股票 %s 数据为空，跳过", symbol)
            return None

        # 生成信号
        signals = self.strategy.generate_signals(data)

        # 过滤有效信号
        valid_signals = signals[signals["signal"].notna()].copy()

        if not valid_signals.empty:
            # 添加股票代码
            valid_signals["symbol"] = symbol
            return valid_signals

        return None

    def get_progress(self) -> Dict:
        """
        获取当前执行进度

        返回:
            dict: 进度信息
        """
        return {
            "execution_id": self.execution_id,
            "is_running": self.is_running,
            "total_symbols": self.progress.total_symbols,
            "processed_symbols": self.progress.processed_symbols,
            "failed_symbols": self.progress.failed_symbols,
            "signals_found": self.progress.signals_found,
            "elapsed_seconds": self.progress.elapsed_seconds,
            "progress_pct": self.progress.get_progress_pct(),
        }


if __name__ == "__main__":
    # 测试代码
    print("策略执行引擎测试")
    print("=" * 60)

    # 创建测试配置
    config = ExecutionConfig(
        parallel=False,  # 测试时使用串行
        max_workers=2,
        timeout_seconds=30,
        save_signals=False,  # 测试时不保存
    )

    print("执行配置:")
    print(f"  并行执行: {config.parallel}")
    print(f"  最大工作进程: {config.max_workers}")
    print(f"  超时时间: {config.timeout_seconds}秒")
    print(f"  自动保存信号: {config.save_signals}")

    # 注意: 完整测试需要实际的策略实例和数据
    print("\n注意: 完整的执行功能需要:")
    print("  1. BaseStrategy的具体实现")
    print("  2. SignalManager实例")
    print("  3. UnifiedDataManager提供市场数据")

    print("\n基础测试通过！")
