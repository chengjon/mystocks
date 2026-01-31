"""
集成回测服务
Integrated Backtest Service
"""

import hashlib
import json
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.gpu.api_system.utils.cache_optimization import CacheManager
from src.gpu.api_system.utils.gpu_acceleration_engine import GPUAccelerationEngine
from src.gpu.api_system.utils.gpu_utils import GPUResourceManager
from src.gpu.api_system.utils.monitoring import MetricsCollector
from src.gpu.api_system.utils.redis_utils import RedisQueue

try:
    from src.gpu.api_system.api_proto.backtest_pb2 import (
        BacktestRequest,
        BacktestResponse,
        BacktestResult,
        BacktestStatus,
        PerformanceMetrics,
    )
    from src.gpu.api_system.api_proto.backtest_pb2_grpc import BacktestServiceServicer
except ImportError:
    # Fallback if generated files use absolute imports that don't match this structure
    # or if sys.path hacking is needed.
    import sys

    sys.path.append("/opt/claude/mystocks_spec/src/gpu/api_system/api_proto")
    from backtest_pb2 import (
        BacktestRequest,
        BacktestResponse,
        BacktestStatus,
        BacktestResult,
        PerformanceMetrics,
    )
    from backtest_pb2_grpc import BacktestServiceServicer

import grpc

logger = logging.getLogger(__name__)


class IntegratedBacktestService(BacktestServiceServicer):
    """集成回测服务实现"""

    def __init__(
        self,
        gpu_manager: GPUResourceManager,
        redis_queue: RedisQueue,
        metrics_collector: MetricsCollector,
    ):
        # 基础组件
        super().__init__(gpu_manager, redis_queue, metrics_collector)

        # 集成组件
        self.cache_manager = CacheManager()
        self.gpu_engine = GPUAccelerationEngine(gpu_manager, metrics_collector)
        self.running_backtests = {}
        self.backtest_lock = threading.RLock()
        self.executor = ThreadPoolExecutor(max_workers=5)

        # 配置参数
        self.config = {
            "max_concurrent_backtests": 3,
            "gpu_acceleration_enabled": True,
            "cache_enabled": True,
            "real_monitoring": True,
            "auto_optimization": True,
            "result_retention_days": 30,
        }

        # 初始化缓存
        self.cache_manager.initialize()

        logger.info("集成回测服务初始化完成")

    def initialize(self):
        """初始化服务"""
        logger.info("正在初始化集成回测服务...")

        # 启动GPU加速引擎
        self.gpu_engine.initialize()

        # 启动缓存预热
        self._preload_cache()

        # 启动后台任务
        self._start_background_tasks()

        logger.info("集成回测服务初始化完成")

    def _preload_cache(self):
        """预热缓存"""
        try:
            # 预加载常用策略配置
            common_strategies = [
                "trend_following",
                "momentum",
                "mean_reversion",
                "arbitrage",
                "ml_classification",
                "ml_regression",
            ]

            for strategy in common_strategies:
                cache_key = f"strategy_config_{strategy}"
                strategy_config = {
                    "strategy_type": strategy,
                    "parameters": self._get_default_parameters(strategy),
                    "gpu_optimized": True,
                }
                self.cache_manager.set_data(cache_key, strategy_config, data_type="market_data")

            logger.info("缓存预热完成，预加载了%s个策略配置", len(common_strategies))

        except Exception as e:
            logger.error("缓存预热失败: %s", e)

    def _get_default_parameters(self, strategy_type: str) -> Dict[str, Any]:
        """获取默认策略参数"""
        defaults = {
            "trend_following": {
                "lookback_period": 20,
                "moving_average_window": 50,
                "rsi_period": 14,
                "bollinger_period": 20,
                "volume_threshold": 1000000,
            },
            "momentum": {
                "momentum_period": 20,
                "volatility_threshold": 0.02,
                "trend_strength": 0.6,
                "volume_confirmation": True,
            },
            "mean_reversion": {
                "lookback_period": 30,
                "entry_threshold": 2.0,
                "exit_threshold": 0.5,
                "volatility_window": 20,
            },
            "arbitrage": {
                "price_threshold": 0.01,
                "volume_threshold": 500000,
                "time_window": 300,
                "transaction_cost": 0.0003,
            },
            "ml_classification": {
                "model_type": "random_forest",
                "features": ["price_change", "volume", "rsi", "macd"],
                "training_window": 1000,
                "prediction_horizon": 5,
            },
            "ml_regression": {
                "model_type": "ridge",
                "features": ["sma_20", "sma_50", "rsi", "macd", "bb_position"],
                "training_window": 2000,
                "prediction_horizon": 10,
            },
        }
        return defaults.get(strategy_type, {})

    def _start_background_tasks(self):
        """启动后台任务"""
        # 启动监控线程
        monitor_thread = threading.Thread(target=self._monitor_backtests, daemon=True)
        monitor_thread.start()

        # 启动结果清理线程
        cleanup_thread = threading.Thread(target=self._cleanup_old_results, daemon=True)
        cleanup_thread.start()

        logger.info("后台任务启动完成")

    def _monitor_backtests(self):
        """监控运行中的回测"""
        while True:
            try:
                time.sleep(60)  # 每分钟检查一次

                with self.backtest_lock:
                    current_time = datetime.now()
                    completed_backtests = []

                    for backtest_id, backtest_info in self.running_backtests.items():
                        # 检查是否超时
                        start_time = datetime.fromisoformat(backtest_info["start_time"])
                        if current_time - start_time > timedelta(hours=24):  # 24小时超时
                            logger.warning("回测 %s 超时，标记为失败", backtest_id)
                            self._update_backtest_status(backtest_id, "failed", "回测超时")
                            completed_backtests.append(backtest_id)

                        # 检查GPU资源使用情况
                        if backtest_info.get("gpu_accelerated", False):
                            gpu_stats = self.gpu_manager.get_gpu_stats()
                            if gpu_stats.get("utilization", 0) < 10:  # GPU利用率过低
                                logger.info("回测 %s GPU利用率过低: %s%", backtest_id, gpu_stats["utilization"])
                                # 可以考虑重新分配资源

                    # 清理已完成的回测
                    for backtest_id in completed_backtests:
                        del self.running_backtests[backtest_id]

            except Exception as e:
                logger.error("监控回测失败: %s", e)

    def _cleanup_old_results(self):
        """清理旧结果"""
        while True:
            try:
                time.sleep(3600)  # 每小时清理一次

                datetime.now() - timedelta(days=self.config["result_retention_days"])

                # 这里可以实现结果清理逻辑
                # 清理过期的缓存结果
                logger.info("清理%s天前的回测结果", self.config["result_retention_days"])

            except Exception as e:
                logger.error("清理旧结果失败: %s", e)

    def IntegratedBacktest(self, request: BacktestRequest, context: grpc.ServicerContext) -> BacktestResponse:
        """集成回测接口"""
        time.time()
        backtest_id = f"integrated_{int(time.time())}_{hash(str(request.strategy_config))}"

        try:
            logger.info("开始集成回测: %s", backtest_id)

            # 验证请求参数
            validation_result = self._validate_request(request)
            if not validation_result["valid"]:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(validation_result["error"])
                return BacktestResponse(
                    backtest_id=backtest_id,
                    status=BacktestStatus.FAILED,
                    message=validation_result["error"],
                )

            # 检查并发限制
            if len(self.running_backtests) >= self.config["max_concurrent_backtests"]:
                context.set_code(grpc.StatusCode.RESOURCE_EXHAUSTED)
                context.set_details("并发回测数量已达上限")
                return BacktestResponse(
                    backtest_id=backtest_id,
                    status=BacktestStatus.QUEUED,
                    message="回测已排队等待",
                )

            # 初始化回测状态
            with self.backtest_lock:
                self.running_backtests[backtest_id] = {
                    "start_time": datetime.now().isoformat(),
                    "status": "processing",
                    "gpu_accelerated": self.config["gpu_acceleration_enabled"],
                    "original_request": request,
                    "progress": 0,
                }

            # 异步执行回测
            self.executor.submit(self._execute_integrated_backtest, backtest_id, request)

            # 立即返回响应
            return BacktestResponse(
                backtest_id=backtest_id,
                status=BacktestStatus.RUNNING,
                message=f"回测已启动，ID: {backtest_id}",
            )

        except Exception as e:
            logger.error("集成回测失败: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")

            with self.backtest_lock:
                if backtest_id in self.running_backtests:
                    del self.running_backtests[backtest_id]

            return BacktestResponse(
                backtest_id=backtest_id,
                status=BacktestStatus.FAILED,
                message=f"回测失败: {e}",
            )

    def _validate_request(self, request: BacktestRequest) -> Dict[str, Any]:
        """验证请求参数"""
        try:
            # 检查股票代码
            if not request.stock_codes:
                return {"valid": False, "error": "股票代码不能为空"}

            # 检查时间范围
            if request.end_time <= request.start_time:
                return {"valid": False, "error": "结束时间必须大于开始时间"}

            # 检查策略配置
            if not request.strategy_config:
                return {"valid": False, "error": "策略配置不能为空"}

            # 检查参数合理性
            strategy_params = json.loads(request.strategy_config)
            if "lookback_period" in strategy_params and strategy_params["lookback_period"] <= 0:
                return {"valid": False, "error": "回看周期必须大于0"}

            return {"valid": True}

        except Exception as e:
            return {"valid": False, "error": f"参数验证失败: {e}"}

    def _execute_integrated_backtest(self, backtest_id: str, request: BacktestRequest):
        """执行集成回测"""
        try:
            with self.backtest_lock:
                self.running_backtests[backtest_id]["status"] = "processing"

            logger.info("开始执行集成回测: %s", backtest_id)

            # 解析策略配置
            strategy_config = json.loads(request.strategy_config)
            strategy_config.get("strategy_type", "trend_following")

            # 缓存检查
            if self.config["cache_enabled"]:
                cached_result = self._check_cache_for_result(request)
                if cached_result:
                    logger.info("回测 %s 使用缓存结果", backtest_id)
                    self._save_backtest_result(backtest_id, cached_result, from_cache=True)
                    return

            # 生成缓存键
            cache_key = self._generate_cache_key(request)

            # 分配GPU资源
            gpu_id = None
            if self.config["gpu_acceleration_enabled"]:
                gpu_id = self.gpu_manager.allocate_gpu(f"backtest_{backtest_id}", priority="high", memory_required=1024)
                if gpu_id:
                    logger.info("回测 %s 分配GPU: %s", backtest_id, gpu_id)
                    self.running_backtests[backtest_id]["gpu_accelerated"] = True

            try:
                # 执行GPU加速回测
                if gpu_id and self.config["gpu_acceleration_enabled"]:
                    backtest_result = self._execute_gpu_backtest(backtest_id, request, strategy_config, gpu_id)
                else:
                    # CPU回测
                    backtest_result = self._execute_cpu_backtest(backtest_id, request, strategy_config)

                # 保存结果
                self._save_backtest_result(backtest_id, backtest_result, from_cache=False)

                # 更新缓存
                if self.config["cache_enabled"]:
                    self.cache_manager.set_data(cache_key, backtest_result, data_type="computation_results")

                # 自动优化建议
                if self.config["auto_optimization"]:
                    optimization_suggestions = self._generate_optimization_suggestions(backtest_result)
                    backtest_result["optimization_suggestions"] = optimization_suggestions

                logger.info("集成回测完成: %s", backtest_id)

            finally:
                # 释放GPU资源
                if gpu_id:
                    self.gpu_manager.release_gpu(f"backtest_{backtest_id}", gpu_id)
                    logger.info("回测 %s 释放GPU: %s", backtest_id, gpu_id)

        except Exception as e:
            logger.error("执行集成回测失败: %s - %s", backtest_id, e)
            self._update_backtest_status(backtest_id, "failed", str(e))
        finally:
            with self.backtest_lock:
                if backtest_id in self.running_backtests:
                    del self.running_backtests[backtest_id]

    def _check_cache_for_result(self, request: BacktestRequest) -> Optional[Dict[str, Any]]:
        """检查缓存中是否有结果"""
        try:
            cache_key = self._generate_cache_key(request)
            cached_result = self.cache_manager.get_data(cache_key, data_type="computation_results")

            if cached_result:
                logger.info("找到缓存结果: %s", cache_key)
                return cached_result

            return None
        except Exception as e:
            logger.error("检查缓存失败: %s", e)
            return None

    def _generate_cache_key(self, request: BacktestRequest) -> str:
        """生成缓存键"""
        key_components = [
            "backtest",
            ",".join(sorted(request.stock_codes)),
            request.start_time,
            request.end_time,
            request.strategy_config,
            str(request.initial_capital),
            str(request.commission_rate),
        ]
        return hashlib.md5("|".join(key_components).encode()).hexdigest()

    def _execute_gpu_backtest(
        self,
        backtest_id: str,
        request: BacktestRequest,
        strategy_config: Dict,
        gpu_id: int,
    ) -> Dict[str, Any]:
        """执行GPU加速回测"""
        try:
            # 使用GPU加速引擎执行回测
            backtest_result = self.gpu_engine.backtest_engine.run_gpu_backtest(
                stock_codes=request.stock_codes,
                start_time=request.start_time,
                end_time=request.end_time,
                strategy_config=strategy_config,
                initial_capital=request.initial_capital,
                commission_rate=request.commission_rate,
                cache_manager=self.cache_manager,
            )

            # 记录GPU使用指标
            gpu_stats = self.gpu_manager.get_gpu_stats()
            backtest_result["gpu_metrics"] = {
                "gpu_id": gpu_id,
                "utilization": gpu_stats.get("utilization", 0),
                "memory_usage": gpu_stats.get("memory_usage", 0),
                "processing_time": time.time() - backtest_result.get("start_time", time.time()),
            }

            return backtest_result

        except Exception as e:
            logger.error("GPU回测失败: %s", e)
            # 回退到CPU
            logger.info("回退到CPU回测: %s", backtest_id)
            return self._execute_cpu_backtest(backtest_id, request, strategy_config)

    def _execute_cpu_backtest(
        self, backtest_id: str, request: BacktestRequest, strategy_config: Dict
    ) -> Dict[str, Any]:
        """执行CPU回测"""
        try:
            # 使用标准回测引擎
            backtest_result = super().RunBacktest(
                (request.original_request if hasattr(request, "original_request") else request),
                None,
            )

            # 添加CPU标记
            backtest_result["cpu_accelerated"] = True
            backtest_result["gpu_metrics"] = None

            return backtest_result

        except Exception as e:
            logger.error("CPU回测失败: %s", e)
            raise e

    def _save_backtest_result(self, backtest_id: str, result: Dict[str, Any], from_cache: bool = False):
        """保存回测结果"""
        try:
            with self.backtest_lock:
                self.running_backtests[backtest_id]["result"] = result
                self.running_backtests[backtest_id]["status"] = "completed"
                self.running_backtests[backtest_id]["completed_at"] = datetime.now().isoformat()
                self.running_backtests[backtest_id]["from_cache"] = from_cache

            # 记录完成指标
            self.metrics_collector.record_task_metrics("backtest", "completed", result.get("execution_time", 0))

            logger.info("回测结果已保存: %s", backtest_id)

        except Exception as e:
            logger.error("保存回测结果失败: %s", e)

    def _update_backtest_status(self, backtest_id: str, status: str, message: str):
        """更新回测状态"""
        try:
            with self.backtest_lock:
                if backtest_id in self.running_backtests:
                    self.running_backtests[backtest_id]["status"] = status
                    self.running_backtests[backtest_id]["message"] = message
                    self.running_backtests[backtest_id]["updated_at"] = datetime.now().isoformat()

            logger.info("回测状态更新: %s -> %s", backtest_id, status)

        except Exception as e:
            logger.error("更新回测状态失败: %s", e)

    def _generate_optimization_suggestions(self, backtest_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成优化建议"""
        suggestions = []

        try:
            # 基于回测结果生成建议
            performance = backtest_result.get("performance", {})

            # 收益率优化建议
            if performance.get("total_return", 0) < 0.1:  # 收益率低于10%
                suggestions.append(
                    {
                        "type": "return_optimization",
                        "priority": "high",
                        "message": "收益率偏低，建议调整策略参数",
                        "suggestions": [
                            "增加趋势跟踪周期",
                            "优化止盈止损点位",
                            "考虑多因子组合策略",
                        ],
                    }
                )

            # 风险优化建议
            if performance.get("max_drawdown", 0) > 0.2:  # 最大回撤超过20%
                suggestions.append(
                    {
                        "type": "risk_optimization",
                        "priority": "high",
                        "message": "风险较高，建议优化风险管理",
                        "suggestions": [
                            "降低仓位大小",
                            "设置更严格的风控规则",
                            "分散投资到更多股票",
                        ],
                    }
                )

            # 交易频率优化建议
            trade_count = performance.get("trade_count", 0)
            if trade_count > 1000:  # 交易过于频繁
                suggestions.append(
                    {
                        "type": "frequency_optimization",
                        "priority": "medium",
                        "message": "交易频率过高，建议优化交易策略",
                        "suggestions": [
                            "增加交易信号过滤",
                            "提高入场条件",
                            "减少小额交易",
                        ],
                    }
                )

            # GPU优化建议
            gpu_metrics = backtest_result.get("gpu_metrics", {})
            if gpu_metrics and gpu_metrics.get("utilization", 0) < 50:
                suggestions.append(
                    {
                        "type": "gpu_optimization",
                        "priority": "low",
                        "message": "GPU利用率较低，建议优化计算任务",
                        "suggestions": [
                            "增加批量处理大小",
                            "使用更复杂的模型",
                            "并行处理更多股票",
                        ],
                    }
                )

            return suggestions

        except Exception as e:
            logger.error("生成优化建议失败: %s", e)
            return []

    def GetBacktestStatus(self, request, context) -> BacktestStatus:
        """获取回测状态"""
        try:
            backtest_id = request.backtest_id

            with self.backtest_lock:
                if backtest_id in self.running_backtests:
                    backtest_info = self.running_backtests[backtest_id]
                    return BacktestStatus(
                        backtest_id=backtest_id,
                        status=backtest_info.get("status", "unknown"),
                        message=backtest_info.get("message", ""),
                        progress=backtest_info.get("progress", 0),
                        start_time=backtest_info.get("start_time", ""),
                        completed_at=backtest_info.get("completed_at", ""),
                        gpu_accelerated=backtest_info.get("gpu_accelerated", False),
                    )
                else:
                    # 检查是否已完成（可能已经在结果中）
                    if hasattr(self, "completed_backtests") and backtest_id in self.completed_backtests:
                        result = self.completed_backtests[backtest_id]
                        return BacktestStatus(
                            backtest_id=backtest_id,
                            status="completed",
                            message="回测已完成",
                            progress=100,
                            start_time=result.get("start_time", ""),
                            completed_at=result.get("completed_at", ""),
                            gpu_accelerated=result.get("gpu_accelerated", False),
                        )
                    else:
                        context.set_code(grpc.StatusCode.NOT_FOUND)
                        context.set_details(f"未找到回测: {backtest_id}")
                        return BacktestStatus()

        except Exception as e:
            logger.error("获取回测状态失败: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")
            return BacktestStatus()

    def GetBacktestResult(self, request, context) -> BacktestResult:
        """获取回测结果"""
        try:
            backtest_id = request.backtest_id

            with self.backtest_lock:
                if backtest_id in self.running_backtests:
                    backtest_info = self.running_backtests[backtest_id]
                    result = backtest_info.get("result")

                    if result:
                        return self._convert_to_backtest_result(backtest_id, result)
                    else:
                        context.set_code(grpc.StatusCode.NOT_FOUND)
                        context.set_details(f"回测结果尚未准备好: {backtest_id}")
                        return BacktestResult()
                else:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"未找到回测: {backtest_id}")
                    return BacktestResult()

        except Exception as e:
            logger.error("获取回测结果失败: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")
            return BacktestResult()

    def _convert_to_backtest_result(self, backtest_id: str, result: Dict[str, Any]) -> BacktestResult:
        """转换为回测结果消息"""
        try:
            performance = result.get("performance", {})

            # 转换性能指标
            performance_metrics = PerformanceMetrics(
                total_return=performance.get("total_return", 0.0),
                annualized_return=performance.get("annualized_return", 0.0),
                sharpe_ratio=performance.get("sharpe_ratio", 0.0),
                max_drawdown=performance.get("max_drawdown", 0.0),
                win_rate=performance.get("win_rate", 0.0),
                profit_factor=performance.get("profit_factor", 0.0),
                trade_count=performance.get("trade_count", 0),
                max_consecutive_losses=performance.get("max_consecutive_losses", 0),
                recovery_factor=performance.get("recovery_factor", 0.0),
                calmar_ratio=performance.get("calmar_ratio", 0.0),
                sortino_ratio=performance.get("sortino_ratio", 0.0),
                information_ratio=performance.get("information_ratio", 0.0),
                beta=performance.get("beta", 0.0),
                alpha=performance.get("alpha", 0.0),
                volatility=performance.get("volatility", 0.0),
            )

            # 转换优化建议
            optimization_suggestions = result.get("optimization_suggestions", [])

            return BacktestResult(
                backtest_id=backtest_id,
                status=BacktestStatus.COMPLETED,
                performance_metrics=performance_metrics,
                optimization_suggestions=optimization_suggestions,
                execution_time=result.get("execution_time", 0.0),
                gpu_metrics=result.get("gpu_metrics"),
                from_cache=result.get("from_cache", False),
                completed_at=result.get("completed_at", ""),
                timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error("转换回测结果失败: %s", e)
            raise e

    def GetIntegratedBacktestStats(self, request, context):
        """获取集成回测统计信息"""
        try:
            with self.backtest_lock:
                running_count = len(self.running_backtests)
                gpu_accelerated_count = sum(
                    1 for info in self.running_backtests.values() if info.get("gpu_accelerated", False)
                )

            stats = {
                "timestamp": datetime.now().isoformat(),
                "running_backtests": running_count,
                "gpu_accelerated_backtests": gpu_accelerated_count,
                "total_backtests": len(self.running_backtests),
                "gpu_utilization": self.gpu_manager.get_gpu_stats().get("utilization", 0),
                "cache_hit_rate": self.cache_manager.get_cache_performance_report()
                .get("cache_stats", {})
                .get("overall_hit_rate", 0),
                "system_status": ("healthy" if running_count < self.config["max_concurrent_backtests"] else "busy"),
            }

            return json.dumps(stats, ensure_ascii=False)

        except Exception as e:
            logger.error("获取集成回测统计失败: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")
            return json.dumps({"error": str(e)})

    def stop(self):
        """停止服务"""
        logger.info("正在停止集成回测服务...")

        # 停止所有运行中的回测
        with self.backtest_lock:
            for backtest_id, backtest_info in self.running_backtests.items():
                if backtest_info.get("status") == "processing":
                    self._update_backtest_status(backtest_id, "cancelled", "服务停止")

        # 关闭线程池
        self.executor.shutdown(wait=True)

        # 关闭缓存管理器
        self.cache_manager.shutdown()

        logger.info("集成回测服务已停止")
