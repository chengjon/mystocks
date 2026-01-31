"""
Pytest配置文件
定义共享的fixtures和测试配置
"""

import os
import sys
from pathlib import Path

import pytest

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def gpu_available():
    """检查GPU是否可用，并在WSL2环境下初始化GPU"""
    try:
        # 检测WSL2环境并初始化GPU
        import platform

        if "microsoft" in platform.uname().release.lower():
            # WSL2环境，需要显式初始化
            import sys

            sys.path.insert(0, str(PROJECT_ROOT))
            from wsl2_gpu_init import initialize_wsl2_gpu

            initialize_wsl2_gpu()

        import cudf

        # 简单的GPU测试
        cudf.DataFrame({"a": [1, 2, 3]})
        return True
    except Exception as e:
        print(f"GPU initialization failed: {e}")
        return False


@pytest.fixture(scope="session")
def redis_available():
    """检查Redis是否可用"""
    try:
        import redis

        r = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0,
        )
        r.ping()
        return True
    except Exception:
        return False


@pytest.fixture
def mock_gpu_manager():
    """模拟GPU资源管理器"""
    from unittest.mock import Mock

    manager = Mock()
    manager.allocate_gpu.return_value = 0  # GPU device ID
    manager.release_gpu.return_value = True
    manager.is_gpu_available.return_value = True
    manager.get_gpu_utilization.return_value = 0.5  # 50% utilization

    return manager


@pytest.fixture
def mock_redis_queue():
    """模拟Redis队列"""
    from unittest.mock import Mock

    queue = Mock()
    queue.enqueue.return_value = "task_12345"
    queue.get_status.return_value = "pending"
    queue.update_status.return_value = True
    queue.get_result.return_value = {"status": "completed"}

    return queue


@pytest.fixture
def mock_metrics_collector():
    """模拟指标收集器"""
    from unittest.mock import Mock

    collector = Mock()
    collector.record_metric.return_value = None
    collector.increment_counter.return_value = None
    collector.observe_histogram.return_value = None

    return collector


@pytest.fixture
def sample_market_data():
    """生成样本市场数据"""
    from datetime import datetime, timedelta

    import numpy as np
    import pandas as pd

    # 生成1000天的数据
    dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(1000)]

    data = {
        "date": dates,
        "open": np.random.uniform(10, 20, 1000),
        "high": np.random.uniform(15, 25, 1000),
        "low": np.random.uniform(8, 15, 1000),
        "close": np.random.uniform(10, 20, 1000),
        "volume": np.random.randint(1000000, 10000000, 1000),
    }

    return pd.DataFrame(data)


@pytest.fixture
def sample_strategy_config():
    """样本策略配置"""
    return {
        "strategy_type": "trend_following",
        "lookback_period": 20,
        "moving_average_window": 50,
        "position_size": 0.1,
        "stop_loss": 0.02,
        "take_profit": 0.05,
    }


@pytest.fixture
def sample_ml_training_data():
    """生成ML训练样本数据"""
    import numpy as np
    import pandas as pd

    n_samples = 10000

    data = {
        "price": np.random.uniform(10, 100, n_samples),
        "volume": np.random.randint(1000000, 100000000, n_samples),
        "sma_20": np.random.uniform(10, 100, n_samples),
        "rsi": np.random.uniform(0, 100, n_samples),
        "macd": np.random.uniform(-5, 5, n_samples),
        "target": np.random.randint(0, 2, n_samples),  # Binary classification
    }

    return pd.DataFrame(data)


@pytest.fixture(scope="session")
def test_config():
    """测试配置"""
    return {
        "gpu_device_id": 0,
        "gpu_memory_fraction": 0.5,
        "max_batch_size": 100,
        "cache_ttl": 60,
        "timeout": 120,
        "max_retries": 3,
    }
