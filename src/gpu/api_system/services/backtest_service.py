"""
回测服务
Backtest Service
"""

import logging
import time
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import queue

from src.utils.gpu_utils import GPUResourceManager
from src.utils.redis_utils import RedisQueue
from src.utils.monitoring import MetricsCollector
from api_proto.backtest_pb2 import (
    BacktestRequest,
    TaskResponse,
    QueryRequest,
    QueryResponse,
    HistoryResponse,
    BatchRequest,
    BatchResponse,
    PerformanceMetrics,
    ParameterOptimizationRequest,
    OptimizationResult,
)
from api_proto.backtest_pb2_grpc import BacktestServiceServicer
import grpc

logger = logging.getLogger(__name__)


class BacktestEngine:
    """回测引擎"""

    def __init__(self, gpu_manager: GPUResourceManager):
        self.gpu_manager = gpu_manager
        self.strategy_cache = {}
        self.result_cache = {}
        self.processing_queue = queue.Queue()
        self.max_concurrent_backtests = 5

    def run_backtest(self, request: BacktestRequest) -> Dict[str, Any]:
        """执行回测"""
        try:
            logger.info(f"开始执行回测: {request.backtest_id}")
            start_time = time.time()

            # 数据预处理
            market_data = self._prepare_market_data(request)

            # 策略加载
            strategy = self._load_strategy(
                request.strategy_type, request.strategy_config
            )

            # 回测执行
            if self.gpu_manager.get_available_gpu_count() > 0:
                results = self._run_backtest_gpu(market_data, strategy, request)
            else:
                results = self._run_backtest_cpu(market_data, strategy, request)

            # 计算性能指标
            performance_metrics = self._calculate_performance_metrics(results, request)

            # 生成报告
            backtest_report = self._generate_backtest_report(
                results, performance_metrics
            )

            processing_time = time.time() - start_time

            results = {
                "backtest_id": request.backtest_id,
                "status": "completed",
                "processing_time": processing_time,
                "market_data_points": len(market_data),
                "backtest_report": backtest_report,
                "performance_metrics": performance_metrics,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"回测完成: {request.backtest_id}, 耗时: {processing_time:.2f}秒"
            )
            return results

        except Exception as e:
            logger.error(f"回测执行失败: {request.backtest_id}, 错误: {e}")
            return {
                "backtest_id": request.backtest_id,
                "status": "failed",
                "error_message": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _prepare_market_data(self, request: BacktestRequest) -> pd.DataFrame:
        """准备市场数据"""
        # 这里应该从数据库获取实际的市场数据
        # 当前模拟数据
        dates = pd.date_range(start=request.start_date, end=request.end_date, freq="D")
        n_points = len(dates)

        # 生成模拟价格数据
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, n_points)
        prices = [100.0]
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))

        market_data = pd.DataFrame(
            {
                "date": dates,
                "open": prices,
                "high": [p * 1.01 for p in prices],
                "low": [p * 0.99 for p in prices],
                "close": prices,
                "volume": np.random.randint(10000, 100000, n_points),
            }
        )

        return market_data

    def _load_strategy(self, strategy_type: str, strategy_config: Dict) -> Any:
        """加载策略"""
        strategy_key = (
            f"{strategy_type}_{hash(json.dumps(strategy_config, sort_keys=True))}"
        )

        if strategy_key in self.strategy_cache:
            return self.strategy_cache[strategy_key]

        # 根据策略类型创建策略
        if strategy_type == "trend_following":
            strategy = TrendFollowingStrategy(strategy_config)
        elif strategy_type == "momentum":
            strategy = MomentumStrategy(strategy_config)
        elif strategy_type == "mean_reversion":
            strategy = MeanReversionStrategy(strategy_config)
        elif strategy_type == "arbitrage":
            strategy = ArbitrageStrategy(strategy_config)
        else:
            raise ValueError(f"不支持策略类型: {strategy_type}")

        self.strategy_cache[strategy_key] = strategy
        return strategy

    def _run_backtest_gpu(
        self, market_data: pd.DataFrame, strategy: Any, request: BacktestRequest
    ) -> Dict[str, Any]:
        """GPU加速回测"""
        try:
            # 分配GPU资源
            gpu_id = self.gpu_manager.allocate_gpu(
                request.backtest_id, priority="medium", memory_required=1024
            )

            if gpu_id:
                logger.info(f"使用GPU {gpu_id} 执行回测")

                # 这里应该使用cuDF进行GPU加速计算
                # 当前模拟GPU处理
                results = strategy.run_backtest(market_data)

                # 释放GPU资源
                self.gpu_manager.release_gpu(request.backtest_id, gpu_id)

                return {"results": results, "gpu_used": True, "gpu_id": gpu_id}
            else:
                # GPU资源不足，回退到CPU
                logger.warning("GPU资源不足，使用CPU执行回测")
                return self._run_backtest_cpu(market_data, strategy, request)

        except Exception as e:
            logger.error(f"GPU回测失败: {e}")
            return self._run_backtest_cpu(market_data, strategy, request)

    def _run_backtest_cpu(
        self, market_data: pd.DataFrame, strategy: Any, request: BacktestRequest
    ) -> Dict[str, Any]:
        """CPU回测"""
        logger.info("使用CPU执行回测")
        results = strategy.run_backtest(market_data)
        return {"results": results, "gpu_used": False}

    def _calculate_performance_metrics(
        self, backtest_results: Dict, request: BacktestRequest
    ) -> PerformanceMetrics:
        """计算性能指标"""
        results = backtest_results["results"]

        # 基础指标计算
        total_return = results.get("total_return", 0.0)
        annual_return = total_return * (252 / len(results.get("dates", [])))
        volatility = results.get("volatility", 0.0)
        sharpe_ratio = annual_return / volatility if volatility > 0 else 0.0
        max_drawdown = results.get("max_drawdown", 0.0)

        # 风险指标
        var_95 = results.get("var_95", 0.0)
        var_99 = results.get("var_99", 0.0)
        beta = results.get("beta", 0.0)
        alpha = results.get("alpha", 0.0)

        # 交易统计
        total_trades = results.get("total_trades", 0)
        winning_trades = results.get("winning_trades", 0)
        losing_trades = results.get("losing_trades", 0)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0

        return PerformanceMetrics(
            total_return=total_return,
            annual_return=annual_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            var_95=var_95,
            var_99=var_99,
            beta=beta,
            alpha=alpha,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            timestamp=datetime.now().isoformat(),
        )

    def _generate_backtest_report(
        self, results: Dict, performance_metrics: PerformanceMetrics
    ) -> Dict[str, Any]:
        """生成回测报告"""
        return {
            "summary": {
                "total_return": f"{performance_metrics.total_return:.2%}",
                "annual_return": f"{performance_metrics.annual_return:.2%}",
                "sharpe_ratio": f"{performance_metrics.sharpe_ratio:.2f}",
                "max_drawdown": f"{performance_metrics.max_drawdown:.2%}",
                "win_rate": f"{performance_metrics.win_rate:.2%}",
            },
            "risk_metrics": {
                "volatility": f"{performance_metrics.volatility:.2%}",
                "var_95": f"{performance_metrics.var_95:.2%}",
                "var_99": f"{performance_metrics.var_99:.2%}",
                "beta": f"{performance_metrics.beta:.2f}",
                "alpha": f"{performance_metrics.alpha:.2f}",
            },
            "trading_statistics": {
                "total_trades": performance_metrics.total_trades,
                "winning_trades": performance_metrics.winning_trades,
                "losing_trades": performance_metrics.losing_trades,
                "win_rate": f"{performance_metrics.win_rate:.2%}",
            },
            "gpu_acceleration": results.get("gpu_used", False),
            "gpu_id": results.get("gpu_id"),
            "generation_time": datetime.now().isoformat(),
        }


class TrendFollowingStrategy:
    """趋势跟踪策略"""

    def __init__(self, config: Dict):
        self.config = config
        self.ma_window = config.get("ma_window", 20)
        self.rsi_window = config.get("rsi_window", 14)
        self.entry_threshold = config.get("entry_threshold", 0.02)
        self.exit_threshold = config.get("exit_threshold", 0.01)

    def run_backtest(self, market_data: pd.DataFrame) -> Dict[str, Any]:
        """执行趋势跟踪策略回测"""
        df = market_data.copy()

        # 计算移动平均
        df["ma"] = df["close"].rolling(window=self.ma_window).mean()

        # 计算RSI
        df["rsi"] = self._calculate_rsi(df["close"])

        # 生成交易信号
        df["signal"] = 0
        df.loc[df["close"] > df["ma"] * (1 + self.entry_threshold), "signal"] = 1
        df.loc[df["close"] < df["ma"] * (1 - self.exit_threshold), "signal"] = -1

        # 计算收益
        df["returns"] = df["close"].pct_change()
        df["strategy_returns"] = df["signal"].shift(1) * df["returns"]

        # 计算累计收益
        df["cumulative_returns"] = (1 + df["strategy_returns"]).cumprod()

        return {
            "total_return": df["cumulative_returns"].iloc[-1] - 1,
            "annual_return": df["strategy_returns"].mean() * 252,
            "volatility": df["strategy_returns"].std() * np.sqrt(252),
            "sharpe_ratio": (df["strategy_returns"].mean() * 252)
            / (df["strategy_returns"].std() * np.sqrt(252)),
            "max_drawdown": (
                df["cumulative_returns"].cummax() - df["cumulative_returns"]
            ).max(),
            "total_trades": abs(df["signal"]).sum(),
            "winning_trades": (df["strategy_returns"] > 0).sum(),
            "dates": df["date"].tolist(),
            "returns": df["strategy_returns"].tolist(),
        }

    def _calculate_rsi(self, prices: pd.Series) -> pd.Series:
        """计算RSI指标"""
        delta = prices.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=self.rsi_window).mean()
        avg_loss = loss.rolling(window=self.rsi_window).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi


class MomentumStrategy:
    """动量策略"""

    def __init__(self, config: Dict):
        self.config = config
        self.lookback_period = config.get("lookback_period", 10)
        self.entry_threshold = config.get("entry_threshold", 0.05)
        self.exit_threshold = config.get("exit_threshold", 0.03)

    def run_backtest(self, market_data: pd.DataFrame) -> Dict[str, Any]:
        """执行动量策略回测"""
        df = market_data.copy()

        # 计算动量指标
        df["momentum"] = df["close"].pct_change(self.lookback_period)

        # 生成交易信号
        df["signal"] = 0
        df.loc[df["momentum"] > self.entry_threshold, "signal"] = 1
        df.loc[df["momentum"] < -self.exit_threshold, "signal"] = -1

        # 计算收益
        df["returns"] = df["close"].pct_change()
        df["strategy_returns"] = df["signal"].shift(1) * df["returns"]

        # 计算累计收益
        df["cumulative_returns"] = (1 + df["strategy_returns"]).cumprod()

        return {
            "total_return": df["cumulative_returns"].iloc[-1] - 1,
            "annual_return": df["strategy_returns"].mean() * 252,
            "volatility": df["strategy_returns"].std() * np.sqrt(252),
            "sharpe_ratio": (df["strategy_returns"].mean() * 252)
            / (df["strategy_returns"].std() * np.sqrt(252)),
            "max_drawdown": (
                df["cumulative_returns"].cummax() - df["cumulative_returns"]
            ).max(),
            "total_trades": abs(df["signal"]).sum(),
            "winning_trades": (df["strategy_returns"] > 0).sum(),
            "dates": df["date"].tolist(),
            "returns": df["strategy_returns"].tolist(),
        }


class MeanReversionStrategy:
    """均值回归策略"""

    def __init__(self, config: Dict):
        self.config = config
        self.bollinger_window = config.get("bollinger_window", 20)
        self.bollinger_std = config.get("bollinger_std", 2)
        self.entry_threshold = config.get("entry_threshold", 1.5)
        self.exit_threshold = config.get("exit_threshold", 0.5)

    def run_backtest(self, market_data: pd.DataFrame) -> Dict[str, Any]:
        """执行均值回归策略回测"""
        df = market_data.copy()

        # 计算布林带
        df["ma"] = df["close"].rolling(window=self.bollinger_window).mean()
        df["std"] = df["close"].rolling(window=self.bollinger_window).std()
        df["upper_band"] = df["ma"] + (df["std"] * self.bollinger_std)
        df["lower_band"] = df["ma"] - (df["std"] * self.bollinger_std)

        # 计算z-score
        df["z_score"] = (df["close"] - df["ma"]) / df["std"]

        # 生成交易信号
        df["signal"] = 0
        df.loc[df["z_score"] < -self.entry_threshold, "signal"] = 1
        df.loc[df["z_score"] > self.entry_threshold, "signal"] = -1
        df.loc[abs(df["z_score"]) < self.exit_threshold, "signal"] = 0

        # 计算收益
        df["returns"] = df["close"].pct_change()
        df["strategy_returns"] = df["signal"].shift(1) * df["returns"]

        # 计算累计收益
        df["cumulative_returns"] = (1 + df["strategy_returns"]).cumprod()

        return {
            "total_return": df["cumulative_returns"].iloc[-1] - 1,
            "annual_return": df["strategy_returns"].mean() * 252,
            "volatility": df["strategy_returns"].std() * np.sqrt(252),
            "sharpe_ratio": (df["strategy_returns"].mean() * 252)
            / (df["strategy_returns"].std() * np.sqrt(252)),
            "max_drawdown": (
                df["cumulative_returns"].cummax() - df["cumulative_returns"]
            ).max(),
            "total_trades": abs(df["signal"]).sum(),
            "winning_trades": (df["strategy_returns"] > 0).sum(),
            "dates": df["date"].tolist(),
            "returns": df["strategy_returns"].tolist(),
        }


class ArbitrageStrategy:
    """套利策略"""

    def __init__(self, config: Dict):
        self.config = config
        self.spread_threshold = config.get("spread_threshold", 0.02)
        self.mean_reversion_window = config.get("mean_reversion_window", 20)

    def run_backtest(self, market_data: pd.DataFrame) -> Dict[str, Any]:
        """执行套利策略回测"""
        df = market_data.copy()

        # 模拟价差数据（实际应该来自不同市场）
        df["spread"] = df["close"] - df["open"]
        df["spread_ma"] = df["spread"].rolling(window=self.mean_reversion_window).mean()
        df["spread_std"] = df["spread"].rolling(window=self.mean_reversion_window).std()

        # 生成交易信号
        df["signal"] = 0
        df.loc[df["spread"] < df["spread_ma"] - df["spread_std"], "signal"] = 1
        df.loc[df["spread"] > df["spread_ma"] + df["spread_std"], "signal"] = -1

        # 计算收益
        df["returns"] = df["close"].pct_change()
        df["strategy_returns"] = df["signal"].shift(1) * df["returns"]

        # 计算累计收益
        df["cumulative_returns"] = (1 + df["strategy_returns"]).cumprod()

        return {
            "total_return": df["cumulative_returns"].iloc[-1] - 1,
            "annual_return": df["strategy_returns"].mean() * 252,
            "volatility": df["strategy_returns"].std() * np.sqrt(252),
            "sharpe_ratio": (df["strategy_returns"].mean() * 252)
            / (df["strategy_returns"].std() * np.sqrt(252)),
            "max_drawdown": (
                df["cumulative_returns"].cummax() - df["cumulative_returns"]
            ).max(),
            "total_trades": abs(df["signal"]).sum(),
            "winning_trades": (df["strategy_returns"] > 0).sum(),
            "dates": df["date"].tolist(),
            "returns": df["strategy_returns"].tolist(),
        }


class BacktestService(BacktestServiceServicer):
    """回测服务实现"""

    def __init__(
        self,
        gpu_manager: GPUResourceManager,
        redis_queue: RedisQueue,
        metrics_collector: MetricsCollector,
    ):
        self.gpu_manager = gpu_manager
        self.redis_queue = redis_queue
        self.metrics_collector = metrics_collector
        self.backtest_engine = BacktestEngine(gpu_manager)
        self.active_tasks: Dict[str, Any] = {}
        self.task_history: List[Dict] = []
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=5)

        # 配置
        self.config = {
            "max_concurrent_tasks": 5,
            "task_timeout": 3600,  # 1小时
            "cache_ttl": 300,  # 5分钟缓存
            "max_history_size": 1000,
        }

    def initialize(self):
        """初始化服务"""
        logger.info("正在初始化回测服务...")
        self.running = True
        logger.info("回测服务初始化完成")

    def SubmitBacktest(
        self, request: BacktestRequest, context: grpc.ServicerContext
    ) -> TaskResponse:
        """提交回测任务"""
        try:
            # 检查并发任务数
            if len(self.active_tasks) >= self.config["max_concurrent_tasks"]:
                context.set_code(grpc.StatusCode.RESOURCE_EXHAUSTED)
                context.set_details("当前并发任务数已达上限")
                return TaskResponse()

            # 生成任务ID
            task_id = f"backtest_{int(time.time())}_{hash(json.dumps(request.strategy_config, sort_keys=True))}"

            # 检查缓存
            cache_key = f"{task_id}_{request.start_date}_{request.end_date}"
            if cache_key in self.active_tasks:
                cached_task = self.active_tasks[cache_key]
                return TaskResponse(
                    task_id=task_id,
                    status=cached_task["status"],
                    progress=cached_task["progress"],
                    message=cached_task["message"],
                    created_at=cached_task["created_at"],
                )

            # 添加到活跃任务
            self.active_tasks[cache_key] = {
                "task_id": task_id,
                "status": "pending",
                "progress": 0,
                "message": "任务已提交，等待处理",
                "created_at": datetime.now().isoformat(),
                "request": request,
            }

            # 提交到Redis队列
            task_data = {
                "task_id": task_id,
                "task_type": "backtest",
                "priority": "medium",
                "backtest_request": request,
                "created_at": datetime.now().isoformat(),
            }

            self.redis_queue.enqueue_task("backtest", task_data)

            # 更新任务状态
            self.active_tasks[cache_key]["status"] = "queued"
            self.active_tasks[cache_key]["message"] = "任务已加入队列"

            logger.info(f"回测任务已提交: {task_id}")

            return TaskResponse(
                task_id=task_id,
                status="queued",
                progress=0,
                message="任务已加入队列",
                created_at=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error(f"提交回测任务失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")
            return TaskResponse()

    def QueryBacktest(
        self, request: QueryRequest, context: grpc.ServicerContext
    ) -> QueryResponse:
        """查询回测状态"""
        try:
            task_id = request.task_id

            # 查找活跃任务
            for cache_key, task in self.active_tasks.items():
                if task["task_id"] == task_id:
                    return QueryResponse(
                        task_id=task_id,
                        status=task["status"],
                        progress=task["progress"],
                        message=task["message"],
                        created_at=task["created_at"],
                        updated_at=datetime.now().isoformat(),
                    )

            # 查询Redis任务状态
            task_status = self.redis_queue.get_task_status("backtest", task_id)
            if task_status:
                return QueryResponse(
                    task_id=task_id,
                    status=task_status["status"],
                    progress=0,  # Redis队列中没有进度信息
                    message=task_status.get("updated_at", "查询成功"),
                    created_at=task_status["created_at"],
                    updated_at=task_status.get("updated_at", task_status["created_at"]),
                )

            # 查询历史任务
            for task in self.task_history:
                if task["task_id"] == task_id:
                    return QueryResponse(
                        task_id=task_id,
                        status=task["status"],
                        progress=task.get("progress", 100),
                        message=task.get("message", "任务完成"),
                        created_at=task["created_at"],
                        updated_at=task.get("completed_at", task["created_at"]),
                    )

            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"未找到任务: {task_id}")
            return QueryResponse()

        except Exception as e:
            logger.error(f"查询回测状态失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")
            return QueryResponse()

    def GetBacktestHistory(self, request, context) -> HistoryResponse:
        """获取回测历史"""
        try:
            # 限制返回数量
            limit = min(request.limit, 100)
            history = self.task_history[-limit:]

            return HistoryResponse(
                history=history,
                total_count=len(self.task_history),
                limit=limit,
                timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error(f"获取回测历史失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")
            return HistoryResponse()

    def SubmitBatchBacktest(
        self, request: BatchRequest, context: grpc.ServicerContext
    ) -> BatchResponse:
        """批量提交回测任务"""
        try:
            submitted_tasks = []
            failed_tasks = []

            for i, backtest_request in enumerate(request.backtest_requests):
                try:
                    # 构建批量请求ID
                    batch_task_id = f"batch_{request.batch_id}_{i}"

                    # 添加到活跃任务
                    cache_key = f"{batch_task_id}_{backtest_request.start_date}_{backtest_request.end_date}"
                    self.active_tasks[cache_key] = {
                        "task_id": batch_task_id,
                        "status": "pending",
                        "progress": 0,
                        "message": "批量任务已提交",
                        "created_at": datetime.now().isoformat(),
                        "request": backtest_request,
                    }

                    # 提交到Redis队列
                    task_data = {
                        "task_id": batch_task_id,
                        "task_type": "backtest",
                        "priority": request.priority,
                        "backtest_request": backtest_request,
                        "batch_id": request.batch_id,
                        "batch_index": i,
                        "created_at": datetime.now().isoformat(),
                    }

                    self.redis_queue.enqueue_task("backtest", task_data)

                    submitted_tasks.append(
                        {
                            "task_id": batch_task_id,
                            "status": "queued",
                            "created_at": datetime.now().isoformat(),
                        }
                    )

                except Exception as e:
                    logger.error(f"批量任务提交失败 {i}: {e}")
                    failed_tasks.append({"index": i, "error": str(e)})

            return BatchResponse(
                batch_id=request.batch_id,
                submitted_tasks=submitted_tasks,
                failed_tasks=failed_tasks,
                total_submitted=len(submitted_tasks),
                total_failed=len(failed_tasks),
                timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error(f"批量提交回测失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")
            return BatchResponse()

    def RunOptimization(
        self, request: ParameterOptimizationRequest, context: grpc.ServicerContext
    ) -> OptimizationResult:
        """运行参数优化"""
        try:
            optimization_id = f"opt_{int(time.time())}"

            # 参数优化逻辑
            if request.optimization_type == "grid_search":
                results = self._grid_search_optimization(request)
            elif request.optimization_type == "random_search":
                results = self._random_search_optimization(request)
            elif request.optimization_type == "bayesian_optimization":
                results = self._bayesian_optimization(request)
            else:
                raise ValueError(f"不支持的优化类型: {request.optimization_type}")

            return OptimizationResult(
                optimization_id=optimization_id,
                optimization_type=request.optimization_type,
                parameter_ranges=request.parameter_ranges,
                best_parameters=results["best_params"],
                best_performance=results["best_performance"],
                all_results=results["all_results"],
                total_iterations=results["total_iterations"],
                execution_time=results["execution_time"],
                timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error(f"参数优化失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")
            return OptimizationResult()

    def _grid_search_optimization(
        self, request: ParameterOptimizationRequest
    ) -> Dict[str, Any]:
        """网格搜索优化"""
        start_time = time.time()
        best_performance = float("-inf")
        best_params = {}
        all_results = []

        # 生成参数网格
        param_grid = self._generate_parameter_grid(request.parameter_ranges)

        for params in param_grid:
            try:
                # 创建策略配置
                strategy_config = {**request.strategy_config, **params}

                # 创建回测请求
                backtest_request = BacktestRequest(
                    backtest_id=f"opt_{int(time.time())}",
                    strategy_type=request.strategy_type,
                    strategy_config=strategy_config,
                    start_date=request.start_date,
                    end_date=request.end_date,
                    initial_capital=request.initial_capital,
                )

                # 运行回测
                result = self.backtest_engine.run_backtest(backtest_request)
                performance = result.get("total_return", 0)

                all_results.append(
                    {
                        "parameters": params,
                        "performance": performance,
                        "backtest_result": result,
                    }
                )

                if performance > best_performance:
                    best_performance = performance
                    best_params = params

            except Exception as e:
                logger.warning(f"参数组合优化失败 {params}: {e}")
                continue

        execution_time = time.time() - start_time

        return {
            "best_params": best_params,
            "best_performance": best_performance,
            "all_results": all_results,
            "total_iterations": len(param_grid),
            "execution_time": execution_time,
        }

    def _random_search_optimization(
        self, request: ParameterOptimizationRequest
    ) -> Dict[str, Any]:
        """随机搜索优化"""
        start_time = time.time()
        best_performance = float("-inf")
        best_params = {}
        all_results = []

        # 随机采样参数
        for i in range(request.max_iterations):
            params = {}
            for param_name, param_range in request.parameter_ranges.items():
                if param_range["type"] == "integer":
                    value = np.random.randint(
                        param_range["min"], param_range["max"] + 1
                    )
                elif param_range["type"] == "float":
                    value = np.random.uniform(param_range["min"], param_range["max"])
                elif param_range["type"] == "categorical":
                    value = np.random.choice(param_range["values"])
                else:
                    continue
                params[param_name] = value

            try:
                # 创建策略配置
                strategy_config = {**request.strategy_config, **params}

                # 创建回测请求
                backtest_request = BacktestRequest(
                    backtest_id=f"opt_{int(time.time())}",
                    strategy_type=request.strategy_type,
                    strategy_config=strategy_config,
                    start_date=request.start_date,
                    end_date=request.end_date,
                    initial_capital=request.initial_capital,
                )

                # 运行回测
                result = self.backtest_engine.run_backtest(backtest_request)
                performance = result.get("total_return", 0)

                all_results.append(
                    {
                        "parameters": params,
                        "performance": performance,
                        "backtest_result": result,
                    }
                )

                if performance > best_performance:
                    best_performance = performance
                    best_params = params

            except Exception as e:
                logger.warning(f"随机参数优化失败 {params}: {e}")
                continue

        execution_time = time.time() - start_time

        return {
            "best_params": best_params,
            "best_performance": best_performance,
            "all_results": all_results,
            "total_iterations": i + 1,
            "execution_time": execution_time,
        }

    def _bayesian_optimization(
        self, request: ParameterOptimizationRequest
    ) -> Dict[str, Any]:
        """贝叶斯优化"""
        # 简化实现，实际应该使用专业的贝叶斯优化库
        return self._random_search_optimization(request)

    def _generate_parameter_grid(self, parameter_ranges: Dict) -> List[Dict]:
        """生成参数网格"""
        import itertools

        param_names = list(parameter_ranges.keys())
        param_values = []

        for param_name, param_range in parameter_ranges.items():
            if param_range["type"] == "integer":
                values = list(range(param_range["min"], param_range["max"] + 1))
            elif param_range["type"] == "float":
                values = np.linspace(param_range["min"], param_range["max"], 10)
            elif param_range["type"] == "categorical":
                values = param_range["values"]
            else:
                values = [param_range["default"]]
            param_values.append(values)

        # 生成所有组合
        param_combinations = list(itertools.product(*param_values))

        # 转换为字典格式
        grid = []
        for combination in param_combinations:
            param_dict = dict(zip(param_names, combination))
            grid.append(param_dict)

        return grid

    def get_backtest_statistics(self) -> Dict[str, Any]:
        """获取回测统计信息"""
        return {
            "timestamp": datetime.now().isoformat(),
            "active_tasks": len(self.active_tasks),
            "total_tasks": len(self.task_history),
            "gpu_available": self.gpu_manager.get_available_gpu_count(),
            "gpu_total": len(self.gpu_manager.gpu_ids),
            "queue_status": self.redis_queue.get_queue_statistics(),
            "strategies_used": list(
                set(
                    [
                        task["request"].strategy_type
                        for task in self.active_tasks.values()
                    ]
                )
            ),
        }

    def stop(self):
        """停止服务"""
        logger.info("正在停止回测服务...")
        self.running = False
        self.executor.shutdown(wait=True)
        logger.info("回测服务已停止")
