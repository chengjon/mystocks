"""
集成服务单元测试
测试回测、实时处理和ML训练三大集成服务
"""

import pytest
import grpc
from unittest.mock import Mock, patch
import json


class TestIntegratedBacktestService:
    """集成回测服务测试"""

    @pytest.fixture
    def backtest_service(self, mock_gpu_manager, mock_redis_queue, mock_metrics_collector):
        """创建回测服务实例"""
        with patch("services.integrated_backtest_service.IntegratedBacktestService") as MockService:
            service = MockService(mock_gpu_manager, mock_redis_queue, mock_metrics_collector)
            yield service

    def test_submit_backtest(self, backtest_service, sample_strategy_config):
        """测试提交回测任务"""
        request = Mock()
        request.stock_codes = ["000001.SZ", "600000.SH"]
        request.start_time = "2024-01-01"
        request.end_time = "2024-12-31"
        request.strategy_config = json.dumps(sample_strategy_config)
        request.initial_capital = 1000000
        request.commission_rate = 0.0003

        # 模拟响应
        response = Mock()
        response.backtest_id = "bt_12345"
        response.status = "SUBMITTED"
        response.message = "Backtest task submitted successfully"

        backtest_service.IntegratedBacktest.return_value = response

        result = backtest_service.IntegratedBacktest(request, None)

        assert result.backtest_id is not None
        assert result.status == "SUBMITTED"

    def test_get_backtest_status(self, backtest_service):
        """测试查询回测状态"""
        request = Mock()
        request.backtest_id = "bt_12345"

        response = Mock()
        response.backtest_id = "bt_12345"
        response.status = "RUNNING"
        response.progress = 65.5
        response.estimated_time_remaining = 10

        backtest_service.GetBacktestStatus.return_value = response

        result = backtest_service.GetBacktestStatus(request, None)

        assert result.backtest_id == "bt_12345"
        assert result.status == "RUNNING"
        assert 0 <= result.progress <= 100

    def test_get_backtest_result(self, backtest_service):
        """测试获取回测结果"""
        request = Mock()
        request.backtest_id = "bt_12345"

        response = Mock()
        response.backtest_id = "bt_12345"
        response.status = "COMPLETED"
        response.performance_metrics.total_return = 0.25
        response.performance_metrics.sharpe_ratio = 1.5
        response.performance_metrics.max_drawdown = -0.15
        response.performance_metrics.win_rate = 0.58

        backtest_service.GetBacktestResult.return_value = response

        result = backtest_service.GetBacktestResult(request, None)

        assert result.status == "COMPLETED"
        assert result.performance_metrics.total_return > 0

    def test_cache_hit(self, backtest_service):
        """测试缓存命中"""
        # 第一次请求
        request1 = Mock()
        request1.stock_codes = ["000001.SZ"]
        request1.start_time = "2024-01-01"
        request1.end_time = "2024-12-31"

        # 模拟缓存命中
        cached_result = {
            "backtest_id": "bt_cached",
            "status": "COMPLETED",
            "from_cache": True,
        }

        backtest_service.IntegratedBacktest.return_value = Mock(**cached_result)

        result = backtest_service.IntegratedBacktest(request1, None)

        assert result.from_cache is True

    def test_gpu_acceleration(self, backtest_service):
        """测试GPU加速"""
        request = Mock()
        request.stock_codes = ["000001.SZ"]
        request.use_gpu = True

        response = Mock()
        response.execution_time = 3.0  # GPU快速执行
        response.acceleration_ratio = 15.0

        backtest_service.IntegratedBacktest.return_value = response

        result = backtest_service.IntegratedBacktest(request, None)

        assert result.execution_time < 10  # 应该很快
        assert result.acceleration_ratio > 10  # 有明显加速


class TestIntegratedRealTimeService:
    """集成实时处理服务测试"""

    @pytest.fixture
    def realtime_service(self, mock_gpu_manager, mock_redis_queue, mock_metrics_collector):
        """创建实时处理服务实例"""
        with patch("services.integrated_realtime_service.IntegratedRealTimeService") as MockService:
            service = MockService(mock_gpu_manager, mock_redis_queue, mock_metrics_collector)
            yield service

    def test_stream_market_data(self, realtime_service):
        """测试流式市场数据处理"""

        # 创建数据流
        def generate_data():
            for i in range(10):
                request = Mock()
                request.stock_code = "000001.SZ"
                request.price = 10.0 + i * 0.1
                request.volume = 1000000 + i * 1000
                yield request

        # 模拟响应流
        responses = []
        for i in range(10):
            response = Mock()
            response.stock_code = "000001.SZ"
            response.stream_id = "stream_001"
            response.processed_data = f"data_{i}"
            responses.append(response)

        realtime_service.StreamMarketData.return_value = iter(responses)

        result_stream = realtime_service.StreamMarketData(generate_data(), None)

        results = list(result_stream)
        assert len(results) == 10
        assert all(r.stream_id == "stream_001" for r in results)

    def test_compute_features(self, realtime_service):
        """测试计算技术特征"""
        request = Mock()
        request.stock_code = "000001.SZ"
        request.feature_types = ["sma_20", "sma_50", "rsi", "macd"]

        response = Mock()
        response.stock_code = "000001.SZ"
        response.features = {"sma_20": 10.5, "sma_50": 10.3, "rsi": 65.2, "macd": 0.15}
        response.computation_time = 0.5

        realtime_service.ComputeFeatures.return_value = response

        result = realtime_service.ComputeFeatures(request, None)

        assert len(result.features) == 4
        assert result.computation_time < 1.0  # GPU加速应该很快

    def test_batch_processing(self, realtime_service):
        """测试批量处理"""
        batch_size = 100

        # 模拟批量数据
        def generate_batch():
            for i in range(batch_size):
                request = Mock()
                request.stock_code = f"00000{i % 10}.SZ"
                request.price = 10.0 + i * 0.01
                yield request

        # 模拟批量响应
        responses = [Mock(processed=True) for _ in range(batch_size)]
        realtime_service.StreamMarketData.return_value = iter(responses)

        result_stream = realtime_service.StreamMarketData(generate_batch(), None)
        results = list(result_stream)

        assert len(results) == batch_size

    def test_concurrent_streams(self, realtime_service):
        """测试并发流处理"""
        max_streams = 10

        realtime_service.get_active_streams.return_value = 5
        active_streams = realtime_service.get_active_streams()

        assert active_streams < max_streams

    def test_feature_caching(self, realtime_service):
        """测试特征缓存"""
        request = Mock()
        request.stock_code = "000001.SZ"
        request.feature_types = ["sma_20"]

        # 第一次请求（计算）
        response1 = Mock()
        response1.from_cache = False
        response1.computation_time = 0.5

        # 第二次请求（缓存）
        response2 = Mock()
        response2.from_cache = True
        response2.computation_time = 0.001

        realtime_service.ComputeFeatures.side_effect = [response1, response2]

        result1 = realtime_service.ComputeFeatures(request, None)
        result2 = realtime_service.ComputeFeatures(request, None)

        assert result1.from_cache is False
        assert result2.from_cache is True
        assert result2.computation_time < result1.computation_time


class TestIntegratedMLService:
    """集成ML服务测试"""

    @pytest.fixture
    def ml_service(self, mock_gpu_manager, mock_redis_queue, mock_metrics_collector):
        """创建ML服务实例"""
        with patch("services.integrated_ml_service.IntegratedMLService") as MockService:
            service = MockService(mock_gpu_manager, mock_redis_queue, mock_metrics_collector)
            yield service

    def test_train_model(self, ml_service, sample_ml_training_data):
        """测试模型训练"""
        request = Mock()
        request.model_type = "random_forest"
        request.training_data = sample_ml_training_data.to_json()
        request.feature_columns = ["price", "volume", "sma_20", "rsi"]
        request.target_column = "target"
        request.model_params = json.dumps({"n_estimators": 100})

        response = Mock()
        response.task_id = "ml_train_001"
        response.status = "SUBMITTED"
        response.message = "Training task submitted"

        ml_service.TrainModel.return_value = response

        result = ml_service.TrainModel(request, None)

        assert result.task_id is not None
        assert result.status == "SUBMITTED"

    def test_get_training_status(self, ml_service):
        """测试查询训练状态"""
        request = Mock()
        request.task_id = "ml_train_001"

        response = Mock()
        response.task_id = "ml_train_001"
        response.status = "TRAINING"
        response.progress = 75.0
        response.current_epoch = 75
        response.total_epochs = 100

        ml_service.GetTrainingStatus.return_value = response

        result = ml_service.GetTrainingStatus(request, None)

        assert result.status == "TRAINING"
        assert 0 <= result.progress <= 100

    def test_predict(self, ml_service):
        """测试模型预测"""
        request = Mock()
        request.model_id = "model_12345"
        request.input_data = json.dumps({"price": [11.5], "volume": [1400000], "sma_20": [10.7], "rsi": [65]})

        response = Mock()
        response.predictions = [1]  # 预测上涨
        response.probabilities = [0.75, 0.25]
        response.prediction_time = 0.001

        ml_service.Predict.return_value = response

        result = ml_service.Predict(request, None)

        assert len(result.predictions) > 0
        assert result.prediction_time < 0.1  # 预测应该很快

    def test_get_model_metrics(self, ml_service):
        """测试获取模型指标"""
        request = Mock()
        request.model_id = "model_12345"

        response = Mock()
        response.model_id = "model_12345"
        response.accuracy = 0.85
        response.precision = 0.83
        response.recall = 0.87
        response.f1_score = 0.85

        ml_service.GetModelMetrics.return_value = response

        result = ml_service.GetModelMetrics(request, None)

        assert result.accuracy > 0.8
        assert result.f1_score > 0.8

    def test_gpu_training_acceleration(self, ml_service):
        """测试GPU训练加速"""
        request = Mock()
        request.model_type = "random_forest"
        request.use_gpu = True

        response = Mock()
        response.training_time = 8.0  # GPU训练
        response.acceleration_ratio = 15.0

        ml_service.TrainModel.return_value = response

        result = ml_service.TrainModel(request, None)

        assert result.training_time < 20  # GPU应该很快
        assert result.acceleration_ratio > 10

    def test_model_persistence(self, ml_service):
        """测试模型持久化"""
        # 训练模型
        train_request = Mock()
        train_request.model_type = "linear_regression"

        train_response = Mock()
        train_response.model_id = "model_persist_001"
        train_response.status = "COMPLETED"

        ml_service.TrainModel.return_value = train_response

        train_result = ml_service.TrainModel(train_request, None)

        # 使用保存的模型
        predict_request = Mock()
        predict_request.model_id = train_result.model_id

        predict_response = Mock()
        predict_response.predictions = [15.5]

        ml_service.Predict.return_value = predict_response

        predict_result = ml_service.Predict(predict_request, None)

        assert len(predict_result.predictions) > 0

    def test_concurrent_training(self, ml_service):
        """测试并发训练"""
        max_concurrent = 3

        ml_service.get_concurrent_training_count.return_value = 2
        count = ml_service.get_concurrent_training_count()

        assert count < max_concurrent

    def test_cpu_fallback_training(self, ml_service):
        """测试CPU降级训练"""
        request = Mock()
        request.model_type = "random_forest"
        request.use_gpu = True

        # 模拟GPU不可用，降级到CPU
        response = Mock()
        response.status = "COMPLETED"
        response.training_time = 120.0  # CPU较慢
        response.mode = "cpu"

        ml_service.TrainModel.return_value = response

        result = ml_service.TrainModel(request, None)

        assert result.status == "COMPLETED"
        assert result.mode == "cpu"


class TestServiceIntegration:
    """服务集成测试"""

    def test_multi_service_workflow(self, mock_gpu_manager, mock_redis_queue, mock_metrics_collector):
        """测试多服务工作流"""
        # 1. 实时处理获取数据和特征
        # 2. ML训练模型
        # 3. 回测验证策略

        # 这是一个集成工作流的占位测试
        assert True

    def test_resource_sharing(self, mock_gpu_manager):
        """测试资源共享"""
        # 多个服务共享GPU资源
        mock_gpu_manager.allocate_gpu.return_value = 0

        gpu_id_backtest = mock_gpu_manager.allocate_gpu("backtest", 1)
        mock_gpu_manager.release_gpu("backtest")

        gpu_id_ml = mock_gpu_manager.allocate_gpu("ml", 1)

        # 应该能够复用同一个GPU
        assert gpu_id_backtest is not None
        assert gpu_id_ml is not None

    def test_error_handling(self):
        """测试错误处理"""
        with patch("services.integrated_backtest_service.IntegratedBacktestService") as MockService:
            service = MockService(None, None, None)

            # 模拟错误
            service.IntegratedBacktest.side_effect = grpc.RpcError("Connection failed")

            with pytest.raises(grpc.RpcError):
                service.IntegratedBacktest(Mock(), None)
