"""
回测服务
Backtest Service
"""

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, List

import numpy as np

from src.gpu.api_system.utils.gpu_utils import GPUResourceManager
from src.gpu.api_system.utils.monitoring import MetricsCollector
from src.gpu.api_system.utils.redis_utils import RedisQueue
from src.gpu.api_system.services.backtest_service.backtest_engine import BacktestEngine

try:
    from src.gpu.api_system.api_proto.backtest_pb2 import (
        BacktestRequest,
        BatchRequest,
        BatchResponse,
        HistoryResponse,
        OptimizationResult,
        ParameterOptimizationRequest,
        PerformanceMetrics,
        QueryRequest,
        QueryResponse,
        TaskResponse,
    )
    from src.gpu.api_system.api_proto.backtest_pb2_grpc import BacktestServiceServicer
except ImportError:
    import sys

    sys.path.append("/opt/claude/mystocks_spec/src/gpu/api_system/api_proto")
    from backtest_pb2 import (
        BacktestRequest,
        TaskResponse,
        QueryRequest,
        QueryResponse,
        HistoryResponse,
        BatchRequest,
        BatchResponse,
        ParameterOptimizationRequest,
        OptimizationResult,
    )
    from backtest_pb2_grpc import BacktestServiceServicer

import grpc

logger = logging.getLogger(__name__)

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

    def SubmitBacktest(self, request: BacktestRequest, context: grpc.ServicerContext) -> TaskResponse:
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

            logger.info("回测任务已提交: %s", task_id)

            return TaskResponse(
                task_id=task_id,
                status="queued",
                progress=0,
                message="任务已加入队列",
                created_at=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error("提交回测任务失败: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")
            return TaskResponse()

    def QueryBacktest(self, request: QueryRequest, context: grpc.ServicerContext) -> QueryResponse:
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
            logger.error("查询回测状态失败: %s", e)
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
            logger.error("获取回测历史失败: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")
            return HistoryResponse()

    def SubmitBatchBacktest(self, request: BatchRequest, context: grpc.ServicerContext) -> BatchResponse:
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
                    logger.error("批量任务提交失败 %s: %s", i, e)
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
            logger.error("批量提交回测失败: %s", e)
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
            logger.error("参数优化失败: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")
            return OptimizationResult()

    def _grid_search_optimization(self, request: ParameterOptimizationRequest) -> Dict[str, Any]:
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
                logger.warning("参数组合优化失败 %s: %s", params, e)
                continue

        execution_time = time.time() - start_time

        return {
            "best_params": best_params,
            "best_performance": best_performance,
            "all_results": all_results,
            "total_iterations": len(param_grid),
            "execution_time": execution_time,
        }

    def _random_search_optimization(self, request: ParameterOptimizationRequest) -> Dict[str, Any]:
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
                    value = np.random.randint(param_range["min"], param_range["max"] + 1)
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
                logger.warning("随机参数优化失败 %s: %s", params, e)
                continue

        execution_time = time.time() - start_time

        return {
            "best_params": best_params,
            "best_performance": best_performance,
            "all_results": all_results,
            "total_iterations": i + 1,
            "execution_time": execution_time,
        }

    def _bayesian_optimization(self, request: ParameterOptimizationRequest) -> Dict[str, Any]:
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
            "strategies_used": list(set([task["request"].strategy_type for task in self.active_tasks.values()])),
        }

    def stop(self):
        """停止服务"""
        logger.info("正在停止回测服务...")
        self.running = False
        self.executor.shutdown(wait=True)
        logger.info("回测服务已停止")


