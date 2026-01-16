#!/usr/bin/env python3
"""
连接池配置模块测试套件
提供完整的连接池配置功能测试
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import patch

# 导入被测试的模块
from src.core.connection_pool_config import (
    ConnectionPoolConfig,
    get_pool_config,
    get_optimal_pool_size,
    get_production_pool_config,
    get_development_pool_config,
    get_test_pool_config,
    get_config_for_environment,
)


class TestConnectionPoolConfig:
    """ConnectionPoolConfig 测试类"""

    def test_initialization_with_defaults(self):
        """测试使用默认值的初始化"""
        with patch.dict(os.environ, {}, clear=True):
            config = ConnectionPoolConfig()

            # 连接池基本配置默认值
            assert config.pool_min_connections == 5
            assert config.pool_max_connections == 20
            assert config.pool_timeout == 30
            assert config.pool_recycle == 3600
            assert config.pool_max_queries == 50000
            assert config.pool_max_inactive_connection_lifetime == 300.0

            # 健康检查配置默认值
            assert config.health_check_interval == 60
            assert config.health_check_timeout == 5

            # 监控配置默认值
            assert config.enable_pool_monitoring is True
            assert config.monitoring_interval == 60

    def test_initialization_with_env_vars(self):
        """测试使用环境变量的初始化"""
        env_vars = {
            "POOL_MIN_CONNECTIONS": "10",
            "POOL_MAX_CONNECTIONS": "50",
            "POOL_TIMEOUT": "60",
            "POOL_RECYCLE": "7200",
            "POOL_MAX_QUERIES": "100000",
            "POOL_MAX_INACTIVE_CONNECTION_LIFETIME": "600.5",
            "HEALTH_CHECK_INTERVAL": "120",
            "HEALTH_CHECK_TIMEOUT": "10",
            "ENABLE_POOL_MONITORING": "false",
            "MONITORING_INTERVAL": "30",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConnectionPoolConfig()

            # 验证环境变量被正确读取
            assert config.pool_min_connections == 10
            assert config.pool_max_connections == 50
            assert config.pool_timeout == 60
            assert config.pool_recycle == 7200
            assert config.pool_max_queries == 100000
            assert config.pool_max_inactive_connection_lifetime == 600.5
            assert config.health_check_interval == 120
            assert config.health_check_timeout == 10
            assert config.enable_pool_monitoring is False
            assert config.monitoring_interval == 30

    def test_from_env_class_method(self):
        """测试类方法from_env"""
        with patch.dict(os.environ, {"POOL_MAX_CONNECTIONS": "15"}, clear=True):
            config = ConnectionPoolConfig.from_env()
            assert isinstance(config, ConnectionPoolConfig)
            assert config.pool_max_connections == 15

    def test_validate_config_success(self):
        """测试有效配置验证"""
        env_vars = {
            "POOL_MIN_CONNECTIONS": "5",
            "POOL_MAX_CONNECTIONS": "20",
            "POOL_TIMEOUT": "30",
            "POOL_RECYCLE": "3600",
            "HEALTH_CHECK_INTERVAL": "60",
            "HEALTH_CHECK_TIMEOUT": "5",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConnectionPoolConfig()
            result = config.validate_config()
            assert result is True

    def test_validate_config_min_connections_too_low(self):
        """测试最小连接数过低"""
        env_vars = {
            "POOL_MIN_CONNECTIONS": "0",  # 无效值
            "POOL_MAX_CONNECTIONS": "20",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConnectionPoolConfig()
            with pytest.raises(
                ValueError, match="Minimum connections must be at least 1"
            ):
                config.validate_config()

    def test_validate_config_max_less_than_min(self):
        """测试最大连接数小于最小连接数"""
        env_vars = {
            "POOL_MIN_CONNECTIONS": "20",
            "POOL_MAX_CONNECTIONS": "10",  # 小于最小值
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConnectionPoolConfig()
            with pytest.raises(
                ValueError,
                match="Maximum connections must be greater than or equal to minimum connections",
            ):
                config.validate_config()

    def test_validate_config_timeout_too_low(self):
        """测试连接超时时间过低"""
        env_vars = {
            "POOL_TIMEOUT": "0"  # 无效值
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConnectionPoolConfig()
            with pytest.raises(
                ValueError, match="Connection timeout must be at least 1"
            ):
                config.validate_config()

    def test_validate_config_recycle_negative(self):
        """测试连接回收时间为负数"""
        env_vars = {
            "POOL_RECYCLE": "-1"  # 负数
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConnectionPoolConfig()
            with pytest.raises(
                ValueError, match="Connection recycle time must be non-negative"
            ):
                config.validate_config()

    def test_validate_config_health_check_interval_too_low(self):
        """测试健康检查间隔过低"""
        env_vars = {
            "HEALTH_CHECK_INTERVAL": "0"  # 无效值
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConnectionPoolConfig()
            with pytest.raises(
                ValueError, match="Health check interval must be at least 1"
            ):
                config.validate_config()

    def test_validate_config_health_check_timeout_too_low(self):
        """测试健康检查超时时间过低"""
        env_vars = {
            "HEALTH_CHECK_TIMEOUT": "0"  # 无效值
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConnectionPoolConfig()
            with pytest.raises(
                ValueError, match="Health check timeout must be at least 1"
            ):
                config.validate_config()

    def test_validate_config_boundary_values(self):
        """测试边界值验证"""
        env_vars = {
            "POOL_MIN_CONNECTIONS": "1",  # 最小有效值
            "POOL_MAX_CONNECTIONS": "1",  # 等于最小值
            "POOL_TIMEOUT": "1",  # 最小有效值
            "POOL_RECYCLE": "0",  # 最小有效值
            "HEALTH_CHECK_INTERVAL": "1",  # 最小有效值
            "HEALTH_CHECK_TIMEOUT": "1",  # 最小有效值
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConnectionPoolConfig()
            result = config.validate_config()
            assert result is True

    def test_get_pool_config_dict(self):
        """测试获取连接池配置字典"""
        env_vars = {
            "POOL_MIN_CONNECTIONS": "5",
            "POOL_MAX_CONNECTIONS": "20",
            "POOL_TIMEOUT": "30",
            "POOL_RECYCLE": "3600",
            "POOL_MAX_QUERIES": "50000",
            "POOL_MAX_INACTIVE_CONNECTION_LIFETIME": "300.0",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConnectionPoolConfig()
            config_dict = config.get_pool_config_dict()

            expected_dict = {
                "min_connections": 5,
                "max_connections": 20,
                "timeout": 30,
                "recycle": 3600,
                "max_queries": 50000,
                "max_inactive_connection_lifetime": 300.0,
            }

            assert config_dict == expected_dict

    def test_monitoring_enabled_variations(self):
        """测试监控启用的各种变体"""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
        ]

        for env_value, expected in test_cases:
            env_vars = {"ENABLE_POOL_MONITORING": env_value}
            with patch.dict(os.environ, env_vars, clear=True):
                config = ConnectionPoolConfig()
                assert config.enable_pool_monitoring == expected, (
                    f"Failed for env_value: {env_value}"
                )

    def test_monitoring_enabled_default(self):
        """测试监控启用的默认值"""
        with patch.dict(os.environ, {}, clear=True):
            config = ConnectionPoolConfig()
            assert config.enable_pool_monitoring is True

    def test_type_conversion_from_string(self):
        """测试从字符串转换各种配置值"""
        env_vars = {
            "POOL_MIN_CONNECTIONS": "10",
            "POOL_MAX_CONNECTIONS": "25",
            "POOL_TIMEOUT": "45",
            "POOL_RECYCLE": "1800",
            "POOL_MAX_QUERIES": "75000",
            "POOL_MAX_INACTIVE_CONNECTION_LIFETIME": "450.75",
            "HEALTH_CHECK_INTERVAL": "90",
            "HEALTH_CHECK_TIMEOUT": "15",
            "MONITORING_INTERVAL": "120",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConnectionPoolConfig()

            # 验证所有类型转换
            assert isinstance(config.pool_min_connections, int)
            assert isinstance(config.pool_max_connections, int)
            assert isinstance(config.pool_timeout, int)
            assert isinstance(config.pool_recycle, int)
            assert isinstance(config.pool_max_queries, int)
            assert isinstance(config.pool_max_inactive_connection_lifetime, float)
            assert isinstance(config.health_check_interval, int)
            assert isinstance(config.health_check_timeout, int)
            assert isinstance(config.monitoring_interval, int)

            # 验证转换后的值
            assert config.pool_min_connections == 10
            assert config.pool_max_connections == 25
            assert config.pool_max_inactive_connection_lifetime == 450.75


class TestGlobalFunctions:
    """全局函数测试类"""

    def test_get_pool_config_singleton(self):
        """测试配置单例模式"""
        with patch.dict(os.environ, {}, clear=True):
            # 清除全局状态
            import src.core.connection_pool_config

            src.core.connection_pool_config._pool_config = None

            config1 = get_pool_config()
            config2 = get_pool_config()

            # 应该返回同一个实例
            assert config1 is config2
            assert isinstance(config1, ConnectionPoolConfig)

    def test_get_pool_config_lazily_initialized(self):
        """测试延迟初始化"""
        with patch.dict(os.environ, {}, clear=True):
            # 清除全局状态
            import src.core.connection_pool_config

            src.core.connection_pool_config._pool_config = None

            # 第一次调用应该创建实例
            config1 = get_pool_config()
            assert isinstance(config1, ConnectionPoolConfig)

            # 第二次调用应该返回已存在的实例
            config2 = get_pool_config()
            assert config1 is config2

    def test_get_optimal_pool_size(self):
        """测试获取最优连接池大小"""
        min_conn, max_conn = get_optimal_pool_size()

        # 验证返回值
        assert isinstance(min_conn, int)
        assert isinstance(max_conn, int)
        assert min_conn == 5  # 基础连接数
        assert max_conn == 20  # 基础连接数 * 4
        assert max_conn <= 50  # 最大限制

    def test_get_production_pool_config_development_env(self):
        """测试开发环境获取生产配置"""
        env_vars = {
            "ENVIRONMENT": "development",  # 非生产环境
            "POOL_MIN_CONNECTIONS": "10",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = get_production_pool_config()

            # 非生产环境应使用环境变量值，不应用生产优化
            assert config.pool_min_connections == 10  # 来自环境变量
            assert config.pool_timeout == 30  # 来自默认值，不是10
            assert config.pool_recycle == 3600  # 来自默认值，不是1800

    def test_get_production_pool_config_production_env(self):
        """测试生产环境获取生产配置"""
        env_vars = {"ENVIRONMENT": "production", "POOL_MIN_CONNECTIONS": "10"}

        with patch.dict(os.environ, env_vars, clear=True):
            config = get_production_pool_config()

            # 生产环境应应用优化配置
            min_conn, max_conn = get_optimal_pool_size()
            assert config.pool_min_connections == min_conn
            assert config.pool_max_connections == max_conn
            assert config.pool_timeout == 10  # 更严格的超时
            assert config.pool_recycle == 1800  # 30分钟
            assert config.enable_pool_monitoring is True
            assert config.monitoring_interval == 30

    def test_get_development_pool_config(self):
        """测试开发环境配置"""
        with patch.dict(os.environ, {}, clear=True):
            config = get_development_pool_config()

            # 验证开发环境特定配置
            assert config.pool_min_connections == 2
            assert config.pool_max_connections == 5
            assert config.pool_timeout == 10
            assert config.pool_recycle == 7200  # 2小时

    def test_get_test_pool_config(self):
        """测试测试环境配置"""
        with patch.dict(os.environ, {}, clear=True):
            config = get_test_pool_config()

            # 验证测试环境特定配置
            assert config.pool_min_connections == 1
            assert config.pool_max_connections == 3
            assert config.pool_timeout == 5
            assert config.pool_recycle == 300  # 5分钟

    def test_get_config_for_environment_production(self):
        """测试根据环境获取配置 - 生产环境"""
        env_vars = {"ENVIRONMENT": "production"}
        with patch.dict(os.environ, env_vars, clear=True):
            config = get_config_for_environment()
            # 应该调用生产配置函数
            assert config.pool_timeout == 10  # 生产环境的特征值

    def test_get_config_for_environment_test(self):
        """测试根据环境获取配置 - 测试环境"""
        env_vars = {"ENVIRONMENT": "test"}
        with patch.dict(os.environ, env_vars, clear=True):
            config = get_config_for_environment()
            # 应该调用测试配置函数
            assert config.pool_min_connections == 1  # 测试环境的特征值

    def test_get_config_for_environment_development(self):
        """测试根据环境获取配置 - 开发环境"""
        env_vars = {"ENVIRONMENT": "development"}
        with patch.dict(os.environ, env_vars, clear=True):
            config = get_config_for_environment()
            # 应该调用开发配置函数
            assert config.pool_min_connections == 2  # 开发环境的特征值

    def test_get_config_for_environment_default(self):
        """测试根据环境获取配置 - 默认环境"""
        with patch.dict(os.environ, {}, clear=True):
            config = get_config_for_environment()
            # 默认应该使用开发环境配置
            assert config.pool_min_connections == 2  # 开发环境的特征值

    def test_get_config_for_environment_case_insensitive(self):
        """测试环境名称大小写不敏感"""
        # 测试大小写不敏感的环境处理
        with patch.dict(os.environ, {"ENVIRONMENT": "PRODUCTION"}, clear=True):
            config = get_config_for_environment()
            # 验证确实调用了正确的环境配置函数（通过返回配置的特征值）
            # PRODUCTION会被转换为小写'production'，应该调用get_production_pool_config
            # get_production_pool_config的特征是会将min_connections设置为get_optimal_pool_size()的结果
            min_conn, max_conn = get_optimal_pool_size()
            assert config.pool_min_connections == min_conn  # 验证调用了production配置

        with patch.dict(os.environ, {"ENVIRONMENT": "TEST"}, clear=True):
            config = get_config_for_environment()
            # TEST会被转换为小写'test'，应该调用get_test_pool_config
            assert config.pool_min_connections == 1  # test环境特征值

        with patch.dict(os.environ, {"ENVIRONMENT": "DEVELOPMENT"}, clear=True):
            config = get_config_for_environment()
            # DEVELOPMENT会被转换为小写'development'，应该调用get_development_pool_config
            assert config.pool_min_connections == 2  # development环境特征值


class TestConnectionPoolConfigEdgeCases:
    """ConnectionPoolConfig 边界情况测试类"""

    def test_extreme_connection_numbers(self):
        """测试极端连接数配置"""
        env_vars = {
            "POOL_MIN_CONNECTIONS": "1",  # 最小值
            "POOL_MAX_CONNECTIONS": "1000",  # 大值
            "POOL_MAX_QUERIES": "1000000",  # 大值
            "POOL_TIMEOUT": "600",  # 10分钟
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConnectionPoolConfig()

            # 验证极端值
            assert config.pool_min_connections == 1
            assert config.pool_max_connections == 1000
            assert config.pool_max_queries == 1000000
            assert config.pool_timeout == 600

            # 验证配置仍然有效
            result = config.validate_config()
            assert result is True

    def test_floating_point_precision(self):
        """测试浮点数精度处理"""
        env_vars = {"POOL_MAX_INACTIVE_CONNECTION_LIFETIME": "333.3333333333333"}

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConnectionPoolConfig()
            assert config.pool_max_inactive_connection_lifetime == 333.3333333333333

    def test_empty_string_env_vars(self):
        """测试空字符串环境变量"""
        env_vars = {
            "POOL_MAX_CONNECTIONS": "",  # 空字符串
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # 空字符串在int()转换时会抛出ValueError
            with pytest.raises(ValueError):
                ConnectionPoolConfig()

    def test_invalid_number_formats(self):
        """测试无效数字格式"""
        invalid_values = ["abc", "12.34.56", "1e2e3", "NaN", "inf"]

        for invalid_value in invalid_values:
            env_vars = {"POOL_MAX_CONNECTIONS": invalid_value}

            with patch.dict(os.environ, env_vars, clear=True):
                with pytest.raises(ValueError):
                    ConnectionPoolConfig()

    def test_config_immutability_after_validation(self):
        """测试验证后配置的不可变性（如果需要）"""
        env_vars = {"POOL_MIN_CONNECTIONS": "5", "POOL_MAX_CONNECTIONS": "20"}

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConnectionPoolConfig()
            config.validate_config()

            # 验证配置在验证后仍然是可修改的（除非有特殊设计）
            original_min = config.pool_min_connections
            config.pool_min_connections = 10
            assert config.pool_min_connections != original_min

    def test_memory_efficiency(self):
        """测试内存使用效率"""
        configs = []

        with patch.dict(os.environ, {}, clear=True):
            # 创建多个配置实例
            for _ in range(1000):
                config = ConnectionPoolConfig()
                configs.append(config)

            # 验证所有实例都有正确的属性
            for config in configs:
                assert hasattr(config, "pool_min_connections")
                assert config.pool_min_connections >= 1

    def test_concurrent_access(self):
        """测试并发访问全局配置"""
        import threading

        def worker():
            # 清除全局状态
            import src.core.connection_pool_config

            src.core.connection_pool_config._pool_config = None

            # 并发获取配置
            for _ in range(100):
                config = get_pool_config()
                assert isinstance(config, ConnectionPoolConfig)

        threads = []
        for _ in range(10):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
