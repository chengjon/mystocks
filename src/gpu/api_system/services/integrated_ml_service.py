"""
集成机器学习训练服务
Integrated Machine Learning Training Service
"""

import logging
import time
import threading
import pickle
import json
from typing import Dict, Any, Tuple
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
from pathlib import Path

from src.gpu.api_system.utils.gpu_utils import GPUResourceManager
from src.gpu.api_system.utils.redis_utils import RedisQueue
from src.gpu.api_system.utils.monitoring import MetricsCollector
from src.gpu.api_system.utils.cache_optimization import CacheManager
from src.gpu.api_system.utils.gpu_acceleration_engine import GPUAccelerationEngine

try:
    from src.gpu.api_system.api_proto.ml_pb2 import (
        TrainModelRequest,
        TrainModelResponse,
        PredictRequest,
        PredictResponse,
        ModelMetrics,
        TrainingStatus,
    )
    from src.gpu.api_system.api_proto.ml_pb2_grpc import MLServiceServicer
except ImportError:
    import sys

    sys.path.append("/opt/claude/mystocks_spec/src/gpu/api_system/api_proto")
    from ml_pb2 import (
        TrainModelRequest,
        TrainModelResponse,
        PredictRequest,
        PredictResponse,
        ModelMetrics,
        TrainingStatus,
    )
    from ml_pb2_grpc import MLServiceServicer

import grpc

logger = logging.getLogger(__name__)


class IntegratedMLService(MLServiceServicer):
    """集成机器学习训练服务实现"""

    def __init__(
        self,
        gpu_manager: GPUResourceManager,
        redis_queue: RedisQueue,
        metrics_collector: MetricsCollector,
    ):
        # 基础组件
        self.gpu_manager = gpu_manager
        self.redis_queue = redis_queue
        self.metrics_collector = metrics_collector

        # 集成组件
        self.cache_manager = CacheManager()
        self.gpu_engine = GPUAccelerationEngine(gpu_manager, metrics_collector)

        # 训练任务管理
        self.training_tasks = {}  # task_id -> task_info
        self.task_lock = threading.RLock()

        # 模型存储
        self.models = {}  # model_id -> model_info
        self.model_lock = threading.RLock()

        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=3)

        # 配置参数
        self.config = {
            "max_concurrent_training": 2,
            "model_save_path": "/opt/claude/mystocks_spec/gpu_api_system/models",
            "enable_gpu_training": True,
            "enable_auto_tuning": True,
            "enable_model_cache": True,
            "training_timeout": 7200,  # 2小时训练超时
            "model_retention_days": 30,
        }

        # 性能统计
        self.stats = {
            "total_models_trained": 0,
            "gpu_training_count": 0,
            "cpu_training_count": 0,
            "total_predictions": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

        # 创建模型保存目录
        Path(self.config["model_save_path"]).mkdir(parents=True, exist_ok=True)

        logger.info("集成ML训练服务初始化完成")

    def initialize(self):
        """初始化服务"""
        logger.info("正在初始化集成ML训练服务...")

        # 初始化缓存管理器
        self.cache_manager.initialize()

        # 初始化GPU加速引擎
        self.gpu_engine.initialize()

        # 启动后台任务
        self._start_background_tasks()

        # 加载已保存的模型
        self._load_saved_models()

        logger.info("集成ML训练服务初始化完成")

    def _start_background_tasks(self):
        """启动后台任务"""
        # 训练任务监控线程
        monitor_thread = threading.Thread(target=self._monitor_training_tasks, daemon=True)
        monitor_thread.start()

        # 模型清理线程
        cleanup_thread = threading.Thread(target=self._cleanup_old_models, daemon=True)
        cleanup_thread.start()

        # 性能统计线程
        stats_thread = threading.Thread(target=self._collect_stats, daemon=True)
        stats_thread.start()

        logger.info("后台任务启动完成")

    def _monitor_training_tasks(self):
        """监控训练任务"""
        while True:
            try:
                time.sleep(60)  # 每分钟检查一次

                with self.task_lock:
                    current_time = datetime.now()
                    timeout_tasks = []

                    for task_id, task_info in self.training_tasks.items():
                        # 检查任务超时
                        if task_info["status"] == "training":
                            start_time = datetime.fromisoformat(task_info["start_time"])
                            if current_time - start_time > timedelta(seconds=self.config["training_timeout"]):
                                logger.warning("训练任务 %s 超时", task_id)
                                timeout_tasks.append(task_id)

                    # 标记超时任务为失败
                    for task_id in timeout_tasks:
                        self.training_tasks[task_id]["status"] = "failed"
                        self.training_tasks[task_id]["error"] = "训练超时"

            except Exception as e:
                logger.error("监控训练任务失败: %s", e)

    def _cleanup_old_models(self):
        """清理旧模型"""
        while True:
            try:
                time.sleep(3600)  # 每小时清理一次

                cutoff_time = datetime.now() - timedelta(days=self.config["model_retention_days"])

                with self.model_lock:
                    old_models = []

                    for model_id, model_info in self.models.items():
                        created_time = datetime.fromisoformat(model_info["created_at"])
                        if created_time < cutoff_time:
                            old_models.append(model_id)

                    for model_id in old_models:
                        logger.info("删除过期模型: %s", model_id)
                        # 删除模型文件
                        model_path = Path(self.config["model_save_path"]) / f"{model_id}.pkl"
                        if model_path.exists():
                            model_path.unlink()
                        # 从内存中删除
                        del self.models[model_id]

                    if old_models:
                        logger.info("清理了 %s 个过期模型", len(old_models))

            except Exception as e:
                logger.error("清理旧模型失败: %s", e)

    def _collect_stats(self):
        """收集性能统计"""
        while True:
            try:
                time.sleep(60)  # 每分钟收集一次

                # 记录统计信息
                self.metrics_collector.record_custom_metric("ml_models_trained", self.stats["total_models_trained"])
                self.metrics_collector.record_custom_metric("ml_predictions", self.stats["total_predictions"])

                # GPU训练比例
                total_training = self.stats["gpu_training_count"] + self.stats["cpu_training_count"]
                if total_training > 0:
                    gpu_ratio = self.stats["gpu_training_count"] / total_training * 100
                    self.metrics_collector.record_custom_metric("ml_gpu_training_ratio", gpu_ratio)

            except Exception as e:
                logger.error("收集统计信息失败: %s", e)

    def _load_saved_models(self):
        """加载已保存的模型"""
        try:
            model_dir = Path(self.config["model_save_path"])
            model_files = list(model_dir.glob("*.pkl"))

            for model_file in model_files:
                try:
                    model_id = model_file.stem
                    with open(model_file, "rb") as f:
                        model_data = pickle.load(f)

                    with self.model_lock:
                        self.models[model_id] = {
                            "model": model_data["model"],
                            "metadata": model_data["metadata"],
                            "created_at": model_data.get("created_at", datetime.now().isoformat()),
                            "model_type": model_data.get("model_type", "unknown"),
                        }

                    logger.info("加载模型: %s", model_id)

                except Exception as e:
                    logger.error("加载模型文件失败 %s: %s", model_file, e)

            logger.info("加载了 %s 个已保存的模型", len(self.models))

        except Exception as e:
            logger.error("加载已保存模型失败: %s", e)

    def TrainModel(self, request: TrainModelRequest, context: grpc.ServicerContext) -> TrainModelResponse:
        """训练模型"""
        task_id = f"ml_train_{int(time.time())}_{hash(str(request))}"

        try:
            logger.info("开始训练任务: %s", task_id)

            # 验证请求
            validation_result = self._validate_training_request(request)
            if not validation_result["valid"]:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(validation_result["error"])
                return TrainModelResponse(
                    task_id=task_id,
                    status=TrainingStatus.FAILED,
                    message=validation_result["error"],
                )

            # 检查并发限制
            with self.task_lock:
                active_training_count = sum(1 for task in self.training_tasks.values() if task["status"] == "training")

                if active_training_count >= self.config["max_concurrent_training"]:
                    context.set_code(grpc.StatusCode.RESOURCE_EXHAUSTED)
                    context.set_details("并发训练任务已达上限")
                    return TrainModelResponse(
                        task_id=task_id,
                        status=TrainingStatus.QUEUED,
                        message="训练任务已排队等待",
                    )

                # 初始化训练任务
                self.training_tasks[task_id] = {
                    "task_id": task_id,
                    "status": "training",
                    "start_time": datetime.now().isoformat(),
                    "request": request,
                    "progress": 0,
                }

            # 异步执行训练
            self.executor.submit(self._execute_training, task_id, request)

            return TrainModelResponse(
                task_id=task_id,
                status=TrainingStatus.TRAINING,
                message=f"训练已启动，任务ID: {task_id}",
            )

        except Exception as e:
            logger.error("训练模型失败: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")

            with self.task_lock:
                if task_id in self.training_tasks:
                    del self.training_tasks[task_id]

            return TrainModelResponse(task_id=task_id, status=TrainingStatus.FAILED, message=f"训练失败: {e}")

    def _validate_training_request(self, request: TrainModelRequest) -> Dict[str, Any]:
        """验证训练请求"""
        try:
            # 检查模型类型
            if not request.model_type:
                return {"valid": False, "error": "模型类型不能为空"}

            # 检查训练数据
            if not request.training_data:
                return {"valid": False, "error": "训练数据不能为空"}

            # 检查特征列
            if not request.feature_columns:
                return {"valid": False, "error": "特征列不能为空"}

            # 检查目标列
            if not request.target_column:
                return {"valid": False, "error": "目标列不能为空"}

            return {"valid": True}

        except Exception as e:
            return {"valid": False, "error": f"验证失败: {e}"}

    def _execute_training(self, task_id: str, request: TrainModelRequest):
        """执行训练任务"""
        gpu_id = None

        try:
            logger.info("执行训练任务: %s", task_id)

            # 解析训练数据
            training_data = json.loads(request.training_data)
            df = pd.DataFrame(training_data)

            # 准备特征和目标
            X = df[list(request.feature_columns)]
            y = df[request.target_column]

            # 分配GPU资源
            if self.config["enable_gpu_training"]:
                gpu_id = self.gpu_manager.allocate_gpu(f"ml_train_{task_id}", priority="high", memory_required=2048)

                if gpu_id:
                    logger.info("训练任务 %s 分配GPU: %s", task_id, gpu_id)

            # 执行训练
            if gpu_id and self.config["enable_gpu_training"]:
                model, metrics = self._train_model_gpu(
                    X,
                    y,
                    request.model_type,
                    json.loads(request.model_params) if request.model_params else {},
                )
                self.stats["gpu_training_count"] += 1
            else:
                model, metrics = self._train_model_cpu(
                    X,
                    y,
                    request.model_type,
                    json.loads(request.model_params) if request.model_params else {},
                )
                self.stats["cpu_training_count"] += 1

            # 保存模型
            model_id = f"model_{int(time.time())}_{request.model_type}"
            self._save_model(model_id, model, request.model_type, metrics)

            # 更新任务状态
            with self.task_lock:
                self.training_tasks[task_id]["status"] = "completed"
                self.training_tasks[task_id]["model_id"] = model_id
                self.training_tasks[task_id]["metrics"] = metrics
                self.training_tasks[task_id]["completed_at"] = datetime.now().isoformat()

            self.stats["total_models_trained"] += 1

            logger.info("训练任务完成: %s, 模型ID: %s", task_id, model_id)

        except Exception as e:
            logger.error("执行训练任务失败 %s: %s", task_id, e)

            with self.task_lock:
                if task_id in self.training_tasks:
                    self.training_tasks[task_id]["status"] = "failed"
                    self.training_tasks[task_id]["error"] = str(e)

        finally:
            # 释放GPU资源
            if gpu_id:
                self.gpu_manager.release_gpu(f"ml_train_{task_id}", gpu_id)
                logger.info("训练任务 %s 释放GPU: %s", task_id, gpu_id)

    def _train_model_gpu(self, X: pd.DataFrame, y: pd.Series, model_type: str, params: Dict) -> Tuple[Any, Dict]:
        """GPU训练模型"""
        try:
            import cudf

            # 转换为GPU数据
            X_gpu = cudf.DataFrame.from_pandas(X)
            y_gpu = cudf.Series(y)

            # 选择模型
            if model_type == "linear_regression":
                from cuml.linear_model import LinearRegression

                model = LinearRegression(**params)
            elif model_type == "ridge":
                from cuml.linear_model import Ridge

                model = Ridge(**params)
            elif model_type == "lasso":
                from cuml.linear_model import Lasso

                model = Lasso(**params)
            elif model_type == "random_forest":
                from cuml.ensemble import RandomForestRegressor

                model = RandomForestRegressor(**params)
            elif model_type == "logistic":
                from cuml.linear_model import LogisticRegression

                model = LogisticRegression(**params)
            else:
                raise ValueError(f"不支持的模型类型: {model_type}")

            # 训练模型
            start_time = time.time()
            model.fit(X_gpu, y_gpu)
            training_time = time.time() - start_time

            # 计算评估指标
            y_pred = model.predict(X_gpu)

            if model_type in ["linear_regression", "ridge", "lasso", "random_forest"]:
                # 回归指标
                from cuml.metrics import r2_score, mean_squared_error

                r2 = float(r2_score(y_gpu, y_pred))
                mse = float(mean_squared_error(y_gpu, y_pred))

                metrics = {
                    "r2_score": r2,
                    "mse": mse,
                    "rmse": np.sqrt(mse),
                    "training_time": training_time,
                    "gpu_accelerated": True,
                }
            else:
                # 分类指标
                from cuml.metrics import accuracy_score

                accuracy = float(accuracy_score(y_gpu, y_pred))

                metrics = {
                    "accuracy": accuracy,
                    "training_time": training_time,
                    "gpu_accelerated": True,
                }

            logger.info("GPU训练完成，耗时: %s秒", training_time)

            return model, metrics

        except Exception as e:
            logger.error("GPU训练失败: %s", e)
            raise e

    def _train_model_cpu(self, X: pd.DataFrame, y: pd.Series, model_type: str, params: Dict) -> Tuple[Any, Dict]:
        """CPU训练模型"""
        try:
            from sklearn.linear_model import (
                LinearRegression,
                Ridge,
                Lasso,
                LogisticRegression,
            )
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.metrics import r2_score, mean_squared_error, accuracy_score

            # 选择模型
            if model_type == "linear_regression":
                model = LinearRegression(**params)
            elif model_type == "ridge":
                model = Ridge(**params)
            elif model_type == "lasso":
                model = Lasso(**params)
            elif model_type == "random_forest":
                model = RandomForestRegressor(**params)
            elif model_type == "logistic":
                model = LogisticRegression(**params)
            else:
                raise ValueError(f"不支持的模型类型: {model_type}")

            # 训练模型
            start_time = time.time()
            model.fit(X, y)
            training_time = time.time() - start_time

            # 计算评估指标
            y_pred = model.predict(X)

            if model_type in ["linear_regression", "ridge", "lasso", "random_forest"]:
                # 回归指标
                r2 = r2_score(y, y_pred)
                mse = mean_squared_error(y, y_pred)

                metrics = {
                    "r2_score": float(r2),
                    "mse": float(mse),
                    "rmse": float(np.sqrt(mse)),
                    "training_time": training_time,
                    "gpu_accelerated": False,
                }
            else:
                # 分类指标
                accuracy = accuracy_score(y, y_pred)

                metrics = {
                    "accuracy": float(accuracy),
                    "training_time": training_time,
                    "gpu_accelerated": False,
                }

            logger.info("CPU训练完成，耗时: %s秒", training_time)

            return model, metrics

        except Exception as e:
            logger.error("CPU训练失败: %s", e)
            raise e

    def _save_model(self, model_id: str, model: Any, model_type: str, metrics: Dict):
        """保存模型"""
        try:
            # 保存到内存
            with self.model_lock:
                self.models[model_id] = {
                    "model": model,
                    "metadata": {
                        "model_type": model_type,
                        "metrics": metrics,
                        "created_at": datetime.now().isoformat(),
                    },
                    "created_at": datetime.now().isoformat(),
                    "model_type": model_type,
                }

            # 保存到文件
            model_path = Path(self.config["model_save_path"]) / f"{model_id}.pkl"
            with open(model_path, "wb") as f:
                pickle.dump(
                    {
                        "model": model,
                        "metadata": {
                            "model_type": model_type,
                            "metrics": metrics,
                            "created_at": datetime.now().isoformat(),
                        },
                        "model_type": model_type,
                        "created_at": datetime.now().isoformat(),
                    },
                    f,
                )

            logger.info("模型已保存: %s", model_id)

        except Exception as e:
            logger.error("保存模型失败: %s", e)
            raise e

    def Predict(self, request: PredictRequest, context: grpc.ServicerContext) -> PredictResponse:
        """预测"""
        try:
            model_id = request.model_id

            # 检查模型是否存在
            with self.model_lock:
                if model_id not in self.models:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"未找到模型: {model_id}")
                    return PredictResponse()

                model_info = self.models[model_id]
                model = model_info["model"]

            # 解析输入数据
            input_data = json.loads(request.input_data)
            X = pd.DataFrame(input_data)

            # 执行预测
            start_time = time.time()

            # 检查是否是GPU模型
            if hasattr(model, "__module__") and "cuml" in model.__module__:
                # GPU预测
                import cudf

                X_gpu = cudf.DataFrame.from_pandas(X)
                predictions = model.predict(X_gpu)
                predictions = predictions.to_pandas().tolist()
            else:
                # CPU预测
                predictions = model.predict(X).tolist()

            prediction_time = time.time() - start_time

            self.stats["total_predictions"] += 1

            return PredictResponse(
                model_id=model_id,
                predictions=predictions,
                prediction_time=prediction_time,
                timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error("预测失败: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")
            return PredictResponse()

    def GetTrainingStatus(self, request, context) -> TrainingStatus:
        """获取训练状态"""
        try:
            task_id = request.task_id

            with self.task_lock:
                if task_id not in self.training_tasks:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"未找到训练任务: {task_id}")
                    return TrainingStatus()

                task_info = self.training_tasks[task_id]

                return TrainingStatus(
                    task_id=task_id,
                    status=task_info["status"],
                    progress=task_info.get("progress", 0),
                    start_time=task_info["start_time"],
                    completed_at=task_info.get("completed_at", ""),
                    model_id=task_info.get("model_id", ""),
                    error=task_info.get("error", ""),
                )

        except Exception as e:
            logger.error("获取训练状态失败: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")
            return TrainingStatus()

    def GetModelMetrics(self, request, context) -> ModelMetrics:
        """获取模型指标"""
        try:
            model_id = request.model_id

            with self.model_lock:
                if model_id not in self.models:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"未找到模型: {model_id}")
                    return ModelMetrics()

                model_info = self.models[model_id]
                metadata = model_info["metadata"]
                metrics = metadata["metrics"]

                return ModelMetrics(
                    model_id=model_id,
                    model_type=metadata["model_type"],
                    metrics=metrics,
                    created_at=metadata["created_at"],
                    gpu_accelerated=metrics.get("gpu_accelerated", False),
                )

        except Exception as e:
            logger.error("获取模型指标失败: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")
            return ModelMetrics()

    def GetMLStats(self, request, context):
        """获取ML统计信息"""
        try:
            with self.task_lock:
                active_training_count = sum(1 for task in self.training_tasks.values() if task["status"] == "training")

            stats = {
                "timestamp": datetime.now().isoformat(),
                "total_models_trained": self.stats["total_models_trained"],
                "total_predictions": self.stats["total_predictions"],
                "active_training_tasks": active_training_count,
                "total_models": len(self.models),
                "gpu_training_ratio": (
                    self.stats["gpu_training_count"]
                    / (self.stats["gpu_training_count"] + self.stats["cpu_training_count"])
                    * 100
                    if (self.stats["gpu_training_count"] + self.stats["cpu_training_count"]) > 0
                    else 0
                ),
                "gpu_utilization": self.gpu_manager.get_gpu_stats().get("utilization", 0),
            }

            return json.dumps(stats, ensure_ascii=False)

        except Exception as e:
            logger.error("获取ML统计失败: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")
            return json.dumps({"error": str(e)})

    def stop(self):
        """停止服务"""
        logger.info("正在停止集成ML训练服务...")

        # 等待正在运行的训练任务完成
        self.executor.shutdown(wait=True)

        # 关闭缓存管理器
        self.cache_manager.shutdown()

        logger.info("集成ML训练服务已停止")
